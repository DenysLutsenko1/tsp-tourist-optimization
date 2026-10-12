# TSP Tourist Optimization

Tento projekt je zameraný na optimalizáciu turistických trás (problém cestujúceho – TSP) s ohľadom na reálne údaje o vzdialenostiach, čase cestovania a finančných nákladoch.

## Zdroje údajov a parametre
* **Zdroj údajov:** Všetky vzdialenosti a časy boli prevzaté z **Google Maps**.
* **Matice:**
  * `distance_matrix` – matica vzdialeností v **kilometroch**.
  * `time_matrix` – matica času v **minútach**.
* **Počiatočný bod:** Turisti začínajú v meste **Chattogram** (východný a koncový bod trasy).

## Finančné a spotrebné parametre
* **Cena paliva:** `One_liter_benzin_BDT_coast` – cena za 1 liter benzínu v miestnej mene (BDT).
* **Spotreba paliva:** `fuel_consumption_per_km` – spotreba paliva na 1 kilometer. Priemerná hodnota sa pohybuje v rozmedzí od 0,06 do 0,10, pričom sa používa priemer **0,08 l/km**.

## Váhové koeficienty pre optimalizáciu
Pre vyváženú optimalizáciu trasy sa používajú nasledujúce váhy kritérií:
* **Váha pre vzdialenosť:** `0.3`
* **Váha pre čas:** `0.4`
* **Váha pre peniaze (náklady na palivo):** `0.3`

## Technické nastavenia
* **Generátor náhodných čísel:** `np.random.seed(40)` na zabezpečenie reprodukovateľnosti výsledkov.

## Príprava prostredia (Inštalácia)

1. Uistite sa, že máte nainštalovaný **Python** (odporúčaná verzia 3.11.0 alebo novšia).
2. Stiahnite si alebo klonujte projekt do svojho lokálneho adresára.
3. Otvorte terminál/príkazový riadok v koreňovom priečinku projektu (`tsp-tourist-optimization`) a nainštalujte potrebné závislosti:

## Spustenie projektu

Všetky súbory sa spúšťajú z koreňového adresára projektu pomocou príkazu `python` a názvu súboru:

* `particle_swarm.py` – spustenie algoritmu Particle Swarm Optimization.
* `greedy_algorithm.py` – spustenie hladového algoritmu.
* `genetic_algorithm.py` – spustenie genetického algoritmu.
* `data.py` – uchovávanie údajov o vzdialenostiach, čase a finančných nákladoch. *(Údaje sa pripravia automaticky, preto nie je potrebné spúšťať tento súbor samostatne).*
* `results.py` – vizualizácia výsledkov.