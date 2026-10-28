#!/usr/bin/env python3
"""
sefaria_export.py – Sefaria-Export (gs://sefaria-export) komplett aufschlüsseln.

Nur Python-Standardbibliothek, läuft unter Windows/macOS/Linux (Python 3.8+).

Befehle
-------
  inventory   Komplettes Bucket-Listing (~85.000 Dateien) -> inventory.csv + summary.txt
  books       Bücherliste (ein Eintrag pro Titel) -> books.csv
  download    Gefiltert herunterladen (parallel, mit Fortsetzen)
  links       links0..N.csv laden und in SQLite-Datenbank aufschlüsseln -> links.sqlite
  linkstats   Statistik / Abfrage aus links.sqlite (pro Buch, pro Typ, Buch-Paare)

Beispiele
---------
  python sefaria_export.py inventory
  python sefaria_export.py books
  python sefaria_export.py download --format json --category Tanakh --lang Hebrew --merged-only
  python sefaria_export.py download --format txt --title "Shulchan Arukh, Orach Chayim"
  python sefaria_export.py download --format schemas
  python sefaria_export.py links
  python sefaria_export.py linkstats --book Genesis
  python sefaria_export.py linkstats --book "Shulchan Arukh, Orach Chayim" --pairs 30
"""
import argparse
import csv
import json
import os
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

BUCKET = "sefaria-export"
API = f"https://storage.googleapis.com/storage/v1/b/{BUCKET}/o"
PUBLIC = f"https://storage.googleapis.com/{BUCKET}/"
TEXT_FORMATS = ("json", "txt", "cltk-full", "cltk-flat")
UA = {"User-Agent": "sefaria-export-tool/1.0"}

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))


# ---------------------------------------------------------------- Hilfen
def http_get(url, retries=5):
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            if attempt == retries - 1:
                raise
            wait = 2 ** attempt
            print(f"  Fehler ({e}), neuer Versuch in {wait}s …", file=sys.stderr)
            time.sleep(wait)


def public_url(key):
    return PUBLIC + urllib.parse.quote(key)


def parse_key(key):
    """Bucket-Pfad -> Metadaten.

    {format}/{kat1}/.../{katN}/{titel}/{sprache}/{version}.{ext}
    schemas/{titel}.json   links/linksN.csv   table_of_contents.json
    """
    parts = key.split("/")
    fmt = parts[0] if len(parts) > 1 else "root"
    rec = {"key": key, "format": fmt, "categories": "", "top_category": "",
           "title": "", "language": "", "version": "", "is_merged": False}
    if fmt in TEXT_FORMATS and len(parts) >= 5:
        version = parts[-1].rsplit(".", 1)[0]
        cats = parts[1:-3]
        rec.update(categories=" > ".join(cats), top_category=cats[0] if cats else "",
                   title=parts[-3], language=parts[-2], version=version,
                   is_merged=(version == "merged"))
    elif fmt == "schemas":
        rec["title"] = parts[-1].rsplit(".", 1)[0]
    return rec


# ---------------------------------------------------------------- inventory
def list_bucket(prefix=""):
    """Alle Objekte über die öffentliche GCS-JSON-API (seitenweise, 1000/Seite)."""
    token, page = None, 0
    while True:
        q = {"maxResults": "1000", "fields": "items(name,size,updated),nextPageToken"}
        if prefix:
            q["prefix"] = prefix
        if token:
            q["pageToken"] = token
        data = json.loads(http_get(API + "?" + urllib.parse.urlencode(q)))
        page += 1
        items = data.get("items", [])
        print(f"\r  Seite {page}: {len(items)} Objekte", end="", file=sys.stderr)
        yield from items
        token = data.get("nextPageToken")
        if not token:
            print(file=sys.stderr)
            return


def cmd_inventory(a):
    rows = []
    for it in list_bucket(a.prefix):
        r = parse_key(it["name"])
        r["size"] = int(it.get("size", 0))
        r["updated"] = it.get("updated", "")
        r["url"] = public_url(it["name"])
        rows.append(r)

    fields = ["format", "top_category", "categories", "title", "language", "version",
              "is_merged", "size", "updated", "key", "url"]
    with open(a.out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    # Zusammenfassung
    by_fmt = defaultdict(lambda: [0, 0])
    titles_by_cat = defaultdict(set)
    langs = Counter()
    for r in rows:
        by_fmt[r["format"]][0] += 1
        by_fmt[r["format"]][1] += r["size"]
        if r["format"] == "json":
            titles_by_cat[r["top_category"]].add(r["title"])
            if r["is_merged"]:
                langs[r["language"]] += 1
    lines = [f"Sefaria-Export – {len(rows)} Dateien, "
             f"{sum(r['size'] for r in rows) / 1e9:.2f} GB", "", "Pro Format:"]
    for fmt, (n, s) in sorted(by_fmt.items()):
        lines.append(f"  {fmt:<22} {n:>7} Dateien  {s / 1e6:>10.1f} MB")
    lines += ["", "Titel pro Hauptkategorie (json):"]
    for cat, t in sorted(titles_by_cat.items(), key=lambda x: -len(x[1])):
        lines.append(f"  {cat:<35} {len(t):>6}")
    lines += ["", f"Titel gesamt: {len(set().union(*titles_by_cat.values())) if titles_by_cat else 0}",
              "", "merged-Dateien pro Sprache (json):"]
    for lang, n in langs.most_common():
        lines.append(f"  {lang:<12} {n:>6}")
    text = "\n".join(lines)
    with open(a.summary, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(text)
    print(f"\n-> {a.out}\n-> {a.summary}")


def load_inventory(path):
    if not os.path.exists(path):
        sys.exit(f"{path} fehlt – zuerst 'inventory' ausführen.")
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["size"] = int(r["size"] or 0)
        r["is_merged"] = r["is_merged"] == "True"
    return rows


# ---------------------------------------------------------------- books
def cmd_books(a):
    rows = load_inventory(a.inventory)
    books = {}
    for r in rows:
        if r["format"] != "json":
            continue
        b = books.setdefault(r["title"], {"title": r["title"], "categories": r["categories"],
                                          "top_category": r["top_category"],
                                          "languages": set(), "versions": 0, "json_bytes": 0})
        b["languages"].add(r["language"])
        if not r["is_merged"]:
            b["versions"] += 1
        b["json_bytes"] += r["size"]
    schemas = {r["title"] for r in rows if r["format"] == "schemas"}
    with open(a.out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["title", "top_category", "categories", "languages", "versions",
                    "json_bytes", "has_schema", "schema_url",
                    "json_he_merged", "json_en_merged"])
        for t in sorted(books, key=lambda t: (books[t]["categories"], t)):
            b = books[t]
            base = "json/" + b["categories"].replace(" > ", "/") + f"/{t}/"
            w.writerow([t, b["top_category"], b["categories"], "|".join(sorted(b["languages"])),
                        b["versions"], b["json_bytes"], t in schemas,
                        public_url(f"schemas/{t}.json") if t in schemas else "",
                        public_url(base + "Hebrew/merged.json") if "Hebrew" in b["languages"] else "",
                        public_url(base + "English/merged.json") if "English" in b["languages"] else ""])
    print(f"{len(books)} Titel -> {a.out}")


# ---------------------------------------------------------------- download
def cmd_download(a):
    rows = load_inventory(a.inventory)
    sel = []
    for r in rows:
        if a.format and r["format"] != a.format:
            continue
        if a.category and a.category.lower() not in r["categories"].lower():
            continue
        if a.title and r["title"].lower() != a.title.lower():
            continue
        if a.lang and r["language"].lower() != a.lang.lower():
            continue
        if a.merged_only and r["format"] in TEXT_FORMATS and not r["is_merged"]:
            continue
        sel.append(r)
    total = sum(r["size"] for r in sel)
    print(f"{len(sel)} Dateien, {total / 1e6:.1f} MB ausgewählt")
    if a.dry_run or not sel:
        for r in sel[:50]:
            print("  ", r["key"])
        if len(sel) > 50:
            print(f"   … und {len(sel) - 50} weitere")
        return

    def fetch(r):
        dest = os.path.join(a.dest, *r["key"].split("/"))
        if os.path.exists(dest) and os.path.getsize(dest) == r["size"]:
            return "skip"
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        tmp = dest + ".part"
        with open(tmp, "wb") as f:
            f.write(http_get(r["url"]))
        os.replace(tmp, dest)
        return "ok"

    done = Counter()
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(fetch, r): r for r in sel}
        for i, fu in enumerate(as_completed(futs), 1):
            try:
                done[fu.result()] += 1
            except Exception as e:  # noqa: BLE001
                done["fehler"] += 1
                print(f"\n  FEHLER {futs[fu]['key']}: {e}", file=sys.stderr)
            print(f"\r  {i}/{len(sel)}  {dict(done)}", end="", file=sys.stderr)
    print(f"\nFertig -> {a.dest}")


# ---------------------------------------------------------------- links
def book_of(ref):
    """'Genesis 1:1' -> 'Genesis'; 'Rashi on Genesis 1:1:2' -> 'Rashi on Genesis';
    'Berakhot 2a:3' -> 'Berakhot'.  (Heuristik: Abschnittsangabe am Ende abschneiden.)"""
    ref = ref.strip()
    if " " not in ref:
        return ref
    head, tail = ref.rsplit(" ", 1)
    if tail[:1].isdigit():
        if "-" in tail and head and head[-1:].isdigit():
            head = head.rsplit(" ", 1)[0]
        return head
    return ref


def pick(header, *cands):
    low = {h.lower().strip(): h for h in header}
    for c in cands:
        if c in low:
            return low[c]
    return None


def cmd_links(a):
    os.makedirs(a.dir, exist_ok=True)
    keys = sorted(it["name"] for it in list_bucket("links/") if it["name"].endswith(".csv"))
    print(f"{len(keys)} Link-Dateien: {', '.join(k.split('/')[-1] for k in keys)}")
    paths = []
    for k in keys:
        p = os.path.join(a.dir, k.split("/")[-1])
        if not os.path.exists(p):
            print(f"  lade {k} …")
            with open(p + ".part", "wb") as f:
                f.write(http_get(public_url(k)))
            os.replace(p + ".part", p)
        paths.append(p)

    db = sqlite3.connect(a.db)
    db.executescript("""
        DROP TABLE IF EXISTS links;
        CREATE TABLE links(ref1 TEXT, ref2 TEXT, type TEXT,
                           book1 TEXT, book2 TEXT, cat1 TEXT, cat2 TEXT);
    """)
    n = 0
    for p in paths:
        with open(p, encoding="utf-8", newline="") as f:
            rd = csv.reader(f)
            header = next(rd)
            c1 = pick(header, "citation 1", "ref1", "ref 1")
            c2 = pick(header, "citation 2", "ref2", "ref 2")
            ct = pick(header, "conection type", "connection type", "type")
            t1 = pick(header, "text 1", "book 1")
            t2 = pick(header, "text 2", "book 2")
            k1 = pick(header, "category 1")
            k2 = pick(header, "category 2")
            idx = {h: i for i, h in enumerate(header)}
            g = lambda row, col: row[idx[col]] if col and idx[col] < len(row) else ""  # noqa: E731
            batch = []
            for row in rd:
                r1, r2 = g(row, c1), g(row, c2)
                batch.append((r1, r2, g(row, ct),
                              g(row, t1) or book_of(r1), g(row, t2) or book_of(r2),
                              g(row, k1), g(row, k2)))
                if len(batch) >= 50000:
                    db.executemany("INSERT INTO links VALUES (?,?,?,?,?,?,?)", batch)
                    n += len(batch)
                    batch.clear()
                    print(f"\r  {n:,} Links", end="", file=sys.stderr)
            db.executemany("INSERT INTO links VALUES (?,?,?,?,?,?,?)", batch)
            n += len(batch)
        print(f"\r  {n:,} Links (nach {os.path.basename(p)}, Spalten: {header})", file=sys.stderr)
    print("  Indizes …", file=sys.stderr)
    db.executescript("""
        CREATE INDEX i_b1 ON links(book1); CREATE INDEX i_b2 ON links(book2);
        CREATE INDEX i_r1 ON links(ref1);  CREATE INDEX i_r2 ON links(ref2);
        CREATE INDEX i_t  ON links(type);
    """)
    db.commit()
    db.close()
    print(f"{n:,} Links -> {a.db}")


def cmd_linkstats(a):
    db = sqlite3.connect(a.db)
    q = lambda sql, *p: db.execute(sql, p).fetchall()  # noqa: E731
    if not a.book:
        print("Links gesamt:", q("SELECT COUNT(*) FROM links")[0][0])
        print("\nNach Typ:")
        for t, c in q("SELECT type, COUNT(*) FROM links GROUP BY type ORDER BY 2 DESC"):
            print(f"  {t or '(leer)':<25} {c:>10,}")
        print(f"\nTop {a.pairs} Bücher (Links gesamt):")
        for b, c in q("""SELECT b, SUM(c) FROM (
                             SELECT book1 b, COUNT(*) c FROM links GROUP BY book1
                             UNION ALL SELECT book2, COUNT(*) FROM links GROUP BY book2)
                         GROUP BY b ORDER BY 2 DESC LIMIT ?""", a.pairs):
            print(f"  {b:<50} {c:>9,}")
        return
    book = a.book
    tot = q("SELECT COUNT(*) FROM links WHERE book1=? OR book2=?", book, book)[0][0]
    print(f"{book}: {tot:,} Links")
    print("\nNach Typ:")
    for t, c in q("""SELECT type, COUNT(*) FROM links WHERE book1=? OR book2=?
                     GROUP BY type ORDER BY 2 DESC""", book, book):
        print(f"  {t or '(leer)':<25} {c:>9,}")
    print(f"\nTop {a.pairs} verbundene Bücher:")
    for other, c in q("""SELECT other, COUNT(*) FROM (
                             SELECT book2 other FROM links WHERE book1=?
                             UNION ALL SELECT book1 FROM links WHERE book2=?)
                         GROUP BY other ORDER BY 2 DESC LIMIT ?""", book, book, a.pairs):
        print(f"  {other:<55} {c:>8,}")
    if a.export:
        with open(a.export, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["ref", "linked_ref", "type", "linked_book", "linked_category"])
            for row in db.execute("""SELECT ref1, ref2, type, book2, cat2 FROM links WHERE book1=?
                                     UNION ALL
                                     SELECT ref2, ref1, type, book1, cat1 FROM links WHERE book2=?""",
                                  (book, book)):
                w.writerow(row)
        print(f"\nAlle Links -> {a.export}")


# ---------------------------------------------------------------- CLI
def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("inventory", help="Bucket komplett auflisten")
    s.add_argument("--prefix", default="", help="nur Teilbaum, z. B. json/Talmud/")
    s.add_argument("--out", default="inventory.csv")
    s.add_argument("--summary", default="summary.txt")
    s.set_defaults(fn=cmd_inventory)

    s = sp.add_parser("books", help="eine Zeile pro Titel")
    s.add_argument("--inventory", default="inventory.csv")
    s.add_argument("--out", default="books.csv")
    s.set_defaults(fn=cmd_books)

    s = sp.add_parser("download", help="gefiltert herunterladen")
    s.add_argument("--inventory", default="inventory.csv")
    s.add_argument("--format", help="json | txt | cltk-full | cltk-flat | schemas | links")
    s.add_argument("--category", help="Teilstring der Kategorie, z. B. Tanakh, Talmud/Bavli, Halakhah")
    s.add_argument("--title", help="exakter Titel, z. B. 'Mishneh Torah, Prayer'")
    s.add_argument("--lang", help="Hebrew | English")
    s.add_argument("--merged-only", action="store_true", help="nur merged.* statt aller Versionen")
    s.add_argument("--dest", default="sefaria-data")
    s.add_argument("--workers", type=int, default=8)
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(fn=cmd_download)

    s = sp.add_parser("links", help="Links in SQLite aufschlüsseln")
    s.add_argument("--dir", default="sefaria-links")
    s.add_argument("--db", default="links.sqlite")
    s.set_defaults(fn=cmd_links)

    s = sp.add_parser("linkstats", help="Link-Statistik / Export")
    s.add_argument("--db", default="links.sqlite")
    s.add_argument("--book", help="Buchtitel, z. B. Genesis")
    s.add_argument("--pairs", type=int, default=25)
    s.add_argument("--export", help="alle Links dieses Buchs als CSV")
    s.set_defaults(fn=cmd_linkstats)

    a = p.parse_args()
    if getattr(a, "category", None):
        a.category = a.category.replace("/", " > ")
    a.fn(a)


if __name__ == "__main__":
    main()
