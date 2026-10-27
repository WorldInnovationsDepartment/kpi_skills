# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "python-docx>=1.1",
# ]
# ///
"""Plain-assert (no pytest) regression harness for the brick-writer-121 skill scripts:
brick_common.py, check_chapter.py, brick_status.py.

    uv run tests/brick-writer-121/test_brick.py

Works from any CWD; every fixture (synthetic Ukrainian dissertation parts, a .docx, a project
directory) is generated into a temporary directory, so no real dissertation is needed. Covers: a complete
вступ and a complete розділ 2 that must pass with 0 errors, every major rule on a deliberately broken
variant, .docx input, the whole-project checks B01-B07, JSON output, exit codes and running from another
CWD. Prints a SUMMARY line and exits non-zero on failure.
"""
from __future__ import annotations

import atexit
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from docx import Document

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "skills" / "brick-writer-121" / "scripts"
CHECK, STATUS = SCRIPTS / "check_chapter.py", SCRIPTS / "brick_status.py"
sys.path.insert(0, str(SCRIPTS))
import brick_common as bc  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="brick-test-"))
atexit.register(shutil.rmtree, TMP, ignore_errors=True)
RESULTS = {"pass": 0, "fail": 0, "skip": 0}

N1 = ("Вперше запропоновано модель залежностей мікросервісів програмної системи, яка відрізняється урахуванням "
      "часових вікон відмов, що дозволило прогнозувати каскадні збої з точністю 91 %.")
N2 = ("Удосконалено метод планування розгортання мікросервісів, який відрізняється використанням графа "
      "залежностей, що дозволило зменшити час відновлення на 27 %.")
N3 = ("Удосконалено архітектуру програмної системи оркестрації, яка відрізняється виділенням компонента "
      "прогнозування відмов, що дозволило скоротити простої в 1,8 раза.")
TASKS = [
    "проаналізувати методи оркестрації мікросервісів у хмарних середовищах;",
    "розробити модель залежностей мікросервісів програмної системи;",
    "удосконалити метод планування розгортання мікросервісів;",
    "розробити архітектуру програмної системи оркестрації та перевірити її експериментально.",
]


def vstup(*, novelty=(N1, N2, N3), tasks=TASKS, obj=None, aim=None, drop=(), extra="") -> str:
    obj = obj or ("Об'єктом дослідження є процес розгортання та функціонування мікросервісних програмних систем "
                  "у хмарних середовищах.")
    aim = aim or ("Метою дисертаційної роботи є зменшення часу відновлення мікросервісних програмних систем "
                  "шляхом розроблення методів та архітектури оркестрації.")
    blocks = {
        "relevance": "**Актуальність теми.** Простої хмарних програмних систем коштують операторам до 5 % річного "
                     "доходу [1, 2]. Відомі оркестратори не враховують каскадні відмови мікросервісів [3–5].",
        "link": "**Зв'язок роботи з науковими програмами, планами, темами.** Дослідження виконано в межах НДР "
                "кафедри програмної інженерії «Методи забезпечення надійності програмних систем».",
        "aimhead": "**Мета і завдання дослідження.**",
        "aim": aim,
        "tasks": "Для досягнення мети поставлено такі завдання:\n\n" + "\n".join(f"{k}. {t}" for k, t in enumerate(tasks, 1)),
        "object": obj,
        "subject": "Предметом дослідження є моделі, методи та архітектурні засоби оркестрації мікросервісів.",
        "methods": "**Методи дослідження.** Використано теорію графів, імітаційне моделювання та методи програмної інженерії.",
        "novelty": "**Наукова новизна одержаних результатів:**\n\n" + "\n".join(f"{k}. {t}" for k, t in enumerate(novelty, 1)),
        "practical": "**Практичне значення одержаних результатів.** Розроблену систему впроваджено в ТОВ «Приклад» "
                     "(акт від 12.03.2026).",
        "personal": "**Особистий внесок здобувача.** Усі результати, що виносяться на захист, одержано автором самостійно.",
        "approbation": "**Апробація результатів дисертації.** Результати обговорено на трьох міжнародних конференціях.",
        "publications": "**Публікації.** За темою дисертації опубліковано 4 статті та 3 тези доповідей [6–12].",
        "structure": "**Структура та обсяг дисертації.** Дисертація складається зі вступу, чотирьох розділів, висновків і "
                     "списку джерел. У першому розділі проаналізовано методи оркестрації. У другому розділі "
                     "розроблено модель і метод планування.",
    }
    out = ["# ВСТУП", ""]
    for k, v in blocks.items():
        if k not in drop:
            out += [v, ""]
    out.append(extra)
    return "\n".join(out)


def rozdil2(*, conclusions=True, sub2="2.2", fig_caption=True, fig_cap_num="2.1", formulas=("2.1", "2.2"), extra="",
            concl_items=None) -> str:
    cap = f"Рисунок {fig_cap_num} – Граф залежностей мікросервісів\n" if fig_caption else ""
    f1, f2 = formulas
    out = f"""# РОЗДІЛ 2 МЕТОД ОРКЕСТРАЦІЇ МІКРОСЕРВІСІВ У ХМАРНИХ СИСТЕМАХ

## 2.1 Модель залежностей мікросервісів

Розглянемо програмну систему як орієнтований граф залежностей мікросервісів (рис. 2.1). Вершини графа відповідають
компонентам програмної системи, а ребра — синхронним викликам [12]. Подібні моделі описано в роботах [3, 7] та [1–5].

{cap}
Час відновлення системи після відмови визначається за формулою:

$$ T = \\sum_{{i=1}}^{{n}} t_i \\tag{{{f1}}} $$

Імовірність каскадного збою обчислюється як

W = a / b ({f2})

Вперше запропоновано модель залежностей, яка відрізняється урахуванням часових вікон відмов, що дозволило
прогнозувати каскадні збої з точністю 91 %. Архітектура програмного забезпечення оркестратора містить планувальник
і компонент моніторингу.

## {sub2} Метод планування розгортання

Результати порівняння з базовим оркестратором наведено в табл. 2.1.

Таблиця 2.1 – Час відновлення мікросервісної системи

| Метод | Час відновлення, с |
| Базовий | 41 |
| Запропонований | 30 |

Удосконалений метод зменшив час відновлення на 27 % порівняно з базовим оркестратором. Додаткова архітектура
з прогнозуванням відмов скоротила простої в 1,8 раза. Тестування проведено на кластері з десяти вузлів.

## 2.3 Експериментальна перевірка

### 2.3.1 Стенд для експериментів

Стенд складається з кластера мікросервісів та генератора навантаження для тестування програмної системи.

### 2.3.2 Результати експериментів

Моніторинг системи підтвердив правильність моделі.

{extra}
"""
    if conclusions:
        items = concl_items or [
            "Розроблена модель залежностей дозволяє прогнозувати каскадні збої з точністю 91 %.",
            "Удосконалений метод планування зменшив час відновлення на 27 %.",
            "Архітектура оркестрації скоротила простої в 1,8 раза.",
        ]
        out += "\n## Висновки до розділу 2\n\n" + "\n".join(f"{k}. {t}" for k, t in enumerate(items, 1)) + "\n"
    return out


def run(script: Path, *args, cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script), *map(str, args)], capture_output=True, text=True, cwd=cwd)


def check(name: str, cond: bool, detail: str = ""):
    if cond:
        RESULTS["pass"] += 1
        print(f"[PASS] {name}")
    else:
        RESULTS["fail"] += 1
        print(f"[FAIL] {name}\n{detail[-3000:]}")


def skip(name: str, why: str):
    RESULTS["skip"] += 1
    print(f"[SKIP] {name}: {why}")


def codes(out: str, level: str | None = None) -> set[str]:
    found = set()
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0] in ("ERROR", "WARN", "INFO") and (level is None or parts[0] == level):
            found.add(parts[1].rstrip(":"))
    return found


def mk(name: str, text: str) -> Path:
    p = TMP / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def chk(name: str, text: str, *args, level="ERROR", code=None, expect=True, fname=None) -> subprocess.CompletedProcess:
    """Run check_chapter.py on `text`; assert that `code` is (or is not) reported at `level`."""
    f = mk(fname or f"{name.split(':')[0].replace(' ', '_')}.md", text)
    r = run(CHECK, f, *args)
    got = code in codes(r.stdout, level)
    check(name, got == expect, r.stdout + r.stderr)
    return r


# ---------------------------------------------------------------- project fixtures for brick_status.py

def project(d: Path, *, n_vstup=(N1, N2, N3), n_anot=(N1, N2, N3), n_vys=(N1, N2, N3), tasks=TASKS, n_items_vys=None,
            concl1=True, abbr_list="ОРКС – оркестратор\nХХХХ – невикористане позначення", abbr_text="ОРКС") -> Path:
    d.mkdir(parents=True, exist_ok=True)
    (d / "00-anotatsiia.md").write_text(
        "# АНОТАЦІЯ\n\nДисертація присвячена оркестрації мікросервісів. Наукова новизна одержаних результатів:\n\n"
        + "\n".join(f"{k}. {t}" for k, t in enumerate(n_anot, 1)) + "\n", encoding="utf-8")
    (d / "00b-perelik.md").write_text("# ПЕРЕЛІК УМОВНИХ ПОЗНАЧЕНЬ\n\n" + abbr_list.replace("\n", "\n\n") + "\n", encoding="utf-8")
    (d / "01-vstup.md").write_text(vstup(novelty=n_vstup, tasks=tasks), encoding="utf-8")
    ch1 = ("# РОЗДІЛ 1 АНАЛІЗ МЕТОДІВ ОРКЕСТРАЦІЇ\n\n## 1.1 Огляд оркестраторів\n\nОркестратор мікросервісів керує "
           "розгортанням [1]. Система ОРКС, ОРКС і ще раз ОРКС застосовується широко [2].\n\n## 1.2 Постановка завдання дослідження\n\n"
           "Потрібно зменшити час відновлення програмної системи [3].\n")
    if concl1:
        ch1 += "\n## Висновки до розділу 1\n\n1. Відомі методи не враховують часові вікна відмов.\n"
    (d / "02-rozdil-1.md").write_text(ch1, encoding="utf-8")
    (d / "03-rozdil-2.md").write_text(rozdil2(), encoding="utf-8")
    items = n_items_vys or [f"{k}. {t}" for k, t in enumerate(list(n_vys) + ["Мету дисертаційної роботи досягнуто."], 1)]
    (d / "04-vysnovky.md").write_text("# ВИСНОВКИ\n\n" + "\n".join(items) + "\n", encoding="utf-8")
    (d / "05-spysok.md").write_text(
        "# СПИСОК ВИКОРИСТАНИХ ДЖЕРЕЛ\n\n1. Newman S. Building Microservices. O'Reilly, 2021.\n"
        "2. Іваненко П.П. Оркестрація мікросервісів. Київ: КПІ, 2022. https://doi.org/10.1000/xyz123\n", encoding="utf-8")
    return d


def main() -> int:
    # ------------------------------------------------------------ brick_common unit tests
    s = bc.split_sentences("Результати наведено на рис. 2.1. Автор О.І. Петренко зазначив, що т. д. не потрібно. "
                           "Остання фраза!")
    check("split_sentences keeps «рис.», initials and «т. д.» together",
          len(s) == 3 and s[0].endswith("2.1.") and "О.І. Петренко" in s[1], str(s))
    check("parse_citation: [3, 7], [1–5], [12, с. 40], not a citation",
          bc.parse_citation("3, 7") == [3, 7] and bc.parse_citation("1–5") == [1, 2, 3, 4, 5]
          and bc.parse_citation("12, с. 40") == [12] and bc.parse_citation("N %") is None
          and bc.parse_citation("текст") is None, "")
    check("CHARS_PER_PAGE is 1800", bc.CHARS_PER_PAGE == 1800, "")
    parts = bc.make_parts(bc.parse_blocks(rozdil2(), "md"), "r2.md", "md")
    p = parts[0]
    check("parser: розділ 2 detected with figures/tables/formulas/citations",
          len(parts) == 1 and p.kind == "rozdil" and p.chapter == 2 and len(p.fig_caps) == 1 and len(p.tab_caps) == 1
          and [f["num"] for f in p.formulas] == ["2.1", "2.2"] and len(p.citations) >= 3 and p.concl_index,
          json.dumps(p.to_dict(), ensure_ascii=False)[:800])
    check("pages estimate = chars / 1800", abs(p.pages() - p.chars() / 1800) < 1e-9
          and abs(p.pages(900) - p.chars() / 900) < 1e-9, "")
    plain = "ВСТУП\n\nАктуальність теми. Текст.\n\n2.1 Назва підрозділу\n\nТекст.\n\nВисновки до розділу 2\n\nТекст.\n"
    pp = bc.make_parts(bc.parse_blocks(plain, "txt"), "x.txt", "txt", kind="rozdil", chapter=2)[0]
    check("plain-text headings: «2.1 Назва» and «Висновки до розділу 2» recognised",
          [h["hnum"] for h in pp.headings if h["hnum"]] == ["2.1"] and pp.concl_index, str(pp.headings))
    check("kinds: анотація/вступ/висновки/список/додаток",
          [bc.make_parts(bc.parse_blocks(t, "md"), "x", "md")[0].kind for t in
           ("# АНОТАЦІЯ\n\nТекст.", "# ВСТУП\n\nТекст.", "# ВИСНОВКИ\n\nТекст.", "# СПИСОК ВИКОРИСТАНИХ ДЖЕРЕЛ\n\n1. А.",
            "# ДОДАТОК А\n\nТекст.")] == ["anotatsiia", "vstup", "vysnovky", "spysok", "dodatky"], "")

    # ------------------------------------------------------------ complete вступ
    f = mk("vstup_good.md", vstup())
    r = run(CHECK, f, "--json", TMP / "vstup.json")
    check("complete вступ: exit 0 and no errors", r.returncode == 0 and not codes(r.stdout, "ERROR"), r.stdout + r.stderr)
    check("complete вступ: no N04/N05/N06/N07/N09 warnings", not codes(r.stdout) & {"N04", "N05", "N06", "N07", "N09", "N01"}, r.stdout)
    check("complete вступ: SUMMARY line in sibling format",
          any(l.startswith("SUMMARY: 0 error(s), ") for l in r.stdout.splitlines()), r.stdout)
    d = json.loads((TMP / "vstup.json").read_text(encoding="utf-8"))
    check("--json: findings, parts, summary", d["parts"][0]["kind"] == "vstup" and "findings" in d
          and d["summary"]["ERROR"] == 0 and all({"severity", "code", "message", "location"} <= set(x) for x in d["findings"]),
          json.dumps(d, ensure_ascii=False)[:600])

    # ------------------------------------------------------------ complete розділ 2
    f = mk("rozdil2_good.md", rozdil2())
    r = run(CHECK, f)
    check("complete розділ 2: exit 0 and no errors", r.returncode == 0 and not codes(r.stdout, "ERROR"), r.stdout + r.stderr)
    check("complete розділ 2: no F01/F02/F03/F04/S02/E01 findings",
          not codes(r.stdout) & {"F01", "F02", "F03", "F04", "S01", "S02", "E01", "E03"}, r.stdout)
    check("complete розділ 2: S04 reports pages and the budget", "S04" in codes(r.stdout)
          and "стор." in r.stdout and "25–50" in r.stdout, r.stdout)

    # ------------------------------------------------------------ broken розділ 2
    chk("missing conclusions: S01 ERROR", rozdil2(conclusions=False), code="S01")
    chk("broken numbering (2.1, 2.4): S02 ERROR", rozdil2(sub2="2.4"), code="S02")
    chk("foreign chapter number in a heading: S02 ERROR", rozdil2(sub2="3.2"), code="S02")
    chk("figure referenced without caption: F01 ERROR", rozdil2(fig_caption=False), code="F01")
    chk("caption in the wrong chapter: F02 ERROR", rozdil2(fig_cap_num="3.1"), code="F02")
    chk("formula sequence gap (2.1, 2.3): F04 WARN", rozdil2(formulas=("2.1", "2.3")), level="WARN", code="F04")
    chk("figure caption never referenced: F01 WARN", rozdil2(extra="\nРисунок 2.7 – Зайвий рисунок\n"), level="WARN", code="F01")
    chk("table caption never referenced: F03 WARN", rozdil2().replace("(табл. 2.1)", "(див. нижче)").replace("в табл. 2.1", "нижче"),
        level="WARN", code="F03")
    chk("non-canonical caption: F05 INFO", rozdil2(extra="\nРис. 2.8. Схема.\n"), level="INFO", code="F05")
    chk("number in conclusions not in the body: E01 WARN", rozdil2(concl_items=["Метод зменшив час відновлення на 62 %."]),
        level="WARN", code="E01")
    chk("comparative claim without a number in conclusions: E02 INFO",
        rozdil2(concl_items=["Метод працює краще за базовий оркестратор."]), level="INFO", code="E02")
    chk("results chapter without gradation sentence: N03 WARN",
        rozdil2().replace("Вперше запропоновано", "Запропоновано").replace("Удосконалений", "Новий"), level="WARN", code="N03")
    chk("single child heading (2.3.1 without 2.3.2): S05 WARN", rozdil2().replace("### 2.3.2 Результати експериментів", "Результати."),
        level="WARN", code="S05")
    chk("placeholders [N %] and TODO: E03 ERROR", rozdil2(extra="Покращення становить [N %]. TODO: вставити графік."), code="E03")
    chk("placeholder ??? and FIXME: E03 ERROR", rozdil2(extra="Значення ??? уточнити. FIXME"), code="E03")
    r = chk("Roman XX is not a placeholder", rozdil2(extra="Це характерно для XX століття."), code="E03", expect=False)
    chk("Russian letters: L06 ERROR", rozdil2(extra="Це дает возможность, это ж оцінити сервіс."), code="L06")
    r = chk("calques: L01 WARN with counts", rozdil2(extra="Даний метод являється ефективним, так як об'єм даних зростає. "
                                                  "Система представляє собою набір сервісів; згідно вимог і при допомозі любого тесту."),
            level="WARN", code="L01")
    check("calques: the new entries are reported", all(w in r.stdout for w in ("представляє собою", "згідно вимог", "при допомозі", "любий")),
          r.stdout)
    chk("«існуючий» is INFO only", rozdil2(extra="Існуючий підхід розглянуто."), level="WARN", code="L01", expect=False)
    chk("«існуючий» is reported as INFO", rozdil2(extra="Існуючий підхід розглянуто."), level="INFO", code="L01")
    chk("first person: L02 WARN", rozdil2(extra="Я вважаю, що метод працює."), level="WARN", code="L02")
    chk("first person inside a quote is ignored", rozdil2(extra="Автор процитував: «Я вважаю, що метод працює»."),
        level="WARN", code="L02", expect=False)
    chk("long sentence: L04 INFO", rozdil2(extra=" ".join(["слово"] * 70) + "."), level="INFO", code="L04")
    chk("typography: L07 INFO", rozdil2(extra='Сервіс - це компонент і слово "лапки" та  подвійний пробіл .'), level="INFO", code="L07")
    chk("undefined abbreviation ≥3 times: L03 INFO", rozdil2(extra="ОРКС, ОРКС, ОРКС працює."), level="INFO", code="L03")
    nonse = ("# РОЗДІЛ 2 СТАТИСТИЧНЕ ОЦІНЮВАННЯ ПАРАМЕТРІВ\n\n## 2.1 Оцінки\n\nУ цьому підрозділі розглянуто вибіркові оцінки "
             "середнього та дисперсії для нормального розподілу. Оцінки обчислюють за вибіркою фіксованого обсягу.\n\n"
             "## 2.2 Інтервали\n\nДовірчий інтервал для середнього будують за розподілом Стьюдента.\n\n## Висновки до розділу 2\n\n1. Оцінки побудовано.\n")
    chk("SE lexicon density: N08 INFO on a non-SE chapter", nonse, level="INFO", code="N08")
    # chapter 1
    ch1 = ("# РОЗДІЛ 1 АНАЛІЗ МЕТОДІВ ОРКЕСТРАЦІЇ\n\n## 1.1 Огляд\n\nТекст без жодного посилання на джерела.\n\n"
           "## 1.2 Огляд оркестраторів\n\nІнший текст.\n\n## Висновки до розділу 1\n\n1. Висновок.\n")
    chk("chapter 1 without a problem-statement subsection: S03 WARN", ch1, level="WARN", code="S03")
    chk("chapter 1 without citations: C01 WARN", ch1, level="WARN", code="C01")
    chk("max-ref: citation beyond the list: C02 WARN", rozdil2(extra="Див. [250]."), "--max-ref", "100", level="WARN", code="C02")
    chk("first-citation-order gap: C02 WARN", "# РОЗДІЛ 1 АНАЛІЗ\n\n## 1.1 Огляд\n\nПерше [1], третє [3].\n\n## 1.2 Постановка завдання\n\nДруге [2].\n\n## Висновки до розділу 1\n\n1. Так.\n",
        "--first-citation-order", level="WARN", code="C02")
    chk("mixed citation styles: C03 INFO", rozdil2(extra="Див. також (Newman, 2021)."), level="INFO", code="C03")

    # ------------------------------------------------------------ broken вступ
    chk("novelty item without a gradation marker: N01 ERROR",
        vstup(novelty=(N1, "Розроблено систему оркестрації, яка дозволила зменшити час відновлення архітектури.")), code="N01")
    chk("novelty block missing: N01 ERROR", vstup(drop=("novelty",)), code="N01")
    chk("missing mandatory block (особистий внесок): N04 ERROR", vstup(drop=("personal",)), code="N04")
    chk("missing chapter overview: N04 WARN", vstup().replace("У першому розділі проаналізовано методи оркестрації. У другому розділі "
                                                              "розроблено модель і метод планування.", "Додатки містять акти."),
        level="WARN", code="N04")
    chk("object is not a process: N05 WARN", vstup(obj="Об'єктом дослідження є мікросервісна програмна система."), level="WARN", code="N05")
    chk("aim starts with an infinitive: N06 WARN",
        vstup(aim="Мета дисертаційної роботи — розробити методи та архітектуру оркестрації мікросервісів."), level="WARN", code="N06")
    chk("tasks not starting with an infinitive: N07 WARN",
        vstup(tasks=("Аналіз методів оркестрації;", "розробити модель залежностей;", "Розробка архітектури системи.")),
        level="WARN", code="N07")
    chk("novelty item without distinction/effect: N02 WARN",
        vstup(novelty=(N1, "Вперше запропоновано алгоритм маршрутизації запитів.")), level="WARN", code="N02")
    chk("no architecture among novelty items: N09 WARN", vstup(novelty=(N1, N2)), level="WARN", code="N09")
    chk("annotation novelty without markers: N01 WARN (no block, no markers)",
        "# АНОТАЦІЯ\n\nДисертація присвячена оркестрації мікросервісів у хмарних системах.\n", level="WARN", code="N01")

    # ------------------------------------------------------------ whole-dissertation single file is split
    whole = TMP / "whole.md"
    whole.write_text(vstup() + "\n\n" + rozdil2() + "\n\n# ВИСНОВКИ\n\n1. Висновок.\n", encoding="utf-8")
    r = run(CHECK, whole)
    check("single file with several parts is split (вступ, розділ 2, висновки)",
          all(w in r.stdout for w in ("вступ", "розділ 2", "загальні висновки")) and r.returncode == 0, r.stdout)
    r = run(CHECK, whole, "--kind", "rozdil", "--chapter", "2", "--no-split")
    check("--kind/--chapter override: whole file treated as one розділ 2", "STRUCTURE" in r.stdout and "розділ 2" in r.stdout
          and "S02" not in codes(r.stdout), r.stdout)

    # general conclusions vs chapters (E01 with --body)
    chapters = TMP / "chapters"
    chapters.mkdir()
    (chapters / "r2.md").write_text(rozdil2(), encoding="utf-8")
    vys_ok = mk("vys_ok.md", "# ВИСНОВКИ\n\n1. Метод зменшив час відновлення на 27 %.\n")
    vys_bad = mk("vys_bad.md", "# ВИСНОВКИ\n\n1. Метод зменшив час відновлення на 55 %.\n")
    r1, r2 = run(CHECK, vys_ok, "--body", chapters), run(CHECK, vys_bad, "--body", chapters)
    check("загальні висновки: number found in chapters passes, missing number: E01 WARN",
          "E01" not in codes(r1.stdout, "WARN") and "E01" in codes(r2.stdout, "WARN"), r1.stdout + r2.stdout)

    # ------------------------------------------------------------ .docx input
    doc = Document()
    doc.add_heading("РОЗДІЛ 2 МЕТОД ОРКЕСТРАЦІЇ МІКРОСЕРВІСІВ У ХМАРНИХ СИСТЕМАХ", 1)
    doc.add_heading("2.1 Модель залежностей мікросервісів", 2)
    doc.add_paragraph("Програмну систему подано графом залежностей мікросервісів (рис. 2.1). Результати наведено в табл. 2.1 [12].")
    doc.add_paragraph("Рисунок 2.1 – Граф залежностей мікросервісів")
    doc.add_paragraph("Таблиця 2.1 – Час відновлення мікросервісної системи")
    t = doc.add_table(rows=2, cols=2)
    t.cell(0, 0).text, t.cell(0, 1).text, t.cell(1, 0).text, t.cell(1, 1).text = "Метод", "Час, с", "Базовий", "41"
    doc.add_heading("2.2 Метод планування", 2)
    doc.add_paragraph("Вперше запропоновано метод, що зменшив час відновлення на 41 %.")
    doc.add_heading("Висновки до розділу 2", 2)
    doc.add_paragraph("Метод зменшив час відновлення на 41 %.")
    dpath = TMP / "r2.docx"
    doc.save(str(dpath))
    r = run(CHECK, dpath, "--json", TMP / "docx.json")
    d = json.loads((TMP / "docx.json").read_text(encoding="utf-8"))
    pp = d["parts"][0]
    check(".docx: headings via styles, caption, table; 0 errors",
          r.returncode == 0 and pp["kind"] == "rozdil" and pp["chapter"] == 2 and pp["figures"] == 1 and pp["tables"] == 1
          and pp["headings"] == 4 and pp["has_conclusions"], r.stdout + json.dumps(pp, ensure_ascii=False)[:500])
    text, fmt = bc.load_text(dpath)
    check(".docx: table cells joined with ' | '", fmt == "docx" and "| Метод | Час, с |" in text and "# РОЗДІЛ 2" in text, text)
    doc2 = Document()
    doc2.add_heading("РОЗДІЛ 2 МЕТОД", 1)
    doc2.add_heading("2.1 Перше", 2)
    doc2.add_heading("2.3 Третє", 2)
    doc2.save(str(TMP / "bad.docx"))
    r = run(CHECK, TMP / "bad.docx")
    check(".docx: broken numbering and missing conclusions are caught", {"S01", "S02"} <= codes(r.stdout, "ERROR"), r.stdout)

    # ------------------------------------------------------------ exit codes / errors / CWD
    r = run(CHECK, TMP / "missing.md")
    check("missing file: exit 2 with a clean error", r.returncode == 2 and r.stderr.startswith("error:"), r.stdout + r.stderr)
    pdf = TMP / "x.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    r = run(CHECK, pdf)
    check("PDF: exit 2 and the pdftotext hint", r.returncode == 2 and "pdftotext -layout" in r.stderr, r.stderr)
    r = run(STATUS, pdf)
    check("brick_status on PDF: exit 2", r.returncode == 2, r.stderr)
    r = run(CHECK, rozdil2(conclusions=False) and TMP / "S01.md" if False else mk("noconc.md", rozdil2(conclusions=False)))
    check("exit 1 when there is an ERROR", r.returncode == 1, r.stdout)
    r = run(CHECK, TMP / "rozdil2_good.md", cwd="/")
    check("runs from a different CWD", r.returncode == 0 and "SUMMARY" in r.stdout, r.stdout + r.stderr)
    r = run(CHECK, "rozdil2_good.md", cwd=TMP)
    check("relative path with another CWD", r.returncode == 0, r.stdout + r.stderr)

    # ------------------------------------------------------------ brick_status.py
    good = project(TMP / "proj_good")
    r = run(STATUS, good, "--json", TMP / "status.json", "--md", TMP / "status.md")
    sd = json.loads((TMP / "status.json").read_text(encoding="utf-8"))
    kinds = [row["label"] for row in sd["inventory"]]
    check("status: inventory lists all parts", all(k in kinds for k in ("анотація", "вступ", "розділ 1", "розділ 2", "загальні висновки",
                                                                         "список джерел", "перелік позначень")), str(kinds))
    check("status: consistent novelty gives no B01 and no errors", "B01" not in codes(r.stdout, "ERROR") and "B01" not in codes(r.stdout, "WARN")
          and r.returncode == 0, r.stdout)
    check("status: B04 shares and B06 references INFO", {"B04", "B06"} <= codes(r.stdout, "INFO"), r.stdout)
    check("status: B02 tasks (4) vs conclusions (4) pass", "B02" not in codes(r.stdout, "WARN"), r.stdout)
    check("status: --md written", (TMP / "status.md").exists() and "## Інвентар" in (TMP / "status.md").read_text(encoding="utf-8"), "")
    check("status: B06 counts 2 references and 1 DOI", sd["details"]["references"] == {"count": 2, "latin": 1, "doi": 1}, str(sd["details"]))
    check("status: B03 chapter 1 without conclusions", "B03" not in codes(r.stdout), r.stdout)

    near = N2.replace("зменшити час відновлення на 27 %", "зменшити час відновлення сервісів на 27 %")
    r = run(STATUS, project(TMP / "proj_near", n_vys=(N1, near, N3)))
    check("status B01: one-word difference = WARN «майже збігається», not ERROR",
          "B01" in codes(r.stdout, "WARN") and "майже збігається" in r.stdout and "B01" not in codes(r.stdout, "ERROR"), r.stdout)
    far = ("Удосконалено метод планування розгортання мікросервісів у хмарних середовищах шляхом введення додаткового етапу "
           "попередньої класифікації навантажень і динамічного перерахунку пріоритетів черги.")
    r = run(STATUS, project(TMP / "proj_far", n_anot=(N1, far, N3)))
    check("status B01: same result, very different wording = ERROR, exit 1",
          "B01" in codes(r.stdout, "ERROR") and r.returncode == 1, r.stdout)
    nov = mk("novelty.md", "# Новизна\n\n1. " + N1 + "\n2. " + N2.replace("27 %", "30 %") + "\n3. " + N3 + "\n")
    r = run(STATUS, good, "--novelty", nov)
    check("status --novelty: compares against the single-source file", "novelty" in r.stdout and "B01" in codes(r.stdout), r.stdout)

    r = run(STATUS, project(TMP / "proj_b2", tasks=TASKS, n_items_vys=[f"{k}. Висновок {k}." for k in range(1, 8)]))
    check("status B02: 4 tasks vs 7 conclusions = WARN", "B02" in codes(r.stdout, "WARN"), r.stdout)
    r = run(STATUS, project(TMP / "proj_b2b", tasks=TASKS, n_items_vys=[f"{k}. Висновок {k}." for k in range(1, 7)]))
    check("status B02: 4 tasks vs 6 conclusions (+2 allowed) = ok", "B02" not in codes(r.stdout, "WARN"), r.stdout)
    r = run(STATUS, project(TMP / "proj_b3", concl1=False))
    check("status B03: chapter without «Висновки до розділу» = WARN", "B03" in codes(r.stdout, "WARN") and "розділ 1" in r.stdout, r.stdout)
    r = run(STATUS, good)
    check("status B07: unused listed abbreviation and unlisted frequent one = WARN",
          "B07" in codes(r.stdout, "WARN") and "ХХХХ" in r.stdout, r.stdout)
    pb5 = project(TMP / "proj_b5")
    (pb5 / "04-vysnovky.md").write_text("# ВИСНОВКИ\n\n1. Час відновлення зменшено на 83 %.\n", encoding="utf-8")
    r = run(STATUS, pb5)
    check("status B05: number of the conclusions absent from every chapter = WARN", "B05" in codes(r.stdout, "WARN"), r.stdout)

    r = run(STATUS, whole)
    check("status on one big file: split into parts", "розділ 2" in r.stdout and "вступ" in r.stdout and "INVENTORY" in r.stdout, r.stdout)
    r = run(STATUS, good, cwd="/")
    check("status runs from a different CWD", r.returncode == 0, r.stdout + r.stderr)
    r = run(STATUS, TMP / "no_such_dir")
    check("status: missing path = exit 2", r.returncode == 2, r.stderr)

    print(f"\nSUMMARY: {RESULTS['pass']} passed, {RESULTS['fail']} failed, {RESULTS['skip']} skipped")
    return 1 if RESULTS["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
