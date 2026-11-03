# Zwischensicherung nach Shemot · 03.11.2026

**Nächster Abschnitt: Vaera 1:1. Keine vollständige sprachliche Satzfreigabe.**

## Wiederaufnahme und Grenzen der Rekonstruktion

Im früheren Chat wurde am 03.11.2026 um 12:26:43 Uhr österreichischer Zeit gemeldet: mehr als die Hälfte der 1.024 Absätze gelesen, Vayechi ebenfalls durchgesehen, Produktionsmaster und Kollation neu erzeugt, TEXT_M = 0. Die zu diesem späteren Lauf gehörenden Dateien und Einzelkorrekturen wurden in der jetzigen Umgebung nicht wiedergefunden.

Die Wiederaufnahme basiert deshalb auf den exakt wiederhergestellten Dateien des Commits `61c7b6cee456be6516cb3ca5e8506ab87f48aef0`. Dessen 169 einzeln protokollierte Absätze sind ein älterer gespeicherter Stand und ersetzen nicht den später gemeldeten Fortschritt. Ungespeicherte spätere Korrekturen sind ausdrücklich noch nicht als wiederhergestellt anzusehen.

## Jetzt tatsächlich ausgeführt

- Shemot 1:1 bis 11:1: alle **48 Absätze** zusammenhängend sprachlich gelesen.
- **36 protokollierte Änderungsgruppen, 45 ersetzte Fundstellen**: ausschließlich Nikud und Entfernung irreführender Punktierung der Abkürzung אח"כ. Mehrwortersetzungen können mehr als ein Wort betreffen.
- Beispiele: Sonne statt Diener; Abwesenheit statt Herde; Morgen statt Rindvieh; Gebetszitat וּבָנוּ בָּחַרְתָּ statt וּבְנוֹ בָּחַרְתָּ; Wurzelbezug מִשֹּׁרֶשׁ statt מְשָׁרֵשׁ.
- Keine neuen Konsonantenkorrekturen. Die 20 bereits aktiven, früher belegten Textkorrekturen bleiben bestehen.
- Auffällige Digitaltextstellen wurden einzeln als **Druckabgleich offen** erfasst. In diesem Lauf wurden keine Scanbilder gelesen; die Scan-ZIP-Teile liegen hier nicht vor. Es wurden keine Scanbelege erfunden.
- Original-JSON, alle 46 Nakdan-Dateien, die 1.024 Absatzmarker und alle nicht vokalischen Zeichen der Arbeitszeugen unverändert.
- Master und Kollation neu erzeugt. Vorhandene Entscheidungen der Kollations-TSV wurden übernommen; nicht mehr zuordenbare Altentscheidungen bleiben separat erhalten.
- Alle EN-Felder weiterhin leer.

## Nachweise

- `vokalisierung/Fortsetzung_Shemot_Status_20261103.json`: aktueller Fortsetzungsstatus, historische Chatmeldung, offene Befunde und Absatzprüfsummen.
- `vokalisierung/Fortsetzung_Shemot_Leseprotokoll_20261103.json`: genau die 48 in diesem Lauf gelesenen Absätze.
- `vokalisierung/Fortsetzung_Shemot_Aenderungen_20261103.json`: exakte Ersetzungen mit Begründungen und Vorkommenszahl.
- `fortsetzung_shemot_20261103/basis_61c7b6c/`: Originalmaster und Original-Shemot-Zeugen als Vergleichsbasis.
- `out/Fortsetzung_Shemot_Tests_20261103.txt`: **42 Tests bestanden**.
- `out/band/Od_Yosef_Chai_Halakhot_Masterpruefung.json`: **508 Segmente, 30 Abschnitte, 0 FEHLER, 0 PRÜFEN** in der Strukturprüfung.
- Kollation: **TEXT_M / PLUS_M / MINUS_M = 0**, **TEXT_N = 20** erwartete Abweichungen zum unbearbeiteten Nakdan-Zeugen; VOK = 3.165, UNVOK_M = 25. Diese Zahlen sind keine Zähler verbleibender Sprachfehler.
- Master SHA-256: `103a927eec270e11e1fc7cc68fdf839f82be27364c124660952ab55212921659`.

## Fortsetzung

1. Vaera ab `@@Vaera 1:1@@` in `vokalisierung/meine/OYC_15_Vaera_Teil01.txt` lesen und protokollieren.
2. Ungespeicherte frühere Korrekturen vor Shemot durch erneute Einzelprüfung rekonstruieren. Die Aussage „mehr als die Hälfte gelesen“ allein liefert keine vollständige Liste der Änderungen.
3. Alte und neue Textverdachtsstellen sowie Errata auf Scanseiten 413–415 mit den tatsächlichen Repository-Scans prüfen. Konsonantenkorrekturen nur mit Beleg über `textkorrekturen.json`.
4. Nach jeder abgeschlossenen Parascha Master, Kollation, Schutzprüfung und Sicherung erneuern.

Die Zahl 215 reproduzierbar dokumentierter Einzelprüfungen (169 ältere + 46 neu hinzugekommene; zwei Shemot-Absätze waren schon einzeln gelesen) dient allein der Nachvollziehbarkeit der verfügbaren Protokolle. Sie ist **keine Rückstufung des im früheren Chat gemeldeten Fortschritts**.
