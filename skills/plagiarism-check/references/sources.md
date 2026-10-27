# Free search sources used by `check_web.py`

Last checked: 2026-10-26, from Kyiv (Apple M2 Max, home connection).

| Engine | What it is | Key | Limits observed / documented | Returns |
|---|---|---|---|---|
| `ddgs` | Python library [ddgs 9.16](https://pypi.org/project/ddgs/) (MIT) that scrapes public result pages of DuckDuckGo, Bing, Google, Brave, Yandex, Mojeek, Startpage, Yahoo; `backend="auto"` rotates | none | unofficial; backends answer intermittently and the same query can fail one minute and succeed the next. Probe from this machine (Ukrainian 9-word phrase from a Wikipedia article): quoted phrase on `auto` → 2 hits incl. uk.wikipedia.org (but "No results" on an earlier identical call); a 6-word quoted phrase → nothing on any backend; plain phrase → nothing on `auto`, 5 hits on `yandex` (incl. the right page). English quoted phrase → 5 hits incl. en.wikipedia.org. Hence `search_ddgs` tries quoted/auto, then plain/yandex, then plain/auto. End-to-end on a 1 000-word Ukrainian article: 8 queries → 5 answered, source found | url, title, snippet → page fetched |
| `core` | [CORE API v3](https://core.ac.uk/services/api): ~300 M open-access works, many with full text | optional `CORE_API_KEY` (free registration) | official: anonymous ≈ 5 requests / 10 s; tested anonymously: HTTP 200 and full text in the response for plain queries (Ukrainian included); **HTTP 500 for any quoted phrase** or `fullText:"…"` syntax, so the script sends the plain phrase and relies on relevance ranking. 8 Ukrainian queries → 8 × 5 hits, 0 errors | title, url, **full text** |
| `openalex` | [OpenAlex works search](https://developers.openalex.org) (title/abstract; full-text n-grams for part of the corpus) | `OPENALEX_API_KEY` (free account; keys introduced Feb 2026) or `OPENALEX_MAILTO` | free daily budget (~$0.10/day anonymous, 10× with a key); 429 when exhausted | title, url, abstract only |

Not used, and why:

| Source | Status |
|---|---|
| Google Custom Search JSON API | closed to new customers; existing ones migrate before 2027-01-01 |
| Brave Search API | free tier removed Feb 2026 (metered plans, card required) |
| Bing Web Search API | retired Aug 2025 |
| Serper / Tavily / Exa | commercial; small free quotas, keys, data leaves to a third party |
| Google Scholar | no API; scraping gets blocked |
| Semantic Scholar | free API, abstracts/snippets; rate-limited; would add little over OpenAlex |
| arXiv API | English preprints; CORE already mirrors arXiv full text |
| SearXNG (self-hosted) | would give a stable free meta-search; requires running a server — a good upgrade if ddgs becomes unusable: point `search_ddgs` at it |

Privacy: a query is a 9-word phrase from the manuscript plus nothing else. With 40 queries,
360 words of the text in 9-word pieces reach DuckDuckGo-family servers, CORE and (if
enabled) OpenAlex. Say this to the user before the first run.
