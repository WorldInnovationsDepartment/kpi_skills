НАЦІОНАЛЬНИЙ ТЕХНІЧНИЙ УНІВЕРСИТЕТ УКРАЇНИ

«КИЇВСЬКИЙ ПОЛІТЕХНІЧНИЙ ІНСТИТУТ  
ІМЕНІ ІГОРЯ СІКОРСЬКОГО»

МІНІСТЕРСТВО ОСВІТИ І НАУКИ УКРАЇНИ

НАЦІОНАЛЬНИЙ ТЕХНІЧНИЙ УНІВЕРСИТЕТ УКРАЇНИ

«КИЇВСЬКИЙ ПОЛІТЕХНІЧНИЙ ІНСТИТУТ  
ІМЕНІ ІГОРЯ СІКОРСЬКОГО»

МІНІСТЕРСТВО ОСВІТИ І НАУКИ УКРАЇНИ

Кваліфікаційна наукова

праця на умовах рукопису

**БАРАБАШ АНДРІЙ ОЛЕГОВИЧ**

> УДК 004.65

**ДИСЕРТАЦІЯ**

**МОДЕЛІ ТА МЕТОДИ ОБРОБКИ ЗАПИТІВ В ГЕТЕРОГЕННИХ РОЗПОДІЛЕНИХ НЕРЕЛЯЦІЙНИХ БАЗАХ ДАНИХ**

121 – Інженерія програмного забезпечення

12 – Інформаційні технології

Подається на здобуття наукового ступеня доктора філософії

Дисертація містить результати власних досліджень. Використання ідей, результатів і текстів інших авторів мають посилання на відповідне джерело

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ Андрій БАРАБАШ

> Наукові керівники:
>
> доктор технічних наук, професор
>
> Корнага Ярослав Ігорович;
>
> доктор технічних наук, доцент
>
> Мусієнко Андрій Петрович

Київ – 2024

**  
АНОТАЦІЯ**

***Барабаш А.О.*** Моделі та методи обробки запитів в гетерогенних розподілених нереляційних базах даних. – Кваліфікаційна наукова праця на правах рукопису.

Дисертація на здобуття наукового ступеня доктора філософії за спеціальністю 121 «Інженерія програмного забезпечення». – Національний технічний університет України «Київський політехнічний інститут імені Ігоря Сікорського», Київ, 2024.

Актуальність теми. Існуючі методи та засоби організації сучасних гетерогенних розподілених нереляційних баз даних дає змогу зробити висновок, що вони представляють собою складний комплекс у якому потрібно забезпечити високу швидкість, надійність і достовірність запису і вивантаження даних при умові постійних випадкових або зловмисних впливів на передачу інформації і засоби обробки запитів при постійному збільшені обсягу оброблюваних даних. Однак проведення розробки і інтеграції гетерогенних розподілених нереляційних баз даних вимагає виконання синхронізації обробки запитів та їх контролю. Недоліки сучасних систем управління і моніторингу обробки запитів гетерогенних розподілених нереляційних баз даних виникають під час суміщення різнорідних баз даних. Проте застосування звичайних засобів та апаратів моніторингу обробки запитів є недостатнім, тому що вони виконують тільки базові функції та не контролюють функціонування самої гетерогенної розподіленої структури в умовах постійних їх модифікацій.

Питанням побудови складних технічних систем розглядається в великій кількісті наукових робіт, зокрема, О.А. Машкова, Ю.П. Зайченка, В.Г. Лазарева, О.В. Коваля, В.С. Семеніхіна, В.Ф. Колчина, В.К. Попкова, О.В. Барабаша, Мусієнко А.П.,  Г.А. Кучука, Д.М., Обідіна, О.А. Кононова, а також Д. Девіса, Г. Френка, Р. Прима і ін.

Питання щодо відмовостійкості систем розглядалися в роботах А.А. Авіжиєніса, В.А. Машкова, О.Ю. Ільїна, І.Ю. Субача, Ю.М. Коростіля, В.А. Савченка та інших вчених. Питаннями побудови та управління розподіленими системами займались: В.Є. Мухін, Я.І. Корнага, В. Цветков, А. Алпатов, S. Newman, K. Hoffman, K. Horsedal, B. Burns, D. Baleato, S. Koloth, B. Couriol

В наведених роботах досліджувалися питання проектування та оптимізації складних технічних розподілених систем, які володіють певною ефективністю функціонування у залежності від обраного критерія якості: вартості проектування та експлуатації системи чи середнього часу затримки запиту в мережі або надійності елементів системи. В даних роботах приділялася велика увага задачам синтезу живучих та надійних систем. Про те, в даних роботах недостатньо відображені результати щодо визначення ефективного управління гетерогенними розподіленими нереляційними базами даних з структурою середовища зберігання даних, що змінюється з часом. Отже, недосконалість і обмеженість наукових методів для обробки даних, не дозволяє забезпечити повноцінне функціонування гетерогенних розподілених нереляційних баз даних.

В даний час в теорії та практиці створення та застосування існуючих гетерогенних розподіленими нереляційних баз даних загострилося протиріччя між необхідністю сталого функціонування гетерогенних розподілених нереляційних базах даних та можливостями існуючих методів та моделей забезпечити обробку запитів в гетерогенних розподілених нереляційних базах даних.

Для розв’язання протиріччя, яке було визначене, в дисертаційній роботі розвязується актуальне наукове завдання *щодо розробки моделі та методів обробки запитів в гетерогенних розподілених нереляційних базах даних на основі використання вузлів обробки запитів.*

Дисертаційне дослідження виконане відповідно до планів наукової та науково-технічної діяльності Національного технічного університету України «Київський політехнічний інститут імені Ігоря Сікорського» і кафедри інженерії програмного забезпечення в енергетиці та є частиною досліджень в рамках науково-дослідних робіт: «Оптимізація роботи веб-орієнтованих систем з великим набором даних» (державний реєстраційний № 0117U004913, КПІ ім. Ігоря Сікорського, м. Київ), «Методи управління гетерогенними розподіленими базами даних з динамічною структурою на основі мережецентричного підходу» (державний реєстраційний № 0121U109260, КПІ ім. Ігоря Сікорського, м. Київ), які виконує Національний технічний університет України «Київський політехнічний інститут імені Ігоря Сікорського» у 2020 – 2024 р.

Мета дисертаційної роботи полягає в підвищенні ефективності функціонування гетерогенних розподілених нереляційних баз даних шляхом розробки та реалізації моделі та методів обробки даних в розподілених системах.

Основні завдання дослідження включають:

1\. Провести порівняльний аналіз методів і засобів організації сучасних гетерогенних нереляційних розподілених баз даних для визначення особливостей та проблем їх реалізації.

2\. Дослідити методи і засоби підтримки процесу запису, пошуку та захисту даних в гетерогенних нереляційних розподілених баз даних для підвищення швидкості обробки даних та попередження несанкціонованого доступу.

3\. Розробити модель моніторингу обробки запитів у гетерогенних розподілених нереляційних базах даних.

4\. Розробити метод виявлення некоректної роботи вузлів гетерогенних розподілених нереляційних баз даних на основі застосування дворівневої системи контролю обробки запитів Аналіз, розробка та дослідження механізмів та засобів підтримки процедури моніторингу операцій в розподілених базах даних на основі сенсорів подій.

5\. Розробити метод визначення працездатності вузлів обробки запитів гетерогенних розподілених нереляційних баз даних.

6\. Розробити програмне забезпечення комплексної системи управління та перевірки гетерогенного середовища обробки та зберігання даних в нереляційних базах даних.

Об'єктом досліджень є процес обробки запитів в гетерогенних розподілених нереляційних базах даних.

Предметом досліджень є засоби комплексного моніторингу обробки запитів в гетерогенних розподілених нереляційних базах даних на основі вузлів обробки запитів.

Дисертаційні дослідження проводились на основі теорії гетерогенних розподілених нереляційних баз даних із використанням математичних моделей і методів теорії складних систем, дискретної математики та інших. Теоретичні засади функціонування гетерогенних розподілених баз даних будуються із використанням аналітичного моделювання, комбінаторної теорії, теорії графів та дискретної оптимізації. Механізми теорії моделювання спостережень під час використання експериментальних даних та векторно-матричні операції.

Наукова новизна одержаних результатів.

Удосконалено модель моніторингу обробки запитів у гетерогенних розподілених нереляційних базах даних, яка відрізняється від існуючих використанням механізмів на основі застосування матриці обробки запитів. Зазначена модель дозволяє, у випадку виникнення нештатних ситуацій, передати попередження адміністратору серверу моніторингу обробки запитів, прийняти оперативні рішення щодо реагування на порушення безпеки під час обробки даних.

Вперше розроблено метод виявлення некоректної роботи вузлів гетерогенних розподілених нереляційних баз даних на основі застосування дворівневої системи контролю обробки запитів. Наукова новизна даного методу полягає у визначені прихованих несправностей вузла шляхом взаємного обміну запитами між вузлами з урахуванням припущень щодо синхронності гетерогенних розподілених нереляційних баз даних, а також можливості користувачем визначити вузол обробки. Зазначений метод дозволяє здійснювати виявлення випадків некоректної роботи вузлів обробки запитів.

Удосконалено метод визначення працездатності вузлів обробки запитів гетерогенних розподілених нереляційних баз даних, який відрізняється від існуючих способом обробки запитів на основі визначення апостеріорних ймовірностей справного стану вузлів. Зазначений метод дозволяє підвищити ефективність обробки даних.

Вперше розроблено програмне забезпечення комплексної системи управління та перевірки гетерогенного середовища обробки та зберігання даних в нереляційних базах даних, яке базується на розроблених в дисертації моделі моніторингу обробки запитів, методі виявлення некоректної роботи вузлів бази даних та методі визначення працездатності вузлів обробки запитів. Впровадження зазначеного програмного забезпечення дозволяє підвищити ефективність функціонування гетерогенних розподілених нереляційних баз даних.

Практичне значення отриманих результатів. Реалізація запропонованої в дисертації комплексної системи управління та перевірки гетерогенного середовища обробки та зберігання даних в розподілених нереляційних базах даних дозволяє: проектувати і експлуатувати розподілені бази даних; зменшити час, який дається на обробку запитів за рахунок ефективної побудови розподіленої системи; викунувати зміну параметрів в гетерогенній розподіленій системі обробки даних під час динамічної зміни структури комп’ютерної мережі та параметрів; створення гетерогенних розподілених систем з обробкою даних при заданих відповідно заданих обмежень на параметри мережі.

Проведено аналіз ефективності запропонованих засобів моніторингу обробки запитів, який показав, що, відповідно до отриманих експериментальних даних, із збільшенням кількості запитів за даними моніторингу, зменшується кількість помилкових ідентифікацій подій безпеки до 6,4 %, при цьому імовірність помилок ІІ роду знижується до 1,5 %. Це надає можливість стверджувати, що ефективність функціонування гетерогенних розподілених нереляційних баз даних підвищується.

Результати досліджень прийняті до впровадження в Науково-методичному центрі кадрової політики Міністерства оборони України (акт від 16.01.2024 р.), в Конструкторському бюро інформаційних систем КПІ ім. Ігоря Сікорського (акт від 26.12.2023 р.), в ТОВ «Інтехфорвард» (акт від 27.12.2023 р.), в навчальний процес кафедри інженерії програмного забезпечення в енергетиці Національного технічного університету України «Київський політехнічний інститут імені Ігоря Сікорського» при викладанні дисциплін «Бази даних» та «Побудова масштабованих систем обробки даних в реальному часі» для студентів, які навчаються за освітнім рівнем «Бакалавр» спеціальності 121 «Інженерія програмного забезпечення» денної та заочної форми навчання (акт від 12.02.2024 р.).

Реалізація запропонованої в дисертації комплексної системи управління та перевірки гетерогенного середовища обробки та зберігання даних в розподілених нереляційних базах даних дозволяє: проектувати і експлуатувати розподілені бази даних в умовах впливу зовнішніх та внутрішніх факторів; зменшити час обробки запитів за рахунок ефективної побудови розподіленої системи; здійснювати зміну компонентів гетерогенної розподіленої системи обробки даних при постійній зміні структури комп’ютерної мережі і параметрів цієї мережі; створювати гетерогенні розподілені системи з ефективною обробкою даних щодо вказаних обмежень на параметри системи.

Отже, мета дисертаційного дослідження відповідно щодо підвищення ефективності функціонування гетерогенних розподілених нереляційних баз даних шляхом розробки та реалізації моделі та методів обробки даних в розподілених системах, досягнута та всі часткові наукові завдання вирішені у повній мірі. Отримані наукові результати дисертаційного дослідження є внеском у розвиток інформаційних технологій щодо розроблення архітектури та методів побудови багаторівневих систем, для системного аналізу, дослідження, територіально розподілених комп’ютерних систем і мереж із розосередженими розподіленими базами даних, в тому числі і комерційного призначення.

Перспективними шляхами наукових досліджень є розробка та впровадження нових методів та удосконалення існуючих методів підвищення ефективності функціонування та доступності гетерогенних розподілених нереляційних баз даних в умовах впливу внутрішніх та зовнішніх дестабілізуючих факторів

**Ключові слова:** програмне забезпечення, інформаційна технологія, інформаційна система, контроль обробки запитів, база даних, аналіз даних, гетерогенна розподілена нереляційна база даних, обробка запитів, приховані відмови, інциденти безпеки, прийняття рішень, функціональна стійкість, моніторинг, математичне моделювання, комплексна система управління.

**ANOTATION**

**Barabash A.O.** Models and methods of query processing in heterogeneous distributed non-relational databases. – Qualifying scientific work, the manuscript.

Ph.D. thesis for the Doctor of Philosophy degree, with a speciality in 121 Software Engineering. – National Technical University of Ukraine "Igor Sikorsky Kyiv Polytechnic Institute", Kyiv, 2024.

Relevance of the topic. The existing methods and means of organising modern heterogeneous distributed non-relational databases allow us to conclude that they represent a complex in which it is necessary to ensure high speed, reliability and accuracy of data writing and reading under the condition of constant accidental or malicious influences on the transmission of information and means of processing queries with a constant increase in the amount of data processed. However, developing and integrating heterogeneous distributed non-relational databases requires synchronisation of query processing and their control. The disadvantages of modern systems for managing and monitoring the query processing of heterogeneous distributed non-relational databases arise when combining heterogeneous databases. However, the use of conventional means and devices for monitoring query processing is insufficient since they perform only basic functions and do not control the functioning of the heterogeneous distributed structure itself in the conditions of constant modifications.

A large number of scientific works consider the issue of building complex technical systems, in particular, by O.A. Mashkov, Y.P. Zaychenko, V.G. Lazarev, O.V. Koval, V.S. Semenikhin, V.F. Kolchin, V.K. Popkov, O.V. Barabash, A.P. Musienko, G.A. Kuchuk, D.M. Obidin, O.A. Kononov, as well as D. Davis, G. Frank, R. Prim, and others.

The issues of fault tolerance of systems were considered in the works of A.A. Avizienis, V.A. Mashkov, O.Y. Ilyin, I.Y. Subach, Y.M. Korostil, V.A. Savchenko and other scientists. The issues of construction and management of distributed systems were dealt with by: V.E. Mukhin, Y.I. Kornaga, V. Tsvetkov, A. Alpatov, S. Newman, K. Hoffman, K. Horsedal, B. Burns, D. Baleato, S. Koloth, B. Couriol.

The above works investigated the design and optimisation of complex technical distributed systems with a certain efficiency of operation depending on the chosen quality criterion: the cost of designing and operating the system, the average request delay time in the network, or the reliability of the system elements. In these works, much attention was paid to the problems of synthesising survivable and reliable systems. However, these works do not sufficiently reflect the results of determining the effective management of heterogeneous distributed non-relational databases with a data storage environment structure that changes over time. Consequently, the imperfection and limitations of scientific methods for data processing do not allow to ensure the full functioning of heterogeneous distributed non-relational databases.

At present, in the theory and practice of creating and using existing heterogeneous distributed non-relational databases, the contradiction between the need for sustainable operation of heterogeneous distributed non-relational databases and the capabilities of existing methods and models to provide query processing in heterogeneous distributed non-relational databases has become acute.

To resolve the identified contradiction, the dissertation solves the urgent scientific task of *developing a model and methods for processing queries in heterogeneous distributed non-relational databases based on the use of query processing nodes.*

The dissertation research was carried out in accordance with the plans of scientific and technical-scientific activities of the National Technical University of Ukraine "Igor Sikorsky Kyiv Polytechnic Institute" and the Department of Software Engineering in Energy and is a part of the research within the context of research works: "Optimisation of web-oriented systems with a large data set" (state registration No. 0117U004913, Igor Sikorsky Kyiv Polytechnic Institute, Kyiv), "Methods of managing heterogeneous distributed databases with a dynamic structure based on a network-centric approach" (state registration No. 0121U109260, Igor Sikorsky Kyiv Polytechnic Institute, Kyiv), which are being implemented by the National Technical University of Ukraine "Igor Sikorsky Kyiv Polytechnic Institute" from 2020 to 2024.

The purpose of the dissertation is to improve the efficiency of heterogeneous distributed non-relational databases by developing and implementing a model and methods of data processing in distributed systems.

The main objectives of the study include:

1\. To carry out a comparative analysis of methods and means of organising modern heterogeneous non-relational distributed databases to determine the features and problems of their implementation.

2\. To investigate methods and tools to support the process of recording, searching and protecting data in heterogeneous non-relational distributed databases to increase the speed of data processing and prevent unauthorised access.

3\. Develop a model for monitoring query processing in heterogeneous distributed non-relational databases.

4\. To develop a method for detecting incorrect operation of nodes in heterogeneous distributed non-relational databases based on the use of a two-level query processing control system. Analysis, development and research of mechanisms and tools to support the procedure for monitoring operations in distributed databases based on event sensors.

5\. Develop a method for determining the availability of query processing nodes of heterogeneous distributed non-relational databases.

6\. Develop software for an integrated system for managing and verifying a heterogeneous environment that processes and stores data in non-relational databases.

The object of research is the process of query processing in heterogeneous distributed non-relational databases.

The research subject is the means of comprehensive monitoring of query processing in heterogeneous distributed non-relational databases based on query processing nodes.

The dissertation research was carried out on the basis of the theory of heterogeneous distributed non-relational databases using mathematical models and methods of complex systems theory, discrete mathematics and others. The theoretical foundations of the functioning of heterogeneous distributed databases are built using analytical modelling, combinatorial theory, graph theory and discrete optimisation. Mechanisms of the theory of modelling observations using experimental data and vector-matrix operations.

The scientific novelty of the results.

The article improves the model of monitoring query processing in heterogeneous distributed non-relational databases, which differs from the existing ones by using mechanisms based on the query processing matrix. This model allows, in the event of abnormal situations, to transmit a warning to the administrator of the query processing monitoring server and to make prompt decisions on responding to security breaches during data processing.

For the first time, a method for detecting incorrect operation of nodes in heterogeneous distributed non-relational databases has been developed using a two-level query processing control system. This method's scientific novelty is that it identifies hidden node faults by mutually exchanging queries between nodes, taking into account the assumptions about the synchrony of heterogeneous distributed non-relational databases and the user's ability to determine the processing node. This method allows the detection of cases of incorrect operation of query processing nodes.

Improved method for determining the operability of query processing nodes of heterogeneous distributed non-relational databases. This method differs from the existing ones by processing queries based on determining the posteriori probabilities of the nodes' serviceable state. This method allows for increased data processing efficiency. 

For the first time, software for an integrated system for managing and verifying a heterogeneous environment for processing and storing data in non-relational databases has been developed, based on the query processing monitoring model developed in the thesis, a method for detecting incorrect operation of database nodes, and a method for determining the operability of query processing nodes. Implementation of this software allows increasing the efficiency of heterogeneous distributed non-relational databases.

Practical significance of the results. The implementation of the integrated system for managing and verifying a heterogeneous environment for processing and storing data in distributed non-relational databases proposed in this thesis allows to design and operate distributed databases; to reduce the time given for query processing due to the efficient construction of a distributed system; to make a change in parameters in a heterogeneous distributed data processing system during a dynamic shift in the structure of a computer network and parameters; to create heterogeneous distributed systems with data processing under the given constraints on the network parameters.

An analysis of the effectiveness of the proposed means of monitoring query processing is carried out, which shows that, in accordance with the experimental data obtained, with an increase in the number of queries according to the monitoring data, the number of false identifications of security events decreases to 6.4 %, while the probability of type II errors decreases to 1.5 %. This makes it possible to assert that the efficiency of heterogeneous distributed non-relational databases is increasing.

The results of the research were accepted for implementation in the Scientific and Methodological Centre of Personnel Policy of the Ministry of Defence of Ukraine (act of 16.01.2024), in the Design Bureau of Information Systems of Igor Sikorsky Kyiv Polytechnic Institute (act of 26.12.2023), in Intehforward LLC (act of 27.12.2023), in the educational process of the Department of Software Engineering in Energy of the National Technical University of Ukraine "Igor Sikorsky Kyiv Polytechnic Institute" in teaching the disciplines "Databases" and "Building Scalable Real-Time Data Processing Systems" for students studying for a bachelor's degree with speciality 121 "Software Engineering" full-time and part-time (act of 12.02.2024).

The implementation of the complex system for managing and verifying a heterogeneous environment for processing and storing data in distributed non-relational databases proposed in the thesis allows to design and operate distributed databases under the influence of external and internal factors; to reduce query processing time due to the efficient construction of a distributed system; to change the components of a heterogeneous distributed data processing system with constant changes in the structure of a computer network and the parameters of this network; to create heterogeneous distributed systems with efficient data processing with respect to the specified restrictions on network parameters.

Thus, the goal of the dissertation research, respectively, to improve the efficiency of heterogeneous distributed non-relational databases by developing and implementing a model and methods of data processing in distributed systems has been achieved, and all partial scientific tasks have been fully solved. The obtained scientific results of the dissertation research contribute to the development of information technologies for the development of architecture and methods for building multi-level systems, for system analysis and study of geographically distributed computer systems and networks with dispersed distributed databases, including commercial applications. 

Promising areas of research are the development and implementation of new methods and the improvement of existing methods to improve the efficiency of functioning and availability of heterogeneous distributed non-relational databases under the influence of internal and external destabilising factors

**Keywords:** software, information technology, information system, query processing control, database, data analysis, heterogeneous distributed non-relational database, query processing, hidden failures, security incidents, decision making, functional stability, monitoring, mathematical modelling, integrated management system.

**  
**

**СПИСОК ПУБЛІКАЦІЙ ЗДОБУВАЧА**

*Наукові праці, в яких опубліковані основні наукові результати дисертації:*

1\. Корнага Я.І., Барабаш А.О. Математична модель моніторингу подій в системі управління розподіленими базами даних на основі сенсорів подій. Інфокомунікаційні та комп’ютерні технології, 2023, № 1 (05). С. 148 – 153. ISSN 2788-5518

<https://doi.org/10.36994/2788-5518-2023-01-05-17>

https://visn-icct.uu.edu.ua/index.php/icct/issue/view/5

2\. Корнага Я.І., Барабаш А.О. Порівняльний аналіз методів підвищення швидкості пошуку та запису інформації в базах даних. Науковий журнал «Зв'язок», 2022, № 6 (160). С. 32 – 37. ISSN 2412-9070

<https://doi.org/10>.31673/2412-9070.2022.063237

<http://con.dut.edu.ua/index.php/communication/issue/view/164>

3\. Коротков С.С., Барабаш А.О. Проблема семантичних протиріч у великих обсягах даних. Науковий журнал «Зв'язок», 2022, № 3 (157). С. 31 – 34. ISSN 2412-9070

<https://doi.org/10.31673/2412-9070.2022.033133>

<http://con.dut.edu.ua/index.php/communication/issue/view/161>

4\. Михеєв Ю.І., Барабаш А.О. Автоматизація процесу розробки спеціального контенту. Науковий журнал «Наукоємні технології», 2018. Том. 38. № 2. С. 187 – 194.  ISSN 2075-0781 <https://doi.org/10.18372/2310-5461.38.12831>

<http://jrnl.nau.edu.ua/index.php/SBT/issue/view/655>

5\. Вітюк А.Є., Корнага Я.І., Барабаш А.О. Захоплення невідомих об’єктів мобільним роботом із використанням візуальної інформації. Науковий журнал «Вчені записки Таврійського національного університету імені В.І. Вернадсь­кого. Серія: Технічні науки», 2018. Том 29 (68). № 1. Частина 1. С. 93 – 98. ISSN: 2663-5941

<http://www.tech.vernadskyjournals.in.ua/archive?id=16>

*Наукові праці, які засвідчують апробацію матеріалів дисертації*:

6\. Барабаш А.О., Корнага Я.І., Синчук О.В. Удосконалений метод обробки запитів в розподілених базах даних на основі механізму кешування індексів. ІІІ міжнародна науково-практична конференція «Інформаційні моделюючі технології, системи та комплекси» (ІМТСК-2021), 27-28 травня 2021 р., м. Черкаси. Черкаський національний університет імені Богдана Хмельницького, 2021. С. 57 – 60.

<https://fotius.cdu.edu.ua/wp-content/uploads/2021/05/BOOK_IMTCK_2021.pdf>

7\. Корнага Я.І., Барабаш А.О. Методика оцінки часу обробки запитів серверами гетерогенних розподілених баз даних. XXI Всеукраїнська науково-технічна конференція молодих вчених, аспірантів та студентів «Стан, досягнення та перспективи інформаційних систем і технологій», Одеса, 22 – 23 квітня 2021. Одеса, Видавництво ОНАХТ, 2021 р. С. 26 – 28.

8\. Корнага Я., Шиманський М., Барабаш А. Локалізація тексту на зображеннях за допомогою згорткових нейронних мереж. Міжнародна науково-технічна конференція “Security, Fault Tolerance, Intelligence” ICSFTI 2018. м. Київ, 10-12 травня 2018 р. К.: НТУУ «Київський політехнічний інститут імені Ігоря Сікорського». С. 289 – 293. <https://comsys.kpi.ua/icsfti2018>

9\. Барабаш А.О., Коваль М.О. Використанням принципу справедливості під час обслуговування сенсорних мереж. Десята міжнародна науково-практична конференція «Інтегровані інтелектуальні робототехнічні комплекси (ІІРТК-2018)». Збірка тез, м. Київ, 22-23 травня 2018 року. К.: НАУ, 2018. С. 28 – 30.

10\. Mikhieiev Y., Barabash A. Automation of the Special Content Development Process. Proceedings of the 10th International Scientific and Technical Conference on Intellectual Technologies of Linguistic Analysis, 2017, ITLA 2017. Kyiv, Ukraine, October 24-25, 2017. P. 34 – 40. <http://ccs.nau.edu.ua/ru/lingvo>

11\. Собчук В., Харкевич Ю., Кальчук І., Барабаш А. Застосування принципу адаптивного накопичення діагностичної інформації для контролю та діагностування інформаційної системи підприємства. "Інформаційні технології та комп’ютерне моделювання"; матеріали статей Міжнародної науково-практичної конференції, м. Івано-Франківськ, 5-10 липня 2021 року. – Івано-Франківськ, С. 46-48.

12\. Mukhin V., Kornaga Y., Bazaka Y., Krylov I., Barabash A., Yakovleva A., Mukhin O. The Testing Mechanism for Software and Services Based on Mike Cohn’s Testing Pyramid Modification. The 11th IEEE International Conference on Intelligent Data Acquisition and Advanced Computing Systems: Technology and Applications. September 22-25, 2021 . Cracow, Poland. 2021. P. 53 – 60. (Scopus)

13\. Svynchuk О., Barabash A., Laptiev S. and Laptieva T. Modification of Query Processing Methods in Distributed Databases Using Fractal Trees. CEUR Workshop Proceedings, 2021, Vol. 3200. International Scientific and Practical Conference “Information Security and Information Technologies”: Conference Proceedings. 13-19 September 2021. Kharkiv – Odesa, Ukraine. P. 32–37. ISBN 978-966-676-818-9.  (Scopus) <https://drforum.science/conference_collections/>

14\. Лаптєв О.А., Собчук В.В., Барабаш А.О., Мусієнко А.П. Методи структуризації даних щодо відомих вразливостей програмних та апаратних платформ. «Математика. Інформаційні технології. Освіта. 2022 рік»: збірка тез допов. учасник. ХІ Міжнар. наук.-практ. конф., 3–5 червня 2022 р. Луцьк–Світязь: СНУ імені Лесі Українки, 2022. С. 89-95.

15\. Pichkur V., Laptiev O., Polovinkin I., Barabash A., Sobchuk A. and Salanda I. The Method of Managing Man-generated Risks of Critical Infrastructure Systems Based on Ellipsoidal Evaluation. 2022 IEEE 4th International Conference on Advanced Trends in Information Theory (ATIT), 15-17 December 2022, Kyiv, Ukraine, 2022. P. 133 – 137. (Scopus) https://doi.org/10.1109/ATIT58178.2022.10024244.

16\. Мусієнко А.П., Барабаш А.О. Дослідження існуючих засобів підтримки безпечної обробки запитів в гетерогенних розподілених нереляційних базах даних. Перша міжнародна науково-практична конференція «Сучасні аспекти інженерії програмного забезпечення (Modern aspects of Software Engineering)»: Науковий збірник (м. Київ, 14 грудня 2023 р.). Київ: КПІ ім. Ігоря Сікорського, 2023. С. 32 – 33. <https://bit.ly/3ToOyA2>

# ЗМІСТ

[ПЕРЕЛІК УМОВНИХ ПОЗНАЧЕНЬ [19](#_Toc161146750)](#_Toc161146750)

[ВСТУП [20](#_Toc161146751)](#_Toc161146751)

[РОЗДІЛ 1 ПОРІВНЯЛЬНИЙ АНАЛІЗ СУЧАСНИХ РОЗПОДІЛЕНИХ НЕРЕЛЯЦІЙНИХ БАЗ ДАНИХ [31](#_Toc161146752)](#_Toc161146752)

[1.1. Аналіз організації, зберігання та обробки даних в сучасних розподілених нереляційних базах даних [31](#аналіз-організації-зберігання-та-обробки-даних-в-сучасних-розподілених-нереляційних-базах-даних)](#аналіз-організації-зберігання-та-обробки-даних-в-сучасних-розподілених-нереляційних-базах-даних)

[1.2. Дослідження особливостей побудови сучасних систем управління базами даних [35](#дослідження-особливостей-побудови-сучасних-систем-управління-базами-даних)](#дослідження-особливостей-побудови-сучасних-систем-управління-базами-даних)

[1.3. Аналіз організації розподілених нереляційних баз даних [40](#аналіз-організації-розподілених-нереляційних-баз-даних)](#аналіз-організації-розподілених-нереляційних-баз-даних)

[1.4. Дослідження обробки запитів у гетерогенних розподілених нереляційних базах даних [44](#дослідження-обробки-запитів-у-гетерогенних-розподілених-нереляційних-базах-даних)](#дослідження-обробки-запитів-у-гетерогенних-розподілених-нереляційних-базах-даних)

[1.5. Постановка завдання дослідження та часткових завдань дисертації [47](#постановка-завдання-дослідження-та-часткових-завдань-дисертації)](#постановка-завдання-дослідження-та-часткових-завдань-дисертації)

[Висновки до розділу 1 [49](#висновки-до-розділу-1)](#висновки-до-розділу-1)

[РОЗДІЛ 2 ДОСЛІДЖЕННЯ МЕХАНІЗМІВ МОНІТОРИНГУ ОБРОБКИ ЗАПИТІВ В ГЕТЕРОГЕННИХ РОЗПОДІЛЕНИХ НЕРЕЛЯЦІЙНИХ БАЗАХ ДАНИХ [50](#_Toc161146428)](#_Toc161146428)

[2.1. Аналіз засобів підтримки безпечної обробки запитів в гетерогенних розподілених нереляційних базах даних [50](#аналіз-засобів-підтримки-безпечної-обробки-запитів-в-гетерогенних-розподілених-нереляційних-базах-даних)](#аналіз-засобів-підтримки-безпечної-обробки-запитів-в-гетерогенних-розподілених-нереляційних-базах-даних)

[2.2. Дослідження системи моніторингу обробки запитів в гетерогенних розподілених нереляційних базах даних [62](#дослідження-системи-моніторингу-обробки-запитів-в-гетерогенних-розподілених-нереляційних-базах-даних)](#дослідження-системи-моніторингу-обробки-запитів-в-гетерогенних-розподілених-нереляційних-базах-даних)

[2.3. Розробка моделі моніторингу обробки запитів в гетерогенних розподілених нереляційних базах даних на основі модуля контролю обробки запитів [71](#розробка-моделі-моніторингу-обробки-запитів-в-гетерогенних-розподілених-нереляційних-базах-даних-на-основі-модуля-контролю-обробки-запитів)](#розробка-моделі-моніторингу-обробки-запитів-в-гетерогенних-розподілених-нереляційних-базах-даних-на-основі-модуля-контролю-обробки-запитів)

[2.3.1. Загальна архітектура засобів моніторингу обробки запитів нереляційних баз даних на основі модуля контролю обробки запитів [71](#загальна-архітектура-засобів-моніторингу-обробки-запитів-нереляційних-баз-даних-на-основі-модуля-контролю-обробки-запитів)](#загальна-архітектура-засобів-моніторингу-обробки-запитів-нереляційних-баз-даних-на-основі-модуля-контролю-обробки-запитів)

[2.3.2. Архітектура модулю контролю запропонованої системи моніторингу обробки запитів [77](#архітектура-модулю-контролю-запропонованої-системи-моніторингу-обробки-запитів.)](#архітектура-модулю-контролю-запропонованої-системи-моніторингу-обробки-запитів.)

[Висновки до розділу 2 [81](#висновки-до-розділу-2)](#висновки-до-розділу-2)

[РОЗДІЛ 3 РОЗРОБКА МЕТОДУ ВИЗНАЧЕННЯ НЕСПРАВНОСТІ ВУЗЛІВ ОБРОБКИ ЗАПИТІВ В ГЕТЕРОГЕННИХ РОЗПОДІЛЕНИХ НЕРЕЛЯЦІЙНИХ БАЗАХ ДАНИХ НА ОСНОВІ ЗАСТОСУВАННЯ ДВОРІВНЕВОЇ СИСТЕМИ [82](#_Toc1250191)](#_Toc1250191)

[3.1. Вибір і обґрунтування моніторингової моделі гетерогенних розподілених нереляційних базах даних [83](#вибір-і-обґрунтування-моніторингової-моделі-гетерогенних-розподілених-нереляційних-базах-даних)](#вибір-і-обґрунтування-моніторингової-моделі-гетерогенних-розподілених-нереляційних-базах-даних)

[3.2. Розробка алгоритму моніторинг гетерогенних розподілених нереляційних баз даних на основі використання взаємного інформаційного узгодження [86](#розробка-алгоритму-моніторинг-гетерогенних-розподілених-нереляційних-баз-даних-на-основі-використання-взаємного-інформаційного-узгодження)](#розробка-алгоритму-моніторинг-гетерогенних-розподілених-нереляційних-баз-даних-на-основі-використання-взаємного-інформаційного-узгодження)

[3.3. Розробка алгоритму моніторинг гетерогенної розподіленої нереляційної база даних з прихованими несправностями [97](#розробка-алгоритму-моніторинг-гетерогенної-розподіленої-нереляційної-база-даних-з-прихованими-несправностями)](#розробка-алгоритму-моніторинг-гетерогенної-розподіленої-нереляційної-база-даних-з-прихованими-несправностями)

[3.4. Удосконалений метод визначення працездатності вузлів обробки запитів гетерогенних розподілених нереляційних баз даних [105](#удосконалений-метод-визначення-працездатності-вузлів-обробки-запитів-гетерогенних-розподілених-нереляційних-баз-даних)](#удосконалений-метод-визначення-працездатності-вузлів-обробки-запитів-гетерогенних-розподілених-нереляційних-баз-даних)

[3.5. Порівняльні аналітичні оцінки методу визначення працездатності вузлів обробки запитів гетерогенних розподілених нереляційних баз даних [117](#порівняльні-аналітичні-оцінки-методу-визначення-працездатності-вузлів-обробки-запитів-гетерогенних-розподілених-нереляційних-баз-даних)](#порівняльні-аналітичні-оцінки-методу-визначення-працездатності-вузлів-обробки-запитів-гетерогенних-розподілених-нереляційних-баз-даних)

[Висновки до розділу 3 [128](#висновки-до-розділу-3)](#висновки-до-розділу-3)

[РОЗДІЛ 4 РОЗРОБКА ПРОГРАМНОГО ЗАБЕЗПЕЧЕННЯ КОМПЛЕКСНОЇ СИСТЕМИ УПРАВЛІННЯ ТА ПЕРЕВІРКИ ГЕТЕРОГЕННОГО СЕРЕДОВИЩА ОБРОБКИ ТА ЗБЕРІГАННЯ ДАНИХ В НЕРЕЛЯЦІЙНИХ БАЗАХ ДАНИХ [130](#_Toc161146430)](#_Toc161146430)

[4.1. Розробка спеціалізованого фреймворку для дослідження параметрів та способів контролю за обробкою запитів в гетерогенних розподілених нереляційних базах даних [130](#розробка-спеціалізованого-фреймворку-для-дослідження-параметрів-та-способів-контролю-за-обробкою-запитів-в-гетерогенних-розподілених-нереляційних-базах-даних)](#розробка-спеціалізованого-фреймворку-для-дослідження-параметрів-та-способів-контролю-за-обробкою-запитів-в-гетерогенних-розподілених-нереляційних-базах-даних)

[4.2. Графічний інтерфейс розробленого спеціалізованого середовища комплексної системи управління та перевірки [142](#графічний-інтерфейс-розробленого-спеціалізованого-середовища-комплексної-системи-управління-та-перевірки)](#графічний-інтерфейс-розробленого-спеціалізованого-середовища-комплексної-системи-управління-та-перевірки)

[4.3. Комплексна система управління та перевірки гетерогенного середовища зберігання та обробки даних в розподілених нереляційних базах даних [146](#комплексна-система-управління-та-перевірки-гетерогенного-середовища-зберігання-та-обробки-даних-в-розподілених-нереляційних-базах-даних)](#комплексна-система-управління-та-перевірки-гетерогенного-середовища-зберігання-та-обробки-даних-в-розподілених-нереляційних-базах-даних)

[4.3.1. Розробка комплексної системи управління гетерогенними розподіленими нереляційними базами даних [146](#розробка-комплексної-системи-управління-гетерогенними-розподіленими-нереляційними-базами-даних)](#розробка-комплексної-системи-управління-гетерогенними-розподіленими-нереляційними-базами-даних)

[4.3.2. Підсистема управління та перевірки даних комплексної системи управління та перевірки гетерогенного середовища обробки та зберігання даних в нереляційних базах даних [149](#підсистема-управління-та-перевірки-даних-комплексної-системи-управління-та-перевірки-гетерогенного-середовища-обробки-та-зберігання-даних-в-нереляційних-базах-даних)](#підсистема-управління-та-перевірки-даних-комплексної-системи-управління-та-перевірки-гетерогенного-середовища-обробки-та-зберігання-даних-в-нереляційних-базах-даних)

[4.3.3. Підсистема обробки та підготовки даних [150](#підсистема-обробки-та-підготовки-даних)](#підсистема-обробки-та-підготовки-даних)

[4.3.4. Підсистема синхронізації даних з гетерогенних нереляційних СУБД [151](#підсистема-синхронізації-даних-з-гетерогенних-нереляційних-субд)](#підсистема-синхронізації-даних-з-гетерогенних-нереляційних-субд)

[4.4. Експериментальні досліди параметрів засобів моніторингу обробки запитів [152](#експериментальні-досліди-параметрів-засобів-моніторингу-обробки-запитів)](#експериментальні-досліди-параметрів-засобів-моніторингу-обробки-запитів)

[4.5. Розробка рекомендацій по впровадженню запропонованих моделей та методів [157](#розробка-рекомендацій-по-впровадженню-запропонованих-моделей-та-методів)](#розробка-рекомендацій-по-впровадженню-запропонованих-моделей-та-методів)

[Висновки до розділу 4 [160](#висновки-до-розділу-4)](#висновки-до-розділу-4)

[ВИСНОВКИ [162](#_Toc161146431)](#_Toc161146431)

[СПИСОК ВИКОРИСТАНИХ ДЖЕРЕЛ [165](#_Toc161504912)](#_Toc161504912)

[ДОДАТОК А [183](#_Toc161504913)](#_Toc161504913)

[ДОДАТОК Б [188](#_Toc161504914)](#_Toc161504914)

<span id="_Toc161146750" class="anchor"></span>ПЕРЕЛІК УМОВНИХ ПОЗНАЧЕНЬ

АНСА – алгоритм найбільших статистичних аномалій

АС – автоматизована система

БЗ – база знань

БД – база даних

ГРНБД – гетерогенна розподілена нереляційна база даних

ІКС – інформаційно-керуюча система

ІНС – інтелектуальна система

ІС – інформаційна система

ІТ – інформаційна технологія

КСУ – комплексна система управління

ПЗ – програмне забезпечення

РБД – розподілена база даних

РІКС – розподілена інформаційно-керуюча система

РСУБД – розподілена система управління базами даних

СД – сервер додатків

СКЗ – сервер контролю змін

СМОЗ – система моніторингу обробки запитів

СУБД – система управління базами даних

ШІ – штучний інтелект

<span id="_Toc161146751" class="anchor"></span>ВСТУП

**Актуальність теми.**

Існуючі методи та засоби організації сучасних гетерогенних розподілених нереляційних баз даних дає змогу зробити висновок, що вони представляють собою складний комплекс у якому потрібно забезпечити високу швидкість, надійність і достовірність запису і вивантаження даних при умові постійних випадкових або зловмисних впливів на передачу інформації і засоби обробки запитів при постійному збільшені обсягу оброблюваних даних. Однак проведення розробки і інтеграції гетерогенних розподілених нереляційних баз даних вимагає виконання синхронізації обробки запитів та їх контролю. Недоліки сучасних систем управління і моніторингу обробки запитів гетерогенних розподілених нереляційних баз даних виникають під час суміщення різнорідних баз даних. Проте застосування звичайних засобів та апаратів моніторингу обробки запитів є недостатнім, тому що вони виконують тільки базові функції та не контролюють функціонування самої гетерогенної розподіленої структури в умовах постійних їх модифікацій.

Питанням побудови складних технічних систем розглядається в великій кількісті наукових робіт, зокрема, О.А. Машкова, Ю.П. Зайченка, В.Г. Лазарева, О.В. Коваля, В.С. Семеніхіна, В.Ф. Колчина, В.К. Попкова, О.В. Барабаша, А.П. Мусієнка, Г.А. Кучука, Д.М. Обідіна, О.А. Кононова, а також Д. Девіса, Г. Френка, Р. Прима та інш.

Питання щодо відмовостійкості систем розглядалися в роботах А.А. Авіжиєніса, В.А. Машкова, О.Ю. Ільїна, І.Ю. Субача, Ю.М. Коростіля, В.А. Савченка та інших вчених. Питаннями побудови та управління розпо­діленими системами займались: В.Є. Мухін, Я.І. Корнага, В. Цветков, А. Алпатов, S. Newman, K. Hoffman, K. Horsedal, B. Burns, D. Baleato, S. Koloth, B. Couriol

В наведених роботах досліджувалися питання проектування та оптимізації складних технічних розподілених систем, які володіють певною ефективністю функціонування у залежності від обраного критерія якості: вартості проектування та експлуатації системи чи середнього часу затримки запиту в мережі або надійності елементів системи. В даних роботах приділялася велика увага задачам синтезу живучих та надійних систем. Про те, в даних роботах недостатньо відображені результати щодо визначення ефективного управління гетерогенними розподіленими нереляційними базами даних з структурою середовища зберігання даних, що змінюється з часом. Отже, недосконалість і обмеженість наукових методів для обробки даних, не дозволяє забезпечити повноцінне функціонування гетерогенних розподілених нереляційних баз даних.

В даний час в теорії та практиці створення та застосування існуючих гетерогенних розподіленими нереляційних баз даних загострилося протиріччя між необхідністю сталого функціонування гетерогенних розподілених нереляційних базах даних та можливостями існуючих методів та моделей забезпечити обробку запитів в гетерогенних розподілених нереляційних базах даних.

Для розв’язання протиріччя, яке було визначене, в дисертаційній роботі розв’язується актуальне наукове завдання *щодо розробки моделі та методів обробки запитів в гетерогенних розподілених нереляційних базах даних на основі використання вузлів обробки запитів.*

**Зв'язок роботи з науковими програмами, планами, темами.**

Дисертаційне дослідження виконане відповідно до планів наукової та науково-технічної діяльності Національного технічного університету України «Київський політехнічний інститут імені Ігоря Сікорського» і кафедри інженерії програмного забезпечення в енергетиці та є частиною досліджень в рамках науково-дослідних робіт: «Оптимізація роботи веб-орієнтованих систем з великим набором даних» (державний реєстраційний № 0117U004913, КПІ ім. Ігоря Сікорського, м. Київ), «Методи управління гетерогенними розподіленими базами даних з динамічною структурою на основі мережецентричного підходу» (державний реєстраційний № 0121U109260, КПІ ім. Ігоря Сікорського, м. Київ), які виконує Національний технічний університет України «Київський політехнічний інститут імені Ігоря Сікорського» у 2020 – 2024 р.

Особисто автором в НДР «Оптимізація роботи веб-орієнтованих систем з великим набором даних» запропоновано модель моніторингу систем з великим набором даних; в НДР «Методи управління гетерогенними розподіленими базами даних з динамічною структурою на основі мережецентричного підходу» запропоновано метод виявлення некоректної роботи гетерогенних розподілених баз даних на основі об'єктно–орієнтованих підходів, імітаційного моделювання.

**Мета і завдання досліджень.**

**Метою дисертаційної роботи** є підвищення ефективності функціонування гетерогенних розподілених нереляційних баз даних шляхом розробки та реалізації моделі та методів обробки даних в розподілених системах.

*Основні наукові завдання досліджень,* відповідно до мети, полягають в наступному:

1\. Провести порівняльний аналіз методів і засобів організації сучасних гетерогенних нереляційних розподілених баз даних для визначення особливостей та проблем їх реалізації.

2\. Дослідити методи і засоби підтримки процесу запису, пошуку та захисту даних в гетерогенних нереляційних розподілених баз даних для підвищення швидкості обробки даних та попередження несанкціонованого доступу.

3\. Розробити модель моніторингу обробки запитів у гетерогенних розподілених нереляційних базах даних.

4\. Розробити метод виявлення некоректної роботи вузлів гетерогенних розподілених нереляційних баз даних на основі застосування дворівневої системи контролю обробки запитів Аналіз, розробка та дослідження механізмів та засобів підтримки процедури моніторингу операцій в розподілених базах даних на основі сенсорів подій.

5\. Розробити метод визначення працездатності вузлів обробки запитів гетерогенних розподілених нереляційних баз даних.

6\. Розробити програмне забезпечення комплексної системи управління та перевірки гетерогенного середовища обробки та зберігання даних в нереляційних базах даних.

**Об'єктом досліджень** є процес обробки запитів в гетерогенних розподілених нереляційних базах даних.

**Предметом досліджень** є засоби комплексного моніторингу обробки запитів в гетерогенних розподілених нереляційних базах даних на основі вузлів обробки запитів.

**Методи дослідження.** Дисертаційні дослідження проводились на основі теорії гетерогенних розподілених нереляційних баз даних із використанням математичних моделей і методів теорії складних систем, дискретної математики та інших. Теоретичні засади функціонування гетерогенних розподілених баз даних будуються із використанням аналітичного моделювання, комбінаторної теорії, теорії графів та дискретної оптимізації. Механізми теорії моделювання спостережень під час використання експериментальних даних та векторно-матричні операції.

**Наукова новизна одержаних результатів досліджень** полягає в наступному:

1\. Удосконалено модель моніторингу обробки запитів у гетерогенних розподілених нереляційних базах даних, яка відрізняється від існуючих використанням механізмів на основі застосування матриці обробки запитів. Зазначена модель дозволяє, у випадку виникнення нештатних ситуацій, передати попередження адміністратору серверу моніторингу обробки запитів, прийняти оперативні рішення щодо реагування на порушення безпеки під час обробки даних.

2\. Вперше розроблено метод виявлення некоректної роботи вузлів гетерогенних розподілених нереляційних баз даних на основі застосування дворівневої системи контролю обробки запитів. Наукова новизна даного методу полягає у визначені прихованих несправностей вузла шляхом взаємного обміну запитами між вузлами з урахуванням припущень щодо синхронності гетерогенних розподілених нереляційних баз даних, а також можливості користувачем визначити вузол обробки. Зазначений метод дозволяє здійснювати виявлення випадків некоректної роботи вузлів обробки запитів.

3\. Удосконалено метод визначення працездатності вузлів обробки запитів гетерогенних розподілених нереляційних баз даних, який відрізняється від існуючих способом обробки запитів на основі визначення апостеріорних ймовірностей справного стану вузлів. Зазначений метод дозволяє підвищити ефективність обробки даних.

4\. Вперше розроблено програмне забезпечення комплексної системи управління та перевірки гетерогенного середовища обробки та зберігання даних в нереляційних базах даних, яке базується на розроблених в дисертації моделі моніторингу обробки запитів, методі виявлення некоректної роботи вузлів бази даних та методі визначення працездатності вузлів обробки запитів. Впровадження зазначеного програмного забезпечення дозволяє підвищити ефективність функціонування гетерогенних розподілених нереляційних баз даних.

Наукове значення дослідження полягає в розвитку теорії і методів побудови розподілених систем обробки даних на основі засобів підтримки прийняття рішень, комп'ютерного моделювання процесів обробки запитів та побудові гетерогенних інформаційних систем.

**Практичне** **значення одержаних результатів.**

Практичне значення отриманих результатів. Реалізація запропонованої в дисертації комплексної системи управління та перевірки гетерогенного середовища обробки та зберігання даних в розподілених нереляційних базах даних дозволяє: проектувати і експлуатувати розподілені бази даних; зменшити час, який дається на обробку запитів за рахунок ефективної побудови розподіленої системи; виконувати зміну параметрів в гетерогенній розподіленій системі обробки даних під час динамічної зміни структури комп’ютерної мережі та параметрів; створювати гетерогенні розподілені системи з ефективною обробкою даних щодо вказаних обмежень на параметри системи.

Проведено аналіз ефективності запропонованих засобів моніторингу обробки запитів, який показав, що, відповідно до отриманих експериментальних даних, із збільшенням кількості запитів за даними моніторингу, зменшується кількість помилкових ідентифікацій подій безпеки до 6,4 %, при цьому імовірність помилок ІІ роду знижується до 1,5 %. Це надає можливість стверджувати, що ефективність функціонування гетерогенних розподілених нереляційних баз даних підвищується.

Результати досліджень прийняті до впровадження в Науково-методичному центрі кадрової політики Міністерства оборони України (акт від 16.01.2024 р.), в Конструкторському бюро інформаційних систем КПІ ім. Ігоря Сікорського (акт від 26.12.2023 р.), в ТОВ «Інтехфорвард» (акт від 27.12.2023 р.), в навчальний процес кафедри інженерії програмного забезпечення в енергетиці Національного технічного університету України «Київський політехнічний інститут імені Ігоря Сікорського» при викладанні дисциплін «Бази даних» та «Побудова масштабованих систем обробки даних в реальному часі» для студентів, які навчаються за освітнім рівнем «Бакалавр» спеціальності 121 «Інженерія програмного забезпечення» денної та заочної форми навчання (акт від 12.02.2024 р.).

Перспективними шляхами наукових досліджень є розробка та впровадження нових методів та удосконалення існуючих методів підвищення ефективності функціонування та доступності гетерогенних розподілених нереляційних баз даних в умовах впливу внутрішніх та зовнішніх дестабілізуючих факторів

**Достовірність наукових результатів та практичних рекомендацій дисертації** підтверджується коректним використанням відповідного математичного апарату та обґрунтованими теоретичними твердженнями, а також узгодженістю теоретичних результатів із результатами виконаних експериментальних досліджень.

**У першому розділі** проаналізовано недоліки роботи гетерогенних розподілених нереляційних баз даних. Досліджено питання захищеності та надійності роботи в розподілених нереляційних базах даних. Показано, що для покращення обробки запитів потрібно розробити систему моніторингу, яка б дозволяла оперативно контролювати коректність виконання операцій і періодично відтворювати копії даних в розподілених базах даних.

На основі проведеного аналізу методів і засобів організації сучасних розподілених нереляційних баз даних запропоновано актуальне наукове завдання розробки моделі та методів обробки запитів в гетерогенних розподілених нереляційних базах даних на основі використання вузлів обробки запитів.

**У другому розділі** розглянуто особливості базових засобів підтримки безпечної обробки даних в розподілених нереляційних базах даних. Визначено основні компоненти системи управлінням моніторингу серверу обробки запитів. Показано, що для підтримки інформаційної безпеки СУБД важливі всі три основні аспекти: конфіденційність, цілісність та доступність.

Пропонується побудова багаторівневого захисту нереляційних баз даних на основі моделі Белла-ЛаПадула. Показано, що реалізація засобів захисту розподілених БД на основі запропонованих механізмів забезпечує підтримку необхідного рівня захищеності розподілених БД в умовах динамічної зміни числа користувачів-суб'єктів.

Запропоновано удосконалену модель моніторингу обробки запитів у гетерогенних розподілених нереляційних базах даних, яка відрізняється від існуючих використанням механізмів на основі застосування матриці обробки запитів. Зазначена модель дозволяє, у випадку виникнення нештатних ситуацій, передати попередження адміністратору серверу моніторингу обробки запитів, прийняти оперативні рішення щодо реагування на порушення безпеки під час обробки даних.

Розглянуті питання забезпечення надійності обробки даних в системі моніторингу та запропоновані засоби моніторингу обробки запитів взаємодії Web-інтерфейсу з середовищем зберігання даних на основі модулів контролю. Показано, що даний механізм дозволяє виконати детальний моніторинг транзакцій, запитів, об'єктів і збережених процедур бази даних з повідомленнями про інциденти в режимі реального часу і попередженням вторгнень. Показано, що в зв’язку з завантаженням серверів розподілених нереляційних баз даних потрібно розробити методи для прискорення обробки запитів.

**У третьому розділі** для проведення моніторингу гетерогенних розподілених нереляційних баз даних з визначення прихованих несправностей вузлів обробки запитів використовувалося декілька рівнів. На першому рівні використовуються прості моніторингові процедури. Коли за їх допомогою вдається визначити вузли обробки запитів, які є несправними, то на цьому моніторинг із найменшими витратами часу завершується. Але якщо є неоднозначності щодо визначення елементів розподіленої бази даних, які відмовили, користувач бази даних має запустити моніторингові процедури, які здатні впоратися з складнішими несправностями вузла обробки запитів. В даному випадку висловлене припущення про те, що простіші несправності вузла обробки запитів виникатимуть частіше, ніж складніші. А отже не потрібно відразу використовувати дуже сильні, моніторингові процедури, що вимагають великих часових витрат.

Розроблено два алгоритми, що утворюють дворівневу систему моніторинг прихованих відмов. Моніторинг розпочинається із застосування алгоритму А1, перевагами якого у порівнянні із відомими алгоритмами полягають в тому, що даний алгоритм вимагає меншої надмірності гетерогенної розподіленої нереляційної бази даних, всього два раунди обміну запитами між вузлами обробки запитів гетерогенних розподілених нереляційних баз даних і забезпечує моніторинг гетерогенних розподілених нереляційних баз даних при відмові майже половини її вузлів обробки запитів.

За результати виконання алгоритмів, що були описані вище було розроблено метод виявлення некоректної роботи вузлів гетерогенних розподілених нереляційних баз даних на основі застосування дворівневої системи контролю обробки запитів. Наукова новизна даного методу полягає у визначені прихованих несправностей вузла шляхом взаємного обміну запитами між вузлами з урахуванням припущень щодо синхронності гетерогенних розподілених нереляційних баз даних, а також можливості користувачем визначити вузол обробки. Зазначений метод дозволяє здійснювати виявлення випадків некоректної роботи вузлів обробки запитів.

Удосконалено метод визначення працездатності вузлів обробки запитів гетерогенних розподілених нереляційних баз даних, який відрізняється від існуючих способом обробки запитів на основі визначення апостеріорних ймовірностей справного стану вузлів. Зазначений метод дозволяє підвищити ефективність обробки даних.

Виконано порівняння схем з різною кількістю вузлів за показником ефективності обробки запитів, де апостеріорні імовірності є показником справного стану в умовах отримання позитивних результатів обробки запитів. Показано, що системи з роздільною обробкою запитів одного вузла апостеріорна імовірність дає найвищий показник, а починаючи з системи обробки запитів двох та більше вузлів, в якій реалізовано ланцюгову обробку запитів, апостеріорна ймовірність зменшується з збільшенням кількості вузлів.

**У четвертому розділі** розроблено структуру інформаційної системи та програмне забезпечення для проведення експериментальних досліджень обробки запитів в гетерогенних розподілених нереляційних базах даних.

Запропоновані механізми реалізації комплексної системи управління для контролю за гетерогенними системами управління нереляційних баз даних. Доведено, що запропоновані засоби підтримують можливість конвертації даних з гетерогенних розподілених СУБД для приведення їх в єдиний формат для спільного застосування даних різного типу.

Для аналізу ефективності запропонованих засобів моніторингу подій з пришвидшеною обробкою запитів проведено моделювання експериментів щодо дослідження даних з моніторингу. Достовірність отриманих теоретичних положень підтверджена проведенням експериментальних досліджень.

Таким чином, мета досліджень щодо підвищення ефективності функціонування гетерогенних розподілених нереляційних баз даних шляхом розробки та реалізації моделі та методів обробки даних в розподілених системах виконана та всі часткові наукові завдання розв’язані повністю. Отримані науково обгрунтовані результати досліджень є внеском у розвиток розроблення та дослідження засобів, моделей і методів підтримки прийняття рішень при розробці гетерогенних розподілених нереляційних баз даних на основі моніторингу обробки запитів.

**Особистий внесок здобувача.**

Основні результати наведені в дисертаційному досліджені отримані автором самостійно. В роботі \[1\] автором удосконалено модель моніторингу подій в гетерогенних розподілених нереляційних базах даних на основі використання вузлів обробки запитів; в роботі \[2\] автором проведено порівняльний аналіз методів підвищення швидкості пошуку та запису інформації в базах даних; в роботі \[3\] автором розглянута проблема семантичних протиріч у великих обсягах даних; в роботі \[4\] автором проаналізовано дворівневу системи контролю та обробки запитів; в роботі \[5\] автором проаналізовано модель моніторингу програмного забезпечення.

**Апробація результатів дисертації.**

Основні наукові результати досліджень, які включені до дисертаційного дослідження, доповідалися і обговорювалися на конференціях:

1.  ІІІ міжнародна науково-практична конференція «Інформаційні моделюючі технології, системи та комплекси» (ІМТСК-2021), (27 – 28 травня 2021, Черкаси);

2.  XXI Всеукраїнська науково-технічна конференція молодих вчених, аспірантів та студентів «Стан, досягнення та перспективи інформаційних систем і технологій», (22 – 23 квітня 2021, Одеса)

3.  Міжнародна науково-технічна конференція “Security, Fault Tolerance, Intelligence” ICSFTI (10-12 травня 2018, Київ);

4.  Десята міжнародна науково-практична конференція «Інтегровані інтелектуальні робототехнічні комплекси (ІІРТК-2018)». 22-23 травня 2018, Київ);

5.  10th International Scientific and Technical Conference on Intellectual Technologies of Linguistic Analysis, 2017, ITLA (October 24-25, 2017, Kyiv);

6.  Міжнародна науково-практична конференція "Інформаційні технології та комп’ютерне моделювання" (5-10 липня 2021, Івано-Франківськ);

7.  11th IEEE International Conference on Intelligent Data Acquisition and Advanced Computing Systems: Technology and Applications. (September 22-25, 2021. Cracow, Poland);

8.  CEUR Workshop Proceedings, 2021, Vol. 3200. International Scientific and Practical Conference “Information Security and Information Technologies”: Conference Proceedings. (13-19 September 2021, Kharkiv – Odesa);

9.  ХІ Міжнародна науково-практична конференція «Математика. Інформаційні технології. Освіта» (3–5 червня 2022, Луцьк–Світязь);

10. IEEE 4th International Conference on Advanced Trends in Information Theory (ATIT), (15-17 December 2022, Kyiv);

11. Перша міжнародна науково-практична конференція «Сучасні аспекти інженерії програмного забезпечення (Modern aspects of Software Engineering)»: (14 грудня 2023, Київ).

**Публікації.** Основні наукові результати дисертаційної роботи опубліковані в 16 наукових працях, серед яких 5 наукових статей в фахових журналах \[1 – 5\], затверджених МОН України, а також 11 публікацій в матеріалах наукових конференцій {6 – 16\] (із них 3 проіндексовано в Scopus).

**Обсяг та структура дисертації.** Дисертаційна робота загальним обсягом 192 сторінки машинописного тексту складається зі вступу, чотирьох розділів, висновків, переліку використаних джерел із 154 найменувань та додатків. Дисертація містить 28 рисунків, 6 таблиць і 2 додатки.

<span id="_Toc161146752" class="anchor"></span>РОЗДІЛ 1 ПОРІВНЯЛЬНИЙ АНАЛІЗ СУЧАСНИХ РОЗПОДІЛЕНИХ НЕРЕЛЯЦІЙНИХ БАЗ ДАНИХ

## **1.1. Аналіз організації, зберігання та обробки даних в сучасних розподілених нереляційних базах даних**

## 

В цей час не реляційні бази даних застосовуються в різних напрямах: на виробництвах, в офісах, на підприємствах, при цьому більшість відділів організацій зберігають вузол обробки запитів ої дані в форматі баз даних, отже, бази даних відіграють особливу роль в організації сучасних інструментальних, дослідницьких і промислових інформаційних систем. Сучасні інформаційні системи підтримують значну кількість різних типів СУБД, які розробляються спеціалізованими компаніями \[17-19\].

В кожній організації при збільшені об’ємів інформації, що зберігається в розподілених базах даних та її децентралізації виникає ряд проблем: зокрема актуальними задачами при проектуванні розподілених систем є підвищення ефективності обробки запитів та безпеки даних в гетерогенних розподілених не реляційних базах даних, що містять великі обсяги даних, зокрема персональні дані \[18-21\]. Одною з основних функцій СУБД є пошук даних в БД. Це питання є нагальним, в зв’язку з кількома факторами \[20-22\]:

1\. У мережі Інтернет зберігаються великі масиви інформації, які постійно накопичуються на серверах глобальної мережі.

2\. Технології пошуку інформації недостатньо ефективні при пошуку в великих масивах інформації, зокрема тому, що в результаті пошуку видається значна кількість інформації, більшість якої не відповідає запиту.

3\. За останні роки збільшились технічні можливості сучасної техніки, збільшились об’єми дискових просторів та швидкості обробки інформації, в результаті чого стало можливим створювати великі масиви даних розміщених на різних серверах. Причому пошук по таких БД повинен бути оперативним.

Перспективним напрямком є створення систем, які будуть орієнтовані не тільки на пошук інформації по розподіленим БД, а також і на семантичний аналіз інформації. Алгоритм пошуку базується на механізмі штучного інтелекту і для його підтримки необхідно застосовувати паралельні системи з багато зв’язною структурою подібною до нейронних мереж. Швидкість пошуку в таких системах на декілька порядків вища ніж при процедурі звичайного пошуку \[22-24\].

При обробці даних в базі даних, для забезпечення необхідного рівня захищеності даних, необхідно застосовувати системи моніторингу безпеки. Застосування звичайних засобів і механізмів призводить до недостатньої захищеності даних, тому що вони виконують базові задачі та не дозволяють проводити контроль безпеки функціонування бази даних при умові постійної зміни програмного та апаратного забезпечення. Для кращого рівня захищеності даних потрібно створити особливі механізми моніторингу, які орієнтовані на застосування в розподілених базах даних \[31-32\].

Створення нових методів запису та пошуку даних в базу даних, а також моделі моніторингу безпеки є необхідною умовою для забезпечення високої швидкості обробки інформації на серверах та підвищення ймовірності виявлення та вузол обробки запитів оєчасне попередження несанкціонованих дій зловмисників.

З метою ефективного захисту вузол обробки запитів оїх баз даних, організації повинні вирішувати п'ять найважливіших вимог \[33-35\]:

- Ізолювати чутливі бази даних: підтримувати точний список усіх баз даних, розгорнутих по всьому підприємству і визначити всі конфіденційні дані, що проживають на цих базах даних.

- Усунути вразливості: визначення та виправлення вразливостей і помилок.

- Забезпечення найменшими привілеями: контроль доступу і привілеїв користувачів для доступу тільки до мінімальних даних, які необхідні для виконання вузол обробки запитів оєї роботи.

- Монітор для відхилення: здійснювати належну політику і слідкувати за будь-якими діями, що відхиляються від нормальної та статутної діяльності.

- Відповідь на підозрілу поведінку: оповіщення та реагування на будь-які ненормальні або підозрілі поведінки в реальному часі, щоб знизити ризик нападу.

У сучасному управлінні даними гетерогенні розподілені нереляційні бази даних виділяються своєю здатністю обробляти величезні, різноманітні типи даних, що розвиваються, у розподілених системах. Ці бази даних, що характеризуються відсутністю єдиної моделі даних і розподіленої архітектури, пропонують унікальні виклики і можливості в зберіганні даних і обробці запитів. Потрібно розглянути методи, що використовуються для зберігання та обробки запитів, зосередившись на адаптивності, ефективності та масштабованості, які забезпечують ці системи.

Гетерогенні нереляційні бази даних використовують різні методи зберігання, адаптовані до конкретних моделей даних і вимог до продуктивності. Ці методи можна в широкому сенсі класифікувати за типом нереляційної бази даних:

- Сховища ключ-значення: використовуйте просту модель зберігання даних, де кожен елемент зберігається як ключ у поєднанні з його значенням. Прикладами можуть служити Redis і Amazon DynamoDB. Простота цієї моделі забезпечує швидкий доступ і високу пропускну здатність, що робить її ідеальною для зберігання сесій і кешування.

- Сховища документів: такі як MongoDB і CouchDB, зберігають дані в документах, які є більш гнучкими та ієрархічними, ніж прості пари ключ-значення. Ця структура добре підходить для зберігання, отримання та керування напівструктурованими даними, такими як документи JSON або XML.

- Сховища з широкими стовпцями: такі системи, як Apache Cassandra та Google Bigtable, організовують дані в таблиці, рядки та динамічні стовпці. Ця модель підтримує ефективну агрегацію та аналіз великих обсягів даних, пропонуючи високу масштабованість та продуктивність для аналітичних запитів.

- Графові бази даних: Neo4j та Amazon Neptune зберігають дані у вузлах та ребрах, представляючи сутності та зв'язки. Цей методи чудово підходять для сценаріїв, де зв'язки між точками даних настільки ж важливі, як і самі дані, наприклад, соціальні мережі або рекомендаційні системи.

Обробка запитів у гетерогенних розподілених нереляційних базах даних вимагає складних методів для ефективної роботи з різноманіттям моделей даних та розподіленим характером сховища. Ключові стратегії включають:

- Виконання розподілених запитів: передбачає розбиття запиту на підзапити, які можуть виконуватися паралельно на різних вузлах або базах даних. Цей підхід, який використовується базами даних, такими як Cassandra, підвищує продуктивність запитів, використовуючи можливості паралельної обробки розподіленої системи.

- Стратегії індексування: Ефективна індексація має вирішальне значення для підвищення продуктивності запитів. Нереляційні бази даних реалізують різні методи індексування, такі як B-дерева для сховищ документів або інвертовані індекси для можливостей повнотекстового пошуку. Просунуті стратегії індексування, включаючи складені індекси або матеріалізовані представлення, ще більше оптимізують виконання запитів.

- Розділення та шардинг даних: Дані розділяються та розподіляються між кількома серверами або вузлами, щоб збалансувати навантаження та забезпечити масштабованість. Стратегії шардингу повинні ретельно враховувати ключ розділу, щоб забезпечити рівномірний розподіл даних і мінімізувати гарячі точки.

- Використання кешу: Багато нереляційних баз даних реалізують механізми кешування для зберігання часто використовуваних даних у пам'яті, що значно скорочує час відповіді на запит. Redis, який часто використовується як сховище даних у пам'яті, є прикладом ефективного використання кешування для підвищення продуктивності.

Неоднорідність і розподілений характер цих баз даних створюють проблеми в забезпеченні узгодженої продуктивності запитів і цілісності даних у різних системах. Вирішення цих проблем вимагає інноваційних рішень:

- Моделі узгодженості: Нереляційні бази даних часто використовують остаточну узгодженість для підвищення доступності та толерантності до розділів. Такі методи, як векторні годинники, що використовуються DynamoDB, допомагають керувати узгодженістю між розподіленими вузлами.

- Оптимізація запитів у гетерогенних системах: Проміжне програмне забезпечення та планувальники запитів розробляються для оптимізації запитів у різних нереляційних базах даних, перекладі запитів на рідну мову запитів кожної системи та оптимізації операцій пошуку та агрегації даних.

- Об'єднання даних: У сценаріях, що включають кілька систем баз даних, програмне забезпечення для об'єднання даних забезпечує уніфікований інтерфейс для запитів у цих системах, абстрагуючи базову складність.

Методи зберігання та обробки запитів у розподілених нереляційних базах даних являють собою поєднання інновацій та адаптації до унікальних вимог сучасних додатків, керованих даними. Використовуючи спеціалізовані методи зберігання та передові методи обробки запитів, ці бази даних пропонують безпрецедентну гнучкість, масштабованість і продуктивність. Однак складність управління такими розподіленими системами вимагає постійних досліджень і розробок для подальшого вдосконалення цих методів і вирішення проблем, що виникають.

## **1.2. Дослідження особливостей побудови сучасних систем управління базами даних**

## 

Складовими частинами концепції побудови БД є сукупність принципів та методологій. До сучасних баз даних пред’являються наступні вимоги: висока швидкодія (малий час відгуку на запит), простота поновлення даних, незалежність даних, спільне використання даних багатьма користувачами, безпека даних (цілісність та захист), стандартизація побудови та експлуатації БД, адекватність відображення даних, простий інтерфейс користувача\[36-40\].

Існує два підходи до побудови БД: перший підхід пов'язаний з автоматизацією документообігу, а другий – з автоматизацією управління. Перший підхід передбачає створення універсальної БД, яку можна використовувати для будь-якого алгоритму, а другий – початкове виявлення стандартних алгоритмів програм під які визначаються дані, а об’єктно-орієнтований підхід призвів до збільшення значущості другого підходу\[37-40\].

Еволюція технологій баз даних призвела до значного переходу від традиційних систем управління реляційними базами даних (СУБД) до більш гнучких, масштабованих і різноманітних нереляційних систем управління базами даних (NoSQL). Цей перехід був зумовлений насамперед обмеженнями СУБД в обробці величезних обсягів неструктурованих даних, високою швидкістю транзакцій і потребою в розподілених системах баз даних. Нереляційні бази даних з їх різноманітними моделями даних, включаючи сховища ключ-значення, бази даних документів, сховища з широкими стовпцями та графові бази даних, пропонують індивідуальний підхід до управління даними, який часто більше відповідає конкретним вимогам застосування.

Основні особливості архітектури:

**Масштабованість**: Однією з відмінних рис сучасних нереляційних баз даних є притаманна їм масштабованість. На відміну від реляційних баз даних, які масштабуються по вертикалі (що вимагає більш потужних ресурсів одного сервера), нереляційні бази даних призначені для горизонтального масштабування, між декількома серверами або вузлами. Така конструкція дозволяє розподіляти дані по кластеру, підвищуючи продуктивність і забезпечуючи високу доступність.

Горизонтальне проти вертикального масштабування: нереляційні бази даних досягають успіху в горизонтальному масштабуванні, яке передбачає додавання більшої кількості серверів для обробки підвищеного навантаження. Це контрастує з вертикальним масштабуванням (scaling up), яке поширене в традиційних реляційних базах даних і передбачає модернізацію потужностей одного сервера (процесора, оперативної пам'яті, сховища).

Приклади систем: Cassandra та MongoDB є яскравими прикладами нереляційних баз даних, призначених для горизонтального масштабування. Cassandra, наприклад, відома своєю винятковою масштабованістю запису, розподіляючи дані між багатьма вузлами без єдиної точки відмови. MongoDB дозволяє шардинг, розподіляти дані між кількома серверами, а також балансувати навантаження або перерозподіляти дані за необхідності.

Сценарії застосування: Розглянемо платформу соціальних мереж, яка переживає швидке зростання кількості користувачів і відповідне збільшення обсягу даних. Здатність Cassandra до горизонтального масштабування дозволяє ефективно управляти цим зростанням, забезпечуючи високу доступність і продуктивність.

**Гнучкість схеми:** нереляційні бази даних не вимагають фіксованої схеми перед зберіганням даних. Ця гнучкість дозволяє зберігати неструктуровані або напівструктуровані дані, вміщуючи різні типи та структури даних. Така гнучкість особливо корисна в додатках, що мають справу з моделями даних, що швидко розвиваються.

Динамічні схеми: Нереляційні бази даних, як правило, не вимагають попередньо визначеної схеми, що дозволяє змінювати структуру даних на льоту. Ця гнучкість корисна для додатків, які мають справу з різноманітними типами даних або структурами даних, що швидко змінюються.

Приклади систем: Документоорієнтовані бази даних, такі як MongoDB, підтримують гнучкість схеми, дозволяючи кожному документу мати власну структуру. CouchDB, ще одна база даних документів, пропонує аналогічну гнучкість, що робить її ідеальною для проектів, де модель даних може змінюватися.

Сценарії застосування: Система управління контентом (CMS), яка обробляє різні типи вмісту, включаючи статті, відео та коментарі користувачів, може отримати вигоду від гнучкості схеми баз даних документів. Це дозволяє CMS розвиватися, не вимагаючи значних змін у схемі бази даних.

**Різноманіття моделей даних**: Різноманітність моделей даних, що підтримуються нереляційними базами даних (ключ-значення, документ, широка колонка та графік), дозволяє більш природно узгоджуватися зі специфічними для конкретних додатків структурами даних та шаблонами запитів. Це різноманіття дозволяє розробникам вибрати базу даних, яка найкраще відповідає потребам їхньої програми, оптимізуючи продуктивність та ефективність.

Різноманітні моделі даних: Різноманітність моделей даних у нереляційних базах даних — ключ-значення, документ, широка колонка та графік — підтримує різні типи програм та шаблонів доступу до даних.

Приклади систем: Redis, сховище ключ-значення, оптимізовано для високопродуктивного кешування даних. Компанія Google Bigtable надихнула на створення магазинів з широкими колонками, таких як Apache Cassandra, які підходять для управління великими обсягами даних на багатьох машинах. Neo4j, графова база даних, чудово справляється зі складними зв'язками між точками даних.

Сценарії застосування: Платформа електронної комерції може використовувати Redis для зберігання сеансів і кешування інформації про продукт для швидкого доступу. Соціальна мережа може використовувати Neo4j для ефективного запиту складних відносин між користувачами, таких як друзі та рекомендовані зв'язки.

**Розподілена природа:** нереляційні бази даних за своєю суттю призначені для розподілених середовищ. Вони часто включають вбудовані механізми для реплікації, розбиття та синхронізації даних між кількома вузлами, забезпечуючи доступність і стійкість даних в умовах збоїв сервера або мережевих розділів.

Вбудована реплікація та розбиття даних: нереляційні бази даних призначені для роботи в розподіленій мережі комп'ютерів, пропонуючи механізми для реплікації та розбиття даних для підвищення доступності та відмовостійкості.

Приклади систем: Cassandra надає надійні функції реплікації даних, гарантуючи, що дані копіюються між кількома вузлами. Така конструкція покращує доступність даних і аварійне відновлення.

Сценарії застосування: у глобальному додатку електронної комерції Cassandra може гарантувати, що дані користувачів реплікуються в центрах обробки даних у різних регіонах, мінімізуючи затримки та покращуючи взаємодію з користувачем, надаючи дані з найближчого місця.

**Моделі узгодженості:** нереляційні бази даних часто використовують гнучкі моделі узгодженості, такі як кінцева узгодженість, яка допускає тимчасові невідповідності в обмін на вищу доступність і продуктивність. Це відхід від строгих властивостей ACID (Atomicity, Consistency, Isolation, Durable) реляційних баз даних, пропонуючи баланс між узгодженістю, доступністю та толерантністю до розділів (теорема CAP).

Остаточна узгодженість: нереляційні бази даних часто пропонують настроювані рівні узгодженості, що дозволяє розробникам вибирати між можливою узгодженістю для більшої доступності та сильною узгодженістю для точності даних.

Приклади систем: Amazon DynamoDB пропонує гнучкі моделі узгодженості, включаючи зчитування сильної узгодженості та остаточне зчитування узгодженості, щоб збалансувати затримку та узгодженість на основі вимог програми.

Сценарії застосування: платформа для торгівлі акціями може вимагати суворої послідовності для забезпечення точних балансів на рахунках і виконання угод. На противагу цьому, система рекомендацій щодо продукту може терпіти кінцеву послідовність, надаючи перевагу швидкості, а не миттєвій точності.

Незважаючи на те, що архітектура нереляційних баз даних має численні переваги, вона також створює проблеми. Відсутність фіксованої схеми при підвищенні гнучкості може призвести до неузгодженості даних і проблем з управлінням. Різноманітні моделі даних і мови запитів в різних нереляційних базах даних можуть накладати криву навчання і ускладнювати розробку і обслуговування додатків. Крім того, вибір між моделями узгодженості вимагає ретельного розгляду, щоб переконатися, що поведінка бази даних відповідає вимогам програми.

У порівнянні з класичними базами даних, гетерогенні розподілені нереляційні бази даних пропонують більш гнучке та масштабоване рішення для управління великими обсягами різноманітних даних у розподілених середовищах. Однак це відбувається за рахунок узгодженості транзакцій і гарантій цілісності даних, що надаються традиційними СУБД. Вибір між реляційними і нереляційними базами даних в кінцевому підсумку залежить від конкретних вимог програми, включаючи характер даних, потреби в масштабованості і вимоги до узгодженості.

## **1.3. Аналіз організації розподілених нереляційних баз даних**

## 

Одним з способів організації системи управління базами даних є підтримка розподілених баз даних. Розподілені бази даних реалізуються в локальній або глобальній комп'ютерної мережі. В даному випадку вузли однієї логічної бази даних позкидані в різних під мережах або в віртуальних машинах хмарного середовища з встановленими різними операційними системами \[66-70\].

Такий розподіл даних дозволяє, наприклад, зберігати у вузлах бази даних ті дані, що найчастіше використовуються в даному вузлі. Даний підхід спрощує роботу з велекими даними та передбачає можливість обробляти інші дані БД, про те на доступ до них необхідно затратити деякий час на обмін даних в мережі \[37\].

Основною особливістю розподіленої бази даних є її "прозорість" для користувачів і розробників додатків. Тобто користувачі та розробники представляють розподілену БД у вигляді деякої єдиної логічної локальної БД, не замислюючись про фізичне розташування її компонент. Всі додатки створюються так, як ніби вони працюють з цієї єдиної логічної локальної БД. Налагодження програм також може виконуватися на локальній БД \[67-69\].

Перенесення частин цієї локальної БД в різні вузли мережі може виконуватися в більш пізній час адміністратором БД і воно не тягне за собою зміни додатків. Більш того, користувачі та розробники додатків можуть навіть не знати, де фізично розміщені дані, з якими вони працюють. Пошук і пересилку віддалених даних автоматично виконують програмні засоби СУБД \[69-72\].

Звичайно для того, щоб реалізувати такий простий для кінцевого користувача і розробника механізм подання розподіленої БД, необхідно вирішити ряд проблем. Найбільш очевидні з них пов'язані із забезпеченням цілісності і несуперечності даних розподіленої БД, реалізацією механізму підтримки "прозорості" розподіленої БД, реалізацією єдиного механізму роботи з частинами БД, що знаходяться в СУБД різного типу і розташованими на різнотипних комп'ютерах з різними операційними системами, забезпеченням прийнятнї швидкодії прикладної системи і т.д. \[73-78\].

У більшості випадків розподілена СУБД складається з ядра СУБД і набору додаткових продуктів, які забезпечують роботу з розподіленою БД. Існують СУБД, в яких засоби роботи з розподіленими БД вбудовуються в ядро СУБД. Користувачі розподілених СУБД потрібно звертати увагу на багато факторів, які дозволяють правильно налаштувати роботу баз даних з розподіленим середовищем \[79-82\].

Проте існує певний набір функцій, які повинні бути притаманні кожній розподіленої СУБД. Найбільш поширеним описом цих функцій є наступне: розподілена СУБД забезпечує користувачам доступ до інформації незалежно від того, яке обладнання і яке прикладне програмне забезпечення використовується у вузлах мережі. Розподілена СУБД дозволяє виконувати горизонтальне і вертикальне "розщеплення" таблиць і поміщати дані однієї таблиці в різних вузлах мережі. Запити до даних розподіленої БД формулюються так, як ніби база даних локальна. При обробці транзакцій і виконанні операцій копіювання (відновлення) розподіленої БД забезпечується цілісність всієї БД \[80-86\].

Протоколи управління БД, наприклад протокол двофазної фіксації змін, реалізують механізми блокування, що забезпечують несуперечність даних. Засоби глобальної оптимізації запитів автоматично вибирають найкращий спосіб виконання в локальної або глобальної мережі складних транзакцій, а спеціальні монітори дозволяють отримувати інформацію про параметри виконуються в різних вузлах процесів і на основі цієї інформації виконувати налаштування системи з метою забезпечення максимальної продуктивності роботи \[87-90\].

Організація розподілених нереляційних баз даних відображає зміну парадигми в управлінні даними, що відповідає вимогам складності та масштабованості сучасних додатків. Ці бази даних, різноманітні за своєю архітектурою та моделями даних, пропонують рішення, що виходять за рамки універсального підходу традиційних реляційних баз даних.

Принципи неоднорідності та розподілу:

- Гетерогенність: Відноситься до різноманітності моделей даних, механізмів зберігання та мов запитів у нереляційних базах даних, що задовольняють конкретні типи даних та потреби додатків (наприклад, сховища ключ-значення для швидкого доступу, сховища документів для JSON-подібних структур даних, сховища з широкими стовпцями для аналітичних запитів та графові бази даних для складного відображення зв'язків).

- Розподіл: передбачає розподіл даних у кількох фізичних місцях, або в межах одного центру обробки даних, або в регіонах світу, щоб підвищити доступність даних, відмовостійкість і масштабованість. Стратегія розподілу повинна враховувати моделі розбиття, реплікації та узгодженості даних, щоб збалансувати продуктивність і точність даних.

Архітектурні особливості:

- Розбиття даних: Такі стратегії, як шардинг (горизонтальне розділення), розподіляють дані між кількома вузлами для ефективного керування навантаженням і забезпечення масштабованості. Рішення щодо ключів або атрибутів розділів суттєво впливають на продуктивність запиту та баланс розподілу даних.

- Реплікація: забезпечує доступність і довговічність даних, зберігаючи копії даних на різних вузлах або центрах обробки даних. Стратегії реплікації (наприклад, master-slave, peer-to-peer) впливають на узгодженість і надійність системи баз даних.

- Узгодженість і синхронізація: Управління узгодженістю в розподіленому, гетерогенному середовищі створює проблеми, особливо при балансуванні між сильною узгодженістю та кінцевою узгодженістю для задоволення різних вимог застосування.

Інтеграція моделей даних:

- Уніфікований інтерфейс запитів: розробка уніфікованого інтерфейсу запитів або проміжного програмного забезпечення, яке може взаємодіяти з декількома типами нереляційних баз даних, абстрагуючи їх відмінності та забезпечуючи узгоджений механізм запитів.

- Інтеграція та трансформація даних: методи інтеграції та перетворення даних у гетерогенних нереляційних базах даних, що забезпечує уніфікований доступ до даних та їх обробку. Це може включати процеси ETL (Extract, Transform, Load), озера даних або потокові конвеєри в реальному часі.

Проблеми та вирішення:

- Інтероперабельність: вирішення проблеми інтероперабельності між різноманітними нереляційними базами даних передбачає стандартизацію форматів даних, API та протоколів для полегшення безперебійного обміну даними та операцій у різних системах.

- Узгодженість даних: впровадження механізмів забезпечення узгодженості даних у розподілених базах даних, особливо в умовах мережевих розділів і одночасних оновлень, вимагає інноваційних підходів, таких як стратегії вирішення конфліктів, контроль версій і протоколи консенсусу.

- Оптимізація запитів: оптимізація запитів у гетерогенних базах даних вимагає передових алгоритмів і методів для аналізу шаблонів запитів, локальності даних і планів виконання, щоб мінімізувати затримку та споживання ресурсів.

Реальні сценарії застосування:

- Системи IoT: для управління даними з мільйонів пристроїв IoT потрібні бази даних, які можуть обробляти високу пропускну здатність запису, різноманітні формати даних і географічно розподілені дані. Комбінація баз даних часових рядів для даних датчиків і сховищ документів для метаданих пристроїв може задовольнити ці потреби.

- Соціальні мережі: Додатки соціальних мереж, що мають справу з величезними обсягами неструктурованих даних і складними взаємозв'язками між сутностями, виграють від інтеграції графічних баз даних для соціальних графів зі сховищами ключ-значення для уподобань і дій користувачів.

## **1.4. Дослідження обробки запитів у гетерогенних розподілених нереляційних базах даних**

Розвиток технології баз даних привели до диверсифікації систем, де працюють як нереляційні (NoSQL), так і реляційні (SQL) бази даних, які обслуговує різні потреби додатків. Це різноманіття особливо помітно в гетерогенних розподілених середовищах, де бази даних розподілені між кількома вузлами, щоб забезпечити масштабованість, доступність і відмовостійкість. Порівняльний аналіз методів обробки запитів у гетерогенних розподілених нереляційних базах даних порівняно з розподіленими реляційними базами даних виявляє фундаментальні відмінності в дизайні, функціональності та придатності додатків.

Обробка запитів у нереляційних базах даних:

Нереляційні бази даних, що характеризуються безсхемними моделями даних і горизонтальною масштабованістю, використовують методи обробки запитів, які принципово відрізняються від їх реляційних аналогів. Ці методи призначені для оптимізації продуктивності, гнучкості та масштабованості в розподілених середовищах.

- Приклад: MongoDB (Document Store) MongoDB використовує BSON (Binary JSON) для зберігання документів. Його обробка запитів дозволяє виконувати розширені запити на основі документів, включаючи пошук полів, діапазонів і регулярних виразів. Розподілений дизайн MongoDB підтримує шардинг, коли дані розбиваються між кількома серверами, і набори реплік для забезпечення високої доступності. Обробка запитів у сегментованому кластері передбачає маршрутизацію запитів до відповідних шардів, оптимізацію швидкості запитів і зменшення міжмережевого трафіку.

- Приклад: Apache Cassandra (Wide-Column Store). Обробка запитів Cassandra розроблена для високої масштабованості та відмовостійкості, використовуючи сховище розділених рядків з кінцевою послідовністю. Дані розподіляються між вузлами за допомогою послідовного механізму хешування. CQL (Cassandra Query Language) від Cassandra забезпечує ефективний доступ до даних за допомогою первинного та вторинного індексів. Запити обробляються шляхом знаходження відповідних ключів розділів у розподілених вузлах з настроюваними рівнями узгодженості для балансу між продуктивністю читання/запису та узгодженістю.

Обробка запитів у реляційних базах даних:

Розподілені реляційні бази даних підтримують структуровану схему і підтримують властивості ACID (Atomicity Consistency Isolation Durable). Обробка запитів у цих системах часто наголошує на цілісності та послідовності транзакцій.

Приклад: PostgreSQL з розширенням Citus. Citus перетворює PostgreSQL на розподілену базу даних, дозволяючи їй горизонтально масштабуватися на кількох вузлах. Обробка запитів у Citus передбачає розподіл таблиць між вузлами та розпаралелювання запитів між цими шардами. Citus використовує надійні можливості SQL PostgreSQL, що дозволяє виконувати складні об'єднання, підзапити та транзакції, забезпечуючи відповідність ACID навіть у розподіленій конфігурації.

Приклад: Google Spanner – це глобально розподілена реляційна база даних, яка поєднує в собі переваги традиційних СУБД з масштабованістю NoSQL-систем. Він представляє глобально синхронізований годинник (TrueTime) для підтримки зовнішньої узгодженості транзакцій між розподіленими вузлами. Обробка запитів Spanner дозволяє виконувати SQL-запити з транзакціями ACID через розподілену базу даних, вирішуючи проблеми затримки та узгодженості, які зазвичай пов'язані з розподіленими системами.

Порівняльний аналіз

Основна відмінність між обробкою запитів у нереляційних і реляційних базах даних полягає в їхньому підході до узгодженості, гнучкості схеми та масштабованості.

Узгодженість чи продуктивність: Нереляційні бази даних часто надають пріоритет продуктивності та масштабованості, іноді за рахунок сильної узгодженості. Такі методи, як остаточна узгодженість і настроювані рівні узгодженості в таких системах, як Cassandra, пропонують гнучкість, але вимагають ретельного розгляду для забезпечення цілісності даних. На противагу цьому, розподілені реляційні бази даних, такі як Google Spanner, забезпечують надійну узгодженість розподілених транзакцій, що підходить для додатків, де цілісність даних має першорядне значення.

Гнучкість схеми: нереляційні бази даних пропонують гнучкість схеми, що дозволяє створювати динамічні структури даних і швидку ітерацію при розробці додатків. Ця гнучкість може спростити зберігання напівструктурованих або неструктурованих даних, як це видно в сховищах документів, таких як MongoDB. Розподілені реляційні бази даних підтримують сувору схему, що полегшує цілісність даних і зв'язки, але з часом може вимагати більш попереднього проектування та коригування.

Масштабованість: Обидва типи баз даних мають на меті забезпечити масштабованість, але їхні підходи відрізняються. Нереляційні бази даних, такі як Cassandra та MongoDB, розроблені для легкого горизонтального масштабування, часто з простими стратегіями реплікації та розбиття на розділи. Розподілені реляційні бази даних вимагають більш складних механізмів для підтримки властивостей ACID між вузлами, як це видно з Citus і Spanner.

Вибір між використанням гетерогенної розподіленої нереляційної бази даних або розподіленої реляційної бази даних залежить від конкретних вимог програми, включаючи потребу в масштабованості, узгодженості та гнучкості схеми. Нереляційні бази даних пропонують переваги в обробці великих обсягів різноманітних даних, що розвиваються, з високою масштабованістю та продуктивністю. На відміну від них, реляційні бази даних є кращими для додатків, що вимагають суворої цілісності даних, складних транзакцій і чітко визначених зв'язків даних. Розуміння нюансів методів обробки запитів у цих системах має вирішальне значення для архітекторів і розробників для прийняття обґрунтованих рішень, які відповідають цілям і обмеженням їхньої програми.

## **1.5. Постановка завдання дослідження та часткових завдань дисертації**

## 

Проведений в підрозділах 1.1 - 1.4 аналіз існуюсих методів та засобів організації сучасних гетерогенних розподілених нереляційних баз даних дає нам змогу зробити висновок про те, що гетерогенних розподілених нереляційних баз даних являють собою складний комплекс у якому потрібно забезпечити високу швидкість, надійність і достовірність запису і вивантаження даних при умові постійних випадкових або зловмисних впливів на передачу інформації і засоби обробки запитів у гетерогенних розподілених нереляційних баз даних при постійному збільшені обсягу оброблюваних даних. Однак проведення розробки і інтеграції гетерогенних розподілених нереляційних баз даних вимагає виконання синхронізації обробки запитів та їх контролю. Недоліки сучасних систем управління і моніторингу обробки запитів гетерогенних розподілених нереляційних баз даних виникають під час суміщення різнорідних баз даних. Проте застосування звичайних засобів та апаратів моніторингу обробки запитів є недостатнім у зв’язку з тим, що вони виконують тільки базові функції та не контролюють функціонування самої гетерогенних розподілених нереляційних баз даних в умовах постійних їх модифікацій.

Тому, ***метою дисертаційної роботи*** є підвищення ефективності функціонування гетерогенних розподілених нереляційних баз даних шляхом розробки та реалізації моделі та методів обробки даних в розподілених системах.

Для досягнення мети необхідно вирішити ***наукове завдання*** – Розробка моделі та методів обробки запитів в гетерогенних розподілених нереляційних базах даних на основі використання вузлів обробки запитів.

***Об’єктом дослідження*** є процес обробки запитів в гетерогенних розподілених нереляційних базах даних, а ***предметом дослідження*** – засоби комплексного моніторингу обробки запитів в гетерогенних розподілених нереляційних базах даних на основі вузлів обробки запитів.

Для розв’язання сформульованого наукового завдання необхідно розбити дана наукове завдання на ряд взаємозалежних складових частин, які визначають часткові наукові завдання досліджень. Основними з цих наукових завдань є:

1\. Провести порівняльний аналіз методів і засобів організації сучасних гетерогенних нереляційних розподілених баз даних для визначення особливостей та проблем їх реалізації.

2\. Дослідити методи і засоби підтримки процесу запису, пошуку та захисту даних в гетерогенних нереляційних розподілених баз даних для підвищення швидкості обробки даних та попередження несанкціонованого доступу.

3\. Розробити модель моніторингу обробки запитів у гетерогенних розподілених нереляційних базах даних.

4\. Розробити метод виявлення некоректної роботи вузлів гетерогенних розподілених нереляційних баз даних на основі застосування дворівневої системи контролю обробки запитів Аналіз, розробка та дослідження механізмів та засобів підтримки процедури моніторингу операцій в розподілених базах даних на основі сенсорів подій.

5\. Розробити метод визначення працездатності вузлів обробки запитів гетерогенних розподілених нереляційних баз даних.

6\. Розробити спеціалізоване середовище для моделювання та порівняння експериментальних досліджень запропонованих засобів підтримки процесу обробки запитів в гетерогенних розподілених нереляційних баз даних.

Розвязання сформованих взаємозалежних часткових наукових завдань визначило структуру та зміст дисертаційного дослідження.

## **Висновки до розділу 1**

## 

Дослідженні недоліки, що виникають під час реалізації і функціонування розподілених систем управління базами даних при обробці великих обсягів інформації. Доведено, що для збільшення ефективності процесу обробки запитів в базах даних необхідно застосовувати спеціальні механізми побудови даних.

Досліджено загальну концепцію побудови сучасних систем управління нереляційними базами даних. Розглянуто особливості побудови не реляційних розподілених систем управління базами даних.

Досліджено питання організації та загальні принципи обробки запитів в нереляційних базах даних. Показано, що при виконанні запитів до таблиць виникає проблема, в звязку з різноманітності баз за своєю архітектурою та моделями даних, які пропонують рішення, що виходять за рамки універсального підходу традиційних реляційних баз даних.

Досліджено питання захищеності та надійності роботи в розподілених базах даних. Показано, що для покращення обробки запитів потрібно розробити систему моніторингу, яка б дозволяла оперативно контролювати коректність виконання операцій в гетерогенних розподілених нереляційних базах даних.

На основі проведеного аналізу методів і засобів організації сучасних розподілених баз даних сформульовано актуальність наукового завдання щодо розробки моделі та методів обробки запитів в гетерогенних розподілених нереляційних базах даних на основі використання вузлів обробки запитів.

<span id="_Toc161146428" class="anchor"></span>РОЗДІЛ 2 ДОСЛІДЖЕННЯ МЕХАНІЗМІВ МОНІТОРИНГУ ОБРОБКИ ЗАПИТІВ В ГЕТЕРОГЕННИХ РОЗПОДІЛЕНИХ НЕРЕЛЯЦІЙНИХ БАЗАХ ДАНИХ

## **2.1. Аналіз засобів підтримки безпечної обробки запитів в гетерогенних розподілених нереляційних базах даних**

## 

Розподілені нереляційні бази даних, стали одним з домінуючих інструментів зберігання великих масивів інформації. Теперішні інформаційні додатки спираються на багатокористувацькі розподілені нереляційні бази даних, що реалізовані за технологією клієнт-сервер. Тому забезпечення інформаційної безпеки розподілених нереляційних баз даних, і, в першу чергу, їх серверних компонентів приймає вирішального значення \[137\].

Для розподілених нереляційних баз даних важливі такі три аспекти інформаційної безпеки як конфіденційність, цілісність і доступність. Основна ідея захисту розподілених нереляційних баз даних в дотриманні рекомендацій, які сформульовані для класу безпеки C2 що прописані в "Критеріях оцінки надійних комп'ютерних систем". Для ряду розподілених нереляційних баз даних реалізуються засоби захисту, які характерні для класу B1, однак практичне застосування цих засобів ефективно лише тоді, коли усі компоненти, які складають інформаційну структуру організації відносяться до категорії безпеки B. Необхідно враховувати дві обставини. Перша, для більшості підприємств та комерційних організацій клас безпеки C2 цілком достатній. Друге, засоби захисту для більш захищених версій відстають за вузол обробки запитів оїми характеристиками від звичайних, тому являються дещо застарілими проте й ретельно перевірені засоби \[138\].

Системи управління розподіленими нереляційними базами даних є комплексними та мають підтримувати весь час зростаючий комплекс механізмів щодо обробки даних крос-платформного типу, збільшення їх властивостей сприяє утворенню нових вразливостей у системах безпеки. Дані вразливості постійно відслідковуються фахівцями з систем управління базами даних, які намагаються мінімізувати число таких вразливостей, при цьому для виявлення такого типу загроз потрібно достатньо багато часу, а це може обумовлювати можливість використання таких вразливостей зловмисниками для проникнення до розподілених нереляційних баз даних \[139\].

Зокрема, вже можна стверджувати, що так звані «Внутрішні загрози» та, особливо загрози, що направлені від легальних користувачів які мають привілейованим доступом, є найбільш небезпечними вразливостями з погляду безпеки. Відповідно до щорічного дослідження, що проводиться групою CERT (група аналізу і реагування на порушення безпеки в мережі Інтернет), до 50 відсотків порушень безпеки були викликані саме з боку легальними користувачів, що перевищують вузол обробки запитів ої повноваження. В звітах за 2022 рік щодо оцінки загроз безпеки зауважується, що дві треті опитаних підприємств (які належать до приватного та державного сектору) повідомляли про інциденти, що були викликані внутрішніми причинами порушеннями безпеки, та в певних випадках дані внутрішні загрози призвели до 80% втрат. Також було вказано, що 57% користувачів, які були причетні до порушення безпеки, мали розширений доступ до даних у момент здійснення несанкціонованого доступу. Отже, можна зробити висновок, що використання тільки загальних систем, що забезпечують безпеку інформаційних систем виявляється недостатнім \[140\].

Зокрема, законодавчі і регуляторні вимоги, а саме Закон про захист персональної інформації, зобов'язують державні компанії і організації вживати ряд спеціальних заходів щодо забезпечення приватності, безпеки і цілісності персональних даних. Для виконання даних вимог потрібно застосовувати механізми щодо моніторингу дій суб'єктів мережі, які дозволить в достатній мірі відстежувати та фіксувати здійснювані суб’єктами дії \[141\].

Розвиток загроз щодо забезпечення безпеки відносно існуючої інфраструктури викликає необхідність відповідно захисту даних в розподіленій нереляційній базі даних на найнижчому рівні, при використанні засобів, що можуть керувати специфічними для розподілених нереляційних баз даних загрозами і виконувати взаємодію з внутрішніми легальними користувачами \[142\].

На даний час існує широкий спектр механізмів та засобів щодо забезпечення безпеки обробки запитів в розподілених нереляційних базах даних. Зокрема, як і для інших додатків, спрямовані окремі кошти не можуть забезпечити цілковитий захист розподіленої нереляційної бази даних від усіх можливих загроз і порушень. Для того щоб підвищення ефективності щодо забезпечення безпеки рекомендовано використовувати ряд комплексних засобів, що являють собою відповідну комбінацію різних засобів щодо підтримки безпеки. Приведемо короткий огляд існуючих та використовуваних засобів щодо підтримки безпеки розподіленої нереляційної бази даних.

*Аутентифікація суб'єктів і контроль доступу*

Має наступні переваги: встановлюють ролі суб'єктів і їхніх прав та забезпечують базовий рівень безпеки.

До недоліків відносять:

- складність підтримки високого рівня безпеки;

- недосить гнучкий контроль доступу;

- уразливості для несанкціонованого отримання права доступу;

- неповний контроль легальних користувачів.

Спосіб розподілу ролей суб'єктів, їх логінів та паролів є основним елементом безпеки та часто використовується у різних додатках. Даний механізм визначає базові права суб'єктів та підтримує заданий рівень взаємодії суб'єктів та додатків.

Проте даний механізм має на меті коректну поведінку користувачів у системі, та той факт, що управління їхніми правами доступу відбувається відповідно до встановленої політики безпеки. Проте на практиці це відбувається не завжди так. Часто відповідним суб'єктам надаються зайві права доступу, наприклад, у випадку коли користувачі отримують певні права на доступ до ресурсів більше ніж відведений періоду часу і не повертаються до їх вихідним прав. Крім того часто створюються групові права. Після цього в середині групи не відбувається дискретизація доступу. Отже, даного механізму безпеки недостатньо навіть у випадках обмеження доступу аутентифікованих для легальних користувачів \[143\].

*Вбудовані механізми моніторингу активностей у розподілених нереляційних базах даних*

Має наступні переваги: підтримує механізм детального аналізу активностей у розподілених нереляційних базах даних

До недоліків можна віднести негативний вплив на роботу бази даних, відсутній поділу обов'язків тобто його легко відключити та маніпулювати відповідними зібраними даними, забезпечує реакцію на події порушення безпеки системи постфактум.

Засоби моніторингу обробки запитів в базі даних дозволяють виконати достатньо детальний аналіз дій відповідних суб'єктів з базою даних. Однак, у певних випадках, в комплексних додатках, наведений аналіз практично неможливий. Зокрема, оскільки система моніторингу завжди управляється адміністратором бази даних, що не виконує розподіл відповідних прав суб'єктів, є обов'язковим для більшості політик забезпечення безпеки систем. Дії ж самого адміністратора часто виходять за рамки моніторингу, крім того в цей список можуть потрапляти і інші користувачі, що мають права привілейованого доступу до системи моніторингу, тому що вони можуть управляти роботою засобів моніторингу або змінювати зібрані дані з моніторингу обробки запитів \[144\].

*Механізми аналізу вразливостей розподілених нереляційних баз даних*

Має наступні переваги: визначаються відповідні вразливі місця у конфігурації бази даних та проблеми їхньої безпеки.

До недоліків відносять: запускаються періодично (за звичай не є постійно включеними), не вирішують проблеми безпеки бази даних, не здатні виявляти випадки перевищення прав суб'єктів.

Сканери вразливостей та інші елементи забезпечення оцінки конфігурації певної бази даних є важливим доповненням по відношенню до механізмів безпеки розподілених нереляційних баз даних, але з огляду на те, що вони використовуються не часто (раз на місяць чи квартал), в період проміж скануваннями виникає велика кількість проблем. Наприклад, в результаті аналізу уразливості є шанс виявити можливі уразливості у системі безпеки бази даних, проте неможливо визначити чи були дані уразливості використані та нейтралізовані, а це ускладнює процес підвищення захищеності бази даних від великого руйнування \[145\].

*Засоби криптографічного захисту*

Має наступні переваги: захищають дані які є вразливими.

До недоліків відносять: достатньо повільну робота та високу вартість використання, відповідні додаткові витрати на управління ключем, вплив на швидкодію системи, певні труднощі в управлінні.

Засоби криптографічного захисту даних в базах даних гарантують неможливість прямого доступу до таких вразливих даних, як номери кредитних карток у користувачів із загальним доступом до бази даних, а також відповідний розподіл прав доступу. Дані засоби зазвичай мають високу вартість. Зокрема, сам по собі криптографічний захист є неефективний, з погляду на те, що зашифровані дані часто опиняються у розшифрованому вигляді під час роботи з додатками, це створює відповідні додаткові можливості з доступу до даних \[146\].

*Основні принципи захисту баз даних*

В першу чергу захист баз даних базувався на технології так званої дискреційної безпеки \[147\]. Основними елементами щодо підтримки безпеки баз даних є: ідентифікація і аутентифікація суб'єктів та засоби і певні механізми контролю доступу. Для забезпечення розмежування прав доступу відповідних суб'єктів у мовах програмування, наприклад, в SQL додані команди GRANT та REVOKE для надання і заборони доступу користувачів до бази даних. Однак, для багатьох програм, даних команд ( GRANT та REVOKE ) може бути не достатньо. Тому потрібно використовувати більш складні технології авторизації доступу суб'єктів по відношенню до баз даних та окремо виділити відповідні засоби заборони доступу. Крім того окремо виділяється технології доступу до відповідних даних на основі врахування прав користувачів. У даний час відомо роботи \[148\] де використовують механізми дискреційної безпеки баз даних.

Щодо систем управління базами даних виставляють вимоги до безпеки майже аналогічні тим, що підтримують більшість операційних систем. Проте існує ряд істотних відмінностей у рамках вимог щодо безпеки, тому що системи управління базами даних особливо сприйнятливі щодо загроз наступного типу: несанкціонований доступ, змінення інформації і відмова у обслуговуванні. Проста модель щодо підтримки безпеки розподілених нереляційних баз даних представлена на рис. 2.1.

Браузер клієнта

Web-сервер

Проміжний сервер

Бази даних та системи управління базами даних

Система управління інформаційною безпекою

БД сесій

БД користувачів

API

API

API

Рис. 2.1. Проста модель підтримки безпеки  
розподілених нереляційних базах даних

Відмітимо ряд найбільш важливих вимог, що пред’являються до безпеки для системи управління нереляційними базами даних:

- наявність багаторівневого контролю доступу суб’єктів;

- цілісність;

- надійність;

- конфіденційність;

- живучість.

*Механізм централізованого керування розподіленими нереляційними базами даних*

Проаналізуємо розподілену архітектуру щодо розробки багаторівневої системи управління базами даних. У такій архітектурі дані зберігаються розподілено, але контроль даних відбувається централізовано.

На даний час прийнято два підходи до централізованого управління. В першому підході, його ще називають розподілений підхід, база даних якій ми довіряємо підключається до недовіреної бази даних що знаходиться на сервері. Дані бази даних працює на одному рівні та керує даними що знаходяться на цьому ж рівні. Наприклад, відкрита система управління базами даних керує відкритими (несекретними) даними, відповідно секретна СУБД керує даними які є секретними секретними даними. Весь обіг даних між базами даних відбувається тільки через довірену базу даних. Запити які надходять від користувача надсилаються СУБД на рівні користувача чи на один рівень нижче. Після цього оновлені запити відправляються СУБД лише на рівні користувача. Наприклад, запит користувача який має тип секретний може бути надісланий до секретної і відкритої системи управління базою даних, тоді як запит щодо оновлення для даного користувача надсилається лише в секретну СУБД \[149\].

Як нам відомо за наявності закритих каналів запити що робить користувач типу секретні які містять конфіденційну інформацією можуть відправлятися навіть в відкриті системи управління базами даних. В другому підході щодо централізованого управління відбувається реалізація реплікації даних. У даному випадку несекретні дані реплікуються у базах даних, які належать до типу секретна та особливо секретна, а саме секретні дані реплікуються тільки особливо секретну БД. Отже, запити користувача відправляються системою управління лише на рівні користувача, а запит щодо оновлення надсилається у дубльовану БД. Незважаючи на відсутність закритих каналів щодо передачі запитів, дивлячись на те, що інформація від користувача з оновлення пересилається на верхні рівні БД, утворюється можливість створення закритих каналів у процесі операцій оновлення. Проте відомо, що пропускна здатність утворених каналів зв'язку достатньо низька \[150\]. Отже, можна зробити висновок, що ефективним є підхід на основі технології реплікацій.

*Технологія розподіленого управління розподіленими даними*

В багаторівневій захищеній розподіленій СУБД, всі користувачі, розділені за відповідними рівнями їх доступу до бази даних, однак спільно використовують дану розподілену базу даних, яка включає в себе відповідні дані, що належать до різних рівнів секретності. Дана архітектура системи управління базами даних спирається на відому архітектуру системи управління відповідною розподіленою базою даних та на механізми розподіленого управління даними \[148\].

Дана архітектура включає в себе ряд модулів, які пов'язані між собою багатошаровою захищеною мережею. В однорідному середовищі усі вузли даної системи є однаковими, проте при цьому кожен вузол забезпечує обробку багаторівневих даних. Тобто кожен вузол буде мати вузол обробки запитів ою власну багатошарову захищену систему управління базами даних, що керує локальною багатошаровою базою даних. Крім того кожен вузол включає в себи модуль підтримки розподіленої обробки даних, так званий, захищений розподілений процесор \[147\].

Відповідно архітектура захищеного розподіленого процесора багато в чому схожа на архітектуру системи управління БД.

Фактор багатошаровості системи захисту системи управління БД враховується у всіх процесах, що відбуваються під час обробки даних у базі даних. В першу чергу, необхідно сформовати відповідну єдину політика безпеки, що багато у чому залежить від політики безпеки локальних систем управління БД, всієї мережі та захищених відповідних розподілених процесорів. Алгоритми щодо формування запитів, оновлення і обробки транзакцій в системі управління РБД змінюються з огляду на фактои багаторівневості системи забезпечення безпеки.

Щоб реалізувати механізми розмежування доступу необхідно мати закриті канали, тому, алгоритми підтримки багатошарової захищеної системи управління БД повинні бути сумісні з відповідними алгоритмами класичних систем управління БД для обробки багаторівневих процесів. Дані алгоритми можуть бути реалізовані на основі застосування захищеного розподіленого менеджера транзакцій SDTM. Крім того, методи підтримки безпеки та цілісності для класичних систем управління БД мають бути адаптовані щодо багаторівневих захищених систем управління БД. Як наприклад, захищений SDSM має враховувати фактор багатошаровості системи забезпечення безпеки щодо реалізації певних функцій таких як: ідентифікації, аутентифікації суб'єктів та забезпечення утримання дискреційного контролю безпеки \[144\].

На рис. 2.2 наведена загальна схема засобів, які використовуються для підтримки безпечної обробки даних у розподілених базах даних у клієнт-серверної технології. Дана технологія включає в себе ряд елементів:

• інформаційну систему як середовище передачі даних;

• сервер бази даних;

• саму базу даних;

• робочі місця клієнтів-суб'єктів, що формують запити до сервера бази даних;

• відповідно сервер безпеки даних, якій включає в себе блоки аутентифікації, розпаралелювання доступу до даних, шифрування та управління моніторингом \[148\].

Клієнт у цій моделі через інформаційну систему виконує запити до бази даних, що не залежать від типу мережі (вона може бути як локальна так і корпоративна або глобальна) потрапляють на сервер безпеки даних \[149\].

Сервер безпеки даних включає в себе чотири блоки, що відповідають за відповідний напрямок захисту даних.

Відповідно перший блок виконує функцію внутрішньої аутентифікації, що проведена засобами системи управління БД та зовнішню, яка проводиться відповідними засобами операційної системи. Дана процедура реалізується завдяки перевірці ідентифікатора користувача та його пароля у відповідності до розділу БД, до якого відбувається звернення.

БД

СУБД

БШ

**Сервер бази даних**

БУМ

БОУ

БА

БРД

**Сервер безпеки даних**

Мережа передачі даних

РС

БОУ - блок загального управління

БА - блок аутентфікаціі

БШ - блок шифрування

БРД - блок розмежування доступу

БУМ - блок управління моніторингом

РС - робоча станція

Рис. 2.2. Засоби підтримки безпечної обробки даних в розподілених базах даних

Другий блок сервера це механізм розмежування доступу. В клієнт-серверних мережах найчастіше використовуються наступні моделі: дискреційна, мандатна і рольова. Перші дві моделі використовуються для створення традиційних засобів захисту системи управління БД, а третя модель розроблена достатньо недавно та є більш складною, що базується на принципах, які закладені як і дискреційній, так і в мандатній моделях.

Блок номер три це блок шифрування. В системах управління БД дані шифруються прозорим та непрозорим способами, кожен з цих способів має вузол обробки запитів ої переваги та недоліки. Під час шифрування звичайно використовують певні алгоритми шифрування, наприклад: алгоритми, що належать до групи AES, RSA. Отже, шифрування запитів можна проводити на різних рівнях. Це може бути рівень операційної системи або так і в СУБД.

Четвертий блок сервера це блок управління моніторингом. Крім того, важливим є чинник, що вказує на оперативне реагування на загрози, даний чинник пов'язаний з тим, що процедура моніторингу відбувається за зібраними статистичними даними напротязі певного періоду часу. Проте з іншого боку цього недостатньо для забезпечення комплексного захисту системи управління БД, тому, потрібна розробка таких механізмів моніторингу, що дозволять провести аналіз усів запити клієнтів-робочих точок на сервер БД з огляду на ймовірність реалізації щодо несанкціонованого доступу

*Безпечне середовище РБЗ*

Архітектура безпечної системи управління БД для розподіленої бази даних (рис. 2.3) передбачає наявність певної кількості рівнів секретності в околі однієї системи управління БД.

Операції, що знаходяться на низькому рівні обробляються стандартно. Операції високого рівня та багаторівневі операції обробляються системою управління БД, де зберігаються високо секретні дані та копії даних, що належать до рівня нижчої секретності.

Додатки

Захищений менеджер СУБД

Особливо секретні дані

Копія секретних даних, тільки читання

Копія несекретних даних, тільки читання

Секретні дані

Копія несекретних даних, тільки читання

Несекретні дані

Рис. 2.3. Архітектура безпечної системи управління БД з багаторівневим компонентом

Відмітимо, що дана архітектура має в основі використання засобів тиражування, тобто в ній має бути присутнім менеджер тиражування та необхідна відповідна політика щодо забезпечення цілісності даних.

**  
**

## **2.2. Дослідження системи моніторингу обробки запитів в гетерогенних розподілених нереляційних базах даних**

##  

На даний час механізми моніторингу роботи розподілених баз даних стали активно розвиватися, а особливо це стосується забезпечення безпеки даних в гетерогенних розподілених нереляційних базах даних. Як розглядалося раніше спектр засобів захисту, які традиційно використовуються для захисту гетерогенних розподілених нереляційних базах даних, підтримує управління відповідними правами користувачів, захист уразливих даних і виявлення недоліків чи збоїв конфігурації гетерогенних розподілених нереляційних базах даних. Проте, не достатнє фінансування не здатне забезпечити вирішення ряд важливих аспектів, що пов'язані із забезпеченням безпеки гетерогенних розподілених нереляційних базах даних, зокрема:

• розділення прав з адміністрування і розробці гетерогенних розподілених нереляційних базах даних та систем забезпечення безпеки;

• неправильне використання чи умисне перевищення прав суб'єктів;

• відповідно атаки на бази даних із застосуванням вразливих місць, що не можуть запобігти за допомогою традиційних механізмів забезпечення безпеки.

Методи моніторингу функціонування гетерогенних розподілених нереляційних базах даних покликані усунути приведені недоліки і забезпечити контроль щодо дій суб'єктів, що виконуються в гетерогенних розподілених нереляційних базах даних, попередження щодо виявлення підозрілої діяльності, а також зупинення такої діяльності.

*Мережевий доступ щодо реалізації методів моніторингу функціонування гетерогенних розподілених нереляційних баз даних.*

На початку засоби моніторингу роботи бази даних орієнтовані на певні мережеві додатки. Зокрема мережеве апаратне забезпечення здійснює моніторинг мережевого трафіку щодо пошуку інструкцій підозрілих команд, далі проводить аналіз із урахуванням зазначених правил політики безпеки. Це проводиться для можливості сформувати попередження щодо несанкціонованого доступу до гетерогенної розподіленої нереляційної бази даних та спробах вторгнень. Проте в даному випадку відбувається лише моніторинг мережевих механізмів, тому локальна БД залишається вразливою щодо внутрішніх легальних користувачів, що перевищують вузол обробки запитів ої повноваження. Для того щоб забезпечити ефективний захист, механізми захисту мають використовуватися для будь якої вразливої точки, що знаходиться в мережі, з якої є доступ до розподіленої бази даних. Для розподілених баз даних що містять критично важливі дані, що пов'язані з великою кількістю додатків ціна на подібні засоби захисту виявляється достатньо високою. Зокрема, мережевий підхід щодо реалізації механізмів моніторингу функціонування гетерогенної розподіленої нереляційної бази даних має декілька важливих недоліків:

*Відсутність покриття щодо локального доступу до розподіленої бази даних*

При зборі та аналізі мережевої інформації, запитання щодо локального доступу суб'єктів залишаються поза контролем. Для розв’язання даної проблеми розроблено ряд спеціальних базових програм, що застосовуються як доповнення до вузол обробки запитів оїх мережевих додатків. Цей підхід при встановленні вказаних механізмів як на локальній машині, так і в мережевій інфраструктурі акумулює лише переваги відповідних мережевих додатків. Тому вони залишаються певним чином захищеними від вторгнень. В цей же час локальні агенти здійснюють моніторинг трафіку на локальній машині чи в мережевому середовищі, проте не можуть запобігти вторгнення, тому що мають встановлюватися в ядро системи, а це ускладнює їх установку та технічну підтримку. Щоб база даних функціонувала ефективно недостатньо відстежувати лише мережевий трафік, навіть у випадку коли виконується моніторинг запитів ядра.

Прикладна система управління БД підтримується адміністратором, який супроводжує її з використанням інтерфейсу, однак його дії, зазвичай, у журналі подій системи управління базою даних не відображаються.

Далі, в самій системі управління БД можуть бути уразливості, які дозволяють її пошкодити, а це може призвести до непередбачуваних змін у базі, що не будуть записані в журналі подій.

Крім того, часто виникає необхідність виконання деяких змін у базі даних з використанням команд, обходячи інтерфейс системи управління БД. Зрозуміло, що такі дії потрібно контролювати, тому що велика ймовірність, що зміни будуть невірним. У самих системах ведення вказаних даних не передбачено, оскільки вони надходять ззовні, крім того важливо слідкувати, що всі зміни пророблені до запуску прорахунку, а не під час його виконання чи закінчення.

Вище згадані випадки говорять про те, що одного журналу обробки запитів недостатньо, тому потрібний аудит зміни даних, що відбувається на рівні бази.

Отже, застосування засобів моніторингу на рівні бази даних є ефективним допоміжним інструментом для забезпечення безпеки та виключення помилок під час експлуатації бази даних. Основним показником для вибору механізму, який забезпечує моніторинг, є як найменший вплив прийнятого рішення на ефективність системи.

*Моніторинг збереження даних в гетерогенних розподілених нереляційних баз даних.*

Ще одним підходом щодо реалізації моніторингу обробки запитів, що ґрунтується на можливості вилучення та подальшої обробки інформації наявної в журналі збереження даних у базі. Для систем управління розроблені спеціальні засоби, які володіють можливостями захоплення змін з журналів збереження даних та дозволяють аудитору віддалено від’єднуватися до журналів збереження даних цільових баз, застосовувати фільтри на вибірку необхідних записів та отримувати зручні щодо аналізу звіти у різних форматах і т.д.

Основним недоліком даних систем є те, що захоплення змін відбувається безпосередньо на цільовій базі. Даний процес є досить складним, тому що він пов'язаний з парсингом та трансформацією даних. Проте у порівнянні з підключенням відповідного вбудованого аудиту системи управління БД спосіб захоплення завантажує систему не так сильно, однак і це не завжди можна використовувати на вихідній базі, тим паче у випадку коли система активно працює щодо досягнення вузол обробки запитів оєї цільової функції.

*Архітектура сервера контролю змін в гетерогенних розподілених нереляційних баз даних*

Раціональнішим рішенням буде варіант, коли сервери з розподіленими базами даних цілком позбавляються від всіх сторонніх функцій, і виконання завдань щодо пошуку, обробці і зберіганню інформації щодо змін, які відбуваються на спеціально виділеному сервері. На рис 2.4. представлена архітектура системи моніторингу вказаного типу.

БД

Файли

архіва

Сервер БД

БД

Файли

архіву

Сервер БД

**.**

**.**

Засоби

захоплення

змін

Засоби

захоплення

змін

БД

Рис. 2.4. Архітектура сервера контролю змін

Центральним елементом наведеної архітектури буде Сервер контролю змін, де виконується процес пошуку та обробки записів із архівних журналів, які надходять з серверів на яких розміщені вихідні бази. Даний сервер може обслуговувати декілька вихідних баз. Для цих баз породжується вузол обробки запитів ій процес захоплення та обробки змін. Основною особливістю цієї архітектури є те, відповідні вихідні бази на сервер контролю змін не переміщаються, а інформація щодо структуру бази, а саме складова вмісту словника даних отримується з архівного журналу чи якимось іншим методом передана на сервер контролю змін.

До числа додаткових переваг, які випливають з вказаної архітектури, можна віднести: її економічна вигідність (для реалізації такої системи досить одного нового сервера обробки даних); крім того це можливість отримання інформації про зміни, здійснені в декількох джерелах; ще до переваг можна віднести організацію централізованого зберігання файлів архівних журналів і тому подібне.

Відомо, що при проведенні перевірки обробки запитів в гетерогенних розподілених нереляційних баз даних, особливо таких, що включають в себе велике число записів, які розміщені розподілено, виникає завдання оперативної обробки досить великого обсягу даних щодо обробки запитів моніторингу. Отже, потрібна розробка методу динамічної обробки даних із моніторингу, що забезпечить швидке відстеження потенційних вторгнень та атак на базу даних.

Отже, потрібно розробити систему моніторингу обробки запитів з прискореною обробкою даних і експериментальним чином дослідити її ефективність.

Пропонується система, що включає наступні основні блоки:

блок спеціальних засобів збору даних із моніторингу;

блок засобів активації процесу моніторингу;

блок перетворення, який виконує перетворення обробки запитів моніторингу в дані формату Oracle;

блок накопичення даних до обробки запитів моніторингу і їх зберігання у базі даних, і останній блок обробки даних з моніторингу.

Архітектура даної системи наведена на рис. 2.5.

Блок активації процедури моніторингу

Блок збору

даних з моніторингу

Блок накопичення т зберігання запитів моніторингу

Блок перетворення інформації в формат БД

Блок обробки

запитів моніторингу

Рис.2.5. Архітектура системи моніторингу обробки запитів в гетерогенних розподілених нереляційних баз даних

Розглянемо більш детально особливості застосування наведених вище блоків. Основним новим елементом є блок перетворення даних із моніторингу у формат гетерогенної розподіленої нереляційної бази даних. У загальному випадку даний блок відсутній та дані збираються в єдиному файлі. Крім того, в процесі моніторингу формується вектор критичних обробок запитів ![](media/image1.wmf) пов'язаних з обробками запитів порушення безпеки, потім даний вектор обробляється за з використанням алгоритму. Зокрема, у якості аргументів ![](media/image2.wmf) – виступають фактори, які відслідковуються:

![](media/image3.wmf) – число спроб звернень до деяких даних із бази даних;

![](media/image4.wmf) – число спроб зміни певних даних;

![](media/image5.wmf) – кількість спроб входу до бази даних під якимись ім'ям і т.д.

Для побудови ефективної системи моніторингу обробки запитів дії кожного з суб'єктів потрібно оцінювати за результатами декількох сеансів обробки запитів його роботи із базою даних. В тому випадку, коли база даних є розподіленою, до неї звертається певна кількість суб'єктів, відносно кожного з них потрібно зібрати відповідну інформацію у форматі вектора ![](media/image1.wmf)*.* На практиці, зважаючи на особливості функціонування гетерогенних нереляційних розподілених систем, число записів щодо обробки запитів моніторингу в них виявляється достатньо значним, причому самі дані записи формуються у порядку взаємодії суб'єкта з базою даних, відповідно дані про обробку запитів безпеки щодо кожного суб'єкту виявляються розподіленими відповідно по всьому файлу записів.

Під час обробки файлу записів щодо вектора моніторингу ![](media/image6.wmf) фактично відбувається пошук, вибір даних та кортежів даних за вказаним шаблоном. З збільшенням розміру файлу записів щодо обробки запитів моніторингу збільшується складність та уповільнюється процес пошуку і обробки даних, які характерні при зборі відповідної статистики для розподілених баз даних, що включають в себе значний обсяг даних. Уповільнення у процедурі аналізу даних із моніторингу обробки даних можуть привести до утворення ситуацій пропуску великої кількості атак, а це в вузол обробки запитів ою чергу, знизить безпеку зберігання даних. Отже, виникає завдання зниження часу пошуку та вибірки даних з моніторингу обробки даних.

Для вирішення даного завдання пропонується формувати записи обробки моніторингу із моніторингу у вигляді бази даних, що дозволить використовувати механізми системи управління БД для їх обробки. Зважаючи на те, що дані механізми є спеціальними механізмами обробки даних, заданими в форматі записів баз даних, можна допустити, що в даному випадку ми будемо бачити зниження часу обробки даних із бази даних у порівнянні із механізмом прямого пошуку та вибірки даних із масиву векторів записів даних.

Для дослідження ефективності запропонованих засобів моніторингу обробки запитів з прискореною обробкою даних було проведено експериментальні дослідження часу пошуку та вибірки даних з моніторингу обробки запитів, представлених двояко: в першому випадку було представлено у вигляді файлу як масиву векторів-записів, а у другому це вигляд записів бази даних.

Після проведення аналізу параметрів системи моніторингу обробки запитів у розподілених базах даних розроблена методика, що дозволяє оцінювати ефективність функціонування серверу моніторингу обробки запитів на основі модуль контролю обробки запитів.

Дії суб’єктів у базах даних, по відношенню до інформаційної безпеки можна розділити за наступними ознаками:

1.  Допустима (нормальна) поведінка суб’єктів.

2.  Атака (внутрішні ті зовнішні) порушника.

Нехай ![](media/image7.wmf) – кількість можливих атак на бази даних, ![](media/image8.wmf) – множина допустимих профілів поведінки суб’єктів. Позначимо: ![](media/image9.wmf)– множина атак, що не були виявлені системами моніторингу безпеки, ![](media/image10.wmf)– множина нормальних профілів поведінки суб’єктів, що були неправильно ідентифіковані системою моніторингу безпеки і були визначені як вторгнення.

Ймовірність коректного виявлення атаки розраховується як:

![](media/image11.wmf).

Ймовірність неправильних ідентифікацій допустимих профілів поведінки суб’єктів розраховується як:

![](media/image12.wmf),

де $G - i + o$![](media/image13.wmf) кількість вторгнень, що були виявлені системою моніторингу безпеки.

Крім того ймовірність коректного виявлення атак системою моніторингу безпеки розраховується наступним чином:

![](media/image14.wmf).

Отримана ймовірність використовується як показник для загальної оцінки ефективності функціонування системи моніторингу обробки запитів в гетерогенних розподілених нереляційних баз даних.

Ймовірність правильної роботи серверу моніторингу обробки запитів визначається за формулою:

![](media/image15.wmf),

де ![](media/image16.wmf) – це ймовірність помилки І роду (тобто відсутність реакції на атаку), ![](media/image17.wmf)$P_{II}$ – ймовірність помилки ІІ роду (тобто помилкове спрацювання).

Зробимо оцінки витрат, що були здійснені на створення системи моніторингу безпеки.

С – загальна величина витрат, яку можна записати наступним чином:

![](media/image18.wmf)$С = с_{1} + с_{2} + с_{3} + с_{4} + с_{5} + с_{6} + с_{7}$,

де:

![](media/image19.wmf) – витрати, що були здійснені на апаратну частину збору інформації;

![](media/image20.wmf) – витрати, що були здійснені на впровадження та підтримку ПО;

![](media/image21.wmf)$с_{3}$ – витрати, що були здійснені на систему моніторингу безпеки;

![](media/image22.wmf)$с_{4}$ – витрати, що були здійснені на оплату праці спеціалістів;

![](media/image23.wmf) – витрати, що були здійснені на оплату праці адміністратора;

![](media/image24.wmf) – величина, яка відноситься до обчислювальних витрат, які потрібні системі моніторингу безпеки;

![](media/image25.wmf) – витрати на пропущені вторгнення.

Для отримання загальної оцінки витрат на реалізацію системи моніторингу безпеки в гетерогенних розподілених нереляційних базах даних за весь час спостереження можна отримати за допомогою операції інтегрування при інтегруванні отриманих кривих витрат:

![](media/image26.wmf),

де ![](media/image27.wmf)– витрати, які були здійснені у відповідний момент часу, ![](media/image28.wmf)$C_{\sum}$ – загальна вартість витрат за весь період часу ![](media/image29.wmf).

## **2.3. Розробка моделі моніторингу обробки запитів в гетерогенних розподілених нереляційних базах даних на основі** модуля контролю **обробки запитів** 

## **Загальна архітектура засобів моніторингу обробки запитів нереляційних баз даних на основі** модуля контролю **обробки запитів**

## 

Локально-орієнтовані підходи до моніторингу обробки запитів баз даних в в гетерогенних розподілених комп'ютерних мережах мають істотний недолік: вони понижують загальну продуктивність обробки даних в базах даних  
з погляду на те, що локально-орієнтовані засоби, можуть реалізовувати  
власний механізм аудиту, чи використовують API-функції  
ядра системи управління гетерогенними розподіленими не реляційними  
базами даних для взаємодії з базою даних, а це вимагає значних часових витрат \[128\].

Таким чином, незважаючи на те, що локально-орієнтований підхід є досить ефективним для реалізації основних вимог до моніторингу дій легальних користувачів, а також для виявлення і нейтралізації вторгнень, на практиці мережевий підхід набуває все більшого поширення, незважаючи на його певні недоліки.

Класична модель моніторингу будується на основі алгоритму найбільших статистичних аномалій (АНСА), тобто формуванні вектора Бернулі, який і обробляється сервером моніторингу. Але елементи вектора включають в себе тільки параметри подій, але не включають вплив події на той чи інший елемент системи. Перелік подій підсистем надійності та безпеки СУБД та наслідки і загрози, які виникають при цьому наведені в табл. 2.1.

Таблиця 2.1

Перелік можливих подій підсистем надійності й безпеки і можливих наслідків

| Події підсистем надійності ОС та СУБД |  |  |  |
|:--:|:--:|:--:|:--:|
| Позначення | Події надійності і коректності зберігання даних | Можливі наслідки | Позначення |
| ![](media/image30.wmf) | Спроба порушення доступу до ОС серверу | Порушення цілісності ОС, як наслідок СУБД | ![](media/image31.wmf) |
| ![](media/image32.wmf) | Спроби порушення доступу до елементів робочих станцій користувача | Порушення цілісності ОС, як наслідок підміна даних | ![](media/image33.wmf) |
| ![](media/image34.wmf) | Спроби порушення прав доступу до СУБД та елементів БД | Порушення цілісності даних | ![](media/image35.wmf) |
| ![](media/image36.wmf) | Блокування операцій різних транзакцій | Виконання операцій за неприйнятний час | ![](media/image37.wmf) |
| ![](media/image38.wmf) | Відміна незакінчених транзакцій | Втрата актуальності даних | ![](media/image39.wmf) |
| ![](media/image40.wmf) | Блокування перебудови процедур | Втрата актуальності процедур | ![](media/image41.wmf) |
| ![](media/image42.wmf) | Порушення процесів реплікації | Втрата даних в разі збоїв основного серверу | ![](media/image43.wmf) |
| ![](media/image44.wmf) | Порушення процесів резервного зберігання даних | Втрата даних в разі збоїв серверу | ![](media/image45.wmf) |
| ![](media/image46.wmf) | Порушення процесів роботи тригерів | Втрата актуальності даних | ![](media/image47.wmf) |
| ![](media/image48.wmf) | Порушення процесів роботи функцій | Втрата актуальності даних | ![](media/image49.wmf) |

Приведемо приклад (табл. 2.2) побудованої і-тої порогові матриці для підсистеми надійності ![](media/image50.wmf) по вертикалі ![](media/image51.wmf)а по горизонталі ![](media/image52.wmf).

Дамо визначення для використання їх в моделі моніторингу обробки запитів.

<u>Матрицею збору</u> називається матриця ![](media/image53.wmf), яка кожному вектору типу запиту ![](media/image54.wmf) ставить у відповідність наслідки (відповіді) з вектору можливих наслідків ![](media/image55.wmf).

$c_{1},\ldots.,c_{10}$

Таблиця 2.2

Приклад і-тої матриці збору

|  | ![](media/image56.wmf) | ![](media/image57.wmf) | ![](media/image58.wmf) | ![](media/image59.wmf) | ![](media/image60.wmf) | ![](media/image61.wmf) | ![](media/image62.wmf) | ![](media/image63.wmf) | ![](media/image64.wmf) | ![](media/image65.wmf) |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| ![](media/image66.wmf) | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| ![](media/image67.wmf) | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 |
| ![](media/image68.wmf) | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| ![](media/image69.wmf) | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| ![](media/image70.wmf) | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 1 |
| ![](media/image71.wmf) | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| ![](media/image72.wmf) | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| ![](media/image73.wmf) | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 |
| ![](media/image74.wmf) | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 |
| ![](media/image75.wmf) | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 |

<u>Пороговою матрицею</u> називається матриця ![](media/image76.wmf) (в самому простому випадку одинична) в якій кожному запиту відповідає множина наслідків, які не впливають на роботу системи.

<u>Результуюча матриця</u> ![](media/image77.wmf) - це матриця в які відсутні наслідки, що не впливають на роботу системи.

<u>Вектор експертних оцінок</u> - це вектор ![](media/image78.wmf), який створюється на основі середньо статистичних оцінок експертів про вплив того чи іншого наслідку на ту чи іншу подію.

Опишемо модель моніторингу обробки запитів на основі модулів контролю обробки запитів.

Задано:

Нехай існує множина запитів *Q* розподілених нереляційних баз даних, які можна представити векторами ![](media/image79.wmf).

Також, множина відповідей на запити *A* розподілених баз даних, які можна представити векторами ![](media/image80.wmf).

Створимо матрицю збору ![](media/image81.wmf), яка формується за допомогою функції ![](media/image82.wmf), що дорівнює 1 якщо подія впливає на конкретний наслідок та 0 якщо ні.

Означимо порогову матрицю ![](media/image83.wmf), що визначає наслідки, які не впливають на роботу системи.

Задамо результуючу матрицю (матрицю обробки запитів) ![](media/image84.wmf) - матрицю різниці матриці збору та порогової матриці.

Створимо множину експертних оцінок *W,* які можна представити векторами ![](media/image85.wmf), де ![](media/image86.wmf)- оцінка обробки запиту, а ![](media/image87.wmf).

Задамо результуючий вектор ![](media/image88.wmf), який показує вплив запиту на конкретний елемент системи.

Потрібно отримати:

Вектор повідомлень про вплив подій на конкретні елементи системи та множину обробників, які дозволять оперативно зреагувати засобами контролю стану на інциденти безпеки. А в разі неможливості коректного відновлення роботи системи повідомити адміністраторів для прийняття відповідних рішень.

А саме: ![](media/image89.wmf).

Метод обробки запитів моніторингу на сервері моніторингу обробки запитів:

Твердження 2.1. Якщо існує матриця збору ![](media/image90.wmf)та порогова матриця ![](media/image91.wmf), то ![](media/image92.wmf) є результуючою матрицею, що складається з наслідків, які впливають на роботу системи.

Доведення:

В матрицю збору ![](media/image90.wmf) входять всі наслідки на запит, які були зібрані модулями контролю, а в порогову матрицю ![](media/image91.wmf) входять тільки наслідки, які не впливають на роботу системи.

Різниця цих матриць дає результуючу матрицю ![](media/image93.wmf), яка складається тільки з наслідків обробки запитів, які впливають на роботу системи, тому що при відніманні двох матриць проходить віднімання елементів з однаковими номерами

![](media/image94.wmf),

а це призводить до не попадання в матрицю ![](media/image95.wmf) елементів, які мають однакове значення в матрицях![](media/image96.wmf) та ![](media/image97.wmf).

Твердження 2.2. Нехай існує множина експертних оцінок ![](media/image98.wmf) в якій для кожного запиту визнається оцінка впливу та результуюча матриця ![](media/image99.wmf) в яку входять тільки наслідки, які впливають на роботу системи. Після виконання операцій ![](media/image100.wmf) отримаємо результуючий вектор ![](media/image101.wmf), який визначає наслідки, які впливають на роботу системи.

Доведення:

При множені результуючої матриці та вектору експертних оцінок

![](media/image102.wmf)

отримуємо вектор ![](media/image103.wmf), який показує наскільки той чи інший наслідок впливає на конкретний елемент системи.

Алгоритм роботи моніторингу обробки запитів розподілених нереляційних баз даних на основі модулів контролю обробки запитів:

1\. На кожну базу даних з розподіленої системи будуємо модулі контролю на основі процедур обробки запитів.

2\. Для кожної множини запитів ![](media/image104.wmf), де *q*<sub>k</sub> – *k* запит, який збирається модулями контролю, будується множина відповідей можливих наслідків кожного запиту ![](media/image105.wmf), де *a*<sub>n</sub> – *n* наслідок запиту.

3\. За допомогою модулю контролю отримується матриці збору ![](media/image106.wmf) з простору *S* та передаються їх на сервер моніторингу обробки запитів.

4\. Після передачі матриці на сервер моніторингу обробки запитів проводяться операції різниці між отриманою матрицею ![](media/image107.wmf) та відповідною пороговою матрицею ![](media/image76.wmf), тобто ![](media/image108.wmf).

5\. Проводиться формування експертних оцінок, тобто формування вектору ![](media/image109.wmf), де *w*<sub>z</sub> – експертна оцінка *z* типу запиту.

6\. Після отримання вектору експертних оцінок матриця ![](media/image77.wmf) перемножаться на вектор експертних оцінок ![](media/image110.wmf) відповідно,

![](media/image111.wmf).

7\. Отриманий вектор ![](media/image112.wmf), який показує вплив запиту на конкретний елемент системи, передаються на сервер моніторингу обробки запитів.

8\. Вектор ![](media/image113.wmf) передається в модуль контролю обробки запитів.

9\. В модулі контролю обробки запитів вразі виявлення ситуацій, які можуть спричинити негативні наслідки для баз даних розподіленої системи генерується рішення про застосування тих чи інших мір по нейтралізації негативних наслідків.

10\. У разі виникнення нештатних ситуацій модуль контролю обробки запитів передає сигнал через блок формування попередження адміністратору серверу моніторингу обробки запитів.

Структура запропонованої системи також забезпечує розподіл прав і повноважень між суб'єктами, що є одною з основних вимог до системи безпеки. Адміністратор безпеки цієї системи є персоною, що визначає правила політики безпеки і отримує повідомлення про інциденти від різних джерел, зокрема від адміністратора комп'ютерної системи та адміністратора бази даних. Запропонована система дозволяє забезпечити заданий рівень захисту гетерогенної розподіленої не реляційної бази даних і безперервне виконання обчислювальних операцій базою даних.

## 2.3.2. Архітектура модулю контролю запропонованої системи моніторингу обробки запитів.

## 

Модуль контролю запропонованої системи моніторингу безпеки (СМБ) є окремий механізм, який функціонує в вузлі розподіленої бази даних, при цьому він надійно захищений від зовнішніх атак. (рис. 2.6.).

Модуль контролю автоматично ідентифікує події, що відбуваються в розподіленій комп'ютерній системі. В процесі роботи модуль контролю прикріплюється до тимчасово-виділеної пам'яті (SGA у разі Oracle) і циклічно запускає опитування з моніторингу обробки запитів шляхом вибірки даних з пам'яті з певною частотою. На кожному циклі модуль контролю виконує аналіз активних в даний момент процесів у кожній сесії в базі даних і визначає за допомогою встановлених адміністратором правил підозрілі події. Повідомлення про підозрілі події відправляються на сервер бази даних для їх подальшого аналізу і генерації відповідних повідомлень.

Збір подій

БД

Адміністратор БД

Модуль контролю

Блок формування попередження

БД

Сервер моніторингу обробки запитів

Передача результатів обробки

Корекція налаштувань

Повідомлення про загрозу

Передача матриці подій на сервер

БД

Рис. 2.6. Архітектура засобів моніторингу обробки запитів  
баз даних на основі модулю контролю

Модуль контролю також може примусово достроково припиняти сесії роботи в разі певних порушень з боку користувачів. З іншого боку, для його роботи потрібні незначні обчислювальні ресурси системи і він практично не впливає на операції введення/виводу. Упереджувальна функція модулю контролю може бути реалізована з використанням тригерів або процедур, які вибірково затримують виконання команд на короткі проміжки часу (кілька мілісекунд), що дозволяє модулю контролю вузлу обробки запитів своєчасно реагувати на небезпечні дії.

Структура пропонованої системи також забезпечує розподіл прав і повноважень між суб'єктами, що є одною з основних вимог до системи безпеки. Адміністратор цієї системи є персоною, що визначає правила політики безпеки і отримує повідомлення про інциденти від різних джерел, зокрема від адміністратора комп'ютерної системи та адміністратора бази даних. Запропонований підхід дозволяє, забезпечити достатній рівень захисту гетерогенних не реляційних розподілених баз даних, а з іншого - безперервне виконання обчислювальних операцій системою (рис. 2.7).

Блок обміну даними

Сервер моніторингу обробки запитів

Управління збором даних

Блок профілю

Блок збору даних

Блок доступу до БД

Фільтр запитів

Вихідна черга

БД

Аутентифікація на сервері

Отримання даних

Формування матриці подій

Передача матриці на сервер

Підготовка матриці подій

Рис. 2.7. Архітектура модуля контролю

Виділений сервер в запропонованій системі моніторингу обробки запитів може керувати кількома модулями контролю з різних баз даних, а також він підтримує функцію масштабування числа модулів контролю. Сервер досить просто інтегрується в структуру системи безпеки, що дозволяє підвищити ефективність загального управління безпекою комп'ютерної системи. (рис. 2.8).

Таким чином, в результаті, запропоновано спеціалізований механізм реалізації моніторингу обробки запитів нереляційних баз даних, за допомогою якого виконується комплексний моніторинг усіх дій з базою даних і забезпечується захист від несанкціонованих дій легальних користувачів. Також, даний механізм дозволяє виконати детальний моніторинг транзакцій, запитів, об'єктів і збережених процедур бази даних з оперативним повідомленнями про інциденти і попередженням вторгнень.

Крім того, запропонований механізм дозволяє провести відстеження нових виявлених вразливих місць бази даних і оперативно усунути ці уразливості, що важливо в практичних застосуваннях.

WEB-інтерфейс

Рівень представлення

(з аутентифікацією)

Механізми

безпеки

Рівень сервісів

Обробники

Вхідна

черга

Вихідна

черга

Рівень доступу до даних

Зовнішня система управління

Сховище

даних

Модуль

Рис. 2.8. Архітектура сервера моніторингу обробки запитів

Тому було запропоновано удосконалену модель моніторингу обробки запитів у гетерогенних розподілених нереляційних базах даних, яка відрізняється від існуючих використанням механізмів на основі застосування матриці обробки запитів. Зазначена модель дозволяє, у випадку виникнення нештатних ситуацій, передати попередження адміністратору серверу моніторингу обробки запитів, прийняти оперативні рішення щодо реагування на порушення безпеки під час обробки даних.

## Висновки до розділу 2

## 

Розглянуто особливості базових засобів підтримки безпечної обробки даних в розподілених нереляційних базах даних. Визначено основні компоненти системи управлінням моніторингу серверу обробки запитів. Показано, що для підтримки інформаційної безпеки СУБД важливі всі три основні аспекти: конфіденційність, цілісність та доступність.

Пропонується побудова багаторівневого захисту нереляційних баз даних на основі моделі Белла-ЛаПадула. Показано, що реалізація засобів захисту розподілених БД на основі запропонованих механізмів забезпечує підтримку необхідного рівня захищеності розподілених БД в умовах динамічної зміни числа користувачів-суб'єктів.

Запропоновано удосконалену модель моніторингу обробки запитів у гетерогенних розподілених нереляційних базах даних, яка відрізняється від існуючих використанням механізмів на основі застосування матриці обробки запитів. Зазначена модель дозволяє, у випадку виникнення нештатних ситуацій, передати попередження адміністратору серверу моніторингу обробки запитів, прийняти оперативні рішення щодо реагування на порушення безпеки під час обробки даних.

Розглянуті питання забезпечення надійності обробки даних в системі моніторингу та запропоновані засоби моніторингу обробки запитів взаємодії Web-інтерфейсу з середовищем зберігання даних на основі модулів контролю. Показано, що даний механізм дозволяє виконати детальний моніторинг транзакцій, запитів, об'єктів і збережених процедур бази даних з повідомленнями про інциденти в режимі реального часу і попередженням вторгнень. Показано, що в зв’язку з завантаженням серверів розподілених нереляційних баз даних потрібно розробити методи для прискорення обробки запитів.

<span id="_Toc1250191" class="anchor"></span>**РОЗДІЛ 3 РОЗРОБКА МЕТОДУ ВИЗНАЧЕННЯ НЕСПРАВНОСТІ ВУЗЛІВ ОБРОБКИ ЗАПИТІВ В ГЕТЕРОГЕННИХ РОЗПОДІЛЕНИХ НЕРЕЛЯЦІЙНИХ БАЗАХ ДАНИХ НА ОСНОВІ ЗАСТОСУВАННЯ ДВОРІВНЕВОЇ СИСТЕМИ**

Для проведення моніторингу гетерогенних розподілених нереляційних баз даних з визначення прихованих несправностей вузлів обробки запитів слід використати декілька рівнів. Прихована несправність – це несправність, що не виявляється візуально або штатними методами та засобами контролю і моніторингу, проте виявляється спеціальними методами моніторингу. На першому рівні використовуються прості моніторингові процедури. Коли за їх допомогою вдається визначити вузли обробки запитів, які є несправними, то на цьому моніторинг із найменшими витратами часу завершується. Але якщо є неоднозначності щодо визначення елементів розподіленої бази даних, які відмовили, користувач бази даних має запустити моніторингові процедури, які здатні впоратися з складнішими несправностями вузла обробки запитів. В даному випадку висловлене припущення про те, що простіші несправності вузла обробки запитів виникатимуть частіше, ніж складніші. А отже не потрібно відразу використовувати дуже сильні, моніторингові дії, які потребують великих часових затрат.

В роботі розроблено два алгоритми, що забезпечують дворівневу систему моніторингу гетерогенних розподілених нереляційних баз даних з прихованими несправностями, що дозволяють здійснити моніторинг із різною якістю та різний час, а це узгоджується із ієрархічною концепцією. Якщо несправності не вимагають великої якості моніторинг, то простіший та швидший перший алгоритм, який дозволяє завершити з мінімальними часовими затратами. Якщо рішення негативне, то моніторинг триває із застосуванням потужнішого другого алгоритму.

## **3.1. Вибір і обґрунтування моніторингової моделі гетерогенних розподілених нереляційних базах даних** 

## 

Розглянемо гетерогенну розподілену нереляційну базу даних, яка складається з ![](media/image114.wmf) вузлів обробки запитів, в якій може відмовити не більше ![](media/image115.wmf) вузлів. Дана модель допускає моніторинг більшої кількості несправностей. Так наприклад, для гетерогенної розподіленої нереляційної бази даних, яка складається з ![](media/image116.wmf) вузлів обробки запитів при класичній моделі, яка містить <img src="media/image117.wmf" style="width:0.80833in;height:0.20833in" /> вузлів обробки запитів, число несправностей не перевищує двох, для пропонованої – трьох.

Введемо деякі припущення:

1\. Представимо в вигляді неорієнтованого графа зв'язки між вузлами обробки запитів гетерогенної розподіленої нереляційної бази даних. Мається на увазі, те що будь-яка пара вузлів обробки запитів може обмінюватися повідомленнями з користувачем та між собою. Причому кожен вузол обробки запитів може визначити того хто відправив повідомлення.

2\. Крім того база даних є синхронною. Під синхроністю розуміється наявність апарату, що дозволяє усім вузол обробки запитів бази даних одночасно перейти до моніторинг. Іншими словами процес, що виконується в гетерогенну розподіленій нереляційній базі даних періодично зупиняється в контрольних точках (КТ). Це здійснюється шляхом синхронізації годинника вузлів обробки запитів при запуску бази даних або у подальші моменти із використанням будь якого алгоритму взаємного інформаційного узгодження.

3\. Вузли обробки запитами обмінюються повідомленнями, що вибираються з множини

![](media/image118.wmf)

де ![](media/image119.wmf) – вид запиту, у якого семантика залежить від певного випадку; ![](media/image120.wmf) –протилежне ![](media/image121.wmf); ![](media/image122.wmf) – порожнє повідомлення. Такий варіант застосовується у тих випадках, коли за певний період часу по каналах мережі не передано ніяких повідомлень.

4\. Всі вузли обробки запитів за допомогою засобів моніторинг визначає стан ![](media/image123.wmf). Вузол може набувати два значення ![](media/image124.wmf)(справний) та ![](media/image125.wmf) (несправний).

5\. Під час передачі запитів з різною семантикою вузол обробки запитів витрачає на кожний запит час ![](media/image126.wmf), який не залежить від кількості вузлів обробки запитів на які цей запит відправляється.

6\. Вузол обробки запитів ![](media/image127.wmf) використовує на отримання запиту від вузла обробки запитів![](media/image128.wmf)час ![](media/image129.wmf)

7\. Виконується така нерівність:

![](media/image130.wmf).

Нехай вузол обробки запитів ![](media/image131.wmf)(![](media/image132.wmf)) є «основним». Кожному з інших вузлів обробки запитів («другорядним») вузол обробки запитів *k* повинен передати запит відповідно до допущення 3. Після цього «другорядні» обмінюються повідомленнями про отриману від «основного» інформацію, при цьому кожен утворює початковий набір (ПН), за яким визначаються «нелояльні другорядні» і потім ті, які залишилися досягають угоди з приводу «наказу» «основного», – «прийняти» чи «відкинути».

Нелояльність (прихованість) вузла обробки запитів полягає в довільному спотворенні запиту що передається. При цьому в різних запитах нелояльний «другорядний» передає суперечливі інформацію іншим. Якщо моніторинг гетерогенної розподіленої нереляційної бази даних приводить кожен лояльний (справний) вузол обробки запитів до однозначного визначення нелояльних (несправних) вузлів обробки запитів, то угода між лояльними «другорядними» та лояльним «основним» (якщо в вузлах він є) буде отримана під час обліку кожним «другорядним» думок тільки лояльних вузлів обробки запитів, лояльність яких визначається в результаті процедури моніторинг.

Нехай ![](media/image133.wmf), ![](media/image134.wmf) і, що кожному вузлу обробки запитів в базі даних привузол обробки запитів оєний індивідуальний номер ![](media/image135.wmf)що відомий усім вузлам обробки запитів.

Початковий набір, що формується в n-му вузлі обробки запитів, має вигляд наступної матриці

![](media/image136.wmf),

де

![](media/image137.wmf)

в i-му рядку містяться значення запитів усіх j-х вузлів обробки запитів, отримані в першій ітераціїi-ю і надіслані ним в другій ітерації в n-тий вузол обробки запитів;

в j-му стовпці містяться значення запитів одного і того ж j- го вузла обробки запитів, передані ним усім i-м вузлам обробки запитів;

на головній діагоналі розташовані елементи ![](media/image138.wmf), що є значеннями запитів j-х вузлів обробки запитів, які передані ними ж  
першому раунді.

В алгоритмі застосовується функція *majority*, що визначається по-різному. Введемо наступне визначення цієї функції. Нехай заданий вектор ![](media/image139.wmf) та нехай розряди утворюються за властивістю рівності значень у групи M1,M2,...,Mm, що не перетинаються. Очевидно![](media/image140.wmf).

Нехай ![](media/image141.wmf), де через ![](media/image142.wmf) позначена потужність множини ![](media/image143.wmf) а саме кількість елементів множини. У випадку коли розряди ![](media/image144.wmf), які входять в ![](media/image145.wmf) мають значення ![](media/image146.wmf), то функція ![](media/image147.wmf) визначається рівністю:

![](media/image148.wmf)

Якщо ![](media/image149.wmf), тоді значення функції ![](media/image147.wmf) визначається випадковим підбором індексу групи із числа груп найбільшого розміру.

Необхідно зазначити, що у випадку, якщо ![](media/image150.wmf) (![](media/image151.wmf)) та вектор має парну кількість розрядів, то зазвичай виконується строга нерівність ![](media/image152.wmf). У подальшому досліджується саме такий випадок двійкових векторів.

## **3.2. Розробка алгоритму моніторинг гетерогенних розподілених нереляційних баз даних на основі використання взаємного інформаційного узгодження**

Розглянемо гетерогенну розподілену нереляційну базу даних, що складається з ![](media/image153.wmf)вузлів обробки запитів з номерами ![](media/image154.wmf). Діагностика здійснюється шляхом обміну запитами при припущеннях про синхронність гетерогенної розподіленої нереляційної бази даних та про можливість одержувачем запиту визначити вузол відправника.

Алгоритм А1 складається з наступних етапів:

– етапу пересилок запитів (кроки 1-3);

– етапу аналізу отриманого запитів (кроки 4-7).

Даний етап щодо аналізу виконується всіма вузлами обробки запитів автономно на основі інформації, яка була отримана ним на етапі обміну.

Алгоритм А1 складається з кроків.

Крок 1. k-ий вузол обробки запитів посилає іншим n-м вузлам обробки запитів (n![](media/image155.wmf)k) запит ![](media/image156.wmf) з множини ![](media/image157.wmf). Вважатимемо номер k рівним ![](media/image158.wmf).

Крок 2. n вузлів обробки запитів обмінюються запитами, отриманими від k-го вузла обробки запитів на кроці 1. При цьому вузли обробки запитів, де має місце прихована відмова, передають суперечливі запити різним вузлам обробки запитів.

Кожний n-й вузол обробки запитів (![](media/image159.wmf)) формує з отриманих запитів наступний вектор ![](media/image160.wmf)що містить ![](media/image161.wmf) елементи, для обробки запитів, отриманих від всіх вузлів обробки запитів, включаючи і себе на даному кроці ![](media/image162.wmf)

Крок 3. n вузлів обробки запитів обмінюються значаннями STR(n) (![](media/image163.wmf)), з яких всі формують початковий набір у вигляді наступної матриці ![](media/image164.wmf), в якій вектори STR(n) (![](media/image165.wmf)) розміщуються в порядку зростання номерів вузлів обробки запитів в вигляді рядків, які завжди однозначно визначаються згідно припущення 1.

Крок 4. n-й вузол обробки запитів бази даних, використовуючи функцію ![](media/image147.wmf) до стовпців матриці ![](media/image166.wmf), одержує по одному значенню цієї функції для кожного стовбчика, з яких створює вектор PRSn, елементи якого рівні  
PRSn(j) =![](media/image147.wmf){![](media/image167.wmf)\| i= 1...N}.

Крок 5. n-й вузол обробки запитів бази даних визначає елементи ![](media/image168.wmf)i, j= 1...N - 1 власної матриці ![](media/image166.wmf), що лежать на перетині стовпця j з рядком i, якщо

PRSn(j)![](media/image169.wmf)![](media/image170.wmf) . (3.1)

Визначимо число помічених елементів через ![](media/image171.wmf). Якщо ![](media/image172.wmf), то перейти до кроку 7.

Крок 6. n-й вузол обробки запитів визначає підозрілу область, яка задається у вигляді виразу

![](media/image173.wmf) (3.2)

де i, j – номери вузлів обробки запитів з елементів матриці ![](media/image174.wmf), що відносяться номеру рядка *i* і стовпця j елементу матриці ![](media/image175.wmf) що відрізняється від PRSn(j).

Далі рівність (3.2) зводиться до диз'юнктивної нормальної форми, за рахунок розкриття дужок та виконуються перетворення, іншими словами вираження з кон'юнкції перетворюється до виду диз'юнкції кон'юнкцій. Зокрема для значення обмеження в не більше ніж в ![](media/image176.wmf) несправних вузлів обробки запитів виключаються із розгляду даних з рангом більше ![](media/image176.wmf). Кожні з даних, які залишилися, знаходить допустиме поєднання несправностей, що можуть привести до всіх виявлених несправностей при умові, що їх в базі даних є не більше ніж ![](media/image176.wmf). Коли у рівності ![](media/image177.wmf) залишається більше ніж одна інформація, тоді результат моніторинг неоднозначний і ![](media/image178.wmf), в противному випадку ![](media/image179.wmf).

Крок 7. n-ті вузли обробки запитів формують матриці ![](media/image180.wmf) які отримані з ![](media/image166.wmf) в результаті викреслювання рядків та стовпців, відповідних вузлів обробки запитів, номери що є присутніми в термах, отриманих в результаті перетворень виразу ![](media/image181.wmf) на кроці 6. В результаті отриманих ![](media/image182.wmf) n-ті вузли обробки запитів визначають стан (тобто справність) k-го вузла обробки запитів за наступними правилами:

1\) у випадку коли матриця ![](media/image183.wmf) містить ідентичні елементи, то k-й вузол обробки запитів справний (![](media/image184.wmf));

2\) у випадку коли матриця ![](media/image185.wmf) містить неідентичні елементи, то k-й вузол обробки запитів несправний (![](media/image184.wmf));

3\) у випадку коли частина матриці ![](media/image185.wmf) включає в себе неоднакові елементи, а частина – однакові, то справність k-го вузла обробки запитів не визначена тому діагноз ![](media/image186.wmf).

Крок 8. Кінець алгоритму.

Коли після закінчення алгоритму ![](media/image186.wmf), вважають що моніторинг не виконане успішно, а це служить сигналом для верхній рівень ієрархії (тобто для користувача) про неспроможність Алгоритму А1. У випадку коли ![](media/image187.wmf), то моніторинг виконане успішно.

Блок-схема алгоритму А1 приведена на рисунку 3.1.

Щоб обґрунтувати коректності алгоритму будемо використовувати наступні визначення та положення.

Визначення . Якщо в матриці ![](media/image166.wmf) вузла обробки запитів n (![](media/image188.wmf)) є помічений елемент ![](media/image189.wmf) (i![](media/image190.wmf)j) (тобто на перетині рядка ![](media/image191.wmf) із стовпцем ![](media/image192.wmf) )  
(![](media/image191.wmf), ![](media/image192.wmf) ![](media/image193.wmf) {1,2,...,2t+1}), то вважатимемо, що вузли обробки запитів ![](media/image191.wmf) і ![](media/image192.wmf) взаємно «оточують по несправності» один одного, тобто елемент ![](media/image194.wmf) (![](media/image191.wmf)![](media/image195.wmf)![](media/image192.wmf)) називатимемо елементом «оточення щодо несправності» вузлів обробки запитів ![](media/image191.wmf) і ![](media/image192.wmf).

Означення 2. Сукупність усіх елементів «оточення по несправності» вузлів обробки запитів i для даної ![](media/image196.wmf) називатимемо «несправним оточенням» вузла обробки запитів i і позначимо через ENVIR (i)n.

так

так

так

ПОЧАТОК

ВОЗ k: Zk, k=2t+2

Zk = {![](media/image1970.wmf),![](media/image1980.wmf),![](media/image1990.wmf)}

R=1: СВ n: Zn, (n=1...N-1)

STR(n) = {Z1, Z2,... ZN-1}

R=2: ВОЗ n: STR(n)

Формування Аn

PRSn = majority (An)

PRSn(j) = majority (anij, i=1...N-1)

Визначення an\*ij

PRSn(j) ![](media/image2000.wmf) an\*ij ; Lmax

Lmax= 0

Визначення підозрілої області

ΣП=![](media/image2010.wmf)

Кількість інф більше одного

Формування Вn= An\\ an\*ij}

для детектування справності

k-го вузла обробки запитів

![](media/image2020.wmf)

DIAGNOZ = 0

DIAGNOZ = 1

КІНЕЦЬ

Сигнал в верхній рівень ієрархії (користувач)

Рис. 3.1. Алгоритм А1

1

2

3

4

5

6

7

Теорема 1. Серед умов ![](media/image203.wmf) вузлів обробки запитів *n* (![](media/image204.wmf)) завжди міститься правильне рішення.

Доведення. Нехай ![](media/image205.wmf)– множина несправних вузлів обробки запитів. Вони посилають неправдиві запити або на кроці 2, або на кроці 3 алгоритму та в матриці ![](media/image206.wmf) n вузлів обробки запитів з'являться елементи в стовпцях чи рядках (чи одночасно і в рядках та стовпцях), які відповідають кожному ![](media/image207.wmf). Крім того загальна кількість помічених елементів матриці рівна ![](media/image208.wmf).

Якщо згрупувати елементи ![](media/image209.wmf) виду (![](media/image210.wmf)), які відповідають поміченому елементу ![](media/image211.wmf) матриці ![](media/image164.wmf) (![](media/image212.wmf)) щодо «оточенню по несправності» всіх несправних елементів ![](media/image213.wmf), то справедлива рівність:

![](media/image214.wmf) =![](media/image215.wmf).

Другий індекс «n» показує, що розглядається матриця вузлів обробки запитів n.

Очевидно:

ENVIR ![](media/image216.wmf)= ![](media/image217.wmf),

де LOG_UMN – кон'юнкція номерів вузлів обробки запитів «навколишніх щодо несправності» вузлів обробки запитів ![](media/image218.wmf).

Таким чином

![](media/image219.wmf) = ![](media/image220.wmf)= ![](media/image221.wmf)![](media/image222.wmf).

Після розкриття дужок в ![](media/image223.wmf)![](media/image217.wmf) з'явиться член ![](media/image224.wmf)![](media/image218.wmf). Використовуючи тотожності перетворень на основі яких отримано співвідношення ![](media/image225.wmf)![](media/image226.wmf), то будь яке перетворення ![](media/image227.wmf) дає у результаті ![](media/image221.wmf)![](media/image228.wmf), а це і потрібно було довести.

З теореми 1 випливає наслідок, що якщо ![](media/image229.wmf) включає в себе єдине правомірне рішення, то дане рішення є правильним.

Слід також зауважити, що вузли обробки запитів i є несправним, якщо він на етапах 2 або 3 передає різні запити справним вузлам обробки запитів. Якщо несправність проявляється ще на кроці 2, то має справедлива наступна теорема.

Теорема 2. Якщо для усіх справних вузлів обробки запитів n гетерогенної нереляційної розподіленої бази даних, ![](media/image230.wmf) множина несправних вузлів обробки запитів, то серед ![](media/image231.wmf) буде присутнім правильне рішення ![](media/image225.wmf)![](media/image218.wmf) .

Доведення. Досить показати, що, якщо вузол обробки запитів *n* справний, то в його матриця ![](media/image232.wmf) чи в стовпці, чи в рядку з номером ![](media/image213.wmf) будуть знаходитися помічені елементи, відповідно до кроку 5 алгоритму.

За умовою несправності ![](media/image233.wmf) в базі даних існує, принаймні, два справні вузли обробки запитів з номерами p та m, такі, що ![](media/image234.wmf) їм передає різні запити впродовж кроку 2. Але в силу вузол обробки запитів оєї справності p і m передають на кроці 3 вузлу обробки запитів *n* те, що вони отримали від ![](media/image235.wmf) на кроці 2 не вносячи змін. Отже ![](media/image236.wmf)тобто після обробки власної ![](media/image237.wmf) вузол обробки запитів n буде згідно з теоремою 1, підозрювати ![](media/image238.wmf) в несправності. Крім того, серед рішень буде присутнім правильне рішення ![](media/image239.wmf)

Якщо несправність вузла обробки запитів зявилася на третьому кроці, то правильний розвязок не буде присутнім серед розв’язків алгоритму всіх вузлів обробки запитів. І це справедливо, тому що несправність вузла обробки запитів не дала знати на кроці 2, та не була поширена по всіх вузлах обробки запитів несправними вузлами обробки запитів.

Роботу алгоритм проілюструємо на двох прикладах. Розглянемо гетерогенну розподілену нереляційну базу даних, що складається з N=8 вузлів обробки запитів при числі тих, які відмовили рівним t=3 (N=2t+2). Несправними вузлами обробки запитів являються «основний» та «додатковий» з номерами 4 та 7.

Приклад 1. Досліджувана гетерогенна розподілена нереляційна база даних представлена у вигляді графа (рис. 3.2), на даному графі «нелояльні» вузли обробки запитів помічені штрихуванням. Для легшого сприйняття на графі зображені зв'язки з «нелояльними» вузлами обробки запитів, та значення, що передають нелояльні вузли обробки запитів. Лояльні вузли обробки запитів передають без змін ті значення, що вони отримали.

Розглянемо наприклад один з можливих початкових наборів, початковий набір А, по якому використовуючи функцію ![](media/image147.wmf) визначений вектор ![](media/image240.wmf) .

В початковому наборі A згідно до кроку 5, помічені елементи матриці, що відрізняються від відповідного розряду вектору ![](media/image241.wmf).

На основі кроку 6 алгоритму А1 маємо:

![](media/image242.wmf) ![](media/image243.wmf)

Отже, існує 4 рішення. Виходячи з допущень, що в базі даних існує не більше t=3 відмов, терми, що дають більшу кількість вузлів обробки запитів, які відмовили, виключимо з ![](media/image244.wmf) (крок 6 алгоритму). Єдиним правильним розвязанням для A1 буде матриця B1, яка отримана із A1 після маніпуляції щодо викреслювання рядків та стовпців з номерами 4 і 7(вузли обробки запитів з номерами 4 і 7 вважаються несправними).

5

3

2

6

1

7

G

4

Рис. 3.2. Граф системи, що досліджується

![](media/image245.wmf)

![](media/image246.wmf)

![](media/image247.wmf).

Для визначення справності «основного» (вузол обробки запитів з номером 8, що передавав початковий запит) відповідно до кроку 7 нашого алгоритму проаналізуємо матрицю B1. Та з аналізу видно, що решта вузлів обробки запитів після викреслювання несправних, тобто вузлів 1, 2, 3, 5, 6 отримали від «основного» різні запити (непомічені розряди вектору ![](media/image240.wmf)). Отже, вузол обробки запитів з номером 1, визначає, що «основний» поводився нелояльно. Тому алгоритм А1 завершується з ![](media/image248.wmf), а сам моніторинг виконане успішно та визначено вузол обробки запитів з прихованими несправностями – 4, 7, 8.

Приклад 2. Розглянемо можливість утворення неєдиного правомірного рішення. Поскільки утворення A вже не викликає складності, перейдемо відразу до аналізу матриці A (вузол обробки запитів з номером 1 вибраний довільно).

![](media/image249.wmf)

![](media/image250.wmf)

Згідно з кроку 6 алгоритму A1 маємо:

![](media/image251.wmf) = (3![](media/image252.wmf)4) ![](media/image253.wmf) (3![](media/image252.wmf)7) = 3 ![](media/image252.wmf) 4![](media/image253.wmf)7.

Отже, існує два правомірні рішення та алгоритм завершується з ![](media/image186.wmf) (зупиняючись на кроці 6). На кроці 7 вузол обробки запитів

![](media/image254.wmf).

з номером 1 визначає нелояльність «основного», оскільки не входить в обидві терми ![](media/image255.wmf) – вузли обробки запитів з номерами 1, 2, 5 та 6 отримали від «основного» суперечливі запити.

Необхідно зазначити, що правильне рішення, а саме, вузами обробки запитів, що відмовили є вузли обробки запитів з номерами 4, 7 та 8, є наведеним серед правомірних рішень.

Для подальшої роботи привузол обробки запитів оїмо запитам наступну семантику:

![](media/image256.wmf) (немає несправност, тобто моніторинг пройшло успішно);

![](media/image257.wmf) (виявлена несправність);

![](media/image258.wmf) .

При даних допущенняхалгоритм А1 призводить до наступного:

1\. Якщо в результаті самомоніторинг вузол обробки запитів n виявив вузол обробки запитів ою несправність та може проінформувати інші вузли обробки запитів шляхом передачі запиту ![](media/image259.wmf) (у випадку комунікаційної несправності також буде передано ![](media/image259.wmf), в силу семантичного визначення ![](media/image260.wmf)), тоді алгоритм А1 вирішує задачу моніторинг. Тут крок 1 еквівалентний проведенню самомоніторинг кожного вузла обробки запитів. Після кроку 3 всі ![](media/image166.wmf) міститимуть достовірну інформацію щодо моніторинг гетерогенної розподіленої нереляційної база даних: розряди PRSn, що містять ![](media/image261.wmf), відповідатимуть справним вузлам обробки запитів, а ті, які містять ![](media/image259.wmf)– несправним.

2\. Якщо у випадку виконання алгоритму А1 справний вузол обробки запитів приходить до неоднозначної відповіді щодо задачі моніторинг, то це вузол обробки запитів ідчить про більше число вузлів обробки запитів, які відмовили, або про наявність складних прихованих відмов із якими наш алгоритм А1 не в змозі впоратися.

Приведені на початку допущення 5, 6, та 7, які досі не застосовувались. В подальшому розгляді виконання усіх допущень(1 – 7) буде обов'язкове.

Введемо ще декілька означень деяких властивостей тестів.

Означення 3. Тести будуть називатися абсолютно надійними, тобто що не містять програмних помилок, або які мають таку ж поведінку, незалежно від початкових даних.

Означення 4. Строго синхронними будемо називати тести, час обробки яких в кожному вузлі обробки запитів відомий всім вузлам обробки запитів гетерогенної розподіленої нереляційної база даних.

У випадку коли алгоритм А1 призводить до неоднозначного рішення задачі моніторинг, то вузол обробки запитів n переходить до виконання іншого алгоритму, який отримав назву алгоритм А2.

## **3.3. Розробка алгоритму моніторинг гетерогенної розподіленої нереляційної база даних з прихованими несправностями**

Алгоритм складається із декількох етапів, кожен із яких включає в себе декілька фаз (рис.3.3). Припускається існування певного механізму, що призна­чає для кожного етапу вузол обробки запитів, який здійснює моніторинг, який далі називатимемо «тестером». Впродовж цього етапу тестер не міняється. Алгоритм пропонує дії тестера та дії вузлів обробки запитів, які не є тестерами для кожного етапу.

TSRi

фаза

1 2 . . . r

TSRg

фаза i≠g

1 2 . . . r

TSRk

фаза

1 2 . . . r

Етап I

(ST=1)

Етап II

(ST=2)

Етап N

(ST=N)

…

Рис 3.3. Часова діаграма моніторингу

Фази етапів включають в себе наступні кроки:

Крок 1. Після надходження сигналу із нижнього рівня гетерогенної розподіленої нереляційної бази даних про неспроможність алгоритму А1 (а саме про його неоднозначне рішення про стан вузолів обробки запитів) тестер TSRi (i-й вузол обробки запитів) посилає іншим j-м вузлам обробки запитів (j≠i) запит, які залежно від однозначності визначення стану гетерогенних розподілених нереляційних баз данихможуть бути:

1а: «Я визначив несправні вузли обробки запитів». Посилається у випадку, якщо тестер в результаті виконання алгоритму А1 чи попередніх етапів чи фаз справжнього етапу алгоритму А2 визначив однозначно несправні вузли обробки запитів. Перехід до п.6.

1б: «ВИКОНАТИ ТЕСТ ![](media/image262.wmf)». Вказується тест що слід виконати у фазі ![](media/image263.wmf). При цьому передбачається, що тести, вузлів обробки запитів, що задаються, i, вже доступні усім j-м вузлам обробки запитів. При цьому тестеру(i-й вузол обробки запитів) відомо, який час потрібний кожній з j-х вузлу обробки запитів (j≠i) для обробки наступного тесту. Позначимо цей час через ![](media/image264.wmf)(j) = DELAY ![](media/image265.wmf)(j).

Після закінчення часу t(j) = DELAY ![](media/image266.wmf)(j) i-й вузол обробки запитів направляє j-му вузлу обробки запитів запит: «ВИКОНАТИ ТЕСТ ![](media/image267.wmf)» і так далі.

Крок 2. Обмін даними між j-ми вузлом обробки запитів (j≠i) про отримане завдання від i-го вузла обробки запитів (тестера) виконати ТЕСТ ![](media/image268.wmf).

Крок 3. j-і вузлол обробки запитів обробляють ТЕСТ ![](media/image269.wmf)(j).

Крок 4. j-і вузол обробки запитів передають результати перевірки REZ ![](media/image270.wmf)(j) i-у вузлу обробки запитів (тестеру) та повідомляють про запити них один одного. При цьому, j-й вузол обробки запитів, отримавши від k-го вузла обробки запитів результат тестування, надає його номер k іншим l-м вузлам обробки запитів (l≠k, l≠j, l≠i), а отримананий запит тестеру. Кожний j-й вузол обробки запитів накопичує історію етапів (тобто для всіх етапів ![](media/image271.wmf) матриця G(r,n), в якій знаходяться номер фази r етапу ![](media/image271.wmf), номер вузла обробки запитів n та момент отримання результату тестування від цього вузла обробки запитів. Даний процес триває до настання етапу, перед початком якого проводиться обробка історії попередніх етапів. Після закінчення власного етапу знову ведеться історія етапів, що обробляється після завершення всіх етапів, тобто після завершення усього моніторинг.

Крок 5. Тестер проводить обробку отриманих повідомлень.

5а: Якщо впродовж часу

![](media/image272.wmf) (3.3)

тестер не отримає жодного повідомлення від j-го вузла обробки запитів, те рішення про стан даної «мовчазного» вузла обробки запитів відкладається до завершення всіх етапів. Якщо і у випадку закінчення останнього етапу стан j-го вузла обробки запитів ще не визначений, то він вважається таким, що відмовив.

![](media/image273.wmf)(j) – час витрачається j-м вузлом обробки запитів на обробку запиту ![](media/image262.wmf)отриманого від користувача i в r-й фазі;

![](media/image274.wmf)(i, j) – час витрачається користувачем i на отримання повідомлення MES(i, j) від j-го вузла обробки запитів.

5 б: Якщо на протязі ![](media/image275.wmf)(j) тестер отримає повідомлення у вигляді:

{REZ ![](media/image276.wmf)(j), REZ ![](media/image276.wmf)(j, l) \| l≠i, l≠j}, (3.4)

То у такому випадку перевіряється наступне:

– правильність результатів виконання тесту

{REZ ![](media/image276.wmf)(j), REZ ![](media/image276.wmf)(j, l) \| l=1...N, l≠i, l≠j} = REZ ![](media/image277.wmf); (3.5)

– час вступу відповіді ![](media/image278.wmf)(j) = t.

REZ ![](media/image279.wmf)(j) це результат обробки j-м вузлом обробки запитів тесту, заданого в фазі ![](media/image263.wmf) тестером та поточного етапу моніторинг, а вираз REZ ![](media/image280.wmf)(j, l) –запит про результати обробки l-ми вузлом обробки запитів тесту, заданого у фазі r тестером та поточного етапу моніторинг, отримані j-м вузлом обробки запитів від l-х вузлів обробки запитів у фазі r та передані тестеру.

Мають місце конкретні часові обмеження, визначені строго фіксованим часом обробки тесту та відомим часом, який витрачається на обробку кожного отриманого запиту.

У випадку коли результат обробки тесту неправильний чи час вступу не відповідає тимчасовому ліміту, то вузол обробки запитів вважається таким, який відмовив та виключається з розгляду.

Крок 6. Після закінчення заздалегідь встановленого числа фаз поточного етапу i- й вузлом обробки запитів після невеликої затримки, необхідної в разі різного часу обробки запитів на різних вузлах обробки запитів, передає повідомлення: «МІЙ ЕТАП END». Після цього призначається новий тестер етапу TSRg(g-й ВУЗОЛ ОБРОБКИ ЗАПИТІВ ) (g≠i) та відбувається повторення кроків 1-6.

Кінець алгоритму.

На рис.3.4. наведена блок-схема алгоритму.

Слід зауважити, що i-й вузол обробки запитів може закінчити вузол обробки запитів ій етап і раніше, при цьому не чекаючи завершення обробки всіх визначених на цьому етапі фаз, у випадку коли прийме однозначне рішення задачі моніторинг гетерогенних розподілених нереляційних баз даних (див. крок 1а). В такому разі на закінчення етапу ініціюється відповідь: «Я визначив несправні вузол обробки запитів».

Доведемо коректність алгоритму А2. Для цього спершу відмітимо, у випадку коли останньою фазою кожного етапу буде самомоніторинг, то усі відмови, які знову з'явилися, будуть відомі у системі. Таким чином, в кінці кожного етапу нові відмови, які з'явилися впродовж етапу, будуть виявлені всіма справними вузлами обробки запитів гетерогенної розподіленої нереляційної бази даних. Залишаються вузли обробки запитів, які спеціально поводилися так, а би заплутати справні вузки обробки запитів при спробі виявити відмови. Вказаний алгоритм є коректним в тому розуміні, що при виконанні допущень 5, 6 і 7 вузли обробки запитів з прихованими несправностями виявляються кожним справним вузлом обробки запитів.

так

так

так

ПОЧАТОК

ST=1

ТЕСТЕР TSRi

r=0

r=r+1

TSRi: “Виконати запит Тri”

trT(j)=DELAY Tri(j)

DIAGNOZ=1

ВОЗ j (j![](media/image2810.wmf)i): ЗАПИТ Tri(j)

ВОЗ j (j![](media/image2810.wmf)i): REZ Tri(j);

{REZ Tri(j), REZ Tri(j,l) \| l=1...N; l![](media/image2810.wmf)j}

Заповнення G(r,n)

Мій етап END

КІНЕЦЬ

Рис. 3.4. Алгоритм А2

1

2

3

1б

2

3

Однозначне визначення невідомих ВОЗ

ВОЗ j (j![](media/image2810.wmf)i): обробка запиту

REZ Tri(j)

4

Обробка TSRi результатів перевірки

5а: REZ Tri(j)![](media/image2810.wmf)![](media/image2820.wmf), tr(j)=trT(j)+trП(i,j)

5б: {REZ Tri(j), REZ Tri(j,l)}=REZ Trетал

tr(j)=trэтал

5

r\<rmax

ST\<STmax

ВОЗ j: обработка G(r,n)

gr,n![](media/image2810.wmf)![](media/image2820.wmf)

gr,n![](media/image2810.wmf)trетал

TSRi: “Я визначив несправний ВОЗ ”

Формування j-ми ВОЗ G(r,n)

ST=ST+1

1а

Можна виділити наступні три ситуації:

1\. Якщо j-й вузол обробки запитів несправний, то він надішле суперечливу інформацію хоч б один раз впродовж загальних етапів моніторинг. Інакше при виконанні алгоритму відбудеться збій. Якщо несправність j-й вузол обробки запитів проявився, то під час обробки наступного тесту, він запізниться на Δ= ![](media/image283.wmf)(j) - ![](media/image284.wmf) та тестер виявить це. Передача ж другого запиту в поточній фазі буде зафіксована в історії етапів тих вузлів обробки запитів, яким цей запит було спрямоване.

А починаючи з наступної фази вузол обробки запитів, який запізнився один раз, вже не в змозі «надолужити» тому він знову та знову проявлятиме себе як нелояльний.

Існує і альтернативна можливість – передача невірного результату чергового тесту. Тоді в результаті неспівпадіння вузол обробки запитів, що передав невірний результат, визначається, як такий що вийшов з ладу.

2\. Несправність j-го вузла обробки запитів може проявлятися і в приховуванні запиту, отриманого від справного вузла обробки запитів. Але в цьому випадку буде невідповідність між часом, витраченим на отримання результату тесту ![](media/image279.wmf)та обробку запитів, що передаються тестеру та лімітом часу, який на це відводиться. Згідно допущення 6, якщо j-й вузол обробки запитів посилає i-му вузлу обробки запитів повідомлення, то i-й вузол обробки запитів витратить на його отримання час DELAY_MESr(i,j), а саме несправний вузол обробки запитів знову запізниться а це дозволить усім вузлам обробки запитів виявити її несправність.

3\. Винятковий інтерес викликає випадок, коли вузол обробки запитів «мовчить», тобто передає порожній запит тобто ![](media/image285.wmf). Це тягне за собою не втрати часу, на чому оснований алгоритму А2 та що відрізняє його від алгоритму А1 та від інших підходів, наприклад \[82\]. У випадку коли упродовж усіх етапів i-й вузол обробки запитів не отримав жодного запиту від j-го вузла обробки запитів, то після закінчення кінцевого етапу i-й вузол обробки запитів оголошує j-й вузол обробки запитів несправній. При цьому, якщо j-й вузол обробки запитів дійсно несправний, то це стає відомо усім, кому даний вузол передавав вузол обробки запитів запити (згідно припущення 6 він спізнюватиметься з відповіддю, якщо укриватиме, що отримує запити від i-го або ж його несправність зявиться при спробі відправити суперечливий запит).

Якщо ж j-й вузол обробки запитів справний, але зник комунікаційний шлях між двома вузами обробки запитів, то матиме місце випадок, коли кожний із справних вузлів обробки запитів рахуватиме вузол обробки запитів свого сусіда щодо цьому комунікаційному шляху несправним. Будемо вважати, що ця ситуація допустима і, що її можемо дозволити за рахунок додаткових витрат часу чи використанням механізмів нижчих рівнів, а це дозволить виявити несправність комунікаційного шляху.

Час тривалості алгоритму А2 визначається теоремою.

У випадку несправності j-го вузла обробки запитів уперше зявляється під час обробки тесту ![](media/image279.wmf), тоді про неї буде відомо усім справним вузлам обробки запитів системи не пізніше, ніж в ![](media/image286.wmf)-ій фазі етапу i.

Розглянуті два алгоритми дозволяють створити дворівневу систему моніторинг гетерогенних розподілених нереляційних баз даних з гетерогену розподілену нереляційну базу даних можна зробити строго синхронною, принаймні на час моніторинг. Це дозволить перевести «ворожу» поведінку вузла обробки запитів системи «В тимчасову область» та використати в якості діагностичної ознаки швидкість протікання процесів у кожному з вузлів обробки запитів.

Питання щодо тестів в алгоритмі А2 теж є принциповим. У випадку коли причиною прихованої відмови якого-небудь з вузлів обробки запитів є апаратна несправність, то тести мають тестувати повністю апаратне забезпечення кожного вузлаобробки запитів .

Отже, розроблено два алгоритми, що утворюють дворівневу систему моніторинг прихованих відмов. Моніторинг розпочинається із застосування алгоритму А1, перевагами якого у порівнянні із відомими алгоритмами полягають в тому, що даний алгоритм вимагає меншої надмірності гетерогенної розподіленої нереляційної бази даних, всього два раунди обміну запитами між вузлами обробки запитів гетерогенних розподілених нереляційних баз даних і забезпечує моніторинг гетерогенних розподілених нереляційних баз даних при відмові майже половини її вузлів обробки запитів.

У разі неоднозначного рішення задачі моніторинг, алгоритм А1 формує сигнал про вузол обробки запитів та про свою неспроможність для користувача системи та моніторинг гетерогенних розподілених нереляційних баз даних триває із використанням алгоритму А2, що в якості критерію використовує тривалість виконання фаз алгоритму А2.

За результати виконання алгоритмів, що були описані вище було розроблено метод виявлення некоректної роботи вузлів гетерогенних розподілених нереляційних баз даних на основі застосування дворівневої системи контролю обробки запитів. Наукова новизна даного методу полягає у визначені прихованих несправностей вузла шляхом взаємного обміну запитами між вузлами з урахуванням припущень щодо синхронності гетерогенних розподілених нереляційних баз даних, а також можливості користувачем визначити вузол обробки. Зазначений метод дозволяє здійснювати виявлення випадків некоректної роботи вузлів обробки запитів.

## **3.4. Удосконалений метод визначення працездатності вузлів обробки запитів гетерогенних розподілених нереляційних баз даних**

Для вибору методу перевірки запитів потрібно визначити спосіб обробки інформації для розподіленої нереляційної бази даних, для цього виберемо схему, коли ми проводимо контроль за розподіленої базою, що складається з двох вузлів. Схема перевірки буде відповідати розподіленій нереляційній базі даних, в якій запит від користувача буде проходити через два вузли розподіленої нереляційної бази даних одночасно, а друга схема – коли користувач буде відправляти запит на два вузли розподіленої нереляційної бази даних окремо один від одного. При другій схемі будемо вважати, що користувачу відомо всі параметри вузлів розподіленої нереляційної бази даних за допомогою яких отримуються дані.

Розглянемо схему №1 коли запити ідуть до 2 вузлів розподіленої нереляційної бази даних, які працюють послідовно, та будемо опитувати їх послідовно (рис. 3.5).

![](media/image2870.wmf)

![](media/image2880.wmf)

![](media/image2890.wmf)

![](media/image2900.wmf)

![](media/image2910.wmf)

![](media/image2920.wmf)

![](media/image2930.wmf)

![](media/image2940.wmf)

Рис. 3.5. Схема №1 відправлення запиту до двох вузлів одночасно

В даній схемі користувач:

1\) відправляє запит ![](media/image295.wmf) через вузол ![](media/image296.wmf) на вузол ![](media/image297.wmf);

2\) якщо вузол ![](media/image298.wmf) справний, то він передає запит ![](media/image299.wmf) без спотворень;

3\) відповідь ![](media/image300.wmf) на запит ![](media/image299.wmf) передається також через вузол ![](media/image301.wmf), який в разі справності передає її без спотворень;

4\) користувач приймає відповідь ![](media/image300.wmf) та видає результат ![](media/image302.wmf) за формулою:

![](media/image303.wmf) (3.6)

де ![](media/image304.wmf) – еталонна відповідь для перевірки запиту до вузла розподіленої нереляційної бази даних. Якщо результат ![](media/image305.wmf), то користувач вважає вузол ![](media/image306.wmf) справним, і навпаки, якщо результат ![](media/image307.wmf), то користувач вважає вузол ![](media/image297.wmf) не справним.

Розглянемо схему №2 в якій запит до 2 вузлів розподіленої нереляційної бази даних буде направлятися паралельно, а яким чином вони зв’язані між собою, користувач знає, які запити та відповіді відправляються на вузол (рис. 3.6).

![](media/image3080.wmf)

![](media/image3090.wmf)

![](media/image2890.wmf)

![](media/image3100.wmf)

![](media/image3110.wmf)

![](media/image3120.wmf)

![](media/image3130.wmf)

![](media/image3140.wmf)

![](media/image3150.wmf)

Рис. 3.6. Схема №2 відправлення запиту до двох вузлів розподіленої нереляційної бази даних паралельно

В даній схемі користувач:

1\) відправляє запит ![](media/image316.wmf) на вузол ![](media/image301.wmf);

2\) якщо вузол ![](media/image301.wmf) справний, то він передає відповідь ![](media/image317.wmf) користувачу;

3\) користувач приймає відповідь ![](media/image318.wmf) та видає результат ![](media/image319.wmf) за формулою:

![](media/image320.wmf) (3.7)

де ![](media/image304.wmf) – еталонна відповідь для перевірки запиту до вузла розподіленої нереляційної бази даних. Якщо результат ![](media/image321.wmf), то користувач вважає вузол ![](media/image298.wmf) справним, і навпаки, якщо результат ![](media/image322.wmf), то користувач вважає вузол ![](media/image323.wmf) не справним.

Аналогічним чином користувач проводить перевірку другого вузла розподіленої нереляційної бази даних схеми №2.

Для порівняння схеми №1 та схеми №2 будемо вираховувати ![](media/image324.wmf) справного стану вузла 2, де ![](media/image324.wmf) – апостеріорна імовірність справного стану вузла 2 за умови, що результат запиту ![](media/image325.wmf).

Характеристика ![](media/image324.wmf) буде враховувати припущення:

1\) справність вузлів розподіленої нереляційної бази даних 1,2;

2\) надійність користувача;

3\) імовірність правильного оцінювання відповіді на запит користувачем (якщо користувач не вірно оцінив, то він видає результат перевірки 0 або 1. Вважаємо, що з імовірністю ![](media/image326.wmf) видає 0 і з імовірністю ![](media/image327.wmf)видає 1);

4\) систему оцінювання:

![](media/image328.wmf)

Всі інші припущення будуть описані пізніше.

Тоді за схемою № 2 користувач ![](media/image329.wmf) мають наступні показники найдійності:

1\) апріорна до випробування імовірність справно написаного користувачем запиту ![](media/image330.wmf), тоді ймовірність несправно написаного запиту вираховується як ![](media/image331.wmf);

2\) апріорна імовірність ![](media/image332.wmf) справного вузла розподіленої нереляційної бази даних 2, тоді ймовірність неправильної відповіді вузла вираховується як ![](media/image333.wmf).

Можливі 4 гіпотези ![](media/image334.wmf) справно і несправно написаного запиту користувача та справного і несправного станів вузлу нереляційної розподіленої бази даних 2:

1 – користувач написав правильний запит та відповідь з вузлу нереляційної розподіленої бази даних 2 співпала з еталонною відповіддю;

2 – користувач написав правильний запит, але відповідь не співпала з еталонною;

3 – користувач написав неправильний запит, але відповідь співпала з еталонною;

4 – користувач написав неправильний запит та відповідь не співпала з еталонною.

Для обчислення апостеріорної імовірності використаємо основну теорему Байєса.

Тоді для всіх гіпотез опишемо твердження:

1 – ![](media/image335.wmf), ![](media/image336.wmf).

2 – ![](media/image337.wmf), ![](media/image338.wmf).

3 – ![](media/image339.wmf), ![](media/image340.wmf).

4 – ![](media/image341.wmf), ![](media/image342.wmf).

В зв’язку з тим, що гіпотези утворюють повну групу подій, то сума їх імовірностей:

![](media/image343.wmf) (3.8)

В якості події ![](media/image344.wmf) приймається подія отримання результату ![](media/image345.wmf), тому очевидно, що коли користувач написав правильний запит та вузол 2 справний, то результат ![](media/image325.wmf) буде отримано з імовірністю ![](media/image336.wmf). Якщо користувач написав правильний запит, а вузол 2 несправний, то результат ![](media/image346.wmf) буде отримано з ймовірністю ![](media/image347.wmf). В інших двох варіантах користувач пише неправильний запит, тому він «угадує» результат з імовірністю ![](media/image326.wmf), тому відповідно ![](media/image348.wmf).

Повна ймовірність ![](media/image349.wmf) буде вираховуватися за формулою:

![](media/image350.wmf) (3.9)

Тоді за теоремою Байєса апостеріорні імовірності гіпотез вираховуються:

![](media/image351.wmf) (3.10)

Звідси апостеріорна імовірність достовірності отримання правильної відповіді на запит від вузла нереляційної розподіленої бази даних 2 схеми 2 буде розраховуватися за формулою:

![](media/image352.wmf) (3.11)

Знайдемо формулу для знаходження апостеріорної імовірності для схеми № 1. Коли в схемі №1 є тільки один вузол нереляційної розподіленої бази даних, то вона перевіряється по схемі №2.

Тоді за схемою № 1 користувач ![](media/image353.wmf) має такі показники найдійності:

1\) апріорна імовірність до випробування справно написаного запиту користувачем ![](media/image354.wmf), тоді ймовірність неправильно написаного запиту вираховується як ![](media/image355.wmf);

2\) апріорна імовірність ![](media/image356.wmf) справного вузла нереляційної розподіленої бази даних 1, тоді ймовірність відмови вираховується як ![](media/image357.wmf);

3\) апріорна імовірність ![](media/image332.wmf) справного вузла нереляційної розподіленої бази даних 2, тоді ймовірність відмови вираховується як ![](media/image333.wmf).

Можливі 8 гіпотез ![](media/image334.wmf) справно і несправно написаного запиту користувачем та справного і несправного станів вузла нереляційної розподіленої бази даних 2:

1 – користувач написав правильний запит, вузол нереляційної розподіленої бази даних 1 працює справно та передав запит на вузол нереляційної розподіленої бази даних 2. Вузол нереляційної розподіленої бази даних 2 працює та він відповів вузлу нереляційної розподіленої бази даних 1, а той в вузол обробки запитів ою чергу передав відповідь користувачу;

2 – користувач написав правильний запит, вузол нереляційної розподіленої бази даних 1 працює справно та передав запит на вузол нереляційної розподіленої бази даних 2. Вузол нереляційної розподіленої бази даних 2 працює несправно та він відповів вузлу нереляційної розподіленої бази даних 1, а той в вузол обробки запитів ою чергу передав несправну відповідь користувачу;

3 – користувач написав правильний запит, вузол нереляційної розподіленої бази даних 1 працює несправно та передав запит на вузол нереляційної розподіленої бази даних 2. Вузол нереляційної розподіленої бази даних 2 працює справно та він відповів вузолу нереляційної розподіленої бази даних 1, а той в вузол обробки запитів ою чергу передав відповідь користувачу;

4 – користувач написав правильний запит, вузол нереляційної розподіленої бази даних 1 працює несправно та передав запит на вузол нереляційної розподіленої бази даних 2. Вузол нереляційної розподіленої бази даних 2 працює несправно та він відповів вузолу нереляційної розподіленої бази даних 1, а той в вузол обробки запитів ою чергу передав відповідь користувачу;

5 – користувач написав неправильний запит, вузол нереляційної розподіленої бази даних 1 працює справно та передав запит на вузол нереляційної розподіленої бази даних 2. Вузол нереляційної розподіленої бази даних 2 працює справно та він відповів вузолу нереляційної розподіленої бази даних 1, а той в вузол обробки запитів ою чергу передав відповідь користувачу;

6 – користувач написав неправильний запит, вузол нереляційної розподіленої бази даних 1 працює справно та передав запит на вузол нереляційної розподіленої бази даних 2. Вузол нереляційної розподіленої бази даних 2 працює несправно та він відповів вузолу нереляційної розподіленої бази даних 1, а той в вузол обробки запитів ою чергу передав відповідь користувачу;

7 – користувач написав неправильний запит, вузол нереляційної розподіленої бази даних 1 працює несправно та передав запит на вузол нереляційної розподіленої бази даних 2. Вузол нереляційної розподіленої бази даних 2 працює справно та він відповів вузлу нереляційної розподіленої бази даних 1, а той в вузол обробки запитів ою чергу передав відповідь користувачу;

8 – користувач написав неправильний запит, вузол нереляційної розподіленої бази даних 1 працює несправно та передав запит на вузол нереляційної розподіленої бази даних 2. Вузол нереляційної розподіленої бази даних 2 працює несправно та він відповів вузлу нереляційної розподіленої бази даних 1, а той в вузол обробки запитів ою чергу передав відповідь користувачу.

Тоді для кожної з гіпотез опишемо наступні твердження (гіпотези):

1 – ![](media/image358.wmf), ![](media/image336.wmf).

2 – ![](media/image359.wmf), ![](media/image338.wmf).

3 – ![](media/image360.wmf), ![](media/image340.wmf).

4 – ![](media/image361.wmf), ![](media/image342.wmf).

5 – ![](media/image362.wmf), ![](media/image363.wmf).

6 – ![](media/image364.wmf), ![](media/image365.wmf).

7 – ![](media/image366.wmf), ![](media/image367.wmf).

8 – ![](media/image368.wmf), ![](media/image369.wmf).

В якості події ![](media/image344.wmf) приймається подія отримання результату ![](media/image346.wmf), тому очевидно, що коли користувач написав справний запит, вузол нереляційної розподіленої бази даних 1 та вузол нереляційної розподіленої бази даних 2 справні, то результат ![](media/image346.wmf) буде отримано з імовірністю ![](media/image336.wmf). Якщо користувач написав справний запит, а вузол нереляційної розподіленої бази даних 2 – несправний, то результат ![](media/image370.wmf) буде отримано з імовірністю ![](media/image347.wmf). В інших шести варіантах користувач написав несправний запит або несправний вузол нереляційної розподіленої бази даних 1, тому він «угадує» результат з імовірністю ![](media/image326.wmf), тому відповідно:

![](media/image371.wmf). (3.12)

Повна ймовірність ![](media/image349.wmf) буде вираховуватися за формулою:

![](media/image372.wmf) (3.13)

Тоді за основною теоремою Байєса апостеріорні імовірності вказаних гіпотез визначаються за формулою:

![](media/image373.wmf)(3.14)

Звідси апостеріорна імовірність достовірності обробки запитів вузлом 2 нереляційної розподіленої бази даних за схемою 1 буде розраховуватися за формулою:

![](media/image374.wmf) (3.15)

Отже, за показником ефективності обробки запитів, в якості якого прийнята апостеріорна імовірність справного стану вузлу 2 нереляційної розподіленої бази даних, запропоновано наступні дві схеми для розрахунків імовірності.

Визначимо формулу для знаходження апостеріорної імовірності для варіанту з ![](media/image375.wmf) вузлів нереляційної розподіленої бази даних, які розміщені послідовно та запит відправляється до останнього вузла (рис. 3.7.).

…

…

![](media/image3760.wmf)

![](media/image3770.wmf)

![](media/image3780.wmf)

![](media/image3790.wmf)

![](media/image3800.wmf)

![](media/image3810.wmf)

![](media/image3820.wmf)

![](media/image3130.wmf)

Рис. 3.7. Схема обробки запитів з ![](media/image375.wmf) вузлів  
нереляційної розподіленої бази даних

Тоді за розширеною схемою користувач ![](media/image353.wmf) має показники надійності зазначені нижче:

1\) апріорна імовірність до випробування справно написаного запиту користувачем ![](media/image383.wmf), тоді ймовірність відмови вираховується як ![](media/image355.wmf);

2\) апріорна імовірність ![](media/image356.wmf) справного вузла нереляційної розподіленої бази даних 1, тоді ймовірність відмови вираховується як ![](media/image357.wmf);

…

n\) апріорна імовірність ![](media/image384.wmf) справного вузла нереляційної розподіленої бази даних ![](media/image385.wmf), тоді ймовірність відмови вираховується як ![](media/image386.wmf).

Можливі ![](media/image387.wmf) гіпотез ![](media/image334.wmf) справно і несправно написаного запиту користувачем та справного і несправного станів вузла нереляційної розподіленої бази даних ![](media/image385.wmf):

1 – користувач написав правильний запит, вузол нереляційної розподіленої бази даних 1 працює справно та передав запит на вузол нереляційної розподіленої бази даних 2. … Вузол нереляційної розподіленої бази даних ![](media/image385.wmf) працює та він відповів вузлу нереляційної розподіленої бази даних ![](media/image388.wmf), а той в вузол обробки запитів ою чергу передав відповідь через інші вузли користувачу;

2 – користувач написав правильний запит, вузол нереляційної розподіленої бази даних 1 працює справно та передав запит на вузол нереляційної розподіленої бази даних 2. … Вузол нереляційної розподіленої бази даних ![](media/image385.wmf) працює несправно та він відповів вузлу нереляційної розподіленої бази даних ![](media/image388.wmf), а той в вузол обробки запитів ою чергу передав відповідь через інші вузли користувачу;

…

![](media/image387.wmf) – користувач написав неправильний запит, вузол нереляційної розподіленої бази даних 1 працює несправно та передав запит на вузол нереляційної розподіленої бази даних 2. … Вузол нереляційної розподіленої бази даних ![](media/image385.wmf) працює несправно та він відповів вузлу нереляційної розподіленої бази даних ![](media/image388.wmf), а той в вузол обробки запитів ою чергу передав відповідь через інші вузли користувачу.

Тоді для кожної з гіпотез опишемо наступні твердження:

1 – ![](media/image389.wmf), ![](media/image336.wmf).

2 – ![](media/image390.wmf), ![](media/image338.wmf).

…

![](media/image387.wmf) – ![](media/image391.wmf), ![](media/image392.wmf).

В ролі події ![](media/image344.wmf) визначається подія отримання результату ![](media/image393.wmf), тому очевидно, що коли користувач написав справний запит та вузли справні, то результат ![](media/image393.wmf) буде отримано з імовірністю ![](media/image336.wmf). Якщо користувач написав справний запит, а вузол нереляційної розподіленої бази даних ![](media/image385.wmf) несправний, то результат ![](media/image394.wmf) буде отримано з ймовірністю ![](media/image347.wmf). В інших ![](media/image395.wmf) варіантах користувач написав несправний запит або несправний вузол нереляційної розподіленої бази даних ![](media/image385.wmf), тому він «угадує» результат з імовірністю ![](media/image326.wmf), тому відповідно:

![](media/image396.wmf). (3.16)

Повна ймовірність ![](media/image349.wmf) знаходиться за формулою:

![](media/image397.wmf). (3.17)

Тоді за основною теоремою Байєса апостеріорні імовірності гіпотез обчислюється за формулою:

![](media/image398.wmf) (3.18)

Звідси апостеріорна імовірність достовірності обробки запитів вузлом ![](media/image385.wmf) нереляційної розподіленої бази даних за схемою з ![](media/image385.wmf) вузлами буде розраховуватися за формулою:

![](media/image399.wmf)(3.19)

Отже, за показником ефективності обробки запитів, в якості якого прийнята апостеріорна імовірність справного стану вузлу ![](media/image385.wmf) нереляційної розподіленої бази даних, було запропоновано формули для розрахунку апостеріорної імовірності та розроблено удосконалений метод визначення працездатності вузлів обробки запитів гетерогенних розподілених нереляційних баз даних, який відрізняється від існуючих способом обробки запитів на основі визначення апостеріорних ймовірностей справного стану вузлів. Зазначений метод дозволяє підвищити ефективність обробки даних.

## **3.5. Порівняльні аналітичні оцінки методу визначення працездатності вузлів обробки запитів гетерогенних розподілених нереляційних баз даних**

Проведемо аналітичну оцінку запропонованих розрахунків в пункті 3.2 для системи з одним вузлом. Для знаходження апостеріорної імовірності дано:

1\) користувач відправляє запит ![](media/image316.wmf) на вузол нереляційної розподіленої бази даних ![](media/image298.wmf) та отримує відповідь ![](media/image400.wmf) від вузлу нереляційної розподіленої бази даних;

2\) користувач приймає відповідь ![](media/image401.wmf) та видає результат ![](media/image402.wmf) за формулою:

![](media/image403.wmf)

де ![](media/image304.wmf) – еталонна відповідь для перевірки запиту до вузлу нереляційної розподіленої бази даних. Якщо результат ![](media/image404.wmf), то користувач вважає вузол нереляційної розподіленої бази даних ![](media/image405.wmf) справним, і навпаки, якщо результат ![](media/image406.wmf), то користувач вважає вузол нереляційної розподіленої бази даних ![](media/image407.wmf) несправним;

3\) апріорна (до випробування) імовірність справно написаного запиту користувачем![](media/image408.wmf), імовірність відмови ![](media/image409.wmf);

4\) апріорна імовірність справного стану вузлу нереляційної розподіленої бази даних ![](media/image410.wmf): ![](media/image411.wmf) та відповідно ![](media/image412.wmf).

Можливі 4 гіпотези справно і несправно написаного запиту користувачем та справного та несправного вузлу нереляційної розподіленої бази даних ![](media/image410.wmf) представлено в вигляді:

1 – ![](media/image413.wmf);

2 – ![](media/image414.wmf);

3 – ![](media/image415.wmf);

4 – ![](media/image416.wmf).

Імовірність ![](media/image417.wmf) обчислюється для різних гіпотез по різному:

1 – ![](media/image418.wmf), тому що і користувач написав правильний запит і вузол нереляційної розподіленої бази даних дав правильну відповідь;

2 – ![](media/image419.wmf), тому що користувач написав правильний запит, але вузол нереляційної розподіленої бази даних дав неправильну відповідь;

3 – ![](media/image420.wmf), тому що користувач написав неправильний запит, але вузол нереляційної розподіленої бази даних працює справно;

4 – ![](media/image421.wmf), тому що користувач написав неправильний запит, але вузол нереляційної розподіленої бази даних дав неправильну відповідь.

Звідси повна імовірність розраховується як:

![](media/image422.wmf)

За теоремою Байєса апостеріорні імовірності гіпотез:

![](media/image423.wmf)

Апостеріорна імовірність справного стану вузла нереляційної розподіленої бази даних:

![](media/image424.wmf)

Таким чином, обчислено ![](media/image425.wmf) для схеми з одним вузлом нереляційної розподіленої бази даних.

Проведемо аналітичну оцінку запропонованих розрахунків в пункті 3.2 для системи обробки заитів з двома вузлами нереляційної розподіленої бази даних. Для знаходження апостеріорної імовірності дано:

1\) користувач відправляє запит ![](media/image426.wmf) на вузол нереляційної розподіленої бази даних ![](media/image407.wmf), який пересилає його на вузол нереляційної розподіленої бази даних ![](media/image427.wmf);

2\) вузол нереляційної розподіленої бази даних ![](media/image428.wmf) обробляє запит та відправляє відповідь ![](media/image429.wmf) через вузол нереляційної розподіленої бази даних ![](media/image405.wmf) користувачу;

3\) користувач приймає відповідь ![](media/image430.wmf) та видає результат ![](media/image431.wmf) за формулою:

![](media/image432.wmf)

де ![](media/image304.wmf) – еталонна відповідь для перевірки запиту до вузлу нереляційної розподіленої бази даних. Якщо результат ![](media/image404.wmf), то користувач вважає вузол нереляційної розподіленої бази даних ![](media/image297.wmf) справним, і навпаки, якщо результат ![](media/image406.wmf), то користувач вважає вузол нереляційної розподіленої бази даних ![](media/image433.wmf) несправним;

3\) апріорна (до випробування) імовірність справно написаного запиту користувачем![](media/image434.wmf), імовірність відмови ![](media/image435.wmf);

4\) апріорна імовірність справного стану вузлів ![](media/image296.wmf) та ![](media/image436.wmf): ![](media/image411.wmf) та відповідно ![](media/image412.wmf), ![](media/image437.wmf) та відповідно ![](media/image438.wmf).

Можливі 8 гіпотез справно і несправно написаного запиту користувачем та вузлів нереляційної розподіленої бази даних ![](media/image298.wmf) та ![](media/image439.wmf) представлено у вигляді:

1 – ![](media/image440.wmf);

2 – ![](media/image441.wmf);

3 – ![](media/image442.wmf);

4 – ![](media/image443.wmf);

5 – ![](media/image444.wmf);

6 – ![](media/image445.wmf);

7 – ![](media/image446.wmf);

8 – ![](media/image447.wmf).

Імовірність ![](media/image417.wmf) обчислюється для різних гіпотез по різному:

1 – ![](media/image418.wmf), тому що і користувач написав правильний запит і вузли нереляційної розподіленої бази даних працюють правильно;

2 – ![](media/image419.wmf), тому що користувач написав правильний запит, перший вузол нереляційної розподіленої бази даних працює правильно, але другий вузол нереляційної розподіленої бази даних дав неправильну відповідь;

3 – ![](media/image420.wmf), тому що користувач написав правильний запит, перший вузол нереляційної розподіленої бази даних працює неправильно, а другий вузол нереляційної розподіленої бази даних дав правильну відповідь;

4 – ![](media/image448.wmf), тому що користувач написав правильний запит, перший вузол нереляційної розподіленої бази даних працює неправильно та другий вузол нереляційної розподіленої бази даних дав неправильну відповідь;

5 – ![](media/image449.wmf), тому що користувач написав неправильний запит, перший вузол нереляційної розподіленої бази даних працює правильно та другий вузол нереляційної розподіленої бази даних дав правильну відповідь;

6 – ![](media/image450.wmf), тому що користувач написав неправильний запит, перший вузол нереляційної розподіленої бази даних працює правильно, але другий вузол нереляційної розподіленої бази даних дав неправильну  
відповідь;

7 – ![](media/image451.wmf), тому що користувач написав неправильний запит, перший вузол нереляційної розподіленої бази даних працює неправильно, але другий вузол нереляційної розподіленої бази даних дав правильну  
відповідь;

8 – ![](media/image452.wmf), тому що користувач написав неправильний запит, перший вузол нереляційної розподіленої бази даних працює неправильно та другий вузол нереляційної розподіленої бази даних дав неправильну  
відповідь.

Звідси повна імовірність розраховується як:

![](media/image453.wmf)

За теоремою Байєса апостеріорні імовірності гіпотез:

![](media/image454.wmf)

Апостеріорна імовірність справного стану вузлу нереляційної розподіленої бази даних:

![](media/image455.wmf)

Таким чином, обчислено ![](media/image456.wmf) для схеми з двома вузлами.

Також проведемо аналітичну оцінку запропонованих розрахунків в пункті 3.2 для системи обробки запитів з трьома вузлами.

Візьмемо, що:

1\) апріорна (до випробування) імовірність справно написаного запиту користувачем![](media/image457.wmf), імовірність відмови ![](media/image458.wmf);

2\) апріорна імовірність справного стану вузлів ![](media/image296.wmf), ![](media/image436.wmf) та ![](media/image459.wmf): ![](media/image411.wmf) та відповідно ![](media/image412.wmf), ![](media/image437.wmf) та відповідно ![](media/image438.wmf), ![](media/image460.wmf) та відповідно ![](media/image461.wmf).

Дані для розрахунку знаходяться в таблиці 3.1.

Таблиця 3.1

Значення розрахунку апостеріорної імовірності для трьох послідовних вузлів нереляційної розподіленої бази даних

|  №  | ![](media/image462.wmf) | ![](media/image463.wmf) | ![](media/image464.wmf) |
|:---:|:-----------------------:|:-----------------------:|:-----------------------:|
|  1  |       0,81450637        |            1            |       0,919495376       |
|  2  |       0,04286887        |            0            |            0            |
|  3  |       0,04286868        |           0,5           |       0,024197253       |
|  4  |       0,00225636        |           0,5           |       0,001273541       |
|  5  |       0,04286883        |           0,5           |       0,024197255       |
|  6  |       0,00225644        |           0,5           |       0,001273567       |
|  7  |       0,00225653        |           0,5           |       0,001273558       |
|  8  |       0,00011866        |           0,5           |       6,70305E-05       |
|  9  |       0,04286828        |           0,5           |       0,024197257       |
| 10  |       0,00225646        |           0,5           |       0,001273541       |
| 11  |       0,00225637        |           0,5           |       0,001273548       |
| 12  |       0,00011845        |           0,5           |       6,70361E-05       |
| 13  |       0,00225616        |           0,5           |       0,001273545       |
| 14  |       0,00011893        |           0,5           |       6,70275E-05       |
| 15  |       0,00011857        |           0,5           |       6,70258E-05       |
| 16  |        6,28E-06         |           0,5           |       3,52763E-06       |

Звідси повна імовірність обчислюється як:

![](media/image465.wmf).

Апостеріорна імовірність справного стану вузлу нереляційної розподіленої бази даних:

![](media/image466.wmf).

Отже, обчислено ![](media/image467.wmf) для схеми з трьома вузлами.

Проведемо аналітичну оцінку отриманих розрахунків в пункті 3.4 для системи обробки запитів з чотирма вузлами нереляційної розподіленої бази даних.

Візьмемо, що:

1\) апріорна (до випробування) імовірність справно написаного запиту користувачем![](media/image434.wmf), імовірність відмови ![](media/image468.wmf);

2\) апріорна імовірність справного стану вузлів нереляційної розподіленої бази даних ![](media/image410.wmf), ![](media/image433.wmf), ![](media/image469.wmf) та ![](media/image470.wmf): ![](media/image411.wmf) та відповідно ![](media/image412.wmf), ![](media/image437.wmf) та відповідно ![](media/image438.wmf), ![](media/image460.wmf) та відповідно ![](media/image461.wmf), ![](media/image471.wmf) та відповідно ![](media/image472.wmf).

Дані для розрахунку знаходяться в таблиці 3.2.

Таблиця 3.2

Значення для розрахунку апостеріорної імовірності для трьох послідовних вузлів нереляційної розподіленої бази даних

|  №  | ![](media/image462.wmf) | ![](media/image463.wmf) | ![](media/image464.wmf) |
|:---:|:-----------------------:|:-----------------------:|:-----------------------:|
|  1  |       0,77378088        |            1            |       0,89296745        |
|  2  |       0,04072542        |            0            |            0            |
|  3  |       0,04072554        |           0,5           |       0,02349924        |
|  4  |       0,00214364        |           0,5           |        0,0012382        |
|  5  |       0,04072556        |           0,5           |       0,02349941        |
|  6  |       0,00214367        |           0,5           |        0,0012368        |
|  7  |       0,04072543        |           0,5           |       0,02349937        |
|  8  |       0,00214367        |           0,5           |        0,0012381        |
|  9  |       0,00214356        |           0,5           |        0,0012363        |
| 10  |       0,00011292        |           0,5           |       6,5089E-05        |
| 11  |       0,00214365        |           0,5           |        0,0012354        |
| 12  |       0,00011292        |           0,5           |       6,5088E-05        |
| 13  |       0,00214378        |           0,5           |        0,0012371        |
| 14  |       0,00011294        |           0,5           |       6,5113E-05        |
| 15  |       0,00011275        |           0,5           |       6,5113E-05        |
| 16  |       5,9264E-06        |           0,5           |        3,434E-06        |
| 17  |       0,04072547        |           0,5           |       0,02349934        |
| 18  |       0,00214356        |           0,5           |        0,0012378        |
| 19  |       0,00214367        |           0,5           |        0,0012365        |
| 20  |       0,00011274        |           0,5           |       6,5113E-05        |
| 21  |       0,00214378        |           0,5           |        0,0012371        |
| 22  |       0,00011256        |           0,5           |       6,5112E-05        |
| 23  |       0,00011276        |           0,5           |       6,5112E-05        |
| 24  |       0,00011245        |           0,5           |       6,5112E-05        |
| 25  |       0,00011262        |           0,5           |       6,5112E-05        |
| 26  |       5,9366E-06        |           0,5           |        3,431E-06        |
| 27  |       0,00011273        |           0,5           |       6,5112E-05        |
| 28  |       5,9362E-06        |           0,5           |        3,431E-06        |
| 29  |       0,00214353        |           0,5           |        0,0012371        |
| 30  |       5,9375E-06        |           0,5           |        3,431E-06        |
| 31  |       5,9364E-06        |           0,5           |        3,426E-06        |
| 32  |        3,137E-07        |           0,5           |       1,8032E-07        |

Звідси повна імовірність розраховується як:

![](media/image473.wmf).

Апостеріорна імовірність справного стану вузлу нереляційної розподіленої бази даних:

![](media/image474.wmf).

Отже, обчислено ![](media/image475.wmf) для схеми з чотирма вузлами.

Порівнюючи схеми з різною кількістю вузлів нереляційної розподіленої бази даних за показником ефективності обробки запитів, в розрахунку якого прийнята апостеріорна імовірність коректного стану за умови отримання правильного результату обробки запитів, схема 1 з роздільною обробкою запиту з одного вузла нереляційної розподіленої бази даних дає найбільшу апостеріорну імовірність, а з схеми 2, де реалізовано ланцюгова обробка запитів (послідовна), апостеріорна ймовірність зменшується зі збільшенням кількості вузлів нереляційної розподіленої бази даних. Для роздільної обробки запитів ![](media/image476.wmf), а для ланцюгової обробки запитів ![](media/image477.wmf), ![](media/image478.wmf), ![](media/image479.wmf).

Для визначення проведемо розрахунки для різних базових величин апріорної імовірності. Візьмемо апріорні імовірності визначені рівними:

1\. Апріорна імовірність справно написаного запиту користувачем![](media/image480.wmf), імовірність відмови ![](media/image481.wmf), апріорна імовірність справного стану вузлів: ![](media/image482.wmf) та відповідно ![](media/image483.wmf).

2\. Апріорна (до випробування) імовірність справно написаного запиту користувачем![](media/image484.wmf), імовірність відмови ![](media/image485.wmf), апріорна імовірність справного стану вузлів: ![](media/image486.wmf) та відповідно ![](media/image487.wmf).

3\. Апріорна (до випробування) імовірність справно написаного запиту користувачем![](media/image488.wmf), імовірність відмови ![](media/image489.wmf), апріорна імовірність справного стану вузлів: ![](media/image490.wmf) та відповідно ![](media/image491.wmf).

Після цього здійснемо розрахуноки апостеріорних імовірностей всіх випадків, які визначені апріорною імовірністю. Запишемо результат в таблицю та побудуємо графік (рис. 3.8).

Таблиця 3.3

Визначення апостеріорних імовірностей при відомих значеннях апріорних

| Кількість вузлів | Апріорна імовірність ![](media/image492.wmf) | Апріорна імовірність ![](media/image493.wmf) | Апріорна імовірність ![](media/image494.wmf) | Апріорна імовірність ![](media/image495.wmf) |
|:---|:--:|:--:|:--:|:--:|
| 1 | 0.9978 | 0.9203 | 0.8469 | 0.7758 |
| 2 | 0.9969 | 0.8974 | 0.8068 | 0.7227 |
| 3 | 0.9951 | 0.8771 | 0.7737 | 0.6815 |
| 4 | 0.9939 | 0.8602 | 0.7455 | 0.6511 |

Рис. 3.8. Визначення апостеріорних імовірностей справного стану вузла нереляційної розподіленої бази даних

Аналітичні оцінки використання апостеріорних імовірностей для чотирьох різних гіпотез показали, що зі зниженням апріорної імовірності графік залежностей прямує вниз.

## **Висновки до розділу 3**

## 

Для проведення моніторингу гетерогенних розподілених нереляційних баз даних з визначення прихованих несправностей вузлів обробки запитів слід використати декілька рівнів. Прихована несправність – це несправність, що не виявляється візуально або штатними методами та засобами контролю і моніторингу, проте виявляється спеціальними методами моніторингу. На першому рівні використовуються прості моніторингові процедури. Коли за їх допомогою вдається визначити вузли обробки запитів, які є несправними, то на цьому моніторинг із найменшими витратами часу завершується. Але якщо є неоднозначності щодо визначення елементів розподіленої бази даних, які відмовили, користувач бази даних має запустити моніторингові процедури, які здатні впоратися з складнішими несправностями вузла обробки запитів. В даному випадку висловлене припущення про те, що простіші несправності вузла обробки запитів виникатимуть частіше, ніж складніші. А отже не потрібно відразу використовувати дуже сильні, моніторингові процедури, що вимагають великих часових витрат.

Отже, розроблено два алгоритми, що утворюють дворівневу систему моніторинг прихованих відмов. Моніторинг розпочинається із застосування алгоритму А1, перевагами якого у порівнянні із відомими алгоритмами полягають в тому, що даний алгоритм вимагає меншої надмірності гетерогенної розподіленої нереляційної бази даних, всього два раунди обміну запитами між вузлами обробки запитів гетерогенних розподілених нереляційних баз даних і забезпечує моніторинг гетерогенних розподілених нереляційних баз даних при відмові майже половини її вузлів обробки запитів.

У разі неоднозначного рішення задачі моніторинг, алгоритм А1 формує сигнал про вузол обробки запитів та про свою неспроможність для користувача системи та моніторинг гетерогенних розподілених нереляційних баз даних триває із використанням алгоритму А2.

За результати виконання алгоритмів, що були описані вище було розроблено метод виявлення некоректної роботи вузлів гетерогенних розподілених нереляційних баз даних на основі застосування дворівневої системи контролю обробки запитів. Наукова новизна даного методу полягає у визначені прихованих несправностей вузла шляхом взаємного обміну запитами між вузлами з урахуванням припущень щодо синхронності гетерогенних розподілених нереляційних баз даних, а також можливості користувачем визначити вузол обробки. Зазначений метод дозволяє здійснювати виявлення випадків некоректної роботи вузлів обробки запитів.

Удосконалено метод визначення працездатності вузлів обробки запитів гетерогенних розподілених нереляційних баз даних, який відрізняється від існуючих способом обробки запитів на основі визначення апостеріорних ймовірностей справного стану вузлів. Зазначений метод дозволяє підвищити ефективність обробки даних.

Виконано порівняння схем з різною кількістю вузлів за показником ефективності обробки запитів, де прийнята апостеріорна імовірність коректного стану при умові отримання задовільного результату обробки запитів. Показано, що системи з роздільною обробкою запитів одного вузла апостеріорна імовірність дає найбільший показник, а починаючи з системи обробки запитів двох та більше вузлів, в якій реалізовано ланцюгову обробку запитів, апостеріорна ймовірність зменшується з збільшенням кількості вузлів. Для роздільної обробки запитів ![](media/image476.wmf), а для ланцюгової обробки запитів ![](media/image477.wmf), ![](media/image478.wmf), ![](media/image479.wmf).

<span id="_Toc161146430" class="anchor"></span>РОЗДІЛ 4 РОЗРОБКА ПРОГРАМНОГО ЗАБЕЗПЕЧЕННЯ КОМПЛЕКСНОЇ СИСТЕМИ УПРАВЛІННЯ ТА ПЕРЕВІРКИ ГЕТЕРОГЕННОГО СЕРЕДОВИЩА ОБРОБКИ ТА ЗБЕРІГАННЯ ДАНИХ В НЕРЕЛЯЦІЙНИХ БАЗАХ ДАНИХ

## **4.1. Розробка спеціалізованого фреймворку для дослідження параметрів та способів контролю за обробкою запитів в гетерогенних розподілених нереляційних базах даних**

Для застосування розробленої удосконаленої моделі, яка була описана у другому розділі, та визначених двох методів, які були запропоновані у третьому розділі була розроблена нова інформаційна технологія, яка ввійшла в інформаційну систему для підвищення ефективності обробки запитів в гетерогенних розподілених базах даних.

Інформаційна технологія обробки запитів в гетерогенних розподілених базах даних забезпечує проведення контролю вузлів гетерогенної розподіленої нереляційної бази даних (рис. 4.1). Вхідними даними є: набір вузлів, набір запитів, тестові дані та типи запитів. Після запуску та проходження ініціалізації фреймворку для системи обробки запитів та розгортання середовища відбувається перевірка удосконаленими методами обробки запитів, схеми роботи яких описані у третьому розділі. Після обробки запитів на виході отримуємо такі показники: час обробки запитів кожного вузла, помилки, які виникли при обробці запитів в вузлах, список вузлів, які працюють з помилками та непрацюючі компоненти (типи) цих вузлів.

В системі контролю вузлів використувоються насиупні блоки: розгортання вузлів, підготовка запитів, генерація пакету запитів, перевірка вузлів гетерогенної розподіленої нереляційної бази даних. Опишемо більш детальніше функції блоків в системі контролю вузлів:

Вхідні дані

Набір вузлів

Набір запитів

Тестові дані

Типи запитів

Ініціалізація

Ініціалізація тестового фреймворку

Розгортання вузлів середовища

Контроль вузлів

Розгортання вузлів

Генерація пакету запитів

Підготовка запитів

Перевірка вузлів

Модулі перевірки вузлів

Модуль моніторингу

Модуль виявлення

Модуль визначення

Вихідні дані

Час обробки запитів

Помилки обробки запитів

Вузли з помилками

Непрацюючі компоненти

Рис. 4.1. Схема інформаційної технології перевірки вузлів гетерогенної розподіленої нереляційної бази даних

- в блоці розгортання вузлів вноситься інформація та параметри про ті вузли гетерогенної розподіленої нереляційної бази даних, які будуть перевірятися;

- в блоці підготовки запитів вноситься інформація про запити до вузлів гетерогенної розподіленої нереляційної бази даних;

- в блоці генерації пакету запитів вибираються ті запити та вузли, які будуть перевірятися;

- блок перевірки вузлів відправляє набір запитів в вузли гетерогенної розподіленої нереляційної бази даних та приймає з них відповіді.

Для перевірки вузлів застосовують модулі, які відповідають основним науковим результатам, а саме: модель моніторингу обробки запитів, метод виявлення некоректної роботи вузлів та метод визначення працездатності вузлів обробки запитів.

Рис. 4.2. Функціональна схема інформаційної системи підвищення ефективності системи контролю

Модуль моніторингу

Модуль перевірки вузлів

Модуль аналітики

Модуль розробки плану контролю

Модуль розробки

Модуль планування

БД вимог

БД еталонних запитів

Модуль оцінки результатів

База результатів

Модуль виявлення некоректної роботи

Модуль визначення працездатності

Модуль підготовки відповідей

Модуль передачі запитів

БД еталонних відповідей

Модуль розробки запитів

Модуль розробки груп запитів

Рівень розробки

Рівень даних

Рівень контролю

На основі інформаційної технології було спроектовано інформаційну систему контролю обробки запитів в гетерогенних розподілених нереляційних базах даних, яка складається з основних трьох етапів виконання: етап розробки, етап даних та етап контролю (рис. 4.2). Етап даних визначає збереження даних у гетерогенних розподілених нереляційних базах даних та включає в себе наступні сховища: база даних вимог до запитів, база даних еталонних запитів та база даних еталонних відповідей.

На рівні розробки модуль аналітики баз даних відповідає за формування вимог до розробки запитів та збереження їх в базі даних. Зазвичай, це обов’язки пов’язано з бізнес-аналітиком у команді програмістів, які проводять розробку програмного забезпечення. Розробка плану контролю проводиться на основі аналізу вимог до запитів, які відправлятимуться до нереляційних розподілених баз даних. По готовності вимоги до запитів відправляється до адміністратора для підготовки реальних запитів перевірки.

Модуль розробки плану контролю відповідає на розробку плану контролю командою програмістів. Створюючи вузли розподіленої нереляційної бази даних, розробники зобов’язані покривати функціонал, який був розроблений контрольними запитами та запитами-тестами в зв’язку з тим, що це буде займати менше часу, ніж коли це виконує адміністратор комплексної системи управління.

Рівень контролю відповідає за процес контролю за програмним забезпеченням розподілених нереляційних баз даних. При початку розробник запитів готує тестові запити, які за допомогою написаного фреймворку реалізує у вигляді програмного коду, який перевіряє розроблений вузол нереляційної бази даних.

Адміністратор серверу моніторингу проводить розробку запитів для перевірки вузла та підготовку та запуск цих запитів на базах даних що використовуються. Отримані результати зберігаються у нереляційній базі знань. На основі знайдених помилках у відповідях на запити адміністратор проводить їх опис та проводить модифікацію запитів для уникнення їх в майбутньому.

Для проведення експериментальних досліджень системи моніторингу гетерогенних розподілених нереляційних баз даних було розроблено фреймворк, який допомагає проводити підготовку, відправку запитів, прийом та обробку відповідей від вузлів розподіленої системи. Для розробки фреймворку була використана платформа .NET, яка є сумісною з багатьма операційними системами, особливо тими, які найчастіше використовуються: Windows та Linux. Мовою розробки для фреймворку було обрано C#, в зв’язку з тим, що на ній з кожним роком збільшується кількість написаних програмних продуктів та має повний набір бібліотек для розробки таких спеціальних фреймоворків. Розробка проводилася в середовищі програмування Visual Studio 2022 спеціально для того, щоб створювати готові зборки модулю контролю та розгортати їх на серверах гетерогенних розподілених нереляційних баз даних.

Для запуску системи контролю обробки запитів за механізмами, які були описані в розділах два та три були використані інструменти підміни запитів на запити, які приймає той тип нереляційної розподіленої бази даних за яким проводиться моніторинг та перевірка згідно моделі та методів. При чому ці інструменти дозволяють прописувати різні запити для одного вузла, задавати параметри цих запитів, які використовуються для контролю, та розміщувати їх на різних вузлах розподілених нереляційних баз даних.

Для встановлення розробленого тестового середовища по проведенню перевірки викладених у другому та третьому розділах теоретичних висновків, використовується Docker контейнери, які дозволяють легко змінювати розташування елементів комплексної системи та легко встановлюватися та видалятися. Завдяки цьому немає необхідності у обовязковому використанні конкретної операційної системи.

Для використання у розробці комплексної системи управління опишемо структуру фреймворку та методи, які він буде використовувати (рис. 4.3). В основі фреймворку лежать два класи: ControlCorrect та ControlCapacity.

ErrorDescription

\+ Exception: exception

AuxiliaryModels

\+ GetModel: string

ParametrToken

\+ Conn: void

\+ Disposer: void

ControlCorrect

\+ SetUser: void

\+ SetNode: void

\+ QueryName: void

\+ DefineQuery: void

\+ EtalonAnswer: void

\+ EtalonQueryNode: void

\+ SendQueryNode: void

\+ ClearQueryNode: void

ControlCapacity

Generator

ImitatorNode

FunctionComparers

VerificateResult

ConverterModel

\+ GetUser: void

\+ SetUser: void

\+ SetNode: void

\+ FindByQuery: string

\+ ExecuteQuery: void

\+ Chek: void

\+ SendQueryNode: void

\+ ClearQueryNode: void

\+ GenerSummary: void

\+ GenerFailure: void

\+ AddSummary: void

\+ AddFailure: void

\+ NodeConn: void

\+ NodeFind: string

\+ NodeClear: void

\+ NodeSend: void

\+ CheckBody: bool

\+ CheckHeaders: bool

\+ CheckCode: bool

\+ CheckHttp: bool

\+ CheckExep: bool

+VerificateResult

+ConvertTo

Рис. 4.3. Діаграма класів розробленого фреймворку комплексної системи управління

Клас ControlCorrect відповідає за визначення очікуваної поведінки вузлів розподіленої бази даних та оформлення її у вигляді спеціального запиту. Запит формується у форматі JSON та відправляється у вузол. Також цей клас відповідає за передачу запиту від серверу моніторингу до вузла, який обробляє дані за допомогою нереляційної бази даних. Масив очікуваної поведінки вузлів імітатора зберігається на сервері, і при очікуваному запиті на цей вузол поверне очікувану еталонну відповідь.

В класі ControlCorrect доступні для роботи наступні методи:

1\) SetUser – задати ім’я користувача розподілених нереляційних баз даних;

2\) SetNode – задати ім’я вузла розподілених нереляційних баз даних;

3\) QueryName – задати назву запиту, який буде відправлятися на вузол розподіленої нереляційної бази даних;

4\) DefineQuery – задати параметри запиту, який буде відправлятися на вузол розподіленої нереляційної бази даних;

5\) EtalonAnswer – задати параметри очікуваної відповіді, яка повинна прийти від вузла розподіленої нереляційної бази даних;

6\) EtalonQueryNode – створити запит, в якому буде записана еталонна відповідь вузла розподіленої нереляційної бази даних;

7\) SendQueryNode – надіслати згенерований запит на вузол, якил відноситься до розподіленої нереляційної бази даних;

8\) ClearQueryNode – видалити масив запитів з центрального вузла розподіленої нереляційної бази даних.

Клас ControlCapacity відповідає за створення необхідного для перевірки запиту у головному вузлі розподіленої нереляційної бази даних, формування з даних тіла запиту, який буде відправлятися на вузол розподіленої нереляційної бази даних та перевірку відповіді на відправлнеий запит від головного вузла розподіленої нереляційної бази даних та порівняння її з очікуваною еталонною відповіддю. Якщо очікувана відповідь на запит до розподіленої нереляційної бази даних співпадає з еталонною відповіддю для даного запиту, то перевірка вважається пройдена.

Розглянемо методи класу ControlCapacity:

1\) GetUser – вказати адресу вузла розподіленої нереляційної бази даних, на який відправляється запит;

2\) SetUser – задати ім’я користувача розподілених нереляційних баз даних;

3\) SetNode – задати ім’я вузла розподілених нереляційних баз даних;

4\) FindByQuery – пошук необхідного запиту в масиві запитів до розподілених нереляційних баз даних за його характеристиками;

5\) ExecuteQuery – відправка обраного запиту від користувача на вузол розподіленої нереляційної бази даних;

6\) Chek – перевірка отриманого результату запиту з очікуваною відповіддю на запит до розподіленої нереляційної бази даних.

Було розроблено додатково інші допоміжні класи для фреймворку перевірки гетерогенних розподілених нереляційних баз даних:

- FunctionComparers – містить додаткові функції для порівняння набору відповідей від вузлів гетерогенних розподілених нереляційних баз даних: тіло запиту, набір відповідей, повідомлення про помилки на виконання запитів;

- Generator – відповідає за генерацію тестових запитів для перевірки вузлів гетерогенних розподілених нереляційних баз даних та дозволяє налаштовувати спеціальний формат запиту для внесення результатів у внутрішню базу даних;

- ImitatorNode – відповідає за встановлення з’єднання з вузлами гетерогенних розподілених нереляційних баз даних та передачу запитів до них;

- ParametrToken – налаштування параметрів авторизації до вузлів гетерогенних розподілених нереляційних баз даних, які перевіряються;

- VerificateResult – верифікація результатів запиту на вузоли гетерогенних розподілених нереляційних баз даних, які перевіряються;

- AuxiliaryModels – містить допоміжні моделі для створення запитів за допомогою даного фреймворку;

- ConverterModel – може конвертувати різні моделі для одного типу запитів в інший тип запитів;

- ErrorDescription – опис помилок, які виникають при обробці запитів в гетерогенних розподілених нереляційних баз даних.

Для проведення процедури створення запитів до вузлів гетерогенних розподілених нереляційних баз даних для проведення перевірки цих вузлів потрібно виконати методи по підготовці цих запитів. Розроблений фреймворк дозволяє створювати запити у вигляді JSON-файлів та інші. Запит містить дані про користувача та вузоли гетерогенних розподілених нереляційних баз даних, опис запиту, його тіло та очікувану еталонну відповідь.

Приведемо приклад згенерованого запиту в вигляді JSON файлу, в якому є дві частини – GET i POST – на отримання відповіді з обовязковим включенням id користувача та тіла запиту. Для кожного запиту, що відправляється, є очікувана еталонна відповідь від вузла гетерогенних розподілених нереляційних баз даних.

{

  "User": "Node2",

  "Node": "Node1",

  "Host": "localhost:1521",

  "Query": \[

    {

      " QueryName ": "get user by id",

      "Qery": {

        "Method": "get",

        "Path": "/id/a250"

      },

      " EtalonAnswer ": {

        "StatusCode": 200,

        "Body": {

          "Id": "a250",

          "EtalonAnswer ": "Main User",

          "Email": "main@test.com"

        }

      }

    },

    {

      " QueryName ": "create new user",

      "Query": {

        "Method": "post",

        "Path": "/new",

        "Body": {

          "QueryName": "Second User",

          "Email": "second@test.com"

        }

      },

      " EtalonAnswer ": {

        "\_StatusCode\_": 200,

        "\_Body\_": "User has successfully created"

      }

    }

  \]

}

Після завершення процедури створення відбувається запуск основного вузла та запуск запиту до вузлів гетерогенних розподілених нереляційних баз даних, який дозволить провести перевірку розподіленої системи обробки даних.

За допомогою контейнерів, які використовуються, Docker створюється запит з основного вузла, з якого фреймворк бедн надсилти запит. Створення контейнера з запитами:

serviceimitator2:

    image: mountebank

    ports:

      - "25252:25252"

      - "46842:46842"

Після того, як фреймворк згенерує запит та відправить його на вузол, можемо спостерігати обробку запиту в вузлі гетерогенної розподіленої нереляційної базм даних:

{

 "imposters": \[

  {

      "\_protocol\_": "http",

      "\_port\_": 4684,

      "\_links\_": {

        "\_self\_": {

          "\_href\_": "http://localhost:1521/imposters/46842"

        }

      }

    }

  \]

}

Запуск запитів за допомогою контейнерів у програмному забезпеченні Docker потрібно провести по порядку їх встановлення в черзі:

Запуск запитів, а для цього необхідно:

- Створити Dockerfile для запуску вузлів;

- Створити Dockerfile для запуску запитів;

- Створити docker файл для розгортання основного вузла, вузла який буде перевірятися та набору запитів.

Dockerfile для основного вузла:

*FROM microsoft/aspnetcore:3.1.0*

*COPY /publish /app*

*WORKDIR /app*

*ENV ASPNETCORE_URLS http://\*:50002*

*EXPOSE 50002*

*ENTRYPOINT dotnet Service1.dll*

Файл зберігається з іменем DockerfileNode1 з типом File.

Dockerfile для вузла, що перевіряється:

*FROM microsoft/aspnetcore:3.1.0*

*COPY . /TestProject*

*WORKDIR /TestProject*

*RUN dotnet restore --no-cache*

Файл записується з іменем TestDockerNode з типом File

Docker файл для розгортання системи створення запитів, основного вузла та вузла, який перевіряється:

*version: '1'*

*services:*

*  #Розгортаємо контейнер з основним вузлом за його Dockerfile*

*  testproject:*

*    build: *

*      dockerfile: TestDockerNode*

*    #Запускаємо запити*

*    command: dotnet test*

*    links:*

*      - Node1*

*      - Node2*

*  #Розгортаємо контейнер з вузлом, який буде перевірятися*

*  Node1:*

*    build: *

*      dockerfile: TestDockerNode*

*    ports:*

*      - "50102:50002"*

*    *

*  #Розгортаємо основний вузол     *

*  Node2r2:*

*    image: test*

*    ports:*

*      - "25252:25252"  *

*      - "46842:46842" *

Таким чином в середовищі для перевірки запускаються всі необхідні компоненти у контейнерах. Даний метод не потребує визначеної операційної системи, серверів з визначиними параметрами чи їх довгого налаштування.

Docker файл зберігається у форматі uml. Цей файл запускається через команди консолі:

*docker up --build --no-cache*

## 4.2. Графічний інтерфейс розробленого спеціалізованого середовища комплексної системи управління та перевірки 

## 

Для проведення експериментальних досліджень по перевірці моделей та методів, які були описані в другому та третьму розділах було розроблено спеціальне веб-орієнтоване програмне середовище, яке має назву «комплексної системи управління та перевірки для дослідження ефективності обробки запитів в гетерогенних нереляційних розподілених базах даних» та пристосовано для роботи з різними операційними системами та різними параметрами серерів в хмарних середовищах і не тільки.

Інтерфейс комплексної системи управління та перевірки для дослідження ефективності обробки запитів в гетерогенних нереляційних розподілених базах даних створений так, що за допомогою нього проводяться експерименти щодо вимірів часу створення запитів в відповідних вузлах гетерогенних нереляційних розподілених базах даних та часу оцінки відповіді в повірвнянні з еталонною відповіддю на головному вузлі, а також він дозволяє вимірювати час обробки запиту вузлами гетерогенних нереляційних розподілених базах даних.

За допомогою першої вкладки інтерфейсу рисунок 4.4 проводяться заповнення параметрів вузлів гетерогенних нереляційних розподілених базах даних.

<img src="media/image496.png" style="width:6.69375in;height:4.75903in" />

Рис. 4.4. Заповнення параметрів вузлів гетерогенних нереляційних розподілених базах даних

До цих параметрів відносяться: ip адреса вузла, сервіс вузла, користувач під яким потрібно перевіряти запити, пароль цього користувача та порт через який потрібно заходити в даний вузол. Ця інформація формується у вигляді відповідного списку та передається для подальшого вибору в основне вікно комплексної системи управління та перевірки для дослідження ефективності обробки запитів в гетерогенних нереляційних розподілених базах.

Друга вкладка рисунок 4.5 служить для внесення еталонних типів запитів та еталонних типів відповідей для обробки в комплексній системі управління та перевірки.

<img src="media/image497.png" style="width:6.69375in;height:4.75833in" />

Рис. 4.5. Внесення еталонних типів запитів та еталонних  
типів відповідей для обробки в комплексній системі управління  
та перевірки для дослідження ефективності обробки запитів  
в гетерогенних нереляційних розподілених базах даних

Дана вкладка призначена для дослідження ефективності обробки запитів в гетерогенних нереляційних розподілених базах даних, які будуть відправлятися на вузли гетерогенної нереляційної розподіленої бази даних. В ній є можливість створити не один запит, зберегти їх та відредагвати при потребі. Після створення цих запитів потрібно створити еталонні відповіді на кожний запит до вузлів гетерогенної нереляційної розподіленої бази даних поєднавши їх однозначно.

За допомогою третьої вкладки рисунок 4.6 проводиться експеримент по визначення ефективності обробки запитів в комплексній системі управління та перевірки.

<img src="media/image498.png" style="width:6.69267in;height:4.16038in" />

Рис. 4.6. Визначення часу створення запитів у відповідних вузлах  
гетерогенних нереляційних розподілених баз даних  
та часу оцінки відповіді в повірвнянні з еталонною відповіддю  
на головному вузлі, що дозволяє вимірювати  
час обробки запиту вузлами гетерогенних нереляційних  
розподілених базах даних

Дана вкладка призначена для дослідження ефективності обробки запитів в гетерогенних нереляційних розподілених базах даних. Для цього на вкладці є можливість вибору вузла гетерогенної розподіленої нереляційної бази даних, який потрібно перевірити. Також вибір типу запиту, який потрібно відправити на цей вузол гетерогенної розподіленої нереляційної бази даних. В окремому вікні результат перевірки, тобто порівння відповіді, яка прийшла з вузла гетерогенної розподіленої нереляційної бази даних з еталонною відповіддю. Крім цього, на вкладці присутні часові характеристи проведення експерименту : вимірів часу створення запитів в відповідних вузлах гетерогенних нереляційних розподілених базах даних та часу оцінки відповіді в повірвнянні з еталонною відповіддю на головному вузлі, а також він дозволяє вимірювати час обробки запиту вузлами гетерогенних нереляційних розподілених базах даних.

Таким чином інтерфейс «Комплексної системи управління та перевірки для дослідження ефективності обробки запитів в гетерогенних нереляційних розподілених базах даних» повністю виконує задачі по перевірці моделі та методів, які були описані в другій та третій главі.

## **4.3. Комплексна система управління та перевірки гетерогенного середовища зберігання та обробки даних в розподілених нереляційних базах даних**

## **4.3.1. Розробка комплексної системи управління гетерогенними розподіленими нереляційними базами даних**

## 

Для обробки інформації компанії застосовують власні програми та готові програмні комплекси, які були закуплені, на основі СУБД різного типу. Постійно виникає проблема отримання даних з СУБД на зовнішні ресурси та перевірки доступу до даних в розподіленій нереляційній базі даних. Пропонована система дозволить підтримати всі вищезазначені функції, для цього в якості додаткових методів система забезпечує захист переданих та даних, які обробляються. Крім того, підвищену увагу буде приділено засобам перевірки вузлів розподіленої системи.

Зазвичай на найвищому рівні знаходиться підсистема управління комплексом, яка керує всією складною системою і забезпечує оперативне подання та зберігання інформації для порталу. Представлення  
інформації виконується з єдиного сховища даних, і для вирішення  
цього завдання розробляється підсистема підготовки, обробки та зберігання даних.

В систему надходить вся потрібна інформація, що знаходиться у відповідних форматах і при потребі може використовуватися на ресурсі для перевірки вузлів гетерогенної розподіленої нереляційної бази даних. Для того, щоб інформація з різних зовнішніх джерел (нереляційних баз даних) в коректному форматі потрапляла в єдину відповідь потрібна спеціальна підсистема синхронізації даних з гетерогенних розподілених нереляційних баз даних, тобто підсистема конвертації та перетворення різних типів запитів в єдиний формат для підготовки відповідей. Одночасно необхідно вирішити проблему оптимізації процесу конвертації даних з різнорідних нереляційних баз даних.

На нижньому рівні лежить підсистема отримання даних, вона простим засобом отримання даних з гетерогенних розподілених нереляційних баз даних для подальшої обробки знаходиться в ній інформації (рис. 4.7).

Розглянута комплексна система управління та перевірки має підтримувати наступні сервіси:

\- Єдиний формат обробки даних та підготовки відповіді;

\- Конвертація необхідних даних.

\- Обмін необхідними даними;

\- Моніторинг безпеки необхідних даних;

\- Підключення користувачів та забезпечення безпеки електронних підписів.

**Підсистема синхронізації даних з гетерогенних нереляційних СУБД**

**Підсистема управління та перевірки даних**

**Підсистема обробки та підготовки даних**

**Комплексна система управління**

Модуль взаємодії з користувачами

Модуль обміну даними

Модуль виявлення некоректної роботи вузлів

Модуль створення резервних копій

Модуль експорту даних

Модуль відновлення

Модуль збереження даних

Модуль управління ресурсами

Модуль імпорту даних

Модуль технологічного аналізу

Модуль взаємодії з зовнішніми джерелами

Модуль синхронізації даних

Модуль логістики

Модуль механізмів перевірки даних

Модуль перетворення даних в єдиний формат

Модуль підготовки даних

**Підсистема зберігання та отримання даних**

СУБД

ObjectDB

СУБД

CouchDB

СУБД

Oracle

СУБД

MongoDB)

СУБД

BigData

Модуль моніторингу обробки запитів

Модуль аутентифікації та розмежування доступу

Модуль визначення працездатності вузлів

Рис. 4.7. Структурна схема комплексної системи управління  
та перевірки гетерогенного середовища обробки й зберігання даних  
в нереляційних базах даних

Опишемо детальніше підсистеми комплексної системи управління та перевірки та модулі, які входять до підсистем для представлення процесу обробки та передачі даних в гетерогенних розподілених базах даних. Узагальнена структурна схема комплексної системи управління та перевірки гетерогенним середовищем зберігання та обробки даних в гетерогенних нереляційних базах даних представлена на рисунку 4.7.

## **4.3.2. Підсистема управління та перевірки даних комплексної системи управління та перевірки гетерогенного середовища обробки та зберігання даних в нереляційних базах даних**

## 

Служить для виконання управління комплексною системою та забезпечує функціонування і перевірку всіх елементів,які були використані у системі, у тому числі для забезпечення безперебійного обміну даними.

Дана підсистема містить наступні модулі:

*Взаємодії з користувачами*, що призначений для обробки постійної взаємодії з користувачами, внесення нових користувачів для перевірки гетерогенних нереляційних розподілених баз даних. Інформація про засоби для перевірки та затвердження надходять до модуля аутентифікації та розмежування доступу.

*Аутентифікації та розмежування доступу* забезпечує надання користувачеві відповідного доступу до даних відповідно наявних у нього прав, а також, відповідає за призначення відповідних прав новоствореним користувачам і їх аутентифікацію у випадку потреби для тих користувачів, що вже працювали з вузлами.

*Модуль моніторингу* обробки запитів гетерогенних розподілених нереляційних баз даних призначений для виявлення нештатних ситуацій, передачі попередження адміністратору серверу моніторинг та допомоги у прийнятті оперативних рішень, а спільний з ним модуль аутентифікації та розмежування доступу виконує розподіл прав та обовязків між суб'єктами, а це є одним основною вимогою до системи безпеки.

*Модуль виявлення некоректної роботи вузлів* гетерогенних розподілених нереляційних баз даних призначений для визначення прихованих несправностей вузла шляхом взаємного обміну запитами між вузлами з урахуванням припущень щодо синхронності гетерогенних розподілених нереляційних баз даних, а також можливості користувачем визначити вузол обробки. Зазначений модуль дозволяє здійснювати виявлення випадків некоректної роботи вузлів обробки запитів.

*Модуль визначення працездатності вузлів* гетерогенних розподілених нереляційних баз даних призначений для підвищення ефективності обробки даних способом обробки запитів на основі визначення апостеріорних ймовірностей справного стану вузлів. Отримані модулі позволяють, забезпечити потрібний рівень захисту гетерогенної розподіленої не реляційної бази даних, а також підтримують неперервне виконання обробки запитів системою.

*Обміну даними, що* виконує обмін даними між підсистемою управління та перевірки гетерогенного середовища обробки та зберігання даних в нереляційних базах даних та підсистемою обробки та підготовки даних. При функціонуванні модуль підрозділяється на два сегменти. Перший сегмент виконує експорт інформації, а другий - імпорт інформації. Для підвищення швидкості обміну даними даний модуль безпосередньо пов'язаний з модулем механізмів перевірки даних, а також з модулями експорту, зберігання даних та імпорту.

## **4.3.3. Підсистема обробки та підготовки даних**

## 

Визначає створення програмного середовища щодо підтримки і забезпечення механізмів обробки, підготовки та зберігання даних.

*Модуль резервного копіювання* забезпечує архівування та зберігання всіх даних, що проходять перевірку за зазначений проміжок часу на відповідну дату та час.

*Модуль відновлення* забезпечує завантаження даних з резервних бекапів, створюваних минулим модулем при втраті інформації чи некоректній роботі системи.

*Модуль експорту даних* забезпечує вибір даних, до яких звертається користувач при проведені відповідної перевірки та передачі посилання в модуль механізмів перевірки даних.

*Модуль імпорту даних* служить для вибору тих даних, які потрібно перевіряти. Також виконується передача посилання на дані для запису, як і в попередньому модулі, в механізмі перевірки даних.

*Модуль механізму перевірки даних* виконує перевірку даних на основі модулів, які були описані в підсистемі управління та перевірки а саме: *модуль моніторингу* обробки запитів гетерогенних розподілених нереляційних баз даних, *модуль виявлення некоректної роботи вузлів* гетерогенних розподілених нереляційних баз даних та *модуль визначення працездатності вузлів* гетерогенних розподілених нереляційних баз даних.

*Модуль зберігання даних* використовується для зберігання даних, які користувач завантажує і, в разі потреби, надає доступ до певних носіїв з файлами бази даних.

*Модуль управління ресурсами* призначений для забезпечення управління підсистемою обробки та підготовки даних, а також відповідає за взаємодію з іншими підсистемами.

## **4.3.4. Підсистема синхронізації даних з гетерогенних нереляційних СУБД**

## 

Для підтримки перевірки та контролю за даними, що мають універсальний формат необхідно виконати спеціальні дії по об'єднанню даних з різних гетерогенних розподілених нереляційних баз даних, тому використовується модулі, які виконують перетворення даних до одного формату.

*Модуль технологічного аналізу* виконує проведення аналізу інформації, виконує конвертацію у відомому форматі та перевірку змінених даних.

*Модуль взаємодії з зовнішніми джерелами* виконує функцію підтримки неперервної взаємодії з гетерогенними нереляційними СУБД за допомогою використання відповідних програм.

*Модуль синхронізації даних* застосовується для визначення у гетерогенних нереляційних розподілених базах даних різних типів даних, які можуть бути приведені до універсального виду.

*Модуль логістики* забезпечує управління, контроль руху та планування інформації для різних підсистем.

*Модуль копіювання даних* *в єдиний формат* призначений для передачі даних в єдиному форматі.

*Модуль підготовки даних* використовується для підготовки інформації, які надсилаються модулем взаємодії із зовнішніми джерелами.

*Останньою опишемо **підсистему зберігання та отримання даних *** об'єднує в собі гетерогенні нереляційні СУБД, з якими проводиться робота по перевірці та обробці даних. Дані бази даних можуть бути розподілені на різних серверах або на одному сервері, але в межах однієї віртуальної підмережі для кращого обміну даними та їх перевірці.

## **4.4. Експериментальні досліди параметрів засобів моніторингу обробки запитів**

## 

Основним для проведення експериментальних досліджень є механізм моніторингу обробки запитів, що забезпечує процес постійного оцінювання дій користувачів по відношенню до несанкціонованих дій. Задамо інтервал *∆T*, як оцінку дій користувачів на основі аналізу інформації щодо моніторингу безпеки. У випадку великого значення *∆T* моніторинг буде статичним, тобто, протягом періоду *∆T* дії користувачів не оцінюються з погляду на імовірності здійснення несанкціонованого доступу та відповідно збільшується імовірність по відношенню до загроз безпеці процесів обробки даних.

При експериментальних досліджень застосовувалася комп'ютерна серверна система з наступними параметрами: процесор Intel Core i7-263QM 4Gz, оперативна пам'ять - 16Гб, яка функціонує під управлінням операційної системи Windows 10. При аналізі даних з моніторингу безпеки баз даних, що представлені в вигляді файлу-масиву векторів-записів, розроблений спеціальний модуль, а щодо аналізу даних, які представлені у форматі рядків бази даних використовувалася СУБД Oracle. В процесі досліджень оцінювалися такі характеристики: *Т<sub>зб</sub>* - загальний час збору даних з моніторингу обробки запитів та запису у файл векторів (*Т<sub>зб1</sub>*) або в формат бази даних (*Т<sub>зб2</sub>*); час вибірки даних з моніторингу безпеки *Т<sub>вб1</sub>*, відповідно, з файлу векторів-записів (*Т<sub>вб1</sub>*) чи набору даних в форматі бази даних з використанням Oracle (*Т<sub>вб2</sub>*). У результаті проведеного оцінювання загальний час аналізу даних з моніторингу обробки запитів *Т<sub>ан</sub>* розподілених баз даних звичайними засобами і Oracle як: *Т<sub>ан</sub> = T<sub>зб</sub>* + *T<sub>вб</sub>*.

Під час експериментальних досліджень створювалися масиви даних відносно подій моніторингу обробки запитів різного типу, які знаходяться в діапазоні від 10000 до 100000 (10000, 50000, 100000), при цьому кожне значення містить по 10 контрольних подій (табл. 4.1, рис. 4.8).

Було визначено та проведено десять експериментів щодо генерації набору даних відповідно до подій моніторингу різного типу, далі проводиться знаходження середнього по отриманим даним. На рис. 4.10 наведено діаграму оцінки заагльного часу аналізу даних відповідно до подій моніторингу обробки запитів в розподілених базах даних звичайними засобами і Oracle NoSQL.

Таблиця 4.1

Експериментальні дані щодо обробки запитів моніторингу безпеки для звичайних засобів і Oracle NoSQL.

<table>
<colgroup>
<col style="width: 10%" />
<col style="width: 13%" />
<col style="width: 13%" />
<col style="width: 12%" />
<col style="width: 0%" />
<col style="width: 12%" />
<col style="width: 13%" />
<col style="width: 11%" />
<col style="width: 12%" />
</colgroup>
<tbody>
<tr>
<td rowspan="2">№ експерименту</td>
<td><p>Розмір</p>
<p>ність, Кз</p></td>
<td colspan="3">10000</td>
<td colspan="2">50000</td>
<td colspan="2" style="text-align: center;">100000</td>
</tr>
<tr>
<td>Час Т,с</td>
<td>Звичайні засоби</td>
<td>Oracle NoSQL</td>
<td colspan="2">Звичайні засоби</td>
<td>Oracle NoSQL</td>
<td style="text-align: center;">Звичайні засоби</td>
<td style="text-align: center;">Oracle NoSQL</td>
</tr>
<tr>
<td rowspan="2">1</td>
<td>Тзб</td>
<td>0,095</td>
<td>1,263</td>
<td colspan="2">0,158</td>
<td>8,722</td>
<td style="text-align: center;">0,211</td>
<td style="text-align: center;">21,192</td>
</tr>
<tr>
<td>Твб</td>
<td>2,521</td>
<td>0,029</td>
<td colspan="2">39,951</td>
<td>0,051</td>
<td style="text-align: center;">163,41</td>
<td style="text-align: center;">0,113</td>
</tr>
<tr>
<td rowspan="2">2</td>
<td>Тзб</td>
<td>0,074</td>
<td>1,209</td>
<td colspan="2">0,159</td>
<td>8,629</td>
<td style="text-align: center;">0,242</td>
<td style="text-align: center;">23,132</td>
</tr>
<tr>
<td>Твб</td>
<td>2,483</td>
<td>0,029</td>
<td colspan="2">38,344</td>
<td>0,048</td>
<td style="text-align: center;">156,23</td>
<td style="text-align: center;">0,064</td>
</tr>
<tr>
<td rowspan="2">3</td>
<td>Тзб</td>
<td>0,074</td>
<td>1,361</td>
<td colspan="2">0,157</td>
<td>8,991</td>
<td style="text-align: center;">0,278</td>
<td style="text-align: center;">22,651</td>
</tr>
<tr>
<td>Твб</td>
<td>2,261</td>
<td>0,034</td>
<td colspan="2">39,559</td>
<td>0,049</td>
<td style="text-align: center;">144,59</td>
<td style="text-align: center;">0,085</td>
</tr>
<tr>
<td rowspan="2">4</td>
<td>Тзб</td>
<td>0,079</td>
<td>1,271</td>
<td colspan="2">0,158</td>
<td>8,416</td>
<td style="text-align: center;">0,248</td>
<td style="text-align: center;">21,968</td>
</tr>
<tr>
<td>Твб</td>
<td>2,411</td>
<td>0,029</td>
<td colspan="2">36,221</td>
<td>0,050</td>
<td style="text-align: center;">158,61</td>
<td style="text-align: center;">0,085</td>
</tr>
<tr>
<td rowspan="2">5</td>
<td>Тзб</td>
<td>0,096</td>
<td>1,270</td>
<td colspan="2">0,159</td>
<td>8,694</td>
<td style="text-align: center;">0,269</td>
<td style="text-align: center;">21,858</td>
</tr>
<tr>
<td>Твб</td>
<td>2,489</td>
<td>0,029</td>
<td colspan="2">37,146</td>
<td>0,051</td>
<td style="text-align: center;">152,39</td>
<td style="text-align: center;">0,105</td>
</tr>
<tr>
<td rowspan="2">6</td>
<td>Тзб</td>
<td>0,085</td>
<td>1,313</td>
<td colspan="2">0,159</td>
<td>8,294</td>
<td style="text-align: center;">0,293</td>
<td style="text-align: center;">22,011</td>
</tr>
<tr>
<td>Твб</td>
<td>2,219</td>
<td>0,034</td>
<td colspan="2">38,918</td>
<td>0,048</td>
<td style="text-align: center;">162,04</td>
<td style="text-align: center;">0,105</td>
</tr>
<tr>
<td rowspan="2">7</td>
<td>Тзб</td>
<td>0,095</td>
<td>1,272</td>
<td colspan="2">0,155</td>
<td>8,949</td>
<td style="text-align: center;">0,278</td>
<td style="text-align: center;">21,888</td>
</tr>
<tr>
<td>Твб</td>
<td>2,429</td>
<td>0,029</td>
<td colspan="2">39,441</td>
<td>0,051</td>
<td style="text-align: center;">158,97</td>
<td style="text-align: center;">0,102</td>
</tr>
<tr>
<td rowspan="2">8</td>
<td>Тзб</td>
<td>0,089</td>
<td>1,375</td>
<td colspan="2">0,161</td>
<td>8,881</td>
<td style="text-align: center;">0,258</td>
<td style="text-align: center;">21,664</td>
</tr>
<tr>
<td>Твб</td>
<td>2,502</td>
<td>0,029</td>
<td colspan="2">37,245</td>
<td>0,051</td>
<td style="text-align: center;">163,18</td>
<td style="text-align: center;">0,099</td>
</tr>
<tr>
<td rowspan="2">9</td>
<td>Тзб</td>
<td>0,095</td>
<td>1,322</td>
<td colspan="2">0,158</td>
<td>8,712</td>
<td style="text-align: center;">0,211</td>
<td style="text-align: center;">21,237</td>
</tr>
<tr>
<td>Твб</td>
<td>2,429</td>
<td>0,032</td>
<td colspan="2">37,547</td>
<td>0,051</td>
<td style="text-align: center;">149,62</td>
<td style="text-align: center;">0,091</td>
</tr>
<tr>
<td rowspan="2">10</td>
<td>Тзб</td>
<td>0,091</td>
<td>1,289</td>
<td colspan="2">0,159</td>
<td>8,643</td>
<td style="text-align: center;">0,247</td>
<td style="text-align: center;">22,024</td>
</tr>
<tr>
<td>Твб</td>
<td>2,196</td>
<td>0,029</td>
<td colspan="2">38,248</td>
<td>0,054</td>
<td style="text-align: center;">152,27</td>
<td style="text-align: center;">0,112</td>
</tr>
<tr>
<td rowspan="2" style="text-align: left;">Середнє значення</td>
<td>Тзб</td>
<td>0,091</td>
<td>1,293</td>
<td colspan="2">0,159</td>
<td>8,691</td>
<td style="text-align: center;">0,253</td>
<td style="text-align: center;">21,953</td>
</tr>
<tr>
<td>Твб</td>
<td>2,3949</td>
<td>0,0321</td>
<td colspan="2">38,258</td>
<td>0,048</td>
<td style="text-align: center;">156,27</td>
<td style="text-align: center;">0,089</td>
</tr>
<tr>
<td>Сума</td>
<td><p>Тан=</p>
<p>Тзб+</p>
<p>Твб</p></td>
<td>2,485</td>
<td>1,328</td>
<td colspan="2">38,419</td>
<td>8,738</td>
<td style="text-align: center;">156,51</td>
<td style="text-align: center;">22,048</td>
</tr>
</tbody>
</table>

<img src="media/image499.emf" style="width:6.6in;height:3.09167in" />

Рис.4.8. Експериментальні досліди параметрів системи моніторингу обробки запитів

На рис. 4.9 наведено діаграму розподілу помилкових індикацій інцидентів безпеки.

Рис.4.9. Діаграма розподілу помилкових індикацій інцидентів безпеки

<img src="media/image500.emf" style="width:6.35833in;height:3.075in" />

Рис.4.10. Діаграма оцінки сумарного часу аналізу даних щодо подій моніторингу обробки запитів

В результаті проведених експериментальних досліджень дані, з збільшенням кількості запитів за даними моніторингу безпеки, істотно зростає ефективність за часом аналізу даних із моніторингу безпеки засобами Oracle NoSQL в порівнянні із звичайними засобами. Відповідно до параметру загального часу обробки запитів з моніторингу безпеки (*Т<sub>зб1</sub>\<Т<sub>зб2</sub>*) звичайні засоби є більш ефективними, але вони істотно поступаються засобам Oracle щодо параметру часу обробки запитів з моніторингу безпеки (*Т<sub>вб1</sub>\>\>Т<sub>вб2</sub>*).

У результаті експерименту для 10000 векторів-записів ефективність за загальним часом обробки запитів з моніторингу безпеки (*Т<sub>ан</sub>*) є 88% (1.88 разів: *Т<sub>ан1</sub>*=2.48 с для простих засобів обробки та *Т<sub>ан2</sub>*= 1.32 с для засобів на основі використання Oracle), а для 100000 векторів-записів значення зміниться до 800% (7.09 разів: *Т<sub>ан1</sub>*=156.4 с для простих засобів обробки та *Т<sub>ан2</sub>*=22.05 с для засобів на основі Oracle). У експерементальних застосуваннях у системах моніторингу обробки запитів присутнє постійне нагромадження, тобто збільшення числа векторів-записів, неступним чином, зазначений підхід позволяє набагато збільшити швидкість обробки запитів із моніторингу безпеки в розподілених нереляційних баз даних.

Отже, представлена необхідність підтримки реалізації обробки запитів відносно подій моніторингу безпеки щодо підвищення ефективності обробки запитів при безпеки гетерогенних розподілених нереляційних баз даних. Введено засоби моніторингу обробки запитів з пришвидшеною обробкою запитів. В зв’язку з тим, що при зростаючих обсягах даних при обробці подій моніторингу, самі елементи моніторингу безпеки, які на основі визначеного підходу дозволяють обробляти запити з моніторингу безпеки, а це забезпечує своєчасне формування різних рівнів підозрілості дій користувачів в процесі обробки запитів в гетерогенній розподіленій не реляційній базі даних, а це дозволяє зменшити імовірність атак на систему.

## **4.5. Розробка рекомендацій по впровадженню запропонованих моделей та методів**

## 

При створенні розподілених нереляційних баз даних підприємств крім традиційних завдань (технічного і програмного оснащення) виникає ряд особливих задач, які випливають з розподіленої структурою організацій, а й з застосуванням різних програм при забезпечені стабільної роботи установ.

Дані завдання перевищують можливості традиційних завдань обробки даних в розподілених базах даних та потребують додаткових витрат для програмної та технічної компонент баз даних.

Наочна область побудови гетерогенних розподілених нереляційних СУБД має непросту структуру та тому на першому кроці вона, орзкладається на певну кількість задач, що уподальшому будемо вирішувати окремо, про те вони забезпечують єдину задачу:

створення системи моніторингу обробки запитів гетерогенних розподілених не реляційних баз даних;

створення засобів для забезпечення підвищення швидкості обробки запитів пошуку даних;

створення засобів для забезпечення підвищення швидкості обробки запитів запису даних.

Збір і використання інформаційних баз даних це ключова проблема розроблення єдиного інформаційного простору організації, що вирішується при побудові розподілених баз даних. Джерелом даних для управління служить автоматизована система управління процесами моніторингу, яка забезпечує інформацію щодо операції і ресурсів, що застосовуються під час обробки інформації в розподілених нереляційних базах даних. В зв’язку з цим на першому рівні програмного забезпечення також виділяється ієрархія розподіленої системи автоматизації.

Однією з основних особливостей розподілених баз даних є їх територіальна розміщеність. У структурі програмного забезпечення в зв’язку з цим виділимо ієрархію території діяльності – множина об’єктів, де розміщені підприємства (рис. 4.11).

Сучасна структура побудови інформаційно-керуючої розподіленої бази даних організації представлена такими елементами:

Предметна область гетерогенних розподілених нереляційних баз даних

**ОргП**

**ТерП**

**САП**

**Об’єкт**

Організаційна структура організація

Територія діяльності організація

Система автоматизації організація

Об’єкти організація

Рис. 4.11. Структура предметної області організації

основний сервер, який забезпечує єдине управління у цілях оптимального поділу та застосування ресурсів; управління матеріальними, фінансовими, технічними та людськими ресурсами;

локальні сервери, які розміщені у віддлах, що виконують частину функцій керування;

комп’ютери працівників, що працюють з гетерогенними розподіленими нереляційними системами обробки даних.

На підприємствах є декілька рівнів ієрархії щодо управління: керівництво, служби, головні менеджери, відділи, старші фахівці, працівники, оператори, як показано на рисунку 4.12. На підставі опитування експертів у сфері обслуговування розподілених баз даних і погодження оцінок були призначені основні взаємозвязки в області.

Підприємство

Оператор

Оператор

Оператор

Оператор

Оператор

Оператор

БД

БД

БД

БД

БД

БД

Служба

Відділ

Управління

Рис. 4.12. Структура інформаційних об’єктів підприємства

Апаратне забезпечення системи автоматизації можна представити як сукупність ЕОМ, на яких функціонує програмне забезпечення РБД і які представлені в обчислювальній мережі серверами і робочими станціями користувачів-працівників підприємства. До ЕОМ можуть бути приєднані різного роду периферійні пристрої – принтери, сканеры та ін. Введення периферійних пристроїв в модель здійснюється з тих міркувань, що їм можуть бути призначені у відповідність мережеві ресурси, що вимагає введення відповідних логічних зв’язків.

## Висновки до розділу 4

## 

Розроблено програмне забезпечення (спеціалізований фреймворк) комплексної системи управління та перевірки гетерогенного середовища обробки та зберігання даних в нереляційних базах даних, яке базується на розроблених в дисертації моделі моніторингу обробки запитів, методі виявлення некоректної роботи вузлів бази даних та методі визначення працездатності вузлів обробки запитів. Впровадження зазначеного програмного забезпечення дозволяє підвищити ефективність функціонування гетерогенних розподілених нереляційних баз даних. Показано, що даний фреймворк доцільно застосовувати для проведення експериментів для будь якої операційної системи, а для побудови програмного середовища вибрати мову програмування Java.

Розроблено графічний інтерфейс комплексної системи управління та перевірки гетерогенного середовища зберігання та обробки даних в розподілених нереляційних базах даних, який дозволяє проводити експерименти по визначенню якості обробки запитів в вузлах гетерогенної розподіленої нереляційної бази даних.

Запропоновані механізми реалізації комплексної системи управління та перевірки гетерогенного середовища зберігання та обробки даних в розподілених нереляційних базах даних. Запропоновані засоби забезпечують можливість перетворення ресурсів із гетерогенних нереляційних розподілених баз даних з різним типом зберігання інформації в відповідний формат для контролю за обробкою запитів в різних вузлах.

Для аналізу ефективності запропонованих засобів моніторингу обробки запитів виконано експериментальні дослідження часу обробки запитів і вибірки даних з моніторингу. У відповідності з отриманими експериментальними даними, з збільшенням кількості запитів за даними моніторингу, зменшується кількість помилкових ідентифікацій подій безпеки, а також помилок ІІ роду.

Проведено аналіз ефективності запропонованих засобів моніторингу обробки запитів, який показав, що, відповідно до отриманих експериментальних даних, із збільшенням кількості запитів за даними моніторингу, зменшується кількість помилкових ідентифікацій подій безпеки до 6,4 %, при цьому імовірність помилок ІІ роду знижується до 1,5 %. Це надає можливість стверджувати, що ефективність функціонування гетерогенних розподілених нереляційних баз даних підвищується.

Розроблено рекомендації для подальшого впровадження запропонованих моделі та методів в різні види підприємницьких структур, які працюють з багатьма нереляційними базами даних.

<span id="_Toc161146431" class="anchor"></span>ВИСНОВКИ

1\. На основі виконаного аналізу існуючих методів та моделей на сьогоднішній день в теорії та практиці експлуатації та побудови гетерогенних розподілених нереляційних баз даних в мережах загострилося протиріччя між необхідністю сталого функціонування гетерогенних розподілених нереляційних базах даних та можливостями існуючих методів та моделей забезпечити обробку запитів в гетерогенних розподілених нереляційних базах даних. В наукових працях основну увагу приділяють задачам проектування гетерогенних розподілених систем обробки даних. Про те, в даних роботах не в достатньо відображені питання моніторингу обробки запитів в вузлах баз даних, відсутні механізми виявлення некоректної роботи вузлів та визначення працездатності вузлів для ефективного виконання основних функцій в умовах динамічної зміни серверів баз даних. Недосконалість та неповнота наукових методів підтримки відповідних параметрів функціонування гетерогенних розподілених баз даних, не дозволяє забезпечити ефективну обробку запитів в гетерогенній розподіленій системі обробки даних, тому сформульована в дисертації наукове завдання є актуальним.

2\. Удосконалено модель моніторингу обробки запитів у гетерогенних розподілених нереляційних базах даних, яка відрізняється від існуючих використанням механізмів на основі застосування матриці обробки запитів. Зазначена модель дозволяє, у випадку виникнення нештатних ситуацій, передати попередження адміністратору серверу моніторингу обробки запитів, прийняти оперативні рішення щодо реагування на порушення безпеки під час обробки даних.

3\. Вперше розроблено метод виявлення некоректної роботи вузлів гетерогенних розподілених нереляційних баз даних на основі застосування дворівневої системи контролю обробки запитів. Наукова новизна даного методу полягає у визначені прихованих несправностей вузла шляхом взаємного обміну запитами між вузлами з урахуванням припущень щодо синхронності гетерогенних розподілених нереляційних баз даних, а також можливості користувачем визначити вузол обробки. Зазначений метод дозволяє здійснювати виявлення випадків некоректної роботи вузлів обробки запитів.

4\. Удосконалено метод визначення працездатності вузлів обробки запитів гетерогенних розподілених нереляційних баз даних, який відрізняється від існуючих способом обробки запитів на основі визначення апостеріорних ймовірностей справного стану вузлів. Зазначений метод дозволяє підвищити ефективність обробки даних.

5\. Вперше розроблено програмне забезпечення комплексної системи управління та перевірки гетерогенного середовища обробки та зберігання даних в нереляційних базах даних, яке базується на розроблених в дисертації моделі моніторингу обробки запитів, методі виявлення некоректної роботи вузлів бази даних та методі визначення працездатності вузлів обробки запитів. Впровадження зазначеного програмного забезпечення дозволяє підвищити ефективність функціонування гетерогенних розподілених нереляційних баз даних.

6\. Реалізація запропонованої в дисертації комплексної системи управління та перевірки гетерогенного середовища обробки та зберігання даних в розподілених нереляційних базах даних дозволяє: проектувати і експлуатувати розподілені бази даних в умовах впливу зовнішніх та внутрішніх факторів; зменшити час обробки запитів за рахунок ефективної побудови розподіленої системи; виконувати зміну параметрів гетерогенної розподіленої системи обробки даних при постійній зміні архітектури комп’ютерної мережі і її характеристик; розробляти гетерогенні розподілені системи з ефективною обробкою запитів при наявних обмеженнях на характеристики системи.

7\. Проведено аналіз ефективності запропонованих засобів моніторингу обробки запитів, який показав, що, відповідно до отриманих експериментальних даних, із збільшенням кількості запитів за даними моніторингу, зменшується кількість помилкових ідентифікацій подій безпеки до 6,4 %, при цьому імовірність помилок ІІ роду знижується до 1,5 %. Це надає можливість стверджувати, що ефективність функціонування гетерогенних розподілених нереляційних баз даних підвищується.

8\. Результати досліджень прийняті до впровадження в Науково-методичному центрі кадрової політики Міністерства оборони України (акт від 16.01.2024 р.), в Конструкторському бюро інформаційних систем КПІ ім. Ігоря Сікорського (акт від 26.12.2023 р.), в ТОВ «Інтехфорвард» (акт від 27.12.2023 р.), в навчальний процес кафедри інженерії програмного забезпечення в енергетиці Національного технічного університету України «Київський політехнічний інститут імені Ігоря Сікорського» при викладанні дисциплін «Бази даних» та «Побудова масштабованих систем обробки даних в реальному часі» для студентів освітнього рівня «Бакалавр» спеціальності 121 «Інженерія програмного забезпечення» денної та заочної форми навчання (акт від 12.02.2024 р.).

9\. Мета досліджень щодо підвищенні ефективності функціонування гетерогенних розподілених нереляційних баз даних шляхом розробки та реалізації моделі та методів обробки даних в розподілених системах досягнута і усі поставлені наукові часткові завдання вирішені повністю. Отримані наукові результати дисертаційних досліджень є внеском в розвиток інформаційних технологій для системного аналізу, дослідження, розроблення архітектури та методів побудови багаторівневих, територіально розосереджених комп’ютерних систем і мереж із розподіленими базами даних і знань, зокрема комерційного призначення.

10\. Перспективними шляхами досліджень є розробка нових і удосконалення існуючих моделей та методів підвищення ефективності функціонування та доступності гетерогенних розподілених нереляційних баз даних для безпечної обробки запитів в умовах дії внутрішніх та зовнішніх дестабілізуючих факторів.

<span id="_Toc161504912" class="anchor"></span>СПИСОК ВИКОРИСТАНИХ ДЖЕРЕЛ

1.  Корнага Я.І., Барабаш А.О. Математична модель моніторингу подій в системі управління розподіленими базами даних на основі сенсорів подій. Інфокомунікаційні та комп’ютерні технології, 2023, № 1 (05). С. 148 – 153. ISSN 2788-5518 <https://doi.org/10.36994/2788-5518-2023-01-05-17> https://visn-icct.uu.edu.ua/index.php/icct/issue/view/5

2.  Корнага Я.І., Барабаш А.О. Порівняльний аналіз методів підвищення швидкості пошуку та запису інформації в базах даних. Науковий журнал «Зв'язок», 2022, № 6 (160). С. 32 – 37. ISSN 2412-9070 <https://doi.org/10.31673/2412-9070.2022.063237> <http://con.dut.edu.ua/index.php/communication/issue/view/164>

3.  Коротков С.С., Барабаш А.О. Проблема семантичних протиріч у великих обсягах даних. Науковий журнал «Зв'язок», 2022, № 3 (157). С. 31 – 34. ISSN 2412-9070 <https://doi.org/10.31673/2412-9070.2022.033133> <http://con.dut.edu.ua/index.php/communication/issue/view/161>

4.  Михеєв Ю.І., Барабаш А.О. Автоматизація процесу розробки спеціального контенту. Науковий журнал «Наукоємні технології», 2018. Том. 38. № 2. С. 187 – 194.  ISSN 2075-0781 <https://doi.org/10.18372/2310-5461.38.12831> <http://jrnl.nau.edu.ua/index.php/SBT/issue/view/655>

5.  Вітюк А.Є., Корнага Я.І., Барабаш А.О. Захоплення невідомих об’єктів мобільним роботом із використанням візуальної інформації. Науковий журнал «Вчені записки Таврійського національного університету імені В.І. Вернадсь­кого. Серія: Технічні науки», 2018. Том 29 (68). № 1. Частина 1. С. 93 – 98. ISSN: 2663-5941 <http://www.tech.vernadskyjournals.in.ua/archive?id=16>

6.  Барабаш А.О., Корнага Я.І., Свинчук О.В. Удосконалений метод обробки запитів в розподілених базах даних на основі механізму кешування індексів. ІІІ міжнародна науково-практична конференція «Інформаційні моделюючі технології, системи та комплекси» (ІМТСК-2021), 27-28 травня 2021 р., м. Черкаси. Черкаський національний університет імені Богдана Хмельницького, 2021. С. 57 – 60.

7.  Корнага Я.І., Барабаш А.О. Методика оцінки часу обробки запитів серверами гетерогенних розподілених баз даних. XXI Всеукраїнська науково-технічна конференція молодих вчених, аспірантів та студентів «Стан, досягнення та перспективи інформаційних систем і технологій», Одеса, 22 – 23 квітня 2021. Одеса, Видавництво ОНАХТ, 2021 р. С. 26 – 28.

8.  Корнага Я., Шиманський М., Барабаш А. Локалізація тексту на зображеннях за допомогою згорткових нейронних мереж. Міжнародна науково-технічна конференція “Security, Fault Tolerance, Intelligence” ICSFTI 2018. м. Київ, 10-12 травня 2018 р. К.: НТУУ «Київський політехнічний інститут імені Ігоря Сікорського». С. 289 – 293.

9.  Барабаш А.О., Коваль М.О. Використанням принципу справедливості під час обслуговування сенсорних мереж. Десята міжнародна науково-практична конференція «Інтегровані інтелектуальні робототехнічні комплекси (ІІРТК-2018)». Збірка тез, м. Київ, 22-23 травня 2018 року. К.: НАУ, 2018. С. 28 – 30.

10. Mikhieiev Y., Barabash A. Automation of the Special Content Development Process. Proceedings of the 10th International Scientific and Technical Conferece on Intellectual Technologies of Linguistic Analysis, 2017, ITLA 2017. Kyiv, Ukraine, October 24-25, 2017. P. 34 – 40.

11. Собчук В., Харкевич Ю., Кальчук І., Барабаш А. Застосування принципу адаптивного накопичення діагностичної інформації для контролю та діагностування інформаційної системи підприємства. "Інформаційні технології та комп’ютерне моделювання"; матеріали статей Міжнародної науково-практичної конференції, м. Івано-Франківськ, 5-10 липня 2021 року. – Івано-Франківськ, С. 46-48.

12. Mukhin V., Kornaga Y., Bazaka Y., Krylov I., Barabash A., Yakovleva A., Mukhin O. The Testing Mechanism for Software and Services Based on Mike Cohn’s Testing Pyramid Modification. The 11th IEEE International Conference on Intelligent Data Acquisition and Advanced Computing Systems: Technology and Applications. September 22-25, 2021 . Cracow, Poland. 2021. P. 53 – 60. (Scopus)

13. Svynchuk О., Barabash A., Laptiev S. and Laptieva T. Modification of Query Processing Methods in Distributed Databases Using Fractal Trees. CEUR Workshop Proceedings, 2021, Vol. 3200. International Scientific and Practical Conference “Information Security and Information Technologies”: Conference Proceedings. 13-19 September 2021. Kharkiv – Odesa, Ukraine. P. 32–37. ISBN 978-966-676-818-9.  (Scopus)

14. Лаптєв О.А., Собчук В.В., Барабаш А.О., Мусієнко А.П. Методи структуризації даних щодо відомих вразливостей програмних та апаратних платформ. «Математика. Інформаційні технології. Освіта. 2022 рік»: збірка тез допов. учасник. ХІ Міжнар. наук.-практ. конф., 3–5 червня 2022 р. Луцьк–Світязь: СНУ імені Лесі Українки, 2022. С. 89-95.

15. Pichkur V., Laptiev O., Polovinkin I., Barabash A., Sobchuk A. and Salanda I. The Method of Managing Man-generated Risks of Critical Infrastructure Systems Based on Ellipsoidal Evaluation. 2022 IEEE 4th International Conference on Advanced Trends in Information Theory (ATIT), 15-17 December 2022, Kyiv, Ukraine, 2022. P. 133 – 137. (Scopus)

16. Мусієнко А.П., Барабаш А.О. Дослідження існуючих засобів підтримки безпечної обробки запитів в гетерогенних розподілених нереляційних базах даних. Перша міжнародна науково-практична конференція «Сучасні аспекти інженерії програмного забезпечення (Modern aspects of Software Engineering)»: Науковий збірник (м. Київ, 14 грудня 2023 р.). Київ: КПІ ім. Ігоря Сікорського, 2023.С. 32 – 33.

17. Абдикеев Н.М., Иванюк В.А., Пащенко Ф.Ф. Антикризисная модель управления мировой банковской системой, формирующейся на основе сетецентрического подхода (на примере кризиса 2008 года). Фундаментальные исследования, 2017. №6. С. 86 – 90.

18. Бальченко І. В. Проблеми розроблення неоднорідних розподілених систем управління базами даних. Технічні науки та технології, 2016. С. 67 – 71.

19. Бальченко І.В. Проблеми розроблення неоднорідних розподілених систем управління базами даних. Технічні науки та технології, 2016. № 2 (4). С.67 – 71.

20. Баришев Ю. В., Каплун В. А., Неуйміна К. В. Дискреційна модель та метод розмежування прав доступу до розподілених інформаційних ресурсів. Наукові праці ВНТУ, 2017. № 2.

21. Білова Т. Г. Проектування розподіленої бази даних системи надання електронних адміністративних послуг, 2019.

22. Білова Т.Г. Архітектура системи представлення електронних адміністративних послуг. АСУ та прибори автоматики, 2018. № 175. С. 49 – 53.

23. Білова, Т. Г. Проектування розподіленої бази даних системи надання електронних адміністративних послуг. АСУ та прилади автоматики, 2019. № 176. С. 49 – 54.

24. Бобрешов-Шишов Д. И., Саяркин Л.А., Шаров И.А. Динамическое управление структурой распределенной базы данных. Молодой ученый. 2015. № 7. С. 51 – 53.

25. Бойко Н. І. Перспективні технології дослідження великих даних у розподілених інформаційних системах. Радіоелектроніка, інформатика, управління, 2017. № 4. С. 66 – 76.

26. Бойченко А.В., Рогожин Д.К., Корнеев Д.Г. Алгоритм динамического масштабирования реляционных баз данных в облачных средах. Прикладная информатика. Технічні науки, 2014. №6(2). С. 461 – 464.

27. Болюбаш Ю. Методи опрацювання Великих даних у федеративному сховищі даних. Вісник Національного університету "Львівська політехніка". Комп’ютерні науки та інформаційні технології. 2016. № 843. С. 356 – 365.

28. Болюбаш Ю. Я. Методи та засоби опрацювання великих даних у системах територіального управління. Науковий вісник Національного лісотехнічного університету: збірник наукових праць, 2016. №26.4 С. 341 – 354.

29. Волк М.О., Грідель Р.М., Саранча С.Н., Гавриш Д.А. Алгоритмічна модель процесу розподіленої імітації для технології аналізу розподілених імітаційних моделей. Східно-Європейський журнал передових технологій. 2013. №. 2(66). С. 32 – 36.

30. Гавриш Д.А., Саранча С.Н., Волк М.А. Метод розподілу задач з врахуванням затрат синхронизації при паралельному моделюванні складних цифрових систем в гетерогенному обчислювальному середовищі. Системи обробки інформації, 2015. Вип. 5 (130). С. 122 – 128.

31. Герасименко О.Ю. Децентралізоване управління ресурсами захищеної розподіленої комп’ютерної системи на базі мережоцентричного підходу. Актуальні задачі та досягнення у галузі кібербезпеки. Матеріали Всеукраїнської науково-практичної конференції 23 – 25 листопада 2016 року, м.Кропивницький. с.92 – 93.

32. Герасименко О.Ю. Програмний комплекс для моделювання роботи GRID-системи із підтримкою захищеної обробки даних. Телекомунікаційні та інформаційні технології: науковий журнал. Київ: Державний університет телекомунікацій. 2016. № 4 (53). с.92 – 98.

33. Дворецький М.Л., Боровльова С.Ю., Давиденко Є.О. [Проектування структури розподіленої БД на базі парсингу SQL-запитів](https://scholar.google.com.ua/scholar?oi=bibs&cluster=15913204290615063158&btnI=1&hl=uk). Наукові праці Чорноморського державного університету імені Петра Могили комплексу Києво-Могилянська академія. Серія: Комп’ютерні технології, 2016.

34. Дворецький М.Л., Дворецька С.В., Давиденко Є.О. Інформаційна технологія визначення корисних даних при оптимізації структури та мінімізації обсягів вузла розподіленої БД. Вісник Черкаського державного технологічного університету, 2019. Випуск 4. С. 26 – 35.

35. Дудун Т. В. Концептуальні основи створення бази даних для геоінформаційного картографування розвитку овузол обробки запитів ітнього комплексу України. Український географічний журнал, 2016. № 3: Картографія, геоінформатика. С. 61 – 67.

36. Дьоміна В. М., Побіженко І. О., Білова Т. Г. [Числові моделі опису реальності, які дозволяють обробку великих обсягів даних за умов зростання їх невизначеності при управлінні регіоном](javascript:void(0)). ДТО вісник ХНАУ, серія "Еекономічні науки", 1 (4), С. 297 – 305.

37.  Захарова О.В. Платформи великих даних. Основні задачі, властивості та переваги. Проблеми програмування. 2019. № 3. С. 101 – 115.

38. Зінов'єва І. [Можливості роботи з великими даними в середовищі MongoDB](javascript:void(0)). Зб. тез XXXVII науково-технічної конференції молодих вчених та спеціалістів. 2017.

39. Зінов'єва І.С., Артемчук В.О. [Сучасні підходи до подальшої еволюції концепції баз даних](javascript:void(0)). III International Scientific and Practical Conference Vancouver, Canada, 2020.

40. Зінов'єва І.С., Ситник Н.В. [Підходи до інтеграції розподілених даних на базі polystore](javascript:void(0)). Зб. тез XXXVІII науково-технічної конференції молодих вчених та спеціалістів, 2017.

41. Зінов'єва І.С., Ситник Н.В. [Тенденції розвитку баз даних та їх вивузол обробки запитів ітлення в овузол обробки запитів ітньому процесі сучасного університету](javascript:void(0)). Інформаційні технології - 2020: VІІ Всеукраїнська науково-практична конференція, 2020.

42. Кобичев Р.В. Гайдаржи В.І. Розподілена система управління обчислювальними експериментами. Журнал Сталий розвиток ХХІ століття: управління, технології, моделі. 2017.

43. Кравченко Ю.В., Нікіфоров С.В. Визначення проблематики теорії функціональної стійкості щодо застосування в комп’ютерних системах. Телекомунікаційні та інформаційні технології. 2014. №1. С.12 – 18.

44. Курдеча В.В., Іщенко І.О., Захарчук А.Г. Метод обробки даних в розподіленій мережі інтернету речей. Національний технічний університет України «Київський політехнічний інститут імені Ігоря Сікорського» «Молодий вчений», 2017. № 10 (50).

45. Кучерявий І.В., Веренько А.І, Романюк О.В. Оптимізація запитів до баз даних. XLIX Науково-технічна конференція факультету інформаційних технологій та комп'ютерної інженерії, 2020.

46. Кушнірецька І.І., Кушнірецька О.І., Берко А.Ю. Аналіз інформаційних ресурсів системи динамічної інтеграції слабоструктурованих даних у Web-середовищі. Вісник Національного університету «Львівська політехніка». 2014. № 805: Інформаційні системи та мережі. С. 162 – 169.

47. Миргородський А.В., Романюк О.В. Особливості адміністрування баз даних в хмарних середовищах. XLIX Науково-технічна конференція факультету інформаційних технологій та комп'ютерної інженерії, секція програмного забезпечення, 2020.

48. Мирошник М.А. Інформаційно-керуючі системи на залізничному транспорті ІКСЗТ. Разработка средств защиты информации в распределенных компьютерных системах и сетях, 2015. №1. С. 18 – 25.

49. Мороз Б. І., Кабак Л. В., Буланий О. П. Методи та моделі реплікації інформації в розподілених базах даних з урахуванням якісно-кількісних характеристик інформації. Вісник Академії митної служби України, 2019. № 2.

50. Павлов Д.Ю., Сіциліцин Ю.О. Використання розподілених баз даних при проектуванні інформаційних систем для автоматизації роботи підприємств. Ukrainian Journal of Educational Studies and Information Technology, 2017. Т.5, Випуск 1. С. 290 – 295.

51. Попов М.О., Артюшин Л.М., Топольницький М.В., Титаренко О.В., Шморгун Ю.В. Інтегрування гетерогенних геопросторових даних на основі теорії вузол обробки запитів ідчень демпстера-шейфера. Математичні машини і системи, 2019. № 3. С.35 – 46.

52. Райтер П.М., Григоришин О.М. Аналіз переваг та недоліків сучасних технологій передачі даних для розподілених систем технічної діагностики і моніторингу. I науково-технічна конференція “НК в контексті асоційованого членства України в ЄС”, 2017. С. 77 – 81.

53. Рубець А.В. Система моніторингу для прогнозування використання ресурсів у розподілених системах. Міжвузівський збірник "Наукові нотатки", 2019. No 68. С. 86 – 90.

54. Рукас К., Злоткевич Г. Балансування узгодженості у розподіленому сховищі даних. Системи управління, навігації та зв’язку. Збірник наукових праць, 2020. Т. 2 (60). С. 95 – 100.

55. Рукас К., Злоткевич Г. Стохастична модель для оцінки САР-гарантій для розподілених баз даних. Сучасні інформаційні системи. 2020. Т. 4, № 2.

56. Семошко О., Половинко І. Метод горизонтального масштабування розподілених обчислень у високонавантажених системах. Збірник наукових праць "Електроніка та інформаційні технології", 2020. № 13.

57. Солдатко, Р. В., Сіциліцин, Ю. О. Використання сучасної технології розподілених баз даних при проектуванні інформаційних систем*.* Ukrainian Journal of Educational Studies and Information Technology, 2017. №5 (1). С. 290 – 295.

58. Спасітєлєва С.О., Бурячок В.Л. Комплексний захист гетерогенних корпоративних сховищ даних. Сучасний захист інформації, 2017. №1.

59. Субач І.Ю., Чаузов О.М., Кучук Н.Г. Метод рішення задачі розподілу інформаційного ресурсу в АСУ спеціального призначення при варіативному розмірі інформаційних блоків. Information Technology and Security. 2016. Vol 4., Iss. 2. P. 269 – 276.

60. Субач І.Ю., Чаузов О.М., Кучук Н.Г. Моделі розподілу інформаційного ресурусу в АСУ спеціального призначення. Information Technology and Security. 2016. Vol 4., Iss. 1. P. 74 – 83.

61. Субач І.Ю., Чаузов О.М. Метод розподілу таблиць реляційної бази даних рівного об’єму та різними ймовірностями звертання до них в інформаційно-обчислювальній мережі АСУ. Військовий інститут телекомунікацій та інформатизації, науково-практична конференція „Пріоритетні напрямки розвитку телекомунікаційних систем та мереж спеціального призначення. Застосування підрозділів, комплексів, засобів зв’язку та автоматизації в операції Об’єднаних сил”, 2018.

62. Тарасюк О.М., Таранова К.П., Горбенко А.В. Аналіз особливостей та класифікація систем управління нереляційними базами даних. Системи управління, навігації та зв'язку, 2017. № 4(44).

63. Чаузов О.М. Математична модель розподілу інформаційного ресурсу між транзакціями до сховищ даних. Системи управління навігації та зв’язку, 2015. Випуск 4(36). С. 100 – 102.

64. Шамко В.Є. Концептуальний підхід до визначення структури системи управління просторово-розподіленої мережецентричної системи зенітного ракетного прикриття (engl.). Наука і техніка Повітряних Сил Збройних Сил України. 2020. № 2(39). С. 70 – 76.

65. Шаховська Н.Б., Болюбаш Ю.Я. Модель Великих даних “сутність-характеристика”. Вісник Національного університету "Львівська політехніка". Серія: Інформаційні системи та мережі: збірник наукових праць. 2015. № 814. С. 186 – 196.

66. Шаховська Н.Б., Болюбаш Ю.Я. Опрацювання невизначеності у великих даних. Радіоелектроніка, інформатика, управління, 2014. № 1. С. 96 – 105.

67. Шаховська Н.Б., Болюбаш Ю.Я., Верес О.М. Організація великих даних у розподіленому середовищі. Наукові праці Донецького національного технічного університету. Серія: Обчислювальна техніка та автоматизація, 2014 № 2. С. 147 – 155.

68. Шаховська Н.Б., Болюбаш Ю.Я. Проектування федеративного сховища даних на основі Великих даних. Матеріали ІІІ Міжнародної науково-практичної конференції Інформаційні управляючі системи та технології (ІУСТ), 2014. С. 293 – 296.

69. Шаховська Н.Б., Болюбаш Ю.Я. Федеративне сховище даних для Big Data. Математика. Інформаційні технології. Овузол обробки запитів іта: матеріали Міжнародної науково-практичної конференції, 2014. С. 87 – 88.

70. Шулима О.В., Шендрик В. В., Шестак М. О. Побудова сховища даних системи підтримки прийняття рішень для проектування розподілених енергетичних систем. Вісник Національного університету "Львівська політехніка". Серія: Інформаційні системи та мережі: збірник наукових праць, 2016. № 854. С 291 – 297.

71. Юхимчук М. С., Осіпенко Г. А., Ковтун В. В., Мазур О. В. Аналіз швидкодії розподілених систем управління базами даних. Automation technological and business processes, 2019.

72. Юхимчук М. С., Осіпенко Г. А., Ковтун В. В., Мазур О. В. Аналіз швидкодії розподілених систем управління базами даних. Автоматизація технологічних і бізнес-процесів, 2014. № 3 (19). С. 59 – 63.

73. Adel A. Sewisy, Ali A. Amer, Hassan I. Abdalla A Novel Query-Driven Clustering-Based Technique for Vertical Fragmentation and Allocation in Distributed Database Systems. International Journal on Semantic Web and Information Systems (IJSWIS), 2017. №13(2). Pages: 28 – 36.

74. Ahmet Ercan Topcu, Aimen Mukhtar Rmis Analysis and evaluation of the riak cluster environment in distributed databases. Computer Standards & Interfaces. Elsevier, 2020. V. №72.

75. Allcock B., Bester J., Bresnahan J., Chervenak A.L., Foster I., Kesselman C., Meder S., Nefedova V., Quesnel D., Tuecke S. Data Management and Transfer in High-Performance Computational Grid Environments \[Online\] Abailable at: http://toolkit.globus.org/alliance/publications/papers/dataMgmt.pdf

76. Andrei Kelarev, Xun Yi, Shahriar Badsha, Xuechao Yang, Leanne Rylands, Jennifer Seberry. A multistage protocol for aggregated queries in distributed cloud databases with privacy protection. Future Generation Computer Systems, 2019. V. 90. P. 368 – 380.

77. Artem K., Holoshchuk R., Kunanets N., Shestakevysh T., Rzheuskyi A. Information Support of Scientific Researches of Virtual Communities on the Platform of Cloud Services. Advances in Intelligent Systems and Computing III. CSIT. Advances in Intelligent Systems and Computing, 2019. V. 871. Springer, Cham.

78. Aydt R., Gunter D., Smith W., Swany M., Taylor V., Tierney B., Wolsk R. A Grid Monitoring Architecture \[Online\] Available at: http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.18.6602&rep=rep1&type=pdf.

79. Bakir C., Hakkoymaz V., Diri B., Güçlü M. Comparisons on Intrusion Detection and Prevention Systems in Distributed Databases. DergiParkBalkan Journal of Electrical and Computer Engineering, 2017. V. 7. P. 446 – 455.

80. Banothu, N., Bhukya, S. and Sharma, K. Big-data: Acid versus base for database transactions. 2016 International Conference on Electrical, Electronics, and Optimization Techniques (ICEEOT), available at https://ieeexplore.ieee.org/document/7755401.

81. Beshley M., Seliuchenko M., Lavriv O., Chervenets V., Kholiavka H., Klymash M. Increasing the efficiency of real-time content delivery by improving the technology of priority assignment and processing of IP traffic. Smart Comput. Rev., 2015. V. 5, no. 2. P. 113 – 121.

82. Bhuyan M.H., Bhattacharyya D.K., Kalita J.K. Network Anomaly Detection: Methods, Systems and Tools. IEEE Communications Surveys & Tutorials. 2014. Vol. 16. No. 1. P.303 – 336.

83. Buhyl B., Huskov P., Lavriv O., Bak R., Luntovskyy A. Maximization of Service Flows Rates as a Solution of Network Capacity Allocation Problem. Internet Things Eng. 2018. Appl., vol. 3, no. 1. P. 110 – 121.

84. Bystrov V.V., Khaliullina D.N., Malygina S.N. Development of the Information Support System Components for Personnel Security Management of the Region. In: Silhavy R. (eds) Applied Informatics and Cybernetics in Intelligent Systems. CSOC. Advances in Intelligent Systems and Computing, 2020. V. 1226. Springer, Cham.

85. Chen, X., Fang, H., Lin, T., Vedantam, R., Gupta, S., Dollár, P., Zitnick, C.L. (2015). Microsoft COCO Captions: Data Collection and Evaluation Server. ArXiv, abs/1504.00325, available at https://arxiv.org/pdf/1504.00325.pdf.

86. Chiba, H., Uchiyama, I. SPANG: a SPARQL client supporting generation and reuse of queries for distributed RDF databases. BMC Bioinformatics, 2017. № 18, P. 93 – 102.

87. Cigdem B., Veli H. A New Scalable and Expandable Access Control Model for Distributed Database Systems in Data Security. Department of Computer Engineering, Yildiz Technical University, 2020.

88. Dinh H.T. A Survey of Mobile Cloud Computing: Architecture, APlications, and AProaches \[Online\] / H. T. Dinh, C. Lee, D. Niyato, P. Wang // Wireless Communications and Mobile Computing. 38p. Available at: https://www.eecis.udel.edu/~cshen/859/papers/survey_MCC.pdf.

89. Diogo, M.; Cabral, B.; Bernardino, J. Consistency Models of NoSQL Databases. Future Internet 2019, P. 43 – 51.

90. Dogar F.R., Karagiannis T., Ballani H., Rowstron A. Decentralized Task-Aware Scheduling for Data Center Networks. SIGCOMM '14: proceedings of the 2014 ACM Conference on Special Interest Group on Data Communication: August 17 – 22, 2014, Chicago, IL, USA. Available at: http://rowstron.azurewebsites.net/Publications/task.pdf.

91. Dudun T. V. Conceptual bases of geoinformation of mapping of development of education complex of Ukraine. Journal announcer of Geodesy and Cartography, 2015. V. 1. 30 – 37.

92. Fernando N., Loke S.W., Rahayu W. Mobile cloud computing: A survey. Future Generation Computer Systems. 2013. Vol. 29. Is.1. P.84 – 106.

93. Fisur M., Horban H., Dvoretskyi M. [Methods of Searching for Association Dependencies in Multidimensional Databases](https://scholar.google.com.ua/scholar?oi=bibs&cluster=5500599527835800123&btnI=1&hl=uk). IEEE 13th International Scientific and Technical Conference on Computer Sciences and Information Technologies (CSIT), 2018.

94. Fisur M., Horban H., Shved A., Dvoretskyi M. [Query parsing in order to optimize distributed DB structure](https://scholar.google.com.ua/scholar?oi=bibs&cluster=13554255574157798111&btnI=1&hl=uk) 9th IEEE International Conference on Intelligent Data Acquisition and Advanced Computing Systems: Technology and Applications (IDAACS), 2017.

95. Gasior J., Seredynsky F.  Decentralized job scheduling in the cloud based on a spatially generalized prisoner’s dilemma game. Int. J. APl. Math. Comput. Sci., 2015. Vol. 25. No. 4. P.737 – 751. DOI: 10.1515/amcs-2015-0053.

96. Gessert, F., Wingerath, W., Friedrich, S. et al. NoSQL database systems: a survey and decision guidance. Comput Sci Res Dev 32. 2017. P 353 –365.

97. Gonen, Y.; Gudes, E.; Kandalov, K. New and Efficient Algorithms for Producing Frequent Itemsets with the Map-Reduce Framework. Algorithms 2018,  P. 194. – 201

98. Gorborukov V., Trygub R., Trygub O. Researching semistructured problems of multicriteria optimization using the software system. Наукові записки НаУКМА. Комп’ютерні науки. 2013. т. 151. C. 79 – 88.

99. Gubbi J., Buyya R., Marusic S., Palaniswami M. Internet of Things (IoT): A vision, architectural elements, and future directions. Future Generation Computer Systems. 2013. Vol. 29. Is.7. P.1645 – 1660.

100. Hasan N. M. Building the electronic documentation system for students of the general authority for applied education and training using distributed databases. Journal of Environmental Science, 2019. A. 3, V. 47. P. 33 – 54.

101. Hegr T., Voznak M., Kozak M., Bohac L. Measurement of Switching Latency in High Data Rate Ethernet Networks. Elektronika ir elektrotechnika, ISSN 1392-1215, Vol. 21, No. 3, 2015. P.74 – 78.

102. Heidarian Z., Movahedinia N., Moghim N., Mahdinia P. Intrusion Detection Based on Normal Traffic Specifications. International Journal of Computer Network and Information Security. 2015. Vol.7. No.9. P.32 – 38. DOI: 10.5815/ijcnis.2015.09.04.

103. Her Q., Malenfant J., Zhang Z., Vilk Y., Young J., Tabano D., Hamilton J., Johnson R., Raebel M., Boudreau D., Toh S. Distributed Regression Analysis Application in Large Distributed Data Networks: Analysis of Precision and Operational Performance JMIR Med Inform. 2020. V. 8(6): e15073.

104. Hu V. C., Kuhn D. R., Ferraiolo D. F. Access Control for Emerging Distributed Systems, in Computer, 2018. V. 51. no. 10. P. 100 – 103.

105. Huang Y., Bessis N., Norrington P., Kuonen P., Hirsbrunner B. Exploring decentralized dynamic scheduling for grids and clouds using the community-aware scheduling algorithm. Future Generation Computer Systems. 2013. Vol. 29. Issue 1. P.402 – 415.

106. Hussain H., Saif Ur Rehman Malik, Hameed A., S. U. Khan, G. Bickler, N. Min-Allah, M. B. Qureshi, L. Zhang, W. Yongji, N. Ghani, J. Kolodziej, A.Y. Zomaya, Ch.-Zh. Xu, P. Balaji, A. Vishnu, F. Pinel, J. E. Pecero, D. Kliazovich, P. Bouvry, H. Li, L. Wang, D. Chen, A. Rayes A survey on resource allocation in high performance distributed computing systems. Parallel Computing. 2013. Vol. 39. Issue 11. P.709 – 736.

107. Hwang K., Bai X., Shi Y., Li M., Chen W.-G., Wu Y. Cloud Performance Modeling with Benchmark Evaluation of Elastic Scaling Strategies. IEEE Transactions on Parallel and Distributed Systems, 2016. Vol. 27. Issue 1. P.130 – 143.

108. Ivanyuk V.A., Abdikeyev N. M., Patshenko F. F., Grineva N.V. Сетецентрические методы управления. Network-Centric Methods Management, Management Science, Financial University under The Government of Russian Federation, 2020. V. 7(1). P. 26 – 34.

109. Jalal-Kamali A., Hossain M.S., Kreinovich V. How to Understand Connections Based on Big Data. Cliques to Flexible Granules / Department of Computer Science, University of Texas at El Paso, El Paso. 2014. T.10. P. 63 – 87.

110. Joshi, S., Ameta, S., Lavania, G. Balanced Load in Distributed System with NoSQL Middleware. International Journal of Emerging Technologies and Innovative Research, V.6(5). P.133 – 137.

111. Kalyaev A., Korovin Ia. Adaptive Multiagent Organization of the Distributed Computations. In AASRI Procedia 6, 2014. p.49 – 58.

112. Khobzaoui A., Yousfate A. Intrusion Detection with Multi-Connected Representation. International Journal of Computer Network and Information Security. 2016. Vol.8. No.1. P.35 – 42. DOI: 10.5815/ijcnis.2016.01.05.

113. Kumar, R., Son, L.H., Jha, S. et al. Spatial data analysis using association rule mining in distributed environments: a privacy prospect. Spat. Inf. Res. 2018. № 26. P. 629 – 638.

114. Liao H.-J., Lin Ch.-H.R., Lin Y.-Ch., Tung K.-Y. Intrusion detection system: A comprehensive review. Journal of Network and Computer APlications. 2013. Vol. 36. Issue 1. P.16 – 24.

115. Lin W. Liang Ch., Wang J.Z., Buyya R. Bandwidth-aware divisible task scheduling for cloud computing. Software-Practice and Experience. 2014. Vol. 44. Issue 2. P.163 – 174.

116. Lotfi, N. Data allocation in distributed database systems: a novel hybrid method based on differential evolution and variable neighborhood search. SN Appl. 2019. Sci. 1, P. 17 – 24.

117. M. Asfand-E-Yar and R. Ali, Semantic Integration of Heterogeneous Databases of Same Domain Using Ontology, in IEEE Access, 2020. V. 8. P. 77903 – 77919.

118. Mace J., Bodik P., Fonseca R., Musuvathi M. Targeted Resource Management in Multi-tenant Distributed Systems. Proceedings of the 12th USENIX Symposium on Networked Systems Design and Implementation (NSDI ’15). May 46, 2015, Oakland, CA, USA. P.589 – 603.

119. Mahon, E.: Transitioning the Enterprise to the Cloud: A Business Approach, Cloudworks Publishing Company, 2015. P.178 – 182.

120. Mansouri Y., Prokhorenko V., Ali Babar M. An automated implementation of hybrid cloud for performance evaluation of distributed databases. Journal of Network and Computer Applications, 2020. P. 167 – 181.

121. Mariela J., Curiel H. [Wireless Grids: Recent Advances in Resource and Job Management](http://www.igi-global.com/chapter/wireless-grids/136563). Handbook of Research on Next Generation Mobile Communication Systems.[Athanasios D. Panagopoulos](http://www.igi-global.com/affiliate/athanasios-d-panagopoulos/286498/), editor. Hershey, PA: Information Science Reference, an imprint of IGI Global, 2016. Chapter 12. P. 293 – 320.

122. Maté A. A et al. Novel Multidimensional Approach to Integrate Big Data in Business Intelligence. Journal of Database Management (JDM). 2015. Vol. 26.2. Р. 14 – 31.

123. Megha Agarwal, Arpita Srivastava. A Short Review on Advanced Database Management Systems. Journal of Advanced Database Management & Systems*.* 2017. 4(1). P. 7 – 13.

124.  Mhedhbi, M. Dynamic Configuration With The Haproxy Runtime API Haproxy Technologies. 2017. HAProxy Technologies, available at https://www.haproxy.com/blog/dynamic-configuration-haproxy-runtime-api.

125. Mikrina E.A., Somovb S.K. The optimal online information backup in the data processing systems based on computer networks redundancy. Information technologies controls, 2016. Issue 5. P. 47 – 56.

126. Mishra M.K., Patel Y.S., Rout Y., Mund G.B. A Survey on Scheduling Heuristics in Grid Computing Environment. I.J. Modern Education and Computer Science, MECS press. 2014. Vol.10. p.57 – 83.

127. Mukhin V.Ye., Shyrochin V.P. Adaptive security mechanisms for the computer networks based on risk analysis. Journal of Qafqaz University, Issue: Mathematics and Computer Science. 2013. Vol. 1. Nо.1. P. 11 – 16.

128. Muliukha V., Ilyashenko A., Zaborovsky V., Lukashin A. Cyber-physical aProach to the network-centric robotics control task. AIP Conference Proceedings, 2016. 4p. doi: 10.1063/1.4965420.

129. Naik S. Ensuring Database and Location Transparency in Multiple Heterogeneous Distributed Databases. In: Patel Z., Gupta S. (eds) Future Internet Technologies and Trends. ICFITT. Lecture Notes of the Institute for Computer Sciences, Social Informatics and Telecommunications Engineering, 2018. V. 220. Springer, Cham.

130. NyquistShannon sampling theorem. https://en.wikipedia.org/wiki/Nyquist%E2%80%93Shannon_sampling_theorem.

131. Pawan K. Ch. Paradigms of Machine Learning and Data Analytics. Handling Priority Inversion in Time-Constrained Distributed Databases, 2020. Pages: 19 

132. Popov S. G., Fridman V. S. Review of methods for dynamic distribution of data in distributed database management systems. SPbSPU Journal. Computer Science. Telecommunication and Control Systems, 2018. V. 11, Issue 4. P. 82 – 107.

133. Qing T., Songcan Ch. Cross-heterogeneous-database age estimation through correlation representation learning Neurocomputing Neurocomputing, 2017. V. 238. P. 286 – 295.

134. Qoua L. Her, Jessica M. Malenfant, Sarah Malek, Yury Vilk, Jessica Young, Lingling Li, Jeffery Brown, Sengwee Toh A Query Workflow Design to Perform Automatable Distributed Regression Analysis in Large Distributed Data Networks EGEMS (Wash DC), 2018. V. 6(1): P. 11 – 18.

135. Qureshi M.B., Dehnavi M.M., N. Min-Allah, M.S. Qureshi, H. Hussain, I. Rentifis, N. Tziritas, T. Loukopoulos, S.U. Khan, Ch.-Zh. Xu, A.Y. Zomaya  Survey on Grid Resource Allocation Mechanisms. Journal of Grid Computing. 2014. Vol. 12. Issue 2. P.399 – 441.

136. Rukkas, K., Zholtkevych, G. Distributed Datastores: Towards Probabilistic Approach for Estimation of Dependability. 11th International Conference on ICT in Education, Research, and Industrial Applications, 2015. V.1356. P.523 – 534.

137. Sanjaya Kumar P., Saswati N. An Efficient Data Replication Algorithm for Distributed Systems. International Journal of Cloud Applications and Computing (IJCAC), 2018. № 8(3). P. 18 – 25.

138. Saran, S.; Singh, P.; Ganeshaiah, K. N.; Padalia, H.; Oberoi, K. Interoperable model for bioresource distributed databases. International Archives of the Photogrammetry, Remote Sensing & Spatial Information Sciences. 2018. Vol. XLII-5. P.791 – 800.

139. Shakhovska N.B., Bolubash Y.J., Veres O.M. Big Data federated repository model. Proceedings of 13th International Conference: The Experience of Designing and Application of CAD Systems in Microelectronics, CADSM, 2015. Р. 382 – 384.

140. Shakhovska N., Bolubash Y. Big Data model «entity and characteristics» Econtechmod / Polish Academy of Sciences, Branch in Lublin. 2015. Vol. 4, No. 2. Р. 51 – 58.

141. Shakhovska N., Bolubash Y. Dataspace architecture and manage its components class projectionю Econtechmod Polish Academy of Sciences, Branch in Lublin. 2015. Vol. 4, №. 1. P. 89 – 97.

142. Shakhovska N., Veres O., Bolubash Y., Liliana B Data Space architecture for Big Data managering. Proceedings of the International Conference on Computer Sciences and Information Technologies, 2015. Р. 184 – 187.

143. Shakhovska N., Veres О., Bolubash Y., Bychkovska L. Big Data information technology and data space architecture. Sensors & Transducers. 2015. Vol. 195, Is.12. P. 69 – 77.

144. Shikha M., Parul A., Prakhar Sh., Jharna B. Differential bond energy algorithm for optimal vertical fragmentation of distributed databases. Journal of King Saud University - Computer and Information Sciences, 2018.

145. Shruti Jadon, Rama Shankar Y. Scheduling of Aperiodic Tasks on Multicore Systems. Handling Priority Inversion in Time-Constrained Distributed Databases, 2020. P. 22 – 34.

146. Shuai Zh., Quan Q. Ontology based heterogeneous materials database integration and semantic query. AIP Advances, 2017. V. 7. P. 105 – 125.

147. Shyshatskyi A., Sova O., Zhuravskyi Yu., Nalapko O., Sokil Yu., Ryndin Yu. Аналіз підходів впливу засобів радіоелектронного подавлення на мережецентричну систему управління. Системи управління, навігації та зв’язку. Збірник наукових праць. Полтава: ПНТУ, 2019. Т. 6 (58). С. 129 – 139.

148. Sytnyk N., Zinovieva I. [Evolution of the concept of database organization in the context of the digitalization of society](javascript:void(0)). ДВНЗ «Київський національний економічний університет імені Вадима Гетьмана».

149. Tarvainen P. Survey of the survivability of it systems \[Online\]  VTT Technical Research Center of Finland. 8p. Available at: http://virtual.vtt.fi/virtual/proj1/projects/merlin/pub/survey_of_the_survivability_of_it_systems.pdf

150. Yalamanchili S. Switching Techniques \[Online\] / Available at: http://users.ece.gatech.edu/~sudha/academic/class/Networks/Lectures/3%20-%20Switching%20Techniques/papers/paper.switching.pdf

151. Zaki N., Tennakoon C. BioCarian: search engine for exploratory searches in heterogeneous biological databases. BMC Bioinformatics, 2017. №18. P. 435 – 451.

152. Zatuliveter Yu. S., Fishchenko E. A. Problems of programmability, security and reliability of distributed computing and network-centric control. Part 2: The approach to general solution, 2016. Issue 4. P. 58 – 69.

153. Zheng K., Gu D., Fang F. et al. Data storage optimization strategy in distributed column-oriented database by considering spatial adjacency. Cluster Comput 20, 2017. P. 2833 – 2844.

154. Zygiaris, S. Distributed DataBases and Concurrency Control. Database Management Systems, Emerald Publishing Limited, 2018. P. 265 – 287.

<span id="_Toc161504913" class="anchor"></span>ДОДАТОК А

<img src="media/image501.jpeg" style="width:6.92537in;height:8.67127in" />

<img src="media/image502.jpeg" style="width:6.86567in;height:8.86575in" />

<img src="media/image503.jpeg" style="width:6.79419in;height:9.47761in" />

<img src="media/image504.jpeg" style="width:6.69375in;height:9.09444in" />

<img src="media/image505.jpeg" style="width:6.05903in;height:9.35821in" />

<span id="_Toc161504914" class="anchor"></span>ДОДАТОК Б

**СПИСОК ПУБЛІКАЦІЙ ЗДОБУВАЧА**

*Наукові праці, в яких опубліковані основні наукові результати дисертації:*

1\. Корнага Я.І., Барабаш А.О. Математична модель моніторингу подій в системі управління розподіленими базами даних на основі сенсорів подій. Інфокомунікаційні та компютерні технології, 2023, № 1 (05). С. 148 – 153. ISSN 2788-5518

<https://doi.org/10.36994/2788-5518-2023-01-05-17>

https://visn-icct.uu.edu.ua/index.php/icct/issue/view/5

2\. Корнага Я.І., Барабаш А.О. Порівняльний аналіз методів підвищення швидкості пошуку та запису інформації в базах даних. Науковий журнал «Зв'язок», 2022, № 6 (160). С. 32 – 37. ISSN 2412-9070

<https://doi.org/10>.31673/2412-9070.2022.063237

<http://con.dut.edu.ua/index.php/communication/issue/view/164>

3\. Коротков С.С., Барабаш А.О. Проблема семантичних протиріч у великих обсягах даних. Науковий журнал «Зв'язок», 2022, № 3 (157). С. 31 – 34. ISSN 2412-9070

<https://doi.org/10.31673/2412-9070.2022.033133>

<http://con.dut.edu.ua/index.php/communication/issue/view/161>

4\. Михеєв Ю.І., Барабаш А.О. Автоматизація процесу розробки спеціального контенту. Науковий журнал «Наукоємні технології», 2018. Том. 38. № 2. С. 187 – 194.  ISSN 2075-0781 <https://doi.org/10.18372/2310-5461.38.12831>

<http://jrnl.nau.edu.ua/index.php/SBT/issue/view/655>

5\. Вітюк А.Є., Корнага Я.І., Барабаш А.О. Захоплення невідомих об’єктів мобільним роботом із використанням візуальної інформації. Науковий журнал «Вчені записки Таврійського національного університету імені В.І. Вернадсь­кого. Серія: Технічні науки», 2018. Том 29 (68). № 1. Частина 1. С. 93 – 98. ISSN: 2663-5941

<http://www.tech.vernadskyjournals.in.ua/archive?id=16>

*Наукові праці, які засвідчують апробацію матеріалів дисертації*:

6\. Барабаш А.О., Корнага Я.І., Синчук О.В. Удосконалений метод обробки запитів в розподілених базах даних на основі механізму кешування індексів. ІІІ міжнародна науково-практична конференція «Інформаційні моделюючі технології, системи та комплекси» (ІМТСК-2021), 27-28 травня 2021 р., м. Черкаси. Черкаський національний університет імені Богдана Хмельницького, 2021. С. 57 – 60.

<https://fotius.cdu.edu.ua/wp-content/uploads/2021/05/BOOK_IMTCK_2021.pdf>

7\. Корнага Я.І., Барабаш А.О. Методика оцінки часу обробки запитів серверами гетерогенних розподілених баз даних. XXI Всеукраїнська науково-технічна конференція молодих вчених, аспірантів та студентів «Стан, досягнення та перспективи інформаційних систем і технологій», Одеса, 22 – 23 квітня 2021. Одеса, Видавництво ОНАХТ, 2021 р. С. 26 – 28.

8\. Корнага Я., Шиманський М., Барабаш А. Локалізація тексту на зображеннях за допомогою згорткових нейронних мереж. Міжнародна науково-технічна конференція “Security, Fault Tolerance, Intelligence” ICSFTI 2018. м. Київ, 10-12 травня 2018 р. К.: НТУУ «Київський політехнічний інститут імені Ігоря Сікорського». С. 289 – 293.

<https://comsys.kpi.ua/icsfti2018>

9\. Барабаш А.О., Коваль М.О. Використання принципу справедливості під час обслуговування сенсорних мереж. Десята міжнародна науково-практична конференція «Інтегровані інтелектуальні робототехнічні комплекси (ІІРТК-2018)». Збірка тез, м. Київ, 22-23 травня 2018 року. К.: НАУ, 2018. С. 28 – 30.

10\. Mikhieiev Y., Barabash A. Automation of the Special Content Development Process. Proceedings of the 10th International Scientific and Technical Conference on Intellectual Technologies of Linguistic Analysis, 2017, ITLA 2017. Kyiv, Ukraine, October 24-25, 2017. P. 34 – 40.

<http://ccs.nau.edu.ua/ru/lingvo>

11\. Собчук В., Харкевич Ю., Кальчук І., Барабаш А. Застосування принципу адаптивного накопичення діагностичної інформації для контролю та діагностування інформаційної системи підприємства. "Інформаційні технології та комп’ютерне моделювання"; матеріали статей Міжнародної науково-практичної конференції, м. Івано-Франківськ, 5-10 липня 2021 року. – Івано-Франківськ, С. 46-48.

12\. Mukhin V., Kornaga Y., Bazaka Y., Krylov I., Barabash A., Yakovleva A., Mukhin O. The Testing Mechanism for Software and Services Based on Mike Cohn’s Testing Pyramid Modification. The 11th IEEE International Conference on Intelligent Data Acquisition and Advanced Computing Systems: Technology and Applications. September 22-25, 2021 . Cracow, Poland. 2021. P. 53 – 60. **(Scopus)**

13\. Svynchuk О., Barabash A., Laptiev S. and Laptieva T. Modification of Query Processing Methods in Distributed Databases Using Fractal Trees. CEUR Workshop Proceedings, 2021, Vol. 3200. International Scientific and Practical Conference “Information Security and Information Technologies”: Conference Proceedings. 13-19 September 2021. Kharkiv – Odesa, Ukraine. P. 32–37. ISBN 978-966-676-818-9.  **(Scopus)**

<https://drforum.science/conference_collections/>

14\. Лаптєв О.А., Собчук В.В., Барабаш А.О., Мусієнко А.П. Методи структуризації даних щодо відомих вразливостей програмних та апаратних платформ. «Математика. Інформаційні технології. Освіта. 2022 рік»: збірка тез допов. учасник. ХІ Міжнар. наук.-практ. конф., 3–5 червня 2022 р. Луцьк–Світязь: СНУ імені Лесі Українки, 2022. С. 89-95.

15\. Pichkur V., Laptiev O., Polovinkin I., Barabash A., Sobchuk A. and Salanda I. The Method of Managing Man-generated Risks of Critical Infrastructure Systems Based on Ellipsoidal Evaluation. 2022 IEEE 4th International Conference on Advanced Trends in Information Theory (ATIT), 15-17 December 2022, Kyiv, Ukraine, 2022. P. 133 – 137. **(Scopus)**

https://doi.org/10.1109/ATIT58178.2022.10024244.

16\. Мусієнко А.П., Барабаш А.О. Дослідження існуючих засобів підтримки безпечної обробки запитів в гетерогенних розподілених нереляційних базах даних. Перша міжнародна науково-практична конференція «Сучасні аспекти інженерії програмного забезпечення (Modern aspects of Software Engineering)»: Науковий збірник (м. Київ, 14 грудня 2023 р.). Київ: КПІ ім. Ігоря Сікорського, 2023.С. 32 – 33.

<https://bit.ly/3ToOyA2>

**Відомості про апробацію результатів дисертації**

1.  ІІІ міжнародна науково-практична конференція «Інформаційні моделюючі технології, системи та комплекси» (ІМТСК-2021), (27 – 28 травня 2021, Черкаси); Форма участі – дистанційно.

2.  XXI Всеукраїнська науково-технічна конференція молодих вчених, аспірантів та студентів «Стан, досягнення та перспективи інформаційних систем і технологій», (22 – 23 квітня 2021, Одеса); Форма участі – дистанційно.

3.  Міжнародна науково-технічна конференція “Security, Fault Tolerance, Intelligence” ICSFTI (10-12 травня 2018, Київ); Форма участі – дистанційно.

4.  Десята міжнародна науково-практична конференція «Інтегровані інтелектуальні робототехнічні комплекси (ІІРТК-2018)». 22-23 травня 2018, Київ); Форма участі – дистанційно.

5.  10th International Scientific and Technical Conference on Intellectual Technologies of Linguistic Analysis, 2017, ITLA (October 24-25, 2017, Kyiv); Форма участі – дистанційно.

6.  Міжнародна науково-практична конференція "Інформаційні технології та комп’ютерне моделювання" (5-10 липня 2021, Івано-Франківськ); Форма участі – дистанційно.

7.  11th IEEE International Conference on Intelligent Data Acquisition and Advanced Computing Systems: Technology and Applications. (September 22-25, 2021. Cracow, Poland); Форма участі – дистанційно.

8.  CEUR Workshop Proceedings, 2021, Vol. 3200. International Scientific and Practical Conference “Information Security and Information Technologies”: Conference Proceedings. (13-19 September 2021, Kharkiv – Odesa); Форма участі – дистанційно.

9.  ХІ Міжнародна науково-практична конференція «Математика. Інформаційні технології. Освіта» (3–5 червня 2022, Луцьк–Світязь); Форма участі – дистанційно.

10. IEEE 4th International Conference on Advanced Trends in Information Theory (ATIT), (15-17 December 2022, Kyiv); Форма участі – дистанційно.

11. Перша міжнародна науково-практична конференція «Сучасні аспекти інженерії програмного забезпечення (Modern aspects of Software Engineering)»: (14 грудня 2023, Київ). Форма участі – дистанційно.
