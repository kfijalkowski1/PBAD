---
name: Paper results sections
overview: Napisać sekcje Wyniki, Dyskusja, Ograniczenia i Wnioski w 00-intro.tex po polsku; 4 wykresy strukturalne (2 zagregowane + 2 per-app); bez ARLO; niższe zagregowane PDF-y; kompilacja przez make w tex/.
todos:
  - id: remove-arlo
    content: Usunąć ARLO z Metodologii w 00-intro.tex (3 metody, poprawione listy)
    status: completed
  - id: shrink-mean-charts
    content: Dodać PAPER_HEIGHT_METHOD < PAPER_HEIGHT; re-eksport zagregowanych PDF-ów (skala bez zmian)
    status: completed
  - id: write-wyniki
    content: Napisać \section{Wyniki} (≤½ kolumny tekstu) + 4 figury strukturalne
    status: completed
  - id: write-discussion-conclusion
    content: Napisać Dyskusję (≤½ kolumny), Ograniczenia, Wnioski
    status: completed
  - id: verify-cleanup
    content: Usunąć arlo z SHORT_LABELS; grep brak ARLO; make w tex/
    status: completed
isProject: false
---

# Sekcje Wyniki–Wnioski

## Zakres i korekty wstępne

Eksperyment: **5 aplikacji** (eShop, Pitstop, EventTicketSystem, HotelPricingSystem, Marketplace) × **3 metody** (PPS, PP, ADD). **ARLO — bez wzmianek nigdzie:**

- [`tex/tex/00-intro.tex`](tex/tex/00-intro.tex): skasować `\paragraph{ARLO}`, „cztery” → **trzy metody**, poprawić procedurę syntezy (~87)
- [`code/notebooks/experiment_results.ipynb`](code/notebooks/experiment_results.ipynb): usunąć `"arlo": "ARLO"` z `SHORT_LABELS`

## Dane do wplecenia w tekst

**Metryki strukturalne** (niższe = lepiej), średnia z 5 aplikacji — ranking **PPS > PP > ADD**:

| Metryka | ADD | PP | PPS | Poprawa PPS wzgl. ADD |
|---------|-----|-----|-----|------------------------|
| Dependency degree | 1,382 | 1,243 | 1,176 | **~15%** |
| Change Impact | 0,246 | 0,226 | 0,202 | | **~18%** |

W tekście podać wyłącznie **średnie procenty (~15–18%)** — **bez** rozbicia per-app (szum).

**3/5 aplikacji** zachowuje porządek PPS > PP > ADD (per metryka strukturalna); Marketplace odwraca ranking; Pitstop/ETS — rozbieżność między metrykami. Krótko, bez tabeli.

**F1:** brak wyraźnego zwycięzcy (node F1: rozpiętość ~0,05 między metodami) — **różnice uznane za szum**; tylko w tekście, bez wykresów F1.

**Jakościowo:** odtworzenie gateway/brokera; dekompozycja odpowiedzialności między mikroserwisami zależy od metody.

## Wykresy

PDF-y w [`tex/assets/`](tex/assets/). **4 figury — wyłącznie metryki strukturalne:**

| Plik | Rola |
|------|------|
| `dependency_degree_by_method_mean` | ranking metod (zagregowany) |
| `change_impact_by_method_mean` | potwierdzenie (zagregowany) |
| `dependency_degree_by_app` | rozkład per aplikacja |
| `change_impact_by_app` | rozkład per aplikacja |

Wykresy F1 **pominięte**. Per-app można usunąć później, jeśli braknie miejsca.

### Niższe zagregowane wykresy (oszczędność miejsca)

W [`code/notebooks/_experiment_viz.py`](code/notebooks/_experiment_viz.py):

- `PAPER_HEIGHT = 2.7` — bez zmian (by-app)
- nowe `PAPER_HEIGHT_METHOD ≈ 2.0` — tylko `plot_paper_by_method_mean`
- **Skala osi bez zmian** (te same dane, węższy bbox figury)
- Re-eksport: `uv run python -m notebooks.export_paper_charts`

W LaTeX wykresy zagregowane można dodatkowo wcisnąć przez `\includegraphics[width=\columnwidth]` (naturalnie niższe po zmianie proporcji PDF).

## Struktura sekcji (polski, styl jak w dokumencie)

**Bez** `\todo`, tabel, rozwlekłości. **Nie wspominać:** jednego przebiegu, wyliczania metryk w Wynikach, per-app procentów, ARLO.

### `\section{Wyniki}` — **≤½ kolumny tekstu** + 4 figury

Zwięzły akapit: ranking strukturalny PPS > PP > ADD (~15–18%), 3/5 aplikacji; F1 — brak sygnału; gateway/broker vs. dekompozycja usług.

Figury: 2× mean, 2× by-app (kolejność: mean dep → mean ACI → by-app dep → by-app ACI, lub mean obok siebie w tekście a by-app pod spodem).

### `\section{Dyskusja}` — **≤½ kolumny tekstu**

- Metryki strukturalne jako heurystyka oceny architektur SI
- Dlaczego F1 nie rozstrzyga (normalizacja, równoważne topologie)
- Interpretacja przewagi PPS
- Ekspercka ocena konieczna — SI nie zastąpi architekta

### `\section{Ograniczenia badania}` — krótko

- Mała próba aplikacji (5 systemów)
- Niedobór dużych, dobrze udokumentowanych benchmarków (wymagania funkcjonalne i niefunkcjonalne)
- Metryki grafowe ≠ jakość biznesowa

**Nie wspominać:** pojedynczego przebiegu, braku analizy statystycznej, F1 względem jednej referencji.

### `\section{Wnioski}` — 3–4 zdania

Porównywalność metod; potrzeba lepszych benchmarków i oceny eksperckiej; ograniczona rola pełnej automatyzacji.

## Pliki

| Plik | Zmiana |
|------|--------|
| [`tex/tex/00-intro.tex`](tex/tex/00-intro.tex) | ARLO out; 4 sekcje; 4 `\figure` |
| [`code/notebooks/_experiment_viz.py`](code/notebooks/_experiment_viz.py) | `PAPER_HEIGHT_METHOD`; re-eksport mean PDF |
| [`code/notebooks/experiment_results.ipynb`](code/notebooks/experiment_results.ipynb) | ARLO z etykiet |

## Weryfikacja

- `grep -i arlo tex/tex/00-intro.tex` → brak
- `cd tex && make` — PDF buduje się, figury wczytane
- Liczby zgodne z `groupby('method').mean()` na danych final
