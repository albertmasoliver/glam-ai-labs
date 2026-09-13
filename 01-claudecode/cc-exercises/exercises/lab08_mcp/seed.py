#!/usr/bin/env python3
"""Build the little database the server reads. Run once.

Run it:  python3 seed.py
"""

import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent / "library.db"

ROWS = [
    ("The Left Hand of Darkness", "Ursula K. Le Guin", 1969, "sf"),
    ("The Dispossessed", "Ursula K. Le Guin", 1974, "sf"),
    ("A Wizard of Earthsea", "Ursula K. Le Guin", 1968, "fantasy"),
    ("Solaris", "Stanislaw Lem", 1961, "sf"),
    ("The Cyberiad", "Stanislaw Lem", 1965, "sf"),
    ("His Master's Voice", "Stanislaw Lem", 1968, "sf"),
    ("Kindred", "Octavia E. Butler", 1979, "sf"),
    ("Dawn", "Octavia E. Butler", 1987, "sf"),
    ("Parable of the Sower", "Octavia E. Butler", 1993, "sf"),
    ("Hard-Boiled Wonderland", "Haruki Murakami", 1985, "fiction"),
    ("Kafka on the Shore", "Haruki Murakami", 2002, "fiction"),
    ("The Fifth Season", "N. K. Jemisin", 2015, "fantasy"),
    ("The Obelisk Gate", "N. K. Jemisin", 2016, "fantasy"),
    ("The Stone Sky", "N. K. Jemisin", 2017, "fantasy"),
]


def main():
    DB.unlink(missing_ok=True)
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE book (title TEXT, author TEXT, year INTEGER, shelf TEXT)")
    conn.executemany("INSERT INTO book VALUES (?, ?, ?, ?)", ROWS)
    conn.commit()
    conn.close()
    print(f"wrote {DB.name}: {len(ROWS)} books")


if __name__ == "__main__":
    main()
