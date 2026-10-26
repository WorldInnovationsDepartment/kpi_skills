"""Scoring backends for the ai-text-detector skill (imported by detect_ai.py and calibrate.py).

Three open methods, all runnable offline on a laptop once the models are cached:

  binoculars  Hans et al., "Spotting LLMs with Binoculars", ICML 2024 (arXiv:2401.12070), BSD-3-Clause
              reference code github.com/ahans30/Binoculars. Zero-shot: score = log-PPL(performer) /
              cross-PPL(observer, performer). LOWER score = more machine-like. The paper's thresholds
              (0.9015 F1-optimal, 0.8536 low-FPR) were tuned for Falcon-7B / Falcon-7B-instruct on
              English; for any other pair run calibrate.py.
  fastdetect  Bao et al., "Fast-DetectGPT", ICLR 2024 (arXiv:2310.05130), MIT, analytic variant with one
              model as sampling and scoring model: conditional probability curvature
              d = (log p(x) - E[log p]) / sqrt(Var[log p]). HIGHER = more machine-like. No universal
              threshold; use calibrate.py.
  desklib     desklib/ai-text-detector-v1.01 (MIT), DeBERTa-v3-large fine-tuned on RAID. Supervised,
              ENGLISH ONLY, outputs a probability. Max 768 tokens.

Model pairs for the zero-shot methods are Qwen3 base/post-trained models (Apache-2.0): Qwen3 lists
Ukrainian among its 119 languages, which is why they are the default here instead of Falcon/Llama.
"""
from __future__ import annotations

import math
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

PAIRS = {
    # size: (observer, performer)   -- observer = base model, performer = instruction-tuned model
    "small": ("Qwen/Qwen3-0.6B-Base", "Qwen/Qwen3-0.6B"),
    "medium": ("Qwen/Qwen3-1.7B-Base", "Qwen/Qwen3-1.7B"),
    "large": ("Qwen/Qwen3-4B-Base", "Qwen/Qwen3-4B"),
    "falcon": ("tiiuae/falcon-7b", "tiiuae/falcon-7b-instruct"),   # the paper's pair; ~28 GB in fp16
}
DESKLIB = "desklib/ai-text-detector-v1.01"

# Paper thresholds (Falcon-7B pair, English). Kept as the uncalibrated fallback with a loud caveat.
BINOCULARS_F1_THRESHOLD = 0.9015310749276843
BINOCULARS_LOW_FPR_THRESHOLD = 0.8536432310785527
DESKLIB_THRESHOLD = 0.5

METHODS = ("binoculars", "fastdetect", "desklib")
# Direction: +1 means a higher score is more AI-like, -1 the opposite.
DIRECTION = {"binoculars": -1, "fastdetect": +1, "desklib": +1}


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def pick_device(requested: str = "auto") -> str:
    import torch
    if requested != "auto":
        return requested
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


@dataclass
class ChunkScore:
    score: float
    tokens: int
    extra: dict | None = None


class _Base:
    name = "base"

    def score(self, text: str, max_tokens: int) -> ChunkScore:  # pragma: no cover - interface
        raise NotImplementedError

    def models(self) -> list[str]:  # pragma: no cover - interface
        return []


class Binoculars(_Base):
    name = "binoculars"

    def __init__(self, observer: str, performer: str, device: str = "auto", dtype: str = "auto"):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.device = pick_device(device)
        if dtype == "auto":
            torch_dtype = torch.float32 if self.device == "cpu" else torch.float16
        else:
            torch_dtype = getattr(torch, dtype)
        self.observer_name, self.performer_name = observer, performer
        t0 = time.time()
        log(f"[binoculars] loading {observer} + {performer} on {self.device} ({torch_dtype}) ...")
        self.tok = AutoTokenizer.from_pretrained(observer)
        if self.tok.pad_token_id is None:
            self.tok.pad_token = self.tok.eos_token
        self.obs = AutoModelForCausalLM.from_pretrained(observer, torch_dtype=torch_dtype).to(self.device).eval()
        self.perf = AutoModelForCausalLM.from_pretrained(performer, torch_dtype=torch_dtype).to(self.device).eval()
        ptok = AutoTokenizer.from_pretrained(performer)
        if ptok.get_vocab() != self.tok.get_vocab():
            raise SystemExit("observer and performer must share a tokenizer (use base + instruct of the same family)")
        log(f"[binoculars] ready in {time.time() - t0:.0f}s")

    def models(self) -> list[str]:
        return [self.observer_name, self.performer_name]

    def score(self, text: str, max_tokens: int = 512) -> ChunkScore:
        import torch
        import torch.nn.functional as F
        enc = self.tok(text, return_tensors="pt", truncation=True, max_length=max_tokens)
        ids = enc["input_ids"].to(self.device)
        if ids.shape[1] < 2:
            return ChunkScore(float("nan"), int(ids.shape[1]))
        with torch.no_grad():
            lo = self.obs(input_ids=ids).logits[:, :-1].float()
            lp = self.perf(input_ids=ids).logits[:, :-1].float()
        labels = ids[:, 1:]
        logp_perf = F.log_softmax(lp, dim=-1)
        ppl = -logp_perf.gather(-1, labels.unsqueeze(-1)).squeeze(-1).mean()           # log-perplexity (performer)
        p_obs = F.softmax(lo, dim=-1)
        x_ppl = -(p_obs * logp_perf).sum(-1).mean()                                       # cross-perplexity
        return ChunkScore(float(ppl / x_ppl), int(ids.shape[1]), {"log_ppl": float(ppl), "x_ppl": float(x_ppl)})


class FastDetectGPT(_Base):
    name = "fastdetect"

    def __init__(self, model: str, device: str = "auto", dtype: str = "auto"):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.device = pick_device(device)
        torch_dtype = (torch.float32 if self.device == "cpu" else torch.float16) if dtype == "auto" else getattr(torch, dtype)
        self.model_name = model
        log(f"[fastdetect] loading {model} on {self.device} ...")
        self.tok = AutoTokenizer.from_pretrained(model)
        self.model = AutoModelForCausalLM.from_pretrained(model, torch_dtype=torch_dtype).to(self.device).eval()

    def models(self) -> list[str]:
        return [self.model_name]

    def score(self, text: str, max_tokens: int = 512) -> ChunkScore:
        import torch
        import torch.nn.functional as F
        ids = self.tok(text, return_tensors="pt", truncation=True, max_length=max_tokens)["input_ids"].to(self.device)
        if ids.shape[1] < 2:
            return ChunkScore(float("nan"), int(ids.shape[1]))
        with torch.no_grad():
            logits = self.model(input_ids=ids).logits[:, :-1].float()
        labels = ids[:, 1:]
        lprobs = F.log_softmax(logits, dim=-1)
        ll = lprobs.gather(-1, labels.unsqueeze(-1)).squeeze(-1)
        probs = lprobs.exp()
        mean_ref = (probs * lprobs).sum(-1)
        var_ref = (probs * lprobs.square()).sum(-1) - mean_ref.square()
        d = (ll.sum() - mean_ref.sum()) / var_ref.sum().clamp_min(1e-6).sqrt()
        return ChunkScore(float(d), int(ids.shape[1]), {"log_likelihood": float(ll.mean())})


class Desklib(_Base):
    name = "desklib"

    def __init__(self, model: str = DESKLIB, device: str = "auto"):
        import torch
        import torch.nn as nn
        from huggingface_hub import hf_hub_download
        from safetensors.torch import load_file
        from transformers import AutoConfig, AutoModel, AutoTokenizer

        # The model card's PreTrainedModel subclass breaks on transformers 5.x, so the checkpoint is loaded by hand:
        # DeBERTa-v3-large encoder ("model.*" keys) + mean pooling + one linear head ("classifier.*" keys).
        class DesklibAIDetectionModel(nn.Module):
            def __init__(self, config):
                super().__init__()
                self.model = AutoModel.from_config(config)
                self.classifier = nn.Linear(config.hidden_size, 1)

            def forward(self, input_ids, attention_mask):
                last_hidden_state = self.model(input_ids=input_ids, attention_mask=attention_mask)[0]
                mask = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
                pooled = (last_hidden_state * mask).sum(1) / torch.clamp(mask.sum(1), min=1e-9)
                return self.classifier(pooled)

        self.device = pick_device(device)
        self.model_name = model
        log(f"[desklib] loading {model} on {self.device} ...")
        self.tok = AutoTokenizer.from_pretrained(model)
        config = AutoConfig.from_pretrained(model)
        net = DesklibAIDetectionModel(config)
        weights = Path(model) / "model.safetensors" if Path(model).is_dir() else Path(hf_hub_download(model, "model.safetensors"))
        state = load_file(str(weights))
        missing, unexpected = net.load_state_dict(state, strict=False)
        missing = [k for k in missing if "position_ids" not in k]
        if missing or unexpected:
            raise SystemExit(f"desklib checkpoint mismatch: missing={missing[:5]} unexpected={unexpected[:5]}")
        self.model = net.to(self.device).eval()

    def models(self) -> list[str]:
        return [self.model_name]

    def score(self, text: str, max_tokens: int = 768) -> ChunkScore:
        import torch
        enc = self.tok(text, padding="max_length", truncation=True, max_length=min(max_tokens, 768), return_tensors="pt")
        with torch.no_grad():
            logits = self.model(enc["input_ids"].to(self.device), enc["attention_mask"].to(self.device))
        prob = float(torch.sigmoid(logits).item())
        return ChunkScore(prob, int(enc["attention_mask"].sum()))


def build(method: str, size: str = "medium", observer: str | None = None, performer: str | None = None,
          device: str = "auto") -> _Base:
    if method == "binoculars":
        o, p = PAIRS[size]
        return Binoculars(observer or o, performer or p, device=device)
    if method == "fastdetect":
        o, _ = PAIRS[size]
        return FastDetectGPT(observer or o, device=device)
    if method == "desklib":
        return Desklib(observer or DESKLIB, device=device)
    raise SystemExit(f"unknown method {method}; choose from {METHODS}")


# ----------------------------------------------------------------------------- thresholds

def default_threshold(method: str) -> tuple[float | None, str]:
    """(threshold, provenance). None = no sensible default, report raw scores only."""
    if method == "binoculars":
        return BINOCULARS_F1_THRESHOLD, "paper default (Falcon-7B pair, English) - UNCALIBRATED for this pair/language"
    if method == "desklib":
        return DESKLIB_THRESHOLD, "model-card default (English only)"
    return None, "no default; run calibrate.py"


def is_ai(method: str, score: float, threshold: float) -> bool:
    if math.isnan(score):
        return False
    return score < threshold if DIRECTION[method] < 0 else score >= threshold


def hf_offline_hint() -> str:
    if os.environ.get("HF_HUB_OFFLINE") == "1":
        return "HF_HUB_OFFLINE=1: models must already be in the cache."
    return "First run downloads the models to ~/.cache/huggingface (0.6B pair ~2.4 GB, 1.7B ~7 GB, 4B ~16 GB)."
