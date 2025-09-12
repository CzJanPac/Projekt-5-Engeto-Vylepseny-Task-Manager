# Task Manager (Python + MySQL)

## 1) Hlavní aplikace (`main.py`)

### Popis
Tato aplikace je jednoduchý **task manager**, který umožňuje:

- Přidávat nové úkoly s názvem a popisem  
- Zobrazovat úkoly s možností filtrování podle stavu  
- Aktualizovat stav úkolů (**probíhá / hotovo**)  
- Odstraňovat úkoly z databáze  

Data jsou ukládána do **MySQL databáze (`task_manager`)** s tabulkou `ukoly`. Každý úkol obsahuje:

| Sloupec           | Popis                          |
|------------------|--------------------------------|
| `id`             | unikátní identifikátor         |
| `nazev`          | název úkolu                    |
| `popis`          | popis úkolu                    |
| `stav`           | aktuální stav (nezahájeno, probíhá, hotovo) |
| `datum_vytvoreni`| automaticky uložen čas vytvoření |

#### Požadavky
- Python 3.8+  
- MySQL server běžící lokálně  
- Python knihovna: `mysql-connector-python`

```bash
pip install mysql-connector-python
```

#### Konfigurace
V souboru `main.py` se nachází přihlašovací údaje k MySQL:

```python
host="localhost"
user="root"
password="1111"
```

Upravte dle vaší konfigurace serveru.

#### Vytvoření databáze a tabulky
Funkce `vytvoreni_tabulky()` se volá automaticky při spuštění programu, takže se tabulka vytvoří, pokud ještě neexistuje.

### Spuštění aplikace
```bash
python main.py
```

Po spuštění se zobrazí hlavní menu:

```
Správce úkolů - Hlavní menu
1. Přidat nový úkol
2. Zobrazit úkoly
3. Aktualizovat stav úkolu
4. Odstranit úkol
5. Ukončit program
```

#### Funkce menu
- **Přidat nový úkol**  
  - Uživateli se zobrazí výzva pro zadání názvu a popisu úkolu  
  - Kontrola: název max. 255 znaků, žádná prázdná pole  
  - Úkol se uloží do databáze  

- **Zobrazit úkoly**  
  - Zobrazí všechny úkoly se stavem `nezahájeno` a `probíhá`  
  - Možnost filtrace podle stavu: `nezahájeno`, `probíhá`, `hotovo`, nebo všechny úkoly  
  - Zobrazeny jsou: pořadí, název, popis, stav, datum vytvoření  

- **Aktualizovat stav úkolu**  
  - Uživatel vybere úkol podle čísla v seznamu  
  - Vybere nový stav: `probíhá` nebo `hotovo`  
  - Stav se uloží do DB, zpětná zpráva informuje o úspěchu  

- **Odstranit úkol**  
  - Uživatel vybere úkol podle čísla  
  - Úkol se odstraní z DB a vypíše se zpráva o odstranění  

- **Ukončit program**  
  - Program se ukončí  

---

## 2) Testovací kód (`test_main.py`)

### Popis
Testovací skript je napsán s použitím **pytest**. Slouží k ověření funkčnosti CRUD operací aplikace.  

Testy používají samostatnou databázi `task_manager_test`, aby nezasahovaly do produkční databáze.

### Instalace potřebných knihoven
```bash
pip install mysql-connector-python
pip install pytest
```

- `mysql-connector-python` – pro práci s MySQL databází  
- `pytest` – framework pro spouštění testů  

### Importy v testovacím skriptu
```python
import pytest
import mysql.connector
from main import pripojeni_db, pridat_ukol, aktualizovat_ukol, odstranit_ukol, zobrazit_ukoly
```

- `pytest` – framework, který umožňuje definovat testy jako funkce a využívat fixture  
- `mysql.connector` – přímá práce s databází pro přípravu a úklid testovací databáze  
- Funkce z `main.py` – testujeme CRUD operace a jejich výstupy  

### Spuštění testů
```bash
pytest test_main.py -v
```

- `-v` – zobrazí podrobné informace o průběhu testů  
- Po testech se testovací databáze automaticky odstraní, takže zůstává čisté prostředí

