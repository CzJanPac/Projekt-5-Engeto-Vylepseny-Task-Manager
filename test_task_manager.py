import pytest
import mysql.connector
from main import pripojeni_db, pridat_ukol, aktualizovat_ukol, odstranit_ukol, zobrazit_ukoly

TEST_DB = "task_manager_test"

# ---------------- Fixtures ---------------- #
@pytest.fixture(scope="function")
def setup_test_db():
    # Vytvoření testovací DB a tabulky před každým testem
    conn = mysql.connector.connect(host="localhost", user="root", password="1111")
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {TEST_DB}")
    conn.commit()
    cursor.close()
    conn.close()

    conn = mysql.connector.connect(host="localhost", user="root", password="1111", database=TEST_DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ukoly (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nazev VARCHAR(255) NOT NULL,
            popis TEXT,
            stav ENUM('nezahajeno','probiha','hotovo') DEFAULT 'nezahajeno',
            datum_vytvoreni TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

    yield  # tady se spustí test

    # Odstranění testovací DB po testu
    conn = mysql.connector.connect(host="localhost", user="root", password="1111")
    cursor = conn.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {TEST_DB}")
    conn.commit()
    cursor.close()
    conn.close()

def connect_test_db():
    conn = mysql.connector.connect(host="localhost", user="root", password="1111", database=TEST_DB)
    cursor = conn.cursor()
    return conn, cursor

# ---------------- Testy přidání úkolu ---------------- #
def test_pridat_ukol_positivni(setup_test_db, monkeypatch):
    # Použij testovací DB
    monkeypatch.setattr("main.DB_NAME", TEST_DB)

    # Přidání validního úkolu
    success, msg = pridat_ukol("Test úkol", "Popis test úkolu")

    # Ověření úspěšného přidání
    assert success is True
    assert "byl přidán" in msg

def test_pridat_ukol_negativni(setup_test_db, monkeypatch):
    monkeypatch.setattr("main.DB_NAME", TEST_DB)

    # Pokus o přidání nevalidního úkolu (prázdný název a popis)
    success, msg = pridat_ukol("", "")

    # Ověření, že funkce selže a vrátí správnou zprávu
    assert success is False
    assert "musí být vyplněny" in msg

# ---------------- Testy aktualizace úkolu ---------------- #
def test_aktualizovat_ukol_positivni(setup_test_db, monkeypatch):
    monkeypatch.setattr("main.DB_NAME", TEST_DB)

    # Přidání úkolu, který budeme aktualizovat
    conn, cursor = connect_test_db()
    cursor.execute("INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)", ("Update test", "Popis"))
    conn.commit()
    id_ukolu = cursor.lastrowid
    cursor.close()
    conn.close()

    # Aktualizace stavu úkolu
    success, msg = aktualizovat_ukol(id_ukolu, "probiha")

    # Ověření úspěšné aktualizace
    assert success is True
    assert "byl aktualizován" in msg

def test_aktualizovat_ukol_negativni(setup_test_db, monkeypatch):
    monkeypatch.setattr("main.DB_NAME", TEST_DB)

    # Pokus o aktualizaci neexistujícího úkolu
    success, msg = aktualizovat_ukol(9999, "probiha")

    # Ověření selhání a správné chybové hlášky
    assert success is False
    assert "neexistuje" in msg

# ---------------- Testy odstranění úkolu ---------------- #
def test_odstranit_ukol_positivni(setup_test_db, monkeypatch):
    monkeypatch.setattr("main.DB_NAME", TEST_DB)

    # Přidání úkolu pro odstranění
    conn, cursor = connect_test_db()
    cursor.execute("INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)", ("Delete test", "Popis"))
    conn.commit()
    id_ukolu = cursor.lastrowid
    cursor.close()
    conn.close()

    # Odstranění úkolu
    success, msg = odstranit_ukol(id_ukolu)

    # Ověření úspěšného odstranění
    assert success is True
    assert "byl odstraněn" in msg

def test_odstranit_ukol_negativni(setup_test_db, monkeypatch):
    monkeypatch.setattr("main.DB_NAME", TEST_DB)

    # Pokus o odstranění neexistujícího úkolu
    success, msg = odstranit_ukol(9999)

    # Ověření selhání a správné chybové hlášky
    assert success is False
    assert "neexistuje" in msg

# ------------- Testy zobrazení seznamu úkolů ------------ #
def test_zobrazit_ukoly_positivni(setup_test_db, monkeypatch):
    monkeypatch.setattr("main.DB_NAME", TEST_DB)

    # Přidání dvou úkolů do DB
    pridat_ukol("Úkol 1", "Popis 1")
    pridat_ukol("Úkol 2", "Popis 2")

    # Získání seznamu úkolů
    success, msg, rows = zobrazit_ukoly()

    # Ověření, že funkce vrací očekávané úkoly
    assert success is True
    assert len(rows) == 2
    assert rows[0][1] == "Úkol 1"  # název prvního úkolu
    assert rows[1][1] == "Úkol 2"  # název druhého úkolu

def test_zobrazit_ukoly_negativni(setup_test_db, monkeypatch):
    monkeypatch.setattr("main.DB_NAME", TEST_DB)

    # Vyprázdnění tabulky, aby byla DB prázdná
    conn, cursor = connect_test_db()
    cursor.execute("DELETE FROM ukoly")
    conn.commit()
    cursor.close()
    conn.close()

    # Získání seznamu úkolů
    success, msg, rows = zobrazit_ukoly()

    # Ověření, že funkce správně vrací prázdný seznam
    assert success is True
    assert rows == []
    assert "Seznam úkolů je prázdný" in msg
