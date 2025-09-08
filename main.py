"""
Projekt č.5 Vylepšený Task manager do kurzu Tester s Pythonem od Engeta

author: Jan Páč
email: czjanpac@gmail.com
"""

import mysql.connector
from mysql.connector import Error

DB_NAME = "task_manager"

# Připojení k MySQL serveru a zajištění, že databáze existuje
def pripojeni_db():
    try:
        # Připojení k MySQL serveru (bez databáze)
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

        # Připojení už k databázi task_manager
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

# Vytvoření tabulky (volá se jen jednou na začátku)
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
                stav ENUM('nezahájeno', 'probiha', 'hotovo') DEFAULT 'nezahájeno',
                datum_vytvoreni DATE DEFAULT (CURRENT_DATE)
            )
        """)
        conn.commit()
    except Error as e:
        print(f"Chyba při vytváření tabulky: {e}")
    finally:
        cursor.close()
        conn.close()

# Přidání úkolu do databáze
def pridat_ukol():
    while True:
        nazev = input("Zadejte název úkolu: ").strip()
        popis = input("Zadejte popis úkolu: ").strip()

        if not nazev or not popis:
            print("Název i popis úkolu musí být vyplněny, zkuste to znovu.")
            continue

        conn, cursor = pripojeni_db()
        if not conn:
            return
        try:
            cursor.execute(
                "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)",
                (nazev, popis)
            )
            conn.commit()
            print(f"Úkol '{nazev}' byl přidán.")
            break
        except Error as e:
            print(f"Chyba při přidávání úkolu: {e}")
        finally:
            cursor.close()
            conn.close()

# Zobrazení všech úkolů z databáze
def zobrazit_ukoly():
    conn, cursor = pripojeni_db()
    if not conn:
        return
    try:
        # Filtr: pouze "nezahájeno" nebo "probiha"
        cursor.execute("SELECT id, nazev, popis, stav, datum_vytvoreni FROM ukoly WHERE stav IN ('nezahájeno', 'probiha')")
        rows = cursor.fetchall()
        if not rows:
            print("Seznam úkolů je prázdný.")
            return
        print("\nSeznam úkolů:")
        for row in rows:
            print(f"{row[0]}. {row[1]} - {row[2]} | Stav: {row[3]} | Vytvořeno: {row[4]}")
    except Error as e:
        print(f"Chyba při načítání úkolů: {e}")
    finally:
        cursor.close()
        conn.close()

# Aktualizace stavu vybraného úkolu z databaze
def aktualizovat_ukol():
    zobrazit_ukoly()
    ukol_id = input("Zadejte ID úkolu, kterému chcete aktualizovat stav: ").strip()
    if not ukol_id.isdigit():
        print("Neplatné ID.")
        return

    print("""Vyberte nový stav úkolu:
1. Probíhá
2. Hotovo""")
    volba = input("Volba 1-2: ").strip()
    stav_map = {"1": "probiha", "2": "hotovo"}
    if volba not in stav_map:
        print("Neplatná volba stavu.")
        return

    conn, cursor = pripojeni_db()
    if not conn:
        return
    try:
        cursor.execute(
            "UPDATE ukoly SET stav = %s WHERE id = %s",
            (stav_map[volba], int(ukol_id))
        )
        conn.commit()
        print(f"Úkol {ukol_id} byl aktualizován na stav '{stav_map[volba]}'.")
    except Error as e:
        print(f"Chyba při aktualizaci úkolu: {e}")
    finally:
        cursor.close()
        conn.close()


# Odstranění úkolu z databáze    
def odstranit_ukol():
    zobrazit_ukoly()
    ukol_id = input("Zadejte ID úkolu, který chcete odstranit: ").strip()
    if not ukol_id.isdigit():
        print("Neplatné ID.")
        return

    conn, cursor = pripojeni_db()
    if not conn:
        return
    try:
        cursor.execute("DELETE FROM ukoly WHERE id = %s", (int(ukol_id),))
        conn.commit()
        print(f"Úkol {ukol_id} byl odstraněn.")
    except Error as e:
        print(f"Chyba při odstraňování úkolu: {e}")
    finally:
        cursor.close()
        conn.close()

# Hlavní menu je zároveň funkce, která celý program spouští
def hlavni_menu():
    vytvoreni_tabulky()
    while True:
        print("""
Správce úkolů - Hlavní menu
1. Přidat nový úkol
2. Zobrazit všechny úkoly
3. Aktualizovat stav úkolu
4. Odstranit úkol
5. Ukončit program""")
        vyber_z_menu = input("Vyberte možnost 1-5: ").strip()
        if not vyber_z_menu.isdigit() or not 1 <= int(vyber_z_menu) <= 5:
            print("Neplatná volba.")
            continue

        vyber_z_menu = int(vyber_z_menu)

        if vyber_z_menu == 1:
            pridat_ukol()
        elif vyber_z_menu == 2:
            zobrazit_ukoly()
        elif vyber_z_menu == 3:
            aktualizovat_ukol()
        elif vyber_z_menu == 4:
            odstranit_ukol()
        elif vyber_z_menu == 5:
            print("Konec programu.")
            break

if __name__ == "__main__":
    hlavni_menu()
