# Reference style: splncs04 (Springer proceedings)

LNNS papers built with the llncs template use the **splncs04** style. The entries below follow
the template's own sample (`samplepaper.tex`, 2026) and Springer's instructions. In `paper.md`,
write each entry **without its number**: the builder numbers the list, and `**bold**` marks the
journal volume.

## Rules

1. **Authors.** "Surname, I.", with no space between multiple initials: "Webb, G.I.". Hyphenated
   given names keep the hyphen: "Müller, K.-R.". Separate authors with ", ".
2. **More than six authors.** Give the first author and "et al.": "Ke, G., et al.:".
3. **Colon** after the author list, then the title in sentence case with no quotation marks.
4. **Year** in parentheses at the end of the bibliographic part: "(2016)".
5. **Page ranges** use an en dash: "99–110". In LaTeX that is "--"; in `paper.md`, write "–".
6. **DOI** last, as a URL: "https://doi.org/10.1007/…" (the LaTeX builder turns it into `\doi{…}`).
   Springer strongly encourages DOIs. **Add one only after checking it on doi.org or Crossref.**
7. **Web pages** carry "last accessed YYYY/MM/DD".
8. **Latin alphabet only.**
   1. Transliterate Cyrillic author names (KMU 2010 for Ukrainian).
   2. Translate the title into English in square brackets, or give its official English title.
   3. Add "(in Ukrainian)" at the end.
9. **Journal names** may be abbreviated in ISO 4 style, as in the template ("J. Mach. Learn.
   Res."), or given in full. Pick one and use it consistently.
10. **Order.** Use citation order or alphabetical order by first author (`citation_order` in
    `paper.md`). Use `scripts/renumber_refs.py` to switch between them, because it renumbers the
    citations in the body as well.

## Templates

| Type | splncs04 form |
|---|---|
| Journal article | `Author, F., Author, S.: Title of the article. Journal Abbrev. **2**(5), 99–110 (2016). https://doi.org/10.xxxx/yyyy` |
| Proceedings paper (LNCS/LNNS) | `Author, F., Author, S.: Title of a proceedings paper. In: Editor, F., Editor, S. (eds.) CONFERENCE 2016. LNNS, vol. 999, pp. 1–13. Springer, Cham (2016). https://doi.org/10.1007/978-3-…` |
| Proceedings without editors | `Author, A.-B.: Contribution title. In: 9th International Proceedings on Proceedings, pp. 1–2. Publisher, Location (2010)` |
| IEEE / ACM conference | `Chen, T., Guestrin, C.: XGBoost: a scalable tree boosting system. In: Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, pp. 785–794. ACM, New York (2016). https://doi.org/10.1145/2939672.2939785` |
| Book | `Author, F., Author, S., Author, T.: Book Title. 2nd edn. Publisher, Location (1999)` |
| Book chapter | `Author, F.: Chapter title. In: Editor, A. (ed.) Book Title, pp. 15–30. Publisher, Location (2020)` |
| Preprint | `Author, F., Author, S.: Title. arXiv preprint arXiv:2401.01234 (2024)` |
| Software / data | `Author, F.: Name of the dataset. Figshare (2017). https://doi.org/10.6084/m9.figshare.5235823` |
| Web page | `Name of the Site: Page title. https://example.org/page, last accessed 2026/10/25` |
| Ukrainian source | `Petrenko, I.: Methods of adaptive control [Metody adaptyvnoho keruvannia]. Adapt. Syst. Autom. Control **2**(41), 22–27 (2022). https://doi.org/10.20535/… (in Ukrainian)` |

## Converting from other styles

| From | Change |
|---|---|
| DSTU 8302:2015 (`*Xu, R.* Survey … / R. Xu, D. Wunsch // IEEE … – 2005. – Vol. 16, iss. 3. – P. 645–678.`) | Rebuild it as `Xu, R., Wunsch, D.: Survey … IEEE … **16**(3), 645–678 (2005)`. Drop the "//", "–" separators, "Vol.", "P." and the leading italic author |
| APA (`Li, S., & Deng, W. (2023). Title. Journal, 13(3), 1195–1215.`) | Remove the "&", move the year to the end in parentheses, put a colon after the authors, and turn "13(3)" into "**13**(3)" |
| IEEE (`[1] S. Li and W. Deng, "Title," *Journal*, vol. 13, no. 3, pp. 1195–1215, 2023.`) | Put surnames first, remove the quotation marks and "vol./no./pp.", and move the year to the end |

`check_paper.py` checks the shape of each entry heuristically:

1. an "Authors:" head (`refs.format`);
2. the year in parentheses (`refs.format`);
3. "et al." for more than six authors (`refs.etal`);
4. Latin script (`refs.latin`);
5. DOIs (`refs.doi`);
6. access dates on web references (`refs.url`).

It cannot check punctuation inside titles or the accuracy of the entries themselves. Verify those
against the sources.
