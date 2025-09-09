"""
Projekt č.5 Vylepšený Task manager do kurzu Tester s Pythonem od Engeta

author: Jan Páč
email: czjanpac@gmail.com
"""

import mysql.connector
from mysql.connector import Error

DB_NAME = "task_manager"

# --- Připojení k DB a vytvoření tabulky ---
def pripojeni_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111"
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        conn.commit()
        cursor.close()
        conn.close()

        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111",
            database=DB_NAME
        )
        cursor = conn.cursor()
        return conn, cursor
    except Error as e:
        print(f"Nastala chyba při práci s databází: {e}")
        return None, None

def vytvoreni_tabulky():
    conn, cursor = pripojeni_db()
    if not conn:
        return
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ukoly (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nazev VARCHAR(255) NOT NULL,
                popis TEXT,
                stav ENUM('nezahajeno', 'probiha', 'hotovo') DEFAULT 'nezahajeno',
                datum_vytvoreni TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    except Error as e:
        print(f"Chyba při vytváření tabulky: {e}")
    finally:
        cursor.close()
        conn.close()

# --- CRUD funkce ---
def pridat_ukol(nazev, popis):
    if not nazev or not popis:
        return False, "Název i popis úkolu musí být vyplněny."
    conn, cursor = pripojeni_db()
    if not conn:
        return False, "Nepodařilo se připojit k databázi."
    try:
        cursor.execute(
            "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)",
            (nazev, popis)
        )
        conn.commit()
        return True, f"Úkol '{nazev}' byl přidán.\n"
    except Error as e:
        return False, f"Chyba při přidávání úkolu: {e}"
    finally:
        cursor.close()
        conn.close()

def zobrazit_ukoly(filtr=None):
    conn, cursor = pripojeni_db()
    if not conn:
        return False, "Nepodařilo se připojit k databázi.", []
    try:
        if filtr:
            placeholders = ', '.join(['%s'] * len(filtr))
            query = f"""
                SELECT id, nazev, popis, stav, datum_vytvoreni
                FROM ukoly
                WHERE stav IN ({placeholders})
            """
            cursor.execute(query, tuple(filtr))
        else:
            cursor.execute("SELECT id, nazev, popis, stav, datum_vytvoreni FROM ukoly")
        rows = cursor.fetchall()
        if not rows:
            return True, "Seznam úkolů je prázdný.", []
        return True, "Seznam úkolů:", rows
    except Error as e:
        return False, f"Chyba při načítání úkolů: {e}", []
    finally:
        cursor.close()
        conn.close()

def aktualizovat_ukol(cislo_ukolu, novy_stav):
    if novy_stav not in ('probiha', 'hotovo'):
        return False, "Neplatný stav."
    conn, cursor = pripojeni_db()
    if not conn:
        return False, "Nepodařilo se připojit k databázi."
    try:
        cursor.execute("SELECT nazev FROM ukoly WHERE id=%s", (cislo_ukolu,))
        row = cursor.fetchone()
        if not row:
            return False, f"Úkol s číslem {cislo_ukolu} neexistuje."
        nazev_ukolu = row[0]
        cursor.execute("UPDATE ukoly SET stav=%s WHERE id=%s", (novy_stav, cislo_ukolu))
        conn.commit()
        return True, f"Úkol číslo {cislo_ukolu} ('{nazev_ukolu}') byl aktualizován na stav '{novy_stav}'.\n"
    except Error as e:
        return False, f"Chyba při aktualizaci úkolu: {e}"
    finally:
        cursor.close()
        conn.close()

def odstranit_ukol(cislo_ukolu):
    conn, cursor = pripojeni_db()
    if not conn:
        return False, "Nepodařilo se připojit k databázi."
    try:
        cursor.execute("SELECT nazev FROM ukoly WHERE id=%s", (cislo_ukolu,))
        row = cursor.fetchone()
        if not row:
            return False, f"Úkol s číslem {cislo_ukolu} neexistuje."
        nazev_ukolu = row[0]
        cursor.execute("DELETE FROM ukoly WHERE id=%s", (cislo_ukolu,))
        conn.commit()
        return True, f"Úkol číslo {cislo_ukolu} ('{nazev_ukolu}') byl odstraněn.\n"
    except Error as e:
        return False, f"Chyba při odstraňování úkolu: {e}"
    finally:
        cursor.close()
        conn.close()

# --- Funkce menu ---
def pridani_ukolu_menu():
    while True:
        nazev = input("Zadejte název úkolu: ").strip()
        if len(nazev) > 255:
            print("Název úkolu je příliš dlouhý (max. 255 znaků). Zadejte ho prosím znovu.\n")
            continue
        popis = input("Zadejte popis úkolu: ").strip()
        success, msg = pridat_ukol(nazev, popis)
        print(msg)
        if success:
            break

def zobrazeni_ukolu_menu():
    stav_map = {
        'nezahajeno': 'nezahájeno',
        'probiha': 'probíhá',
        'hotovo': 'hotovo'
    }

    success, msg, rows = zobrazit_ukoly(filtr=['nezahajeno', 'probiha'])
    print(msg)
    for idx, row in enumerate(rows, start=1):
        stav_text = stav_map.get(row[3], row[3])
        print(f"{idx}. {row[1]} - {row[2]} | Stav: {stav_text} | Vytvořeno: {row[4]}")
    print()

    while True:  # Opakovat, dokud uživatel nezadá platnou volbu
        volba_filtru = input("Zadejte 'f' pro otevření filtrování nebo stiskněte Enter pro návrat do menu: ").strip().lower()
        print()
        if volba_filtru == 'f':
            while True:
                print("Vyberte stav pro zobrazení:")
                print("1. nezahájeno")
                print("2. probíhá")
                print("3. hotovo")
                print("4. všechny úkoly")
                stav_volba = input("Vyberte možnost 1-4: ").strip()
                print()

                if stav_volba == '1':
                    stav_filter = ['nezahajeno']
                elif stav_volba == '2':
                    stav_filter = ['probiha']
                elif stav_volba == '3':
                    stav_filter = ['hotovo']
                elif stav_volba == '4':
                    stav_filter = None
                else:
                    print("Neplatná volba, zadejte novou volbu.\n")
                    continue

                success, msg, rows = zobrazit_ukoly(filtr=stav_filter)
                print(msg)
                for idx, row in enumerate(rows, start=1):
                    stav_text = stav_map.get(row[3], row[3])
                    print(f"{idx}. {row[1]} - {row[2]} | Stav: {stav_text} | Vytvořeno: {row[4]}")
                print()
                break
            break  # Ukončí hlavní while po zobrazení filtrovaných úkolů
        elif volba_filtru == '':
            break  # Enter vrátí do hlavního menu
        else:
            print("Neplatná volba.\n")


def aktualizace_ukolu_menu():
    stav_map = {
        'nezahajeno': 'nezahájeno',
        'probiha': 'probíhá',
        'hotovo': 'hotovo'
    }

    while True:
        success, msg, rows = zobrazit_ukoly()
        if not rows:
            print("Seznam úkolů je prázdný, nelze provést akci.")
            print()
            break
        print(msg)
        for idx, row in enumerate(rows, start=1):
            stav_text = stav_map.get(row[3], row[3])
            print(f"{idx}. {row[1]} - Stav: {stav_text}")
        cislo_ukolu = input("Zadejte číslo úkolu k aktualizaci: ").strip()
        if not cislo_ukolu.isdigit() or int(cislo_ukolu) < 1 or int(cislo_ukolu) > len(rows):
            print("Úkol s tímto číslem neexistuje.\n")
            continue
        skutecne_id = rows[int(cislo_ukolu)-1][0]

        print()
        print("Vyberte nový stav:")
        print("1. probíhá")
        print("2. hotovo")
        stav_volba = input("Zadejte číslo 1-2: ").strip()
        if stav_volba == '1':
            novy_stav = "probiha"
        elif stav_volba == '2':
            novy_stav = "hotovo"
        else:
            print("Neplatná volba stavu.\n")
            continue
        success, msg = aktualizovat_ukol(skutecne_id, novy_stav)
        print(msg)
        break

def odstraneni_ukolu_menu():
    stav_map = {
        'nezahajeno': 'nezahájeno',
        'probiha': 'probíhá',
        'hotovo': 'hotovo'
    }

    while True:
        success, msg, rows = zobrazit_ukoly()
        if not rows:
            print("Seznam úkolů je prázdný, nelze provést akci.")
            print()
            break
        print(msg)
        for idx, row in enumerate(rows, start=1):
            stav_text = stav_map.get(row[3], row[3])
            print(f"{idx}. {row[1]} - Stav: {stav_text}")
        cislo_ukolu = input("Zadejte číslo úkolu k odstranění: ").strip()
        if not cislo_ukolu.isdigit() or int(cislo_ukolu) < 1 or int(cislo_ukolu) > len(rows):
            print("Úkol s tímto číslem neexistuje.\n")
            continue
        skutecne_id = rows[int(cislo_ukolu)-1][0]
        success, msg = odstranit_ukol(skutecne_id)
        print(msg)
        break

# --- Hlavní menu ---
def hlavni_menu():
    vytvoreni_tabulky()
    while True:
        print("""Správce úkolů - Hlavní menu
1. Přidat nový úkol
2. Zobrazit úkoly
3. Aktualizovat stav úkolu
4. Odstranit úkol
5. Ukončit program""")
        volba = input("Vyberte možnost 1-5: ").strip()
        print()
        if volba == '1':
            pridani_ukolu_menu()
        elif volba == '2':
            zobrazeni_ukolu_menu()
        elif volba == '3':
            aktualizace_ukolu_menu()
        elif volba == '4':
            odstraneni_ukolu_menu()
        elif volba == '5':
            print("Konec programu.")
            break
        else:
            print("Neplatná volba.\n")

# --- MAIN ---
if __name__ == "__main__":
    hlavni_menu()
