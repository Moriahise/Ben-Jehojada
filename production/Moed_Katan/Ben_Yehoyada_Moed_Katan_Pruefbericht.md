# Ben Yehoyada · Moed Katan · Prüfbericht

Stand: 31.10.2026. Datenaufbereitung nach Arbeitsanleitung Fassung 1.5_20261005, Teil A. **Ein vollständiger BILINGUAL-Arbeitsmaster; keine Übersetzung und kein InDesign-Satz.**

## Ergebnis

| Merkmal | Geprüfter Endstand |
|---|---|
| Band | 01 |
| Quellenbelegter Kommentarbereich | Daf 5a–29a |
| Vorhandene Daf-Abschnitte | 16 |
| Segmente | 69; BYH-0000001 bis BYH-0000069 |
| Lemma / Freiform | 69 / 0 |
| Hebräischer Text gegen Senlake | 69/69 wortgleich nach Entfernung der vorgesehenen Ausgabeerklärungen und Markierungen |
| Dicta-Kopfbänder mit ref | 66/69 = 95,7 % |
| Kopfband als unverändertes Senlake-Lemma, ohne ref | 3: BYH-0000010, BYH-0000046, BYH-0000050 |
| Hebräische Fußnoten | 257 |
| Validator | 0 FEHLER; 17 PRUEFEN, einzeln gesichtet |
| Gegenprüfung A–F | jeweils 0 Befunde |
| Mehrteiliges Lemma G | 1: BYH-0000069, gesichtet und unverändert belassen |
| Pipeline-Regressionstests | 23/23 bestanden |
| Matching-Selbsttest | 4/4 bestanden |
| Format | UTF-8 mit BOM, CRLF, CDATA |
| Englische Felder | alle 69 `<en>` und alle 69 `<band_en>` leer; englische Daf-Titel vorhanden |

## Bandplan und Seitenlimit

Die unveränderte Pipeline-Kalibrierung ergibt nach den unten dokumentierten Korrekturen:

| Anteil | Geschätzte Seiten |
|---|---:|
| Textkörper einschließlich Kopfbändern und Fußnotentext | 72,434442 |
| FRONT_MATTER der Pipeline | 16 |
| Summe vor Reserve | 88,434442; aufgerundet 89 |
| Zusätzlich vorgesehene Reserve | 12 |
| Summe mit Reserve | aufgerundet 101 |

Damit bleiben sowohl 588 geschätzte Seiten vor Reserve als auch 600 Seiten einschließlich Reserve eingehalten. Die tatsächliche physische Seitenzahl ist erst nach Übersetzung und Satz feststellbar. Die 16 Seiten FRONT_MATTER sind ein Planungsparameter; die BILINGUAL-Datei enthält keine erfundenen Titel-, Rechte- oder Impressumseiten.

Der Zielwert von etwa 540 Seiten ist kein Mindestumfang. Der vorliegende Quellbestand passt vollständig in einen Band. Eine Auffüllung, eine Teilung oder das Hinzufügen anderer Traktate wäre sachlich unbegründet.

Vorhandene Abschnitte: **5a, 9a, 9b, 11a, 16a, 16b, 17a, 18a, 18b, 21b, 25a, 25b, 26a, 28a, 28b, 29a.** Fehlende Dafim wurden nicht mit erfundenen Segmenten ergänzt. Keine Daf-Gruppe wurde geteilt.

## Eingaben und Versionstreue

Ausgangsstand des Repositorys: `ad42c473351f191013cfe39c827db2960c2660d2`.

Als Textquellen wurden ausschließlich diese beiden Repository-Dateien verwendet:

| Datei | Git-Blob-SHA |
|---|---|
| `Ben Yehoyada on Moed Katan - he - Senlake edition 2019 based on Ben Yehoyada, Jerusalem, 1897.txt` | `2dc3908d4b5372a0aa28cd1b142357f7d1cd7c88` |
| `מועד_קטן.combinedfullhaser.txt` | `ca5d48d19cfbd48206b001cba68eb7c88655c82a` |

Die unveränderten Bytes wurden vor dem Lauf anhand der Git-Blob-SHAs geprüft. Die Rohdateien bleiben unverändert. Keine externe Talmudquelle, kein fremder englischer Text und keine API-Abfrage wurde für den Textbestand verwendet. Die vom Pipeline-Code historisch verwendete Bezeichnung „Sefaria-Mapping“ bezeichnet hier ausschließlich die lokale Zuordnung zur angegebenen Dicta-Datei.

| Produktionsgrundlage | Git-Blob-SHA |
|---|---|
| `ben-yehoyada-pipeline-v3_2_1_2026-10-05.zip` | `2eab4448a8e1e0beec0c9cc2304e6154f06d95f5` |
| `Ben_Yehoyada_Arbeitsanleitung_AKTUELL_Fassung1.5_20261005.txt` | `e9f9b020e15c4b9d065bec795a58a686bb17ed08` |
| ursprüngliche `glossary_he.json` | `8e19ce5fe164897ad0ad5c5ca6cb37d6448fcc5f` |

Parameter: `--tractate 'Moed Katan' --band-words 42 --band-en empty --sample-daf 9a --glossary <Repository>/glossary_he.json`. Für Moed Katan liegt im freigegebenen Paket keine Quellkorrekturdatei vor; es wurde keine erfunden oder auf die Rohquelle angewandt. Alle Python-Dateien des Pakets bleiben unverändert. Eine lokale Ergänzung der dafür vorgesehenen `band_overrides.json` korrigiert BYH-0000009; siehe `band_overrides_Moed_Katan.json`.

Die Schätzung wird erst nach Zuordnung und den belegten Schlusskorrekturen berechnet. `Quellenmanifest.json` enthält zusätzlich die SHA-256-Prüfsummen sämtlicher Eingaben und des fertigen Masters.

## Lektorat und dokumentierte Schlusskorrekturen

Automatische Prüfungen bestätigen Texttreue und Struktur, ersetzen aber keine inhaltliche Zuordnung. Zwei fast gleichlautende Bibelzitate bzw. Segensaufforderungen benötigen eine Kontextentscheidung.

| Segment | Befund und Entscheidung |
|---|---|
| BYH-0000009, 9a.6 | Der zunächst automatisch gewählte Vers in Dicta 9a:15 steht im Bericht über Tempelweihe und Jom Kippur. Der Kommentar behandelt dagegen den erneuten Abschied der Schüler am Morgen und ihre Quellenangabe. Die Antwort der Schüler mit demselben Vers steht tatsächlich in Dicta **9a:21**. Dieser belegte ref wird über den vorgesehenen Override eingetragen. Kopfband direkt aus diesem Dicta-Segment; Senlake-Daf, Absatz, Lemma und Kommentar unverändert. |
| BYH-0000010, 9a.7 | Die automatische Wahl **9b:8** betrifft R. Shimon ben Halafta und Rav; der Kommentar behandelt R. Shimon ben Yohai und seinen Sohn. Der passende Kontext steht in Dicta **9a:23**, mit abweichenden Präfixen `זיל גביהון דליברכוך`. Der unveränderte Wortlautprüfer erreicht dort nur 0,333 Deckung und würde die Zuordnung blockieren. Konservative Lösung im fertigen Master: vorhandenes Senlake-Lemma als Kopfband, **kein ref**. Der Kontextbeleg bleibt hier und im Audit dokumentiert; er wird nicht als wortidentische Dicta-Zuordnung ausgegeben. |
| BYH-0000004 | In `דף למ"ד ע"א` ist למ"ד die Blattzahl 30. Fußnote `הָאוֹת ל` durch `מִסְפָּר 30` ersetzt. Das Kürzel im Kommentar bleibt unverändert. |
| BYH-0000020 | Senlake erklärt `[416]` erst bei `עולה מספר תי"ו ... במילואה`. Die Automatik setzte diese Zahl am ersten Vorkommen `תי"ו תחיה`. Dieselbe Fußnote wird hinter den dritten Beleg nach `עולה מספר` verschoben; keine Zahl hinzuerfunden und kein Kommentartext geändert. |
| BYH-0000046 | Die automatische Auflösung `הרי"ף = רבנו יצחק אלפסי` ist durch die beiden Quellen hier nicht abgesichert. Diese Fußnote entfernt; `הרי"ף` im Kommentar erhalten. Keine andere Person eingesetzt. |
| BYH-0000069 | `רבינו מהר"ם אלשיך` verwendet die bereits im Repository-Glossar dokumentierte alternative Lesart Moshe. Fußnote mit Meir durch Moshe ersetzt. Der Name Alshich bleibt im Quelltext stehen. |

Der ursprüngliche Pipeline-Rohlauf mit aktuellem Glossar und dem Override zu BYH-0000009 ist als `Audit/Pipeline_Rohmaster.txt` und `Audit/Pipeline_Rohbericht.txt` aufbewahrt. Die dortigen **67 automatischen Dicta-Zuordnungen und 258 Fußnoten** beschreiben den Zwischenstand. Maßgeblich sind die abschließend geprüften **66 Dicta-Zuordnungen und 257 Fußnoten** im fertigen Master. Das ist keine stillschweigende Gleichsetzung der beiden Stände.

Nach dem Rohlauf wurden genau sechs Felder geändert: `band_he` und Entfernung des `ref` bei BYH-0000010 sowie jeweils das Fußnoten enthaltende `he` bei BYH-0000004, 0000020, 0000046 und 0000069. Nach Entfernung der Fußnoten bleibt jedes `he` quellenidentisch. Alle Lemmata, BYH-IDs, n/daf-Werte, Daf-Titel, englischen Felder und übrigen Feldinhalte bleiben unverändert. Der Feldvergleich wird maschinell gegen diese erlaubte Änderungsliste geprüft (`Audit/Feldvergleich.json`).

Die beiden ursprünglichen Lemma-Rückfälle bleiben erhalten:

| Segment | Quellenbefund |
|---|---|
| BYH-0000046, 18b.5 | Senlake: `מלמד שחשדוהו מאשת איש`. Dicta 18b:18 behandelt die entsprechende Verdächtigung Mosches, formuliert aber `מלמד שכל אחד קינא לאשתו ממשה`. Die Pipeline findet keine ausreichend wortgleiche Zuordnung; im Master bleibt das Senlake-Lemma ohne ref. |
| BYH-0000050, 25b.1 | Senlake: `אי בדינא דידי, גברא בר גברא ניעול ברישא`. Dicta 25b:1 erzählt den zugehörigen Vorgang am Übergang mit den Kamelen, hat aber deutlich anderen Wortlaut. Kein ref konstruiert; Lemma-Rückfall bleibt. |

BYH-0000002 trägt weiterhin den Senlake-Daf **5a** und den aus Dicta belegten ref **5b:1**. Die Formel `קרי עליה ושם דרך...` und die Erzählung vom Schüler und dem Vortrag bestätigen die Nachbarblattzuordnung. Kommentar-Daf und Dicta-ref werden nicht künstlich angeglichen.

## Einzelprüfung der 17 PRUEFEN-Fälle

Die Meldungen bleiben im originalen Validatorbericht sichtbar. Sie wurden nicht gelöscht oder durch niedrigere Prüfgrenzen unterdrückt.

| BYH-Endziffern | Dicta-ref im Master | Sichtbefund |
|---|---|---|
| 0000003 | 5a:23 | Senlake ergänzt `בעולם הזה`; die Auslegung von Weg und Erlösung passt zum belegten Ausspruch. |
| 0000005 | 9a:18 | `זה בזה` gegenüber `זה לזה`; Torwunder identisch. |
| 0000007 | 9a:18 | Senlake zitiert den Psalm weiter aus; Dicta kürzt ihn nach `שאו שערים ראשיכם` mit `וגו'`. Quelle nicht ergänzt. |
| 0000009 | 9a:21 | Quellenangabe und Zitierformel weichen ab; Erzählkontext über den zweiten Abschied durch Override richtiggestellt. |
| 0000011 | 9b:2 | `הדור יתבי וקא מיבעיא להו` gegenüber `הדר יתבי וקא מבעי להו`; zweite Frage zu Torah und Mizwot. |
| 0000013 | 9b:5 | `אלא צעורי צערו לי` gegenüber `אבל צעורי צערן`; dieselbe vermeintliche Verwünschung und folgende Auslegung. |
| 0000015 | 9b:12 | `קבורתה` gegenüber `קברה`; Kommentar zur Greisin passt. |
| 0000017 | 16a:3 | Freiere Frageform, `שלוחא דבית דין` gegenüber `שליחא דבי דינא`; richtige gerichtliche Vorladung. |
| 0000022 | 16a:23 | Lemma reicht über die Dicta-Blattgrenze: `מה ירך בסתר` am Ende 16a:23, `אף דברי תורה בסתר` als 16b:1. Das Kopfband bleibt ein zusammenhängender Ausschnitt aus 16a:23; kein erfundener zusammengesetzter ref. Vollständiges Lemma und Kommentar erhalten. Bei der Übersetzung Unterschied nach Regel 53d beachten. |
| 0000023 | 16b:2 | Senlake ergänzt `ראה` und formuliert `מבחוץ`; Rabbi und R. Hiyya sowie die Namensauslegung stimmen im Kontext überein. |
| 0000039 | 18a:8 | `עלייהו` gegenüber `עליהן`, weitere Vokalisierungsvariante; dieselbe Fingernagelstelle. |
| 0000043 | 18b:12 | `שדה פלונית` gegenüber `שדה פלוני`; der Kommentar bezeichnet die eigene Lesart ausdrücklich als die hiesige Fassung. |
| 0000048 | 25a:21 | `זקף ארוניה` gegenüber `זקפה לארונה`; gleicher Sargvorgang und dieselbe Verschonung. |
| 0000049 | 25a:15 | `דלויי רישין / אתי ליה בתרין` gegenüber `דלויי רישין / אתא בתרין`; R. Ammi und R. Assi beim Heraufbringen Rav Hunas. |
| 0000055 | 25b:7 | `אתי דגלת` gegenüber `אתא לדגלת`; Kommentar erläutert den Gang zum anschwellenden Tigris. |
| 0000065 | 28a:22 | Präfix- und Vokalisierungsvarianten bei `דחקת רגליה`; gleiche Geschichte über Rav Ashi und Bar Natan. |
| 0000067 | 28b:10 | `די לא ידל` gegenüber `דלא ידל`; Wortformvariante des Spruchs. |

Das mehrteilige Lemma BYH-0000069 endet nach dem vollständigen Spruch über Synagoge, Lehrhaus und Empfang der Schekhina. Der anschließende unvokalisierte Kommentar beginnt `יש להקשות`; er ist nicht ins Lemma geraten. Das abschließende `/` steht so in der Senlake-Auszeichnung und wurde nicht stillschweigend in ein anderes Satzzeichen umgewandelt.

## Glossaraktualisierung

`glossary_he.json` wurde im Repository aktualisiert: **279 globale Abkürzungseinträge bleiben erhalten; keine neue pauschale Auflösung.** `_meta.stand` dokumentiert den Moed-Katan-Lauf und seine Belege. Die bestehenden `alt`-Hinweise bei **למ"ד, מהר"ם und הרי"ף** enthalten jetzt die im Band geprüften Kontexte. Die globalen Hauptlesarten und `letter_names` bleiben unverändert. Eine vermeintliche Verbesserung der Trefferquote durch unsichere Ergänzungen wurde vermieden.

Die automatische Trefferquote bleibt **181/191 = 94,8 %**. Das ist ein Parser-/Glossarwert vor der Kontextkorrektur und kein Nachweis, dass jede automatische Fußnote sachlich richtig war; die oben dokumentierte Fußnotensichtprüfung ergänzt ihn.

| Offen erkanntes Token | Beleg | Entscheidung |
|---|---|---|
| ההי"ן | BYH-0000003, `במלוי ההי"ן` | Buchstabenform/Füllung; keine globale Abkürzungsauflösung. |
| דלתי"ן | BYH-0000005, `שני דלתי"ן` | Plural des Buchstabennamens. |
| ט"ו | BYH-0000006, `ט"ו שיר המעלות` | Zahl 15 im Kontext; kein neuer Glossareintrag nötig. |
| ט"ל | BYH-0000007, `ט"ל אותיות` | Zahl 39 im Kontext. |
| למ"ח | BYH-0000022, `למ"ח מעלות` | Präfix plus Zahl 48 im Kontext. |
| אב"ג | BYH-0000032, `שיום אב"ג` | Die ersten drei Wochentage als Buchstabengruppe, kein allgemeines Akronym. |
| זרנטא"ח | BYH-0000032, `בתולע שקורין בלשון ערבי` | Arabisches Wort; vom Autor selbst kontextuell erklärt. |
| כ"ס | BYH-0000032, `חזרת שנקרא חסא ובערבי כ"ס` | Arabisches Wort für die genannte Pflanze; keine hebräische Abkürzung. |
| שי"ץ | BYH-0000056, `תמרים רעים שקורין בערבי` | Arabisches Wort; Erklärung bleibt im Kommentar. |
| פ"א | BYH-0000058, `אדרת אליהו דף פ"א` | Blattzahl 81; nicht pauschal „einmal“ oder „Kapitel 1“. |

Da keine neue globale Auflösung eingeführt wurde, wird hier auch keine neu durchgeführte Gesamtkorpusprüfung anderer Traktate behauptet. Die Ergänzungen protokollieren belegte Einzelkontexte und bereits vorhandene Alternativlesarten.

## Muster und verbleibender Satzschritt

Die HTML-Musterdatei für Daf 9a wurde nach der Kontextentscheidung neu erzeugt und inhaltlich gelesen. Eine optische Browserkontrolle war in dieser Umgebung nicht möglich, weil kein Chromium-/Browserprogramm installiert ist. Der HTML-Proof verwendet die unveränderte Pipeline-Typografie mit optionalen Google-Fonts-Verweisen; er ist keine geprüfte Druckausgabe. Es wurde keine Schrift stillschweigend als Produktionsschrift freigegeben.

Für die Übersetzung sind die 17 Wortlautunterschiede, die drei Lemma-Rückfälle und insbesondere die Blattgrenze bei BYH-0000022 zu beachten. Englisch bleibt nach Anleitung in diesem Produktionsschritt leer. InDesign-Aufbau, tatsächliche Seitenzahl, Dividergrenzen, HE/EN-Daf-Synchronität und druckfertige PDF wurden nicht als bereits durchgeführt ausgegeben.

## Wiederholung und Dateien

Vom Repository-Hauptverzeichnis aus:

```bash
python3 production/Moed_Katan/produzieren.py
```

Das Skript entpackt bei jedem Lauf das freigegebene ZIP neu, prüft die Quellen-Prüfsummen, ergänzt nur die dokumentierte Override-Konfiguration, ruft die unveränderte Pipeline auf, führt die kontrollierten Schlusskorrekturen aus und berechnet Bandplan, Validator, Gegenprüfung sowie Tests neu. Es verändert weder Quelldateien noch Pipeline-Archiv. Für bytegleiche Wiederholung muss der in `Quellenmanifest.json` protokollierte Glossarstand verwendet werden. Der Prüfbericht selbst ist der redaktionelle Befund dieses Laufs und wird vom Skript nicht überschrieben.

Der freigegebene Arbeitsmaster heißt ausschließlich **`Ben_Yehoyada_Moed_Katan_Band_01_BILINGUAL.txt`**. `Audit/Pipeline_Rohmaster.txt` ist ein technischer Zwischenstand und nicht für InDesign oder Übersetzung zu verwenden.

SHA-256 des Arbeitsmasters: `78d5ca3ae42dad9fac5630bed008e88243686cf1d01e1b49d303bea8372daf86`.
