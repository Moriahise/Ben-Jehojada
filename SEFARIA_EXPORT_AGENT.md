# Anweisung: Sefaria-Export finden, auflisten und aufschlüsseln

Du arbeitest mit dem öffentlichen Sefaria-Datenexport. Lies diese Anweisung vollständig, bevor du suchst oder lädst. Rate keine Pfade, sondern leite sie aus Listing oder `books.json` ab.

## 1. Wo die Daten liegen

| Was | Adresse |
|---|---|
| Daten (≈ 26 GB, ≈ 85.000 Dateien, ohne Login) | `gs://sefaria-export` = `https://storage.googleapis.com/sefaria-export/` |
| Index aller Texte | `https://raw.githubusercontent.com/Sefaria/Sefaria-Export/master/books.json` |
| Repo (Doku, Beispielskripte) | `https://github.com/Sefaria/Sefaria-Export` |

Das Repo enthält **keine Texte**, nur Index und Werkzeuge. Der Export wird monatlich am 1. erneuert, `books.json` am 2.

## 2. Aufbau des Buckets

```
json/{Kategorie}/…/{Titel}/{Sprache}/{Versionstitel}.json
txt/{Kategorie}/…/{Titel}/{Sprache}/{Versionstitel}.txt
cltk-full/…   cltk-flat/…        (gleiche Struktur, CLTK-Format)
schemas/{Titel}.json             (Struktur/Gliederung eines Werks)
links/links0.csv … linksN.csv    (alle Querverweise)
table_of_contents.json           (gesamter Katalogbaum)
```

Pfad zerlegen (von hinten lesen, die Kategorietiefe ist variabel):
- letzter Teil = Version (`merged` = zusammengeführte, vollständigste Fassung)
- vorletzter = Sprache (`Hebrew` oder `English`)
- drittletzter = Titel
- alles zwischen Format und Titel = Kategorienpfad

Beispiele:
```
json/Tanakh/Torah/Genesis/Hebrew/merged.json
json/Talmud/Bavli/Seder Moed/Shabbat/Hebrew/merged.json
txt/Mishnah/Seder Zeraim/Mishnah Berakhot/English/merged.txt
schemas/Genesis.json
```

## 3. Fallen

- **Leerzeichen, Apostrophe, Kommas** in Pfaden (`Me'or Einayim`, `Shulchan Arukh, Orach Chayim`): in URLs immer kodieren (`urllib.parse.quote`).
- **Nur zwei Sprachordner.** Übersetzungen ins Spanische, Französische, Portugiesische usw. liegen im Ordner `English/` (z. B. `LM 260.1 español.json`). Sprache bei Bedarf aus dem Versionstitel ablesen.
- **Für Volltext immer `merged.*` nehmen**, außer eine bestimmte Edition ist verlangt. Einzelversionen sind oft Fragmente von wenigen hundert Bytes.
- **Listing ist seitenweise** (1000 Einträge pro Seite). Nie annehmen, dass die erste Seite alles ist.
- **Kommentare sind eigene Titel** (`Rashi on Genesis`), mit eigenen Ordnern unter `…/Commentary/…`.
- **Nicht alles herunterladen**, wenn nur ein Teil gebraucht wird. Erst auflisten, dann gezielt laden.

## 4. Wie du auflistest

**Schnellster Weg für einzelne Titel:** `books.json` laden. Jeder Eintrag enthält `title`, `language`, `versionTitle`, `categories` (Liste) und fertige URLs (`json_url`, `txt_url`, `cltk_full_url`, `cltk_flat_url`).

**Vollständiges Listing über die GCS-API** (JSON, seitenweise mit `pageToken`):
```
https://storage.googleapis.com/storage/v1/b/sefaria-export/o?prefix=json/Talmud/&maxResults=1000&fields=items(name,size),nextPageToken
```

**Ordner durchblättern** (XML, nur eine Ebene, über `delimiter`):
```
https://storage.googleapis.com/sefaria-export?prefix=json/&delimiter=/
https://storage.googleapis.com/sefaria-export?prefix=json/Halakhah/&delimiter=/
```
Unterordner stehen in `<CommonPrefixes>`. Bei `<IsTruncated>true</IsTruncated>` geht es mit `&marker=<NextMarker>` weiter.

**Mit installiertem gcloud/gsutil:**
```
gsutil ls "gs://sefaria-export/json/Talmud/"
gcloud storage cp -r "gs://sefaria-export/json/Talmud/" ./talmud/
```

**Kein Netzzugang aus der Shell?** Das ist bei Sandbox-Proxys häufig. Dann die obigen URLs mit dem Web-Fetch-Werkzeug lesen und dem Nutzer ein Skript zum lokalen Ausführen geben. Nicht über andere Wege um die Sperre herum versuchen.

## 5. Links (Querverweise)

- Die Dateien `links/links*.csv` sind groß. Lade sie einzeln und lies **zuerst die Kopfzeile**, statt Spaltennamen anzunehmen.
- Erwartete Spalten sind `Citation 1, Citation 2, Conection Type, Text 1, Text 2, Category 1, Category 2`. Achtung: Sefaria schreibt „Conection“ mit einem n.
- Jeder Link ist ungerichtet. Für „alle Links eines Buches“ in **beiden** Spalten suchen (`Text 1 = X` ODER `Text 2 = X`).
- Für Auswertungen alles in SQLite laden und `Text 1`, `Text 2`, `Citation 1`, `Citation 2` indizieren. Eine CSV-Datei mehrfach zu durchsuchen ist zu langsam.
- Fehlen die Buchspalten, ist der Buchname die Stellenangabe ohne den letzten Abschnitt mit Ziffern (`Rashi on Genesis 1:1:1` → `Rashi on Genesis`).

## 6. Werkzeug: `sefaria_export.py`

Das Werkzeug benötigt nur die Python-Standardbibliothek. Es erledigt alle obigen Schritte und berücksichtigt die Fallen:

```
python sefaria_export.py inventory            # komplettes Listing -> inventory.csv + summary.txt
python sefaria_export.py books                # eine Zeile pro Titel, mit merged-URLs (HE/EN) -> books.csv
python sefaria_export.py download --format json --category Tanakh --lang Hebrew --merged-only --dry-run
python sefaria_export.py download --format txt --title "Shulchan Arukh, Orach Chayim"
python sefaria_export.py download --format schemas
python sefaria_export.py links                # alle links*.csv -> links.sqlite (indiziert)
python sefaria_export.py linkstats            # Gesamtstatistik, Top-Bücher, Link-Typen
python sefaria_export.py linkstats --book Genesis --export genesis_links.csv
```

Der Download läuft parallel, überspringt bereits vorhandene Dateien gleicher Größe und lässt sich fortsetzen. Nutze vor großen Downloads immer `--dry-run`.

## 7. Vorgehen

1. Klären, was gebraucht wird: Titel/Kategorie, Sprache, Format, alle Versionen oder nur merged, Links ja/nein.
2. `inventory` oder `books.json` → Treffer zeigen (Anzahl, Größe) **bevor** geladen wird.
3. Gezielt laden (`download` mit Filtern, `--merged-only` als Standard).
4. Links nur laden, wenn verlangt. Dann `links` → `linkstats`.
5. Ergebnis melden: was geladen wurde, wo es liegt, Umfang, Auffälligkeiten (fehlende Sprache, nur Fragmente).
