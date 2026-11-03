# Od Yosef Chai Halakhot · Rekonstruktion belegbarer Änderungen

03.11.2026. Basis: Commit `3f2472cf0f8c113750fc8a5faa1c45444e516ed0` nach Shemot.

**Die sechs konkret überlieferten Korrekturarten wurden neu zugeordnet, geprüft und wieder eingearbeitet. Eine vollständige historische Rekonstruktion aller ungespeicherten Änderungen ist nicht nachweisbar. Keine sprachliche Gesamtfreigabe.**

## Wiederhergestellte Korrekturarten

Die verfügbaren Meldungen des früheren Chats nennen sechs Korrekturarten, aber keine vollständige Änderungsliste. Die folgenden Stellen wurden jetzt im erhaltenen Text identifiziert und erneut geprüft. Die drei Buchstabenfehler wurden am Originaldruck des Repositorys bestätigt.

| Korrekturart | Stelle | Jetzt eingearbeitet |
|---|---|---|
| Trauernder | Vayera 11:1 | אֲבָל → אָבֵל |
| Oberarmmuskel | Vayera 21:1 | בִּקְבוּרַת → בַּקִּבּוֹרֶת; defektive Konsonantenschreibung erhalten |
| Bier | Toldot 10:2 | הַשָּׂכָר → הַשֵּׁכָר; בְּשָׂכָר → בְּשֵׁכָר |
| Tasche | Chayei Sara 5:1 und 5:2 | הכים → הכיס; zwei Übertragungsfehler, Druck S. 330 |
| Barriere | Vayera 19:1 | חוצך → חוצץ; Druck S. 329 |
| Versorge uns statt ihn | Beshalach 13:7 | וּתְפַרְנְסֶנּוּ → וּתְפַרְנְסֵנוּ; beide Vorkommen |

Diese erneute Zuordnung ersetzt keinen erhaltenen damaligen Diff; die damalige Anzahl der Ersetzungen ist nicht bekannt.

## Zusätzliche, jetzt erkannte Berichtigungen

Diese drei Fundstellen werden ausdrücklich nicht als nachgewiesene damalige Änderungen ausgegeben:

- Beshalach 13:7: תְּכַלְכְּלֶנּוּ → תְּכַלְכְּלֵנוּ, derselbe Gebetszusammenhang in der ersten Person Plural.
- Tetzaveh 1:1: ושמו את שמו → ושמו את שמי. Der Originaldruck S. 393 liest שמי, übereinstimmend mit Numeri 6,27.
- Tetzaveh 1:1: וּשְׁמוֹ אֶת → וְשָׂמוּ אֶת, Verbform des zitierten Verses.

Gesamt dieses Laufs: **11 Änderungsgruppen, 12 ersetzte Fundstellen**, darunter vier einzelne Buchstabenänderungen ausschließlich über `textkorrekturen.json`. Die bisherigen 20 aktiven Textkorrekturen sind unverändert; nun sind insgesamt **24** aktiv.

## Umfang der erneuten Prüfung

**16 Absätze** wurden gezielt zusammenhängend gelesen: Vayera 11:1, 19:1, 21:1; Chayei Sara 5:1–2; Toldot 10:1–2; Beshalach 13:1–7; Tetzaveh 1:1 und 7:1. Dies ist keine vollständige erneute Lektüre aller früher erwähnten Textgruppen oder aller 1.024 Absätze.

Der historische Chatstand bleibt dokumentiert: 481/1.024 am 03.11.2026 um 12:15 Uhr österreichischer Zeit; danach „mehr als die Hälfte“, Vayechi durchgesehen, Master/Kollation neu erzeugt. Die älteren gespeicherten Zähler 169 bzw. 215 ersetzen diesen historischen Fortschritt nicht. Die Chatmeldung allein ist aber kein wiederhergestelltes Einzelprotokoll.

## Problematische Drucklesungen

Zwei jetzt unabhängig am Originaldruck S. 393 bestätigte Wortlaute bleiben offen:

| Stelle | Druckwortlaut | Behandlung |
|---|---|---|
| Tetzaveh 1:1 | אחר נטילת העמידה | Beibehalten; Kontext legt תפילת העמידה nahe. Editorische Prüfung offen. |
| Tetzaveh 7:1 | וגם הנשים נמי מצוה שיטמאו למתים הקרובים | Beibehalten; sachliche Quellenprüfung zu Frauen, Kohanim und מצוה offen. |

Der alte Chat erwähnt zwei problematische Drucklesungen zum Gebetstext und zu Kohanim. **Ob genau diese beiden Stellen damals gemeint waren, ist nicht beweisbar.** Die jetzige Druckprüfung ist deshalb als unabhängig neu gewonnener Befund dokumentiert. Frühere offene Drucklesungen, Fremdwortfragen und der vollständige Errata-Abgleich S. 413–415 bleiben zusätzlich offen.

## Technische Schutzprüfung

- Alle **1.024 Absatzmarker bytegleich** zum Stand vor diesem Lauf.
- Original-JSON und alle **46 Nakdan-Dateien unverändert**.
- Genau **vier dokumentierte einzelne Buchstabenänderungen** gegenüber dem Shemot-Master; alle übrigen Unterschiede sind Nikud. IDs, Reihenfolge, Nummern und Tags unverändert. EN-Felder leer.
- Master: **508 Segmente, 30 Abschnitte, 0 FEHLER, 0 PRÜFEN** in der Strukturprüfung.
- **42 Tests bestanden**: `out/Rekonstruktion_Tests_20261103.txt`.
- Kollation: **TEXT_M / PLUS_M / MINUS_M = 0**, **TEXT_N = 24**, **VOK = 3.173**, **UNVOK_M = 25**. TEXT_N ist durch die 24 aktiven Textkorrekturen erklärt; VOK/UNVOK_M sind keine Freigabezähler.
- Master SHA-256: `c6b90f07fb7f953659b28c28be4c1e5cced60ebeb9ebb618bda8755c3f4fc68c`.

Die ZIP-Teile 017–021 des Originalscans aus `Moriahise/Ben-Jehojada` wurden anhand der Git-Blob-Prüfsummen geprüft. Visuell für diese Befunde gelesen: S. 328, 329, 330, 393 und 394. Weitere heruntergeladene Seiten gelten dadurch nicht als gelesen. Bildkennungen und Prüfsummen stehen in `vokalisierung/Rekonstruktion_Status_20261103.json`.

Exakte Änderungen: `vokalisierung/Rekonstruktion_Aenderungen_20261103.json`. Absatzliste: `vokalisierung/Rekonstruktion_Leseprotokoll_20261103.json`. Vergleichsbasis: `rekonstruktion_20261103/basis_3f2472c/`.

## Verbleibende Rekonstruktionsgrenze

Die vollständige frühere Änderungsliste, das spätere Einzelprotokoll und die damalige Masterdatei liegen nicht vor. Daher lassen sich weder alle damaligen Änderungen zählen noch weitere ungenannte Änderungen sicher ausschließen. Eine bytegenaue vollständige historische Rekonstruktion ist aus den Fortschrittsmeldungen nicht möglich.

Dafür wäre die verlorene Datei, das damalige Änderungsprotokoll oder ein vollständiger Chat-/Werkzeugexport mit den Ersetzungen erforderlich. Eine vollständige erneute sprachliche Prüfung des gesamten möglicherweise betroffenen Textes wäre eine neue Lektoratsleistung; sie wird hier nicht als erledigt ausgegeben.

**Gesichert: alle sechs konkret überlieferten Korrekturarten und drei zusätzliche Fundstellen. Vollständige historische Rekonstruktion: nicht nachweisbar.** Auf Nutzerwunsch Pause nach Sicherung. Reguläre Fortsetzung: Vaera 1:1; zusätzlich Rekonstruktionslücke und offene Befunde beachten.
