---
# ---------------------------------------------------------------------------
# Canonical example manuscript for the asac-paper-format skill.
# Authors, ORCIDs, e-mails, phones and all numeric results below are
# FICTIONAL placeholders that only exercise every feature of build_paper.py.
# The references are real publications, but verify every one before reuse.
# Copy this file, then replace everything.
# ---------------------------------------------------------------------------
language: en            # language of the article body: en | uk
article_type: original  # original | review | short
udc: "004.852"
year: 2026              # optional; leave out and the end matter shows "20__"
issue: "№ 2 (51)"       # optional; leave out and the end matter shows "№ _ (__)"

title_en: "Adaptive gradient boosting with drift-aware reweighting for tabular process data"
title_uk: "Адаптивний градієнтний бустинг зі зважуванням з урахуванням дрейфу для табличних даних технологічних процесів"

authors:
  - surname_en: Petrenko
    name_en: Ivan
    surname_uk: Петренко
    name_uk: Іван
    patronymic_uk: Олегович
    degree_en: PhD student
    degree_uk: аспірант
    position_en: "Department of Computer Engineering, National Technical University of Ukraine “Igor Sikorsky Kyiv Polytechnic Institute”"
    position_uk: "кафедра обчислювальної техніки, Національний технічний університет України «Київський політехнічний інститут імені Ігоря Сікорського»"
    interests_uk: "машинне навчання на табличних даних, адаптивні системи"
    orcid: "0000-0000-0000-0000"
    email: "i.petrenko@example.com"
    phone: "+380 00 000 00 00"
    corresponding: true
  - surname_en: Kovalenko
    name_en: Olena
    surname_uk: Коваленко
    name_uk: Олена
    patronymic_uk: Василівна
    degree_en: "Candidate of Technical Sciences (PhD)"
    degree_uk: "к.т.н."
    rank_en: Associate Professor
    rank_uk: доцент
    position_en: "Associate Professor of the Department of Computer Engineering, Igor Sikorsky Kyiv Polytechnic Institute"
    position_uk: "доцент кафедри обчислювальної техніки КПІ ім. Ігоря Сікорського"
    interests_uk: "інтелектуальна обробка даних, оптимізація складних систем"
    orcid: "0000-0000-0000-0001"
    email: "o.kovalenko@example.com"

# Structured abstracts: 200-250 words and at most 1800 characters each.
abstract_en:
  problem: >-
    Gradient-boosted decision trees remain the strongest baseline for tabular industrial data, yet
    their accuracy degrades when the statistical properties of a technological process drift between
    the training period and operation. Retraining from scratch is expensive and discards useful history,
    while naive sliding windows react slowly to abrupt changes in the process regime.
  purpose: >-
    The purpose of the study is to develop a reweighting scheme that keeps a boosted ensemble accurate
    under gradual and abrupt drift without full retraining.
  methods: >-
    The proposed method estimates drift with a density-ratio classifier between recent and historical
    windows, converts its scores into bounded sample weights, and appends a small number of trees fitted
    to the reweighted residuals. The approach is evaluated on a simulated heat-exchanger data set
    with injected gradual and abrupt drifts and compared with periodic retraining and a sliding window.
  results: >-
    The reweighted ensemble reduced the mean absolute error after abrupt drift by roughly a quarter
    relative to the sliding window while requiring an order of magnitude fewer new trees than periodic
    retraining; under gradual drift both adaptive variants performed similarly.
  conclusions: >-
    Drift-aware reweighting is a cheap way to extend the useful life of boosted models in adaptive
    control loops; future work will address multivariate drift localisation and online threshold
    selection.
abstract_uk:
  problem: >-
    Ансамблі градієнтного бустингу дерев рішень залишаються найсильнішим базовим підходом для табличних
    промислових даних, проте їхня точність знижується, коли статистичні властивості технологічного
    процесу змінюються між періодом навчання та експлуатацією. Повторне навчання з нуля є дорогим і
    відкидає корисну історію, а наївні ковзні вікна повільно реагують на різкі зміни режиму процесу.
    Відкритим залишається питання, як оновлювати вже навчений ансамбль так, щоб зберегти накопичені
    знання та водночас швидко пристосуватися до нового режиму роботи об'єкта управління.
  purpose: >-
    Мета дослідження — розробити схему зважування, яка зберігає точність бустингового ансамблю за
    поступового та різкого дрейфу без повного перенавчання.
  methods: >-
    Запропонований метод оцінює дрейф за допомогою класифікатора відношення густин між поточним та
    історичним вікнами, перетворює його оцінки на обмежені ваги зразків і додає невелику кількість
    дерев, навчених на зважених залишках. Підхід оцінено на змодельованому наборі даних теплообмінника
    з внесеними поступовим і різким дрейфами та порівняно з періодичним перенавчанням і ковзним вікном
    за однакових гіперпараметрів усіх моделей.
  results: >-
    Зважений ансамбль зменшив середню абсолютну похибку після різкого дрейфу приблизно на чверть
    порівняно з ковзним вікном і потребував на порядок менше нових дерев, ніж періодичне перенавчання;
    за поступового дрейфу обидва адаптивні варіанти показали подібні результати.
  conclusions: >-
    Зважування з урахуванням дрейфу є недорогим способом подовжити строк корисного використання
    бустингових моделей у контурах адаптивного управління; подальші дослідження стосуватимуться
    локалізації багатовимірного дрейфу та онлайн-вибору порогів.

keywords_en: [concept drift, gradient boosting, importance weighting, tabular data, adaptive control, process monitoring]
keywords_uk: [дрейф концепції, градієнтний бустинг, зважування за важливістю, табличні дані, адаптивне управління, моніторинг процесів]

funding: "This work was supported by the Ministry of Education and Science of Ukraine (grant No. 0000-placeholder)."

# DSTU 8302:2015, in the form used by the journal's official sample.
# *Italic* marks the heading author, as in the sample. Add a DOI wherever one exists.
references:
  - "*LeCun, Y.* Deep learning / Y. LeCun, Y. Bengio, G. Hinton // Nature. – 2015. – Vol. 521, No. 7553. – P. 436–444. – DOI: 10.1038/nature14539."
  - "*Breiman, L.* Random forests / L. Breiman // Machine Learning. – 2001. – Vol. 45, No. 1. – P. 5–32. – DOI: 10.1023/A:1010933404324."
  - "*Chen, T.* XGBoost: A scalable tree boosting system / T. Chen, C. Guestrin // Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining. – 2016. – P. 785–794. – DOI: 10.1145/2939672.2939785."
  - "*Ke, G.* LightGBM: A highly efficient gradient boosting decision tree / G. Ke, Q. Meng, T. Finley [et al.] // Advances in Neural Information Processing Systems 30 (NIPS 2017). – 2017. – P. 3146–3154."
  - "*Prokhorenkova, L.* CatBoost: unbiased boosting with categorical features / L. Prokhorenkova, G. Gusev, A. Vorobev, A. V. Dorogush, A. Gulin // Advances in Neural Information Processing Systems 31 (NeurIPS 2018). – 2018. – DOI: 10.48550/arXiv.1706.09516."
  - "*Shwartz-Ziv, R.* Tabular data: Deep learning is not all you need / R. Shwartz-Ziv, A. Armon // Information Fusion. – 2022. – Vol. 81. – P. 84–90. – DOI: 10.1016/j.inffus.2021.11.011."
  - "*Grinsztajn, L.* Why do tree-based models still outperform deep learning on typical tabular data? / L. Grinsztajn, E. Oyallon, G. Varoquaux // Advances in Neural Information Processing Systems 35 (NeurIPS 2022). – 2022. – DOI: 10.48550/arXiv.2207.08815."
  - "*Borisov, V.* Deep neural networks and tabular data: A survey / V. Borisov, T. Leemann, K. Seßler [et al.] // IEEE Transactions on Neural Networks and Learning Systems. – 2024. – Vol. 35, No. 6. – P. 7499–7519. – DOI: 10.1109/TNNLS.2022.3229161."
  - "*Gorishniy, Y.* Revisiting deep learning models for tabular data / Y. Gorishniy, I. Rubachev, V. Khrulkov, A. Babenko // Advances in Neural Information Processing Systems 34 (NeurIPS 2021). – 2021. – DOI: 10.48550/arXiv.2106.11959."
  - "*Paladiiev, O.* The influence of the opponent's color model on the general capabilities of neural networks / O. Paladiiev, O. Lisovychenko // Interdepartmental Scientific-Technical Journal «Adaptive Systems of Automatic Control». – 2022. – Vol. 2, iss. 41. – P. 22–27. – DOI: 10.20535/1560-8956.41.2022.271335."
  - "*Lundberg, S. M.* A unified approach to interpreting model predictions / S. M. Lundberg, S.-I. Lee // Advances in Neural Information Processing Systems 30 (NIPS 2017). – 2017. – DOI: 10.48550/arXiv.1705.07874."
  - "*Pedregosa, F.* Scikit-learn: Machine learning in Python / F. Pedregosa, G. Varoquaux, A. Gramfort [et al.] // Journal of Machine Learning Research. – 2011. – Vol. 12. – P. 2825–2830."
---

# Introduction

Data-driven models are increasingly embedded in adaptive control loops, where they predict quality
indicators or equipment states from tabular sensor records [1]. For such data, ensembles of decision
trees [2] and, above all, gradient-boosted trees [3–5] remain the most reliable choice: several recent
benchmarks show that they still match or outperform deep architectures on typical tabular problems
[6–9]. Similar conclusions hold for applied studies of neural models in this journal [10].

A boosted model, however, is trained on a fixed historical window. When the technological process
changes regime, the joint distribution of inputs and targets drifts and the model degrades. Explaining
which features drive the degradation is possible with attribution methods [11], but explanation alone
does not restore accuracy, and full retraining with standard toolkits [12] discards the knowledge
accumulated before the drift.

The task of this work is therefore to develop and evaluate a drift-aware reweighting scheme that
updates an existing boosted ensemble with a small number of additional trees and keeps its error
bounded under both gradual and abrupt drift.

# Materials and methods

Let $D_h$ be the historical training window and $D_r$ the most recent window of $m$ labelled records.
A probabilistic classifier $c(x)$ is trained to separate $D_r$ (label 1) from $D_h$ (label 0); its output
gives the density-ratio estimate

$$ \hat{r}(x) = \frac{|D_h|}{|D_r|} \cdot \frac{c(x)}{1 - c(x)} $$

where $\hat{r}(x)$ is the estimated ratio of the recent to the historical input density. The ratio is
clipped to obtain bounded sample weights

$$ w_i = \min\left(\max\left(\hat{r}(x_i), w_{\min}\right), w_{\max}\right) $$

where $w_{\min}$ and $w_{\max}$ limit the influence of any single record. The update procedure is:

1. compute the weights $w_i$ for the records of $D_h \cup D_r$;
2. fit $k$ new trees to the weighted residuals of the current ensemble;
3. accept the update if the validation error on $D_r$ decreases, otherwise keep the old ensemble.

The evaluation uses a simulated heat-exchanger process with 12 sensor features and two injected drift
scenarios:

- gradual drift of the fouling coefficient over 5000 records;
- abrupt change of the inlet temperature regime at record 10000.

## Compared configurations

The proposed method is compared with periodic full retraining every 2000 records and with a sliding
window of the last 4000 records. All models share the same hyper-parameters, listed in Table 1.

Table: Hyper-parameters shared by all compared models

| Parameter                 | Value |
|---------------------------|-------|
| Learning rate             | 0.05  |
| Maximum tree depth        | 6     |
| Initial number of trees   | 400   |
| Trees added per update, k | 20    |
| Weight bounds             | 0.2–5 |

# Results

Fig. 1 shows the validation error of the reweighted ensemble during the initial training and after
each update. The error stabilises after about one hundred boosting rounds, which justifies the small
number $k$ of trees added per update.

![Validation error of the reweighted ensemble over boosting rounds](fig1.png){width=13cm}

After the abrupt drift, the reweighted ensemble reduced the mean absolute error by approximately 25 %
compared with the sliding window, while periodic retraining reached a similar error only after its
next scheduled retraining. Under gradual drift, the sliding window and the reweighted ensemble
performed similarly (see Discussion).

# Discussion

The advantage of reweighting is concentrated in the period immediately after an abrupt change: the
density-ratio classifier identifies the new regime from a few hundred records, whereas a sliding
window needs to be filled with post-drift data. Under gradual drift the two adaptive strategies are
equivalent, which agrees with the expectation that slow drift is tracked well by any recency-based
scheme. Compared with periodic retraining, the method adds an order of magnitude fewer trees and
keeps the model history, which matters for embedded controllers with limited memory.

# Conclusions

A drift-aware reweighting scheme for gradient-boosted ensembles has been proposed. It estimates the
density ratio between recent and historical data and converts it into bounded sample weights. The
ensemble is updated with a small number of trees fitted to the reweighted residuals instead of being
retrained. On a simulated heat-exchanger process the method reduced the error after abrupt drift by
about a quarter compared with a sliding window. It achieved this with far fewer new trees than periodic
retraining. The approach is therefore suitable for adaptive control loops with limited computing
resources. Future research will address localisation of multivariate drift and online selection of
the weight bounds.
