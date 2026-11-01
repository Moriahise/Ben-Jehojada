# -*- coding: utf-8 -*-
"""
Kopfband-Zuordnung und -Ausschnitt  (Korrektur der Logik aus by_sefaria.py)

WARUM DIESES MODUL EXISTIERT
----------------------------
Die urspruengliche Mechanik hatte zwei voneinander unabhaengige Schwaechen.
Beide fuehren zu einem Kopfband, das die zitierte Stelle nicht enthaelt.

(A) SEGMENTWAHL — "erster Treffer" statt "bester Treffer".
    `match_lemma` arbeitete in Stufen und nahm in jeder Stufe das ERSTE
    Segment, das die Bedingung erfuellte. Die Stufe `headwords` prueft nur
    die ersten vier Woerter. Zwei Gebete auf Berachot 16b beginnen beide mit
    "יהי רצון מלפניך ה'" — das erste gewinnt, obwohl das Lemma das zweite
    meint. Gleiches Muster bei jedem formelhaften Satzanfang
    ("עליו הכתוב אומר", "אמר ליה", "תנו רבנן").

(B) AUSSCHNITT — Anker auf drei Woertern, erstes Vorkommen.
    `trim_band` suchte die ersten drei Lemma-Woerter und schnitt ab dort
    42 Woerter. Steht dieselbe Wendung frueher im Segment noch einmal,
    ankert das Fenster an der falschen Stelle. Berachot 20a:4 enthaelt
    "לא קא מסתפי מר מיצר הרע" und spaeter "לא קא מסתפי מר מעינא בישא";
    gefragt ist die zweite, gekuerzt wurde auf die erste. Scheitern die drei
    Woerter ganz — etwa weil der Ben Jehojada aramaeisch paraphrasiert
    ("והלין בני מתא מחסיא" gegen "בני מתא מחסיא") — fiel die Funktion
    stillschweigend auf die ersten 42 Woerter des Segments zurueck.

DIE KORREKTUR
-------------
Beide Fragen werden von EINER Messung beantwortet: der Ausrichtung des
vollstaendigen Lemmas auf die Wortfolge des Segments (`align_lemma`).
Sie liefert Deckung, Anfang und Ende der zitierten Passage im Segment.

  * Segmentwahl: das Segment mit der hoechsten Deckung des GANZEN Lemmas
    gewinnt — alle Kandidaten werden gemessen, keine Stufe bricht frueh ab.
  * Ausschnitt: das Fenster beginnt `lead` Woerter vor dem ersten und endet
    hinter dem letzten ausgerichteten Wort. Die Wortgrenze wird dabei
    ueberschritten, wenn die Passage laenger ist — sie ist eine Zielgroesse,
    keine Schranke.
  * Wer nicht sicher zugeordnet werden kann, wird als `review` markiert
    statt mit einem plausiblen Fehltreffer gefuellt.

Die Ausrichtung arbeitet auf Skelettformen (ohne Nikud, ohne Lesemuetter),
weil der Ben Jehojada defektiv zitiert, wo der Talmudtext plene schreibt.
"""
import difflib
import os
import re
import unicodedata

NIKUD = re.compile(r'[֑-ׇ]')
TAGS = re.compile(r'<[^>]+>')
PAREN = re.compile(r'\([^)]*\)')
NONHEB = re.compile(r'[^א-ת ]')
# Schlusszeichen, die ein Kuerzel markieren: Gershajim in beiden Schreibungen.
ABBR_TOKEN = re.compile(r'[א-ת]+["״][א-ת]')

# Endbuchstaben -> Grundform. Zusaetzlich faellt die Unterscheidung
# ם/ן am Wortende weg: hebraeisch "צְנוּעִים בַּאֲכִילָתָם" gegen aramaeisch
# "צְנוּעִין בַּאֲכִילָתָן" ist derselbe Wortlaut, und der Ben Jehojada wechselt
# zwischen beiden Formen. Ohne diese Angleichung faellt die Deckung solcher
# Stellen auf null — Berachot 8b:6 war genau so ein Fall.
FINALS = {'ך': 'כ', 'ם': 'ן',
          'ף': 'פ', 'ץ': 'צ',
          # Auch der Wechsel zwischen auslautendem He und Alef faellt weg:
          # hebraeisch אַכְסַדְרָה gegen aramaeisch אַכְסַדְרָא, גְּמָרָא gegen גְּמָרָה.
          # Der Ben Jehojada und die Dicta-Ausgabe waehlen hier nicht dieselbe
          # Form, und an diesem einen Buchstaben scheiterte sonst die
          # Ausrichtung ganzer Stellen (Berachot 10b:5).
          'ה': 'א'}

# Deckungsgrad, ab dem eine Zuordnung als gesichert gilt.
COV_SAFE = 0.60
# Darunter wird zugeordnet, aber zur Handpruefung markiert.
COV_MIN = 0.34
# Absolute Obergrenze fuer das Kopfband, damit ein Ausreisser die Seite
# nicht sprengt. Greift nur, wenn die Passage selbst laenger ist.
BAND_HARD_CAP = 130


_GLOSS = None


def _glossary():
    """Die kuratierte Abkuerzungstabelle, einmal geladen. Fehlt sie, wird
    ohne Aufloesung gearbeitet — die Zuordnung wird dann nur unschaerfer."""
    global _GLOSS
    if _GLOSS is None:
        try:
            from by_glossary import Glossary
            _GLOSS = Glossary()
        except Exception:
            _GLOSS = False
    return _GLOSS or None


def _prefix_alt(g, core):
    """
    Zweitlesung eines Kuerzels ueber die Praefix-Abtrennung.

    Noetig fuer die Faelle, in denen ein Buchstabenname und ein Akronym
    zusammenfallen: "למ״ד" ist der Buchstabe Lamed und zugleich die Kurzform
    von "למאן דאמר". Im Kommentar ueberwiegt der Buchstabe, im Dibbur
    ha-Matchil ("בשלמא למ״ד אכסדרא") ist es das Akronym. Statt eine der
    beiden Lesarten zu erzwingen, wird auch diese Variante gemessen.
    """
    try:
        from by_glossary import norm as gnorm
    except Exception:
        return None
    n = gnorm(core)
    for p in ('ו', 'ש', 'ל', 'ב', 'כ', 'מ', 'ה', 'ד'):
        if n.startswith(p) and len(n) > len(p) + 2:
            r = g.idx.get(gnorm(n[len(p):]))
            if r and r.get('he'):
                return r['he']
    return None


def expand_abbrev(s, alt=False):
    """
    Loest Kuerzel im Lemma auf, bevor verglichen wird.

    Der Ben Jehojada kuerzt im Dibbur ha-Matchil, der Talmudtext schreibt aus:
    "שֶׁרִוּוּהוּ לְהַקָּבָּ"ה" gegen "שֶׁרִוָּהוּ לְהַקָּדוֹשׁ בָּרוּךְ הוּא",
    "בִּשְׁלָמָא לְמַ"דְ" gegen "בִּשְׁלָמָא לְמַאן דְּאָמַר". Ohne Aufloesung
    fehlen dem Vergleich genau die Woerter, die die Stelle identifizieren,
    und ein richtig zugeordnetes Kopfband sieht in der Pruefung falsch aus.
    """
    g = _glossary()
    if not g:
        return s
    out = []
    for tok in (s or '').split():
        # Der Vokalisierungstest muss ohne Nikud laufen: im Lemma steht
        # לְמַ"דְ, nicht למ"ד — mit Vokalzeichen zwischen Buchstabe und
        # Gershajim greift das Muster sonst nie.
        bare = NIKUD.sub('', unicodedata.normalize('NFC', tok))
        if ABBR_TOKEN.search(bare):
            core = bare.strip('.,:;?!()[]"״’\'')
            r = None
            try:
                if alt:
                    a = _prefix_alt(g, core)
                    r = {'he': a} if a else g.resolve(core)
                else:
                    r = g.resolve(core)
            except Exception:
                r = None
            if r and r.get('he'):
                # Die Praefix-Abtrennung liefert "לה + Stamm"; das Pluszeichen
                # ist Darstellung, kein Wort.
                out.append(r['he'].replace('+', ' '))
                continue
        out.append(tok)
    return ' '.join(out)


def norm_he(s):
    """Vergleichsform: ohne Nikud, ohne Tags, ohne Klammerverweise."""
    s = unicodedata.normalize('NFC', s or '')
    s = TAGS.sub(' ', s)
    s = PAREN.sub(' ', s)
    s = NIKUD.sub('', s)
    s = NONHEB.sub(' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def skeleton(s):
    """
    Vergleichsebene: ohne Lesemuetter, mit angeglichenen Endbuchstaben.

    Die Lesemuetter fallen weg, weil der Ben Jehojada defektiv zitiert, wo
    der Talmudtext plene schreibt (גְּאֻלָּה gegen גאולה).
    """
    words = []
    for w in norm_he(s).split():
        w = re.sub(r'[וי]', '', w)
        if w:
            words.append(w[:-1] + FINALS.get(w[-1], w[-1]))
    return ' '.join(words)


def sk_words(s, expand=False, alt=False):
    """Wortliste in Skelettform — die Vergleichsebene fuer die Ausrichtung."""
    if expand:
        s = expand_abbrev(s, alt=alt)
    return [w for w in skeleton(s).split() if w]


def lemma_variants(lemma):
    """
    Die Lesarten eines Lemmas, in denen es im Talmudtext stehen koennte:
    wie geschrieben, mit aufgeloesten Kuerzeln, und mit der Zweitlesung
    mehrdeutiger Kuerzel. Verglichen wird gegen alle; die beste zaehlt.
    """
    out, seen = [], set()
    for v in (sk_words(lemma),
              sk_words(lemma, expand=True),
              sk_words(lemma, expand=True, alt=True)):
        key = ' '.join(v)
        if v and key not in seen:
            seen.add(key)
            out.append(v)
    return out


def align_detail(lemma, segment):
    """
    Richtet das vollstaendige Lemma auf ein Segment aus.

    Rueckgabe: (deckung, erstes_wort, letztes_wort, zusammenhang)

      deckung      Anteil der Lemma-Woerter, die im Segment wiederkehren (0..1)
      erstes_wort  Index des ersten ausgerichteten Segmentworts
      letztes_wort Index des letzten ausgerichteten Segmentworts
      zusammenhang Anteil der laengsten geschlossenen Uebereinstimmung an der
                   Gesamtdeckung — trennt eine echte Zitatstelle von zufaellig
                   verstreuten Allerweltswoertern ("אמר", "ליה", "כי")

    difflib liefert die Uebereinstimmungen in Reihenfolge und beginnt mit dem
    laengsten Block. Genau daran haengt die Korrektur: kommt eine Wendung
    mehrfach vor, gewinnt die Stelle mit der laengeren Uebereinstimmung —
    also die, an der das Lemma wirklich steht.
    """
    sw = sk_words(segment)
    if not sw:
        return 0.0, None, None, 0.0, 0

    # Kuerzel werden versuchsweise aufgeloest, aber nie blind: manche sind
    # mehrdeutig. "למ״ד" ist der Buchstabenname Lamed UND die Kurzform von
    # "למאן דאמר"; "נו״ן" schreibt der Talmud als Wort aus. Deshalb wird
    # beides gemessen — mit und ohne Aufloesung — und die bessere Ausrichtung
    # gilt. Die Aufloesung kann so nur helfen, nie schaden.
    best = (0.0, None, None, 0.0, 0)
    for lw in lemma_variants(lemma):
        if not lw:
            continue
        sm = difflib.SequenceMatcher(None, lw, sw, autojunk=False)
        blocks = [x for x in sm.get_matching_blocks() if x.size > 0]
        if not blocks:
            continue
        matched = sum(x.size for x in blocks)
        longest = max(x.size for x in blocks)
        cov = matched / float(len(lw))
        if cov > best[0]:
            best = (cov, blocks[0].b,
                    blocks[-1].b + blocks[-1].size - 1,
                    longest / float(matched), longest)
    return best


def align_lemma(lemma, segment):
    """Wie align_detail, ohne die absolute Laenge des laengsten Blocks."""
    cov, a, b, contig, _longest = align_detail(lemma, segment)
    return cov, a, b, contig


MIN_RUN = 2


def acceptable(lemma, segment, cov=None):
    """
    Darf diese Zuordnung stehenbleiben?

    Eine niedrige Deckung allein ist kein Ausschlussgrund — der Ben Jehojada
    zitiert frei, und Berachot 35b:5 ("בא וראה שלא כדורות הראשונים" gegen
    "בא וראה מה בין דורות ראשונים") ist mit 0,38 Deckung trotzdem die richtige
    Stelle. Entscheidend ist, ob wenigstens eine zusammenhaengende Wortfolge
    uebereinstimmt. Fehlt die, stammt die Deckung aus verstreuten
    Allerweltswoertern und die Stelle ist geraten: so kam Berachot 10a:20
    ("קרי אנפשיה וכלי כליו רעים" — ein Jesajavers, der im Talmud gar nicht
    steht) an das Kopfband von 10a:1.
    """
    c, a, b, contig, longest = align_detail(lemma, segment)
    if cov is None:
        cov = c
    if cov < COV_MIN:
        return False
    return longest >= MIN_RUN or cov >= COV_SAFE


def score_segment(lemma, segment):
    """
    Bewertet einen Kandidaten.

    Drei Groessen gehen ein:
      Deckung      wie viel des Lemmas ueberhaupt wiederkehrt — traegt die
                   Entscheidung
      Zusammenhang ob die Treffer einen Block bilden oder verstreut liegen
      Dichte       ueber wie viele Segmentwoerter sich die Treffer verteilen

    Die Dichte ist noetig, weil Dicta sehr lange Segmente kennt. Berachot 7a:1
    umfasst ueber 700 Woerter; ein vierwoertiges Lemma wie
    "ואין עזו אלא תפילין" findet darin seine Woerter zwangslaeufig irgendwo
    verstreut und gewann so gegen 6a:6, wo die Wendung wirklich steht. Ein
    Zitat ist kompakt — Treffer quer durch ein halbes Blatt sind Rauschen.
    """
    cov, a, b, contig = align_lemma(lemma, segment)
    if a is None:
        return 0.0, None, None, 0.0
    L = max(1, len(sk_words(lemma)))
    span = max(1, b - a + 1)
    # Der Spielraum ist bewusst grosszuegig: ein Lemma darf Anfang UND Ende
    # einer laengeren Passage zitieren und dazwischen Text ueberspringen —
    # Berachot 17a:2 zitiert den Anfang des Gebets und seinen Schluss, 51
    # Woerter auseinander. Erst weit darueber hinaus wird aus Ausrichtung
    # Zufall: auf 7a:1 verteilen sich vier Lemma-Woerter ueber 600.
    allowance = max(3 * L, L + 60)
    density = min(1.0, float(allowance) / span)
    return cov * (0.70 + 0.30 * contig) * (0.35 + 0.65 * density), a, b, cov


def best_segment(lemma, segments):
    """
    Waehlt unter allen Segmenten das mit der besten Ausrichtung.

    Anders als die alte Stufenlogik bricht hier nichts frueh ab: jedes
    Segment wird gemessen, erst danach faellt die Entscheidung.
    """
    best = (None, -1.0, None, None, 0.0)      # idx, score, a, b, cov
    for i, s in enumerate(segments):
        sc, a, b, cov = score_segment(lemma, s)
        if sc > best[1]:
            best = (i, sc, a, b, cov)
    idx, sc, a, b, cov = best
    if idx is None or cov <= 0:
        return None, 0.0, None, None, 0.0
    return idx, sc, a, b, cov


# Vorsprung, den ein Nachbarblatt haben muss, um das eigene Blatt zu schlagen.
NEIGHBOUR_MARGIN = 0.15


def choose_place(lemma, pages):
    """
    Waehlt Blatt und Segment.

    `pages` ist eine Liste (daf, segmente); der erste Eintrag ist das Blatt,
    das der Ben Jehojada selbst angibt.

    Die Blattangabe des Ben Jehojada ist starke Evidenz und wird nicht leicht
    aufgegeben. Konkret:

      * Sitzt das Lemma auf dem eigenen Blatt sicher (Deckung >= COV_SAFE),
        werden die Nachbarblaetter gar nicht erst befragt. Ohne diese Sperre
        gewinnt eine spaetere Gemara-Zitierung des Mischnasatzes gegen die
        Mischna selbst — bei Berachot 2a:1 ("מאימתי קורין את שמע") genau der
        Fall, weil der Ben Jehojada "בערבית" schreibt, wo die Mischna
        "בערבין" hat, und die Gemara auf 2b die Form des Kommentars trifft.
      * Andernfalls muss ein Nachbarblatt das eigene um NEIGHBOUR_MARGIN
        Deckung uebertreffen. Nur dann verschiebt sich die Zuordnung.
    """
    own_daf, own_segs = pages[0]
    o_idx, o_sc, o_a, o_b, o_cov = best_segment(lemma, own_segs) if own_segs \
        else (None, 0.0, None, None, 0.0)

    if o_idx is not None and o_cov >= COV_SAFE:
        return own_daf, o_idx, o_cov, False

    best = (own_daf, o_idx, o_cov)
    for daf, segs in pages[1:]:
        if not segs:
            continue
        i, sc, a, b, cov = best_segment(lemma, segs)
        if i is None:
            continue
        if cov >= best[2] + NEIGHBOUR_MARGIN:
            best = (daf, i, cov)
    if best[1] is None:
        return None, None, 0.0, False
    return best[0], best[1], best[2], best[0] != own_daf


def method_of(lemma, segment, cov):
    """Beschreibt, wie sicher der Treffer ist — fuer Bericht und Lektorat."""
    S, SS = norm_he(segment), skeleton(segment)
    for variant in (lemma, expand_abbrev(lemma), expand_abbrev(lemma, alt=True)):
        if norm_he(variant) and norm_he(variant) in S:
            return 'contains'
    for lw in lemma_variants(lemma):
        vs = ' '.join(lw)
        if vs and vs in SS:
            return 'skeleton'
    if cov >= COV_SAFE:
        return 'aligned'
    return 'review'


def cut_band(segment, lemma, max_words=42, lead=6, hard_cap=BAND_HARD_CAP):
    """
    Schneidet das Fenster um die zitierte Passage.

    Kernregel: das Fenster endet NICHT vor dem Ende der zitierten Passage.
    `max_words` ist die Zielgroesse fuer den Normalfall; enthaelt das Lemma
    mehr Text, waechst das Band mit. Ohne diese Regel bricht das Kopfband
    mitten im Zitat ab — bei Berachot 20a:4 vor der Frage nach dem boesen
    Blick, auf die der Kommentar sich bezieht.

    Rueckgabe: (text, info) — info dokumentiert die Entscheidung.
    """
    words = segment.split()
    n = len(words)
    cov, a, b, contig = align_lemma(lemma, segment)

    if a is None:
        # Keine Ausrichtung moeglich: Segmentkopf, aber sichtbar markiert.
        text = segment if n <= max_words else ' '.join(words[:max_words]) + ' …'
        return text, {'anchor': None, 'coverage': 0.0, 'words': min(n, max_words),
                      'extended': False, 'truncated_lemma': True}

    start = max(0, a - lead)
    end = max(start + max_words, b + 1)        # Passage immer vollstaendig
    if end - start > hard_cap:
        end = start + hard_cap
    end = min(n, end)
    truncated = end < b + 1                    # nur bei Ueberschreiten des Caps

    # Steht die Passage am Segmentende, waere das Band sonst nur ein Stummel.
    # Dann nach vorne auffuellen, damit der Leser Anlauf hat.
    if end - start < max_words and end >= n:
        start = max(0, end - max_words)

    out = ' '.join(words[start:end])
    if start > 0:
        out = '… ' + out
    if end < n:
        out = out + ' …'
    return out, {'anchor': a, 'coverage': round(cov, 3),
                 'words': end - start,
                 'extended': (end - start) > max_words,
                 'truncated_lemma': truncated}


def band_contains_lemma(band, lemma, need=0.85):
    """
    Abnahmeprüfung: steckt die zitierte Passage wirklich im Kopfband?
    Genau diese Frage blieb bisher ungeprueft — deshalb fielen die
    Fehlzuordnungen erst beim Uebersetzen auf.
    """
    lw = sk_words(lemma, expand=True)
    if not lw:
        return True, 1.0
    cov, a, b, contig = align_lemma(lemma, band)
    return cov >= need, round(cov, 3)


# ------------------------------------------------------------------ Selbsttest
def _selftest():
    """Die vier echten Fehlerfaelle aus Berachot als Regressionstest."""
    ok = True

    # (1) Wendung kommt zweimal vor — das Fenster muss an der zweiten ankern.
    seg20a = ('רַב גִּדֵּל הֲוָה רְגִיל דַּהֲוָה קָא אָזֵל וְיָתֵיב אַשַּׁעֲרֵי דִטְבִילָה אֲמַר לְהוּ הָכִי טְבִילוּ וְהָכִי '
              'טְבִילוּ אָמְרִי לֵהּ רַבָּנַן לָא קָא מִסְתְּפֵי מָר מִיֵּצֶר הָרָע אֲמַר לְהוּ דָּמְיָן בְּאַפַּאי כִּי קָאקֵי '
              'חִוָּרֵי רַבִּי יוֹחָנָן הֲוָה רְגִיל דַּהֲוָה קָא אָזֵל וְיָתֵיב אַשַּׁעֲרֵי דִטְבִילָה אֲמַר כִּי סָלְקָן בְּנוֹת '
              'יִשְׂרָאֵל וְאָתְיָן מִטְּבִילָה מִסְתַּכְּלָן בִּי וְנֶהֱוֵי לְהוּ זַרְעָא דְּשַׁפִּירֵי כְּוָתִי אָמְרִי לֵהּ רַבָּנַן '
              'לָא קָא מִסְתְּפֵי מָר מֵעֵינָא בִּישָׁא אֲמַר לְהוּ אֲנָא מִזַּרְעָא דְּיוֹסֵף קָא אָתֵינָא')
    lem20a = 'לָא קָא מִסְתַּפִי מַר מֵעֵינָא בִּישָׁא?'
    band, info = cut_band(seg20a, lem20a)
    t1 = 'מֵעֵינָא בִּישָׁא' in band
    ok &= t1
    print('  [1] zweites Vorkommen geankert   -> {} Woerter, Deckung {}  {}'
          .format(info['words'], info['coverage'], 'OK' if t1 else 'FEHLER'))

    # (2) Aramaeische Paraphrase am Lemma-Anfang: frueher Totalausfall.
    seg17b = ('שִׁמְעוּ אֵלַי אַבִּירֵי לֵב הָרְחוֹקִים מִצְּדָקָה רַב וּשְׁמוּאֵל וְאָמְרִי לַהּ רַבִּי יוֹחָנָן וְרַבִּי אֶלְעָזָר '
              'חַד אָמַר כָּל הָעוֹלָם כֻּלּוֹ נִזּוֹנִין בִּצְדָקָה וְהֵם נִזּוֹנִין בִּזְרוֹעַ אָמַר רַב אָשֵׁי בְּנֵי מָתָא '
              'מַחְסֵיָא אַבִּירֵי לֵב נִינְהוּ דְּקָא חָזוּ יְקָרָא דְאוֹרָיְתָא תְּרֵי זִמְנֵי בְּשַׁתָּא וְלָא קָמִגַּיַּר גִּיּוֹרָא מִנַּיְהוּ')
    lem17b = 'וְהָלֵין בְּנֵי מָתָא מְחַסְיָא, "אַבִּירֵי לֵב" נִינְהוּ, דְּהָא קָא חָזוּ בְּשִׁבְחָא דְּאוֹרַיְתָא תְּרֵי זִימְנֵי בְּשַׁתָּא, וְלָא מִגַיֵּיר גִּיּוֹרָא מִנַיְהוּ.'
    band2, info2 = cut_band(seg17b, lem17b)
    t2 = 'גִּיּוֹרָא מִנַּיְהוּ' in band2 and info2['anchor'] is not None
    ok &= t2
    print('  [2] Paraphrase ausgerichtet      -> Anker {}, Deckung {}  {}'
          .format(info2['anchor'], info2['coverage'], 'OK' if t2 else 'FEHLER'))

    # (3) Zwei Gebete mit gleichem Anfang — Segmentwahl nach Gesamtdeckung.
    cands = [
        'רַבִּי אֶלְעָזָר בָּתַר דִּמְסַיֵּם צְלוֹתֵהּ אָמַר הָכִי יְהִי רָצוֹן מִלְּפָנֶיךָ ה\' אֱלֹהֵינוּ שֶׁתְּשַׁכֵּן בְּפוּרֵנוּ אַהֲבָה וְאַחְוָה וְשָׁלוֹם וְרֵעוּת',
        'רַבִּי בָּתַר צְלוֹתֵהּ אָמַר הָכִי יְהִי רָצוֹן מִלְּפָנֶיךָ ה\' אֱלֹהַי וֵאלֹהֵי אֲבוֹתַי שֶׁתַּצִּילֵנִי מֵעַזֵּי פָנִים וּמֵעַזּוּת פָּנִים מֵאָדָם רָע וּמִפֶּגַע רָע',
    ]
    lem16b = 'יְהִי רָצוֹן מִלְּפָנֶיךָ, ה\' אֱלֹהַי וֵאלֹהֵי אֲבוֹתַי, שֶׁתַּצִּילֵנִי מֵעַזֵּי פָּנִים, וּמֵעַזּוּת פָּנִים, מֵאָדָם רָע, וּמִפֶּגַע רָע.'
    i3, sc3, a3, b3, cov3 = best_segment(lem16b, cands)
    t3 = (i3 == 1)
    ok &= t3
    print('  [3] richtiges von zwei Gebeten   -> Segment {}, Deckung {}  {}'
          .format(i3, round(cov3, 3), 'OK' if t3 else 'FEHLER'))

    # (4) Wortgrenze wird fuer eine lange Passage geoeffnet.
    #     Kunstwoerter aus echten Buchstaben — Ziffern faellt die
    #     Normalisierung weg, sie taugen hier nicht zur Unterscheidung.
    alef = 'אבגדהזחטכלמנסעפצקרשת'
    vocab = [alef[i // 20] + alef[i % 20] + 'ם' for i in range(80)]
    long_seg = ' '.join(vocab)
    long_lem = ' '.join(vocab[20:75])
    band4, info4 = cut_band(long_seg, long_lem, max_words=42)
    t4 = info4['extended'] and vocab[74] in band4 and not info4['truncated_lemma']
    ok &= t4
    print('  [4] Grenze fuer lange Passage    -> {} Woerter, erweitert={}  {}'
          .format(info4['words'], info4['extended'], 'OK' if t4 else 'FEHLER'))

    # (5) Abnahmeprüfung erkennt ein Band ohne das Lemma.
    bad_ok, bad_cov = band_contains_lemma('מִלָּה1 מִלָּה2 מִלָּה3', lem20a)
    good_ok, good_cov = band_contains_lemma(band, lem20a)
    t5 = (not bad_ok) and good_ok
    ok &= t5
    print('  [5] Kopfbandpruefung             -> schlecht {}, gut {}  {}'
          .format(bad_cov, good_cov, 'OK' if t5 else 'FEHLER'))

    print('\n  SELBSTTEST by_band:', 'BESTANDEN' if ok else 'FEHLGESCHLAGEN')
    return 0 if ok else 1


if __name__ == '__main__':
    import sys
    sys.exit(_selftest())
