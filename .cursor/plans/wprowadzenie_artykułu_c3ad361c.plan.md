---
name: Wprowadzenie artykułu
overview: "Zastąpić angielski szkic w `\\section{Wprowadzenie}` spójnym tekstem po polsku: kontekst GenAI → problem porównywalności → cel i pytania badawcze → hipoteza, bez wkładu pracy i bez powielania „Stanu badań”."
todos:
  - id: write-intro
    content: "Zastąpić itemize (linie 3–10) pięcioma akapitami: kontekst, problem, luka, cel+RQ, hipoteza"
    status: completed
  - id: verify-build
    content: Uruchomić `make` w tex/ i sprawdzić brak duplikacji ze Stanem badań
    status: completed
isProject: false
---

# Wprowadzenie artykułu

## Zakres

Jedyna edycja: [`tex/tex/00-intro.tex`](tex/tex/00-intro.tex), linie 3–10 — usunąć angielski `itemize` i wstawić gotowy tekst wprowadzenia (~¾–1 kolumny w układzie dwukolumnowym).

Bez akapitu „Wkład pracy” (zgodnie z wyborem użytkownika). Bez szczegółów metodologii, wyników ani nazw aplikacji — to zostaje w kolejnych sekcjach.

## Struktura tekstu (5 akapitów)

### 1. Kontekst — „wiemy, jak generować”

- Duże modele językowe coraz skuteczniej wspierają **syntezę architektury** z opisów wymagań, zwłaszcza w stylu mikroserwisowym.
- Krótkie wsparcie literaturą (1–2 cytowania, bez rozwijania): [`schmidSoftwareArchitectureMeets2025`](tex/bibliography.bib), ewentualnie [`carvalhoUsefulnessAutomaticallyGenerated2024`](tex/bibliography.bib) lub [`pereiraGeneratingMicroserviceArchitectures2025`](tex/bibliography.bib).
- Ton jak w istniejącym [`Stan badań`](tex/tex/00-intro.tex): zwięzły, akademicki, po polsku.

### 2. Problem — „ale która technika jest najlepsza?”

- Postęp w **generowaniu** nie idzie w parze z postępem w **porównywalnej ocenie**.
- Otwarte pytanie: jak obiektywnie ustalić, które techniki syntezy dają lepszą architekturę?

### 3. Lukа w literaturze — „ewaluacja arbitralna”

- Metody opisane w publikacjach są oceniane w **heterogenicznych** ustawieniach: inne systemy testowe, inne modele, ocena ekspercka, często **interakcja z użytkownikiem** w pętli.
- Skutek: wyniki poszczególnych prac **nie dają się zestawić** i nie wskazują jednoznacznego lidera.
- Tu tylko streszczenie — bez powielania akapitów z `\subsection{Ewaluacja architektur generowanych przez SI}`; ewentualnie jedno odwołanie do [`schmidSoftwareArchitectureMeets2025`](tex/bibliography.bib).

### 4. Cel i pytania badawcze

**Cel** (sformułowanie z briefu użytkownika):

> Opracować zadanie (protokół) generowania architektury mikroserwisowej z wymagań tekstowych, które umożliwia **mierzenie jakości wyników** w sposób powtarzalny i porównywalny między metodami.

**Pytania badawcze** — osobny akapit lub krótka lista `enumerate`, przetłumaczone z szkicu (linie 7–8):

1. Jak metody syntezy architektury o **minimalnej interakcji użytkownika** radzą sobie na **wspólnych benchmarkach** mikroserwisowych?
2. W jaki sposób można **wiarygodnie porównywać** metody syntezy architektury?

Słownictwo spójne z metodologią: „minimalna interakcja”, „wymagania → graf usług”, „mikroserwisy” — bez wymieniania ADD/PP/PPS (to dopiero w `\section{Metodologia}`).

### 5. Hipoteza

Jedno zdanie (z briefu):

> **Hipoteza:** istnieją **mierzalne różnice** jakości wyników generowania architektury w zależności od zastosowanej metody syntezy.

Bez zapowiadania, która metoda wygrywa — hipoteza jest ex ante, wyniki w `\section{Wyniki}`.

## Styl i spójność

| Aspekt | Wytyczna |
|--------|----------|
| Język | polski, jak reszta [`00-intro.tex`](tex/tex/00-intro.tex) |
| Długość | zwięzła; intro motywuje, nie duplikuje „Stanu badań” |
| Liczby / wyniki | brak |
| ARLO | brak wzmianek |
| Format RQ | `enumerate` lub `\begin{enumerate}` — spójne z `\usepackage{enumitem}` w [`sprawko.cls`](tex/sprawko.cls) |
| Przejście | ostatnie zdanie może zapowiadać strukturę artykułu jednym zdaniem (*„W kolejnych sekcjach …”*) — bez listy wkładów |

## Weryfikacja

Po edycji: `cd tex && make` — brak błędów LaTeX, brak angielskich placeholderów w `\section{Wprowadzenie}`.
