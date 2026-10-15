# Implementácia algoritmov NN, B&B a ACO – podklady do tímového reportu

**Predmet:** Moderné prístupy v optimalizácii  
**Úloha:** Traveling Salesman Problem – turistické lokality (Chattogram, Bangladéš)  
**Zdroj:** M. R. Hossen et al., *Optimal algorithm of the traveling salesman problem for tourist location selection*, International Journal for Simulation and Multidisciplinary Design Optimization, 16, 11 (2025), dokument v priečinku `Article/`.

## Spoločný model a dáta

- 8 uzlov podľa `cfg.city_names`; východiskový aj konečný bod je `Chattogram` (index `0`).
- Použité sú existujúce matice `data.distance_matrix` (km), `time_matrix` (min), `cost_matrix` (BDT).
- Hodnotenie trasy používa presne rovnaký skalárny cieľ ako existujúci kód tímu:

  `F(tour) = 0.3 * sum(distance) + 0.4 * sum(time) + 0.3 * sum(cost)`.

- Hodnoty nie sú normalizované. Jednotky sú rozdielne; to znamená, že významný vplyv na číslo `Overall Score` má zložka nákladov v BDT. **Ide o zachovanie tímovej implementácie, nie všeobecne odporúčaný spôsob normalizácie cieľov.**
- Matice obsahujú rôzne hodnoty pre opačné smery na niektorých hranách. Z tohto dôvodu je implementácia riešená ako smerovaný (asymetrický) TSP. Nevynucujeme symetriu, ani neopravujeme pôvodné údaje.
- Zmena ceny paliva mení `cost_matrix` a zmení teda aj účelovú funkciu bez úprav algoritmov.

## 1. Nearest Neighbor (NN)

**Súbor:** `nearest_neighbor.py`, funkcia `nearest_neighbor_tsp`.

Deterministická heuristika z Algoritmu 5 článku. Od Chattogramu iteratívne vyberie ešte nenavštívený uzol s najmenšou **vzdialenosťou**, pri zhode rozhodne menší index. Po navštívení všetkých bodov sa vráti domov. Výstupom je úplná uzavretá trasa. Zložitosť približne `O(n²)` pri naivnom výbere najbližšieho bodu.

Rozdiel oproti `greedy_algorithm.py`: Greedy pri výbere suseda využíva vážený súčet vzdialenosti, času a ceny; NN využíva výhradne vzdialenosť. Pri súčasných údajoch oba algoritmy náhodou vrátia rovnakú trasu, čo však neznamená, že sú algoritmicky totožné.

## 2. Branch and Bound (B&B)

**Súbor:** `branch_and_bound.py`, funkcia `branch_and_bound_tsp`.

Exaktná metóda podľa princípu Algoritmu 3 článku. Uzol vyhľadávacieho stromu reprezentuje rozpracovanú trasu. Vetvenie pridáva nenavštívený uzol; horná hranica sa inicializuje pomocou realizovateľnej váženej greedy trasy. Dolná hranica zostávajúcej časti je maximum z dvoch prípustných relaxácií:

1. Súčet najlacnejších dovolených **odchádzajúcich** hrán zo súčasného a zostávajúcich uzlov.
2. Súčet najlacnejších dovolených **prichádzajúcich** hrán do zostávajúcich uzlov a počiatočného uzla.

Keď `partial_cost + lower_bound >= best_known`, vetva sa oreže. Každá relaxácia ignoruje niektoré väzby Hamiltonovského cyklu, preto nemôže nadhodnotiť minimum doplnenia. Výsledkom je **globálne optimum** pre definovanú váženú účelovú funkciu. V najhoršom prípade je zložitosť stále faktoriálna/exponenciálna; pre rozsiahle úlohy sa nemusí hodiť.

## 3. Ant Colony Optimization (ACO)

**Súbor:** `ant_colony.py`, funkcia `ant_colony_tsp`.

Stochastická aproximácia inšpirovaná Algoritmom 7 článku. Každý mravec zostaví náhodnú uskutočniteľnú trasu. V ďalšom kroku volí uzol s pravdepodobnosťou úmernou:

`pheromone[current, next]^alpha * (1 / weighted_edge_cost)^beta`.

Po kompletizácii trás sa feromón odparí a na navštívené **orientované** hrany sa pridá `Q / route_score` pre každého mravca. Udržujeme najlepšiu doposiaľ nájdenú trasu. Podmienkou ukončenia je pevný počet iterácií. Nie je garantované globálne optimum.

**Použité hyperparametre:** 30 mravcov; 100 iterácií; `alpha=1`, `beta=3`, `evaporation=0.5`, `Q=100`, úvodný feromón `1.0`. Ide o naše explicitné implementačné rozhodnutia: článok opisuje všeobecné vytváranie trás a aktualizácie feromónu, ale nešpecifikuje všetky uvedené hodnoty pre reprodukciu presného variantu.

**Reprodukcia experimentu:** 10 behov s hodnotami seed 40–49; nezávislý `numpy.random.default_rng(seed)` pre každý beh. Výstupné CSV obsahuje najlepšie nájdené riešenie a priemerný čas z 10 behov, tak ako skripty spolužiakov.

## Overenie a pozorované výsledky

Nasledujúca tabuľka je výsledkom spustenia skriptov na údajoch z `data.py` v tomto balíku (výpočtový čas je závislý od počítača a treba ho zmerať znovu v cieľovom prostredí).

| Metóda | Najlepšie `Overall Score` | Vzdialenosť (km) | Čas (min) | Náklady (BDT) |
| --- | ---: | ---: | ---: | ---: |
| Nearest Neighbor | 4213.9620 | 854.8 | 1380 | 11351.74 |
| Branch and Bound | **4109.2530** | **835.4** | **1326** | **11094.11** |
| Ant Colony Optimization | **4109.2530** (najlepší z 10 behov) | **835.4** | **1326** | **11094.11** |

**Optimálna trasa podľa B&B:** `0 → 4 → 3 → 2 → 1 → 5 → 6 → 7 → 0`.

B&B sa nezávisle overilo úplným brute-force výpočtom všetkých `7! = 5040` možných permutácií zostávajúcich miest s fixovaným štartom v uzle 0. Testy obsahujú aj náhodné asymetrické matice a porovnanie s brute force na malých vstupoch.

### Dôležité obmedzenia a poznámky pre report

- S aktuálnymi ôsmimi lokalitami je možné exaktné riešenie v krátkom čase; z toho nemožno usudzovať škálovateľnosť na stovky miest.
- Algoritmus ACO môže pri iných seed/hyperparametroch skončiť s horším výsledkom; nestačí porovnávať iba najlepší pokus. Pre férovejšiu analýzu experimentov vyhodnoťte priemer, medián, smerodajnú odchýlku, minimum a maximum všetkých 10 behov; tieto štatistiky sa vypisujú do konzoly.
- Tímový CSV formát `algorithm_results.csv` má iba *best score* a *mean execution time*, nie všetky rozptylové charakteristiky.
- Aktuálny projekt porovnáva algoritmy s nerovnakým počtom vyhodnotení cieľa; preto **čas a kvalita nie sú porovnaním pri rovnakom výpočtovom rozpočte**. Toto treba uviesť alebo experimenty metodologicky zosúladiť.
- Pôvodné matice uvádzajú Google Maps ako zdroj, ale zdrojový dokument v repozitári neobsahuje reprodukovateľný export mapových dát. Pre report nezaručujte nezávislé overenie dát.
- Výsledky nemožno bez úprav numericky porovnávať s tabuľkou autorov článku, pretože lokálne náklady/presné matice a ich experimentálne nastavenia sa môžu odlišovať.

## Spustenie

```bash

python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python nearest_neighbor.py
python branch_and_bound.py
python ant_colony.py
python results.py
```

Všetky tri nové skripty zachovávajú existujúcu štruktúru a používajú spoločný pomocný súbor `tsp_common.py`. Ostatné algoritmy spolužiakov nie sú prepisované.
