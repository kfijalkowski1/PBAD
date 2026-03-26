**co chcemy się dowiedzieć**
jak najlepiej generować architekturę
- obiektywne ustalenie która metoda już istniejąca w literaturze jest najlepsza
po co?
- korporacje używają do tego LLMy więc może to być przydatne
- wszystkie metody ewaluowane w architekturze są oceniane arbitralnie, bez porównania między sobą, sprawdzimy różne scenariusze
**hipoteza badawcza**
istnieją mierzalne różnice między metodami generowania architektury pod względem jakości wyników w zależności od użytej metody
**metoda**
narzędzia badawcze
- używamy tych metod co wymieniliśmy w main.pdf (efektywnie też materiały)
- narzędzia GenAI: Claude Code, Perplexity, ChatGPT (efektywnie zasoby)
- metoda oceny: metryki z main.pdf, manualna walidacja z istniejącymi punktami odniesienia w istniejących projektach, porównanie z architekturą referencyjną, sprawdzenie które wymagania są spełnione w jakim stopniu przez wygenerowaną architekturę
- dane: przykładowe projekty wymienionistnieją istotne różnice między metodami generowania architektury pod względem jakości wyników w zależności od użytej metodye w main.pdf
**zmienne zależne/niezależne**
niezależne
- metoda generowania architektury
- aplikacja sprawdzana, co ciągnie za sobą inne wymagania
- model
zależne
- metody oceny - coupling (metryka obiektywna), stopień spełnienia wymagań, stopień zgodności z architekturą referencyjną
**oczekiwane wyniki**
pełne porównanie sprawdzanych metod
**zadania do wykonania i alokacja**
- zrozumienie jak działają brane pod uwagę metody generowania architektury
- zrobienie eksperymentów
- podsumowanie w artykule, zebranie wejść i wyjść, wszystko udokumentować
**braki, trudności, ryzyka**
skończenie się tokenów, zależność od zewnętrznych API podczas eksperymentów
LLMy mogą nie chcieć współpracować