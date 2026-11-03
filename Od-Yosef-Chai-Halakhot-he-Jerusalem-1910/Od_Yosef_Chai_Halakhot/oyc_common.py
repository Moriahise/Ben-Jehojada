# -*- coding: utf-8 -*-
"""
Od Yosef Chai · Halakhot — gemeinsame Grundlagen aller Arbeitsschritte.

Das Werk wird im Format des Ben-Ish-Chai-Buchmanagers (v1.0.17) gesetzt:
Abschnitt = Parascha, Segment = eine Halacha (Ot) mit allen Absaetzen.
Deshalb stehen hier dieselben Kalibrierwerte wie im JSX, und alle Zaehlungen
folgen dessen visibleLength() (Text ohne Tags, getrimmt, UTF-16-Laenge).

Quellenmodell
-------------
Die Sefaria-Datei "Od Yosef Chai; Halakhot - he - Jerusalem, 1910" ist
nach Parascha gegliedert. Je Parascha:
    Tiefe 2: Liste der Halachot, jede Halacha eine Liste von Absaetzen
    Tiefe 1: Liste von Absaetzen (Kuntres Chut HaMeshulash)
Leere Halachot (z. B. Vaera 3) bleiben im Modell als Luecke stehen; sie
erzeugen kein Segment, die Zaehlung der folgenden Halachot bleibt
Sefaria-gleich (Ref "Vaera 4" ist Ot 4).
"""
import hashlib
import json
import os
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _finde_repo(start):
    """Repository-Wurzel = erster Ordner aufwaerts mit glossary_he.json und dem
    Pipeline-ZIP. So laufen die Skripte unter production/… ebenso wie unter
    Od-Yosef-Chai-Halakhot-he-Jerusalem-1910/…"""
    for d in [start] + list(start.parents):
        if (d / 'glossary_he.json').exists() and (d / 'ben-yehoyada-pipeline-v3_2_1_2026-10-05.zip').exists():
            return d
    return start.parents[1]


REPO = _finde_repo(HERE)

WERK_EN = 'Od Yosef Chai; Halakhot'
WERK_HE = 'עוד יוסף חי; הלכות'
WERK_TAG = 'Od_Yosef_Chai_Halakhot'
PROJECT_ATTR = 'Od Yosef Chai Halakhot'
ID_PREFIX = 'OYH-'

SOURCE_JSON = HERE / 'source' / 'Od_Yosef_Chai_Halakhot_-_he_-_Jerusalem_1910.json'
SOURCE_JSON_SHA256 = 'c5c83996dffd446ad3f8711361a438271e0e1e3304c4665fe4ca5b6801d70b62'
SEFARIA_URL = ('https://www.sefaria.org/download/version/'
               'Od%20Yosef%20Chai%3B%20Halakhot%20-%20he%20-%20Jerusalem%2C%201910.json')
NLI_RECORD = 'https://www.nli.org.il/he/books/NNL_ALEPH990019337340205171/NLI'
NLI_DOCID = 'NNL_ALEPH990019337340205171'

PIPELINE_ZIP = REPO / 'ben-yehoyada-pipeline-v3_2_1_2026-10-05.zip'
PIPELINE_ZIP_BLOB = '2eab4448a8e1e0beec0c9cc2304e6154f06d95f5'
GLOSSARY = REPO / 'glossary_he.json'
BIC_JSX = REPO / 'Ben_Ish_Chai_Bilingual_Book_Manager_v1_0_17-Milestone.jsx'

# --- Kalibrierung: identisch mit Ben_Ish_Chai_Bilingual_Book_Manager_v1_0_17 --
# (Halakhah_Ben_Ish_Hai_I.idml: 148 x 210 mm, Keter YG Medium 10/12 pt,
#  Cambria 9/10,8 pt). test_oyc.py liest die Werte aus dem JSX nach.
PAGE_W_MM = 148
PAGE_H_MM = 210
MAX_PAGES = 600
TARGET_PAGES = 540
RESERVED_PAGES = 12
BODY_TARGET = TARGET_PAGES - RESERVED_PAGES
HE_CHARS_PER_PAGE = 1050
EN_CHARS_PER_PAGE = 2000
EN_EXPANSION = 1.95
HE_LEADING_PT = 12
BATCH_MAX_SEGMENTS = 12
BATCH_MAX_CHARS = 30000

# --- Paraschot (Sefaria-Schreibung) -------------------------------------------
PARASHOT = [
    'Bereshit', 'Noach', 'Lech Lecha', 'Vayera', 'Chayei Sara', 'Toldot', 'Vayetzei',
    'Vayishlach', 'Vayeshev', 'Miketz', 'Vayigash', 'Vayechi', 'Shemot', 'Vaera', 'Bo',
    'Beshalach', 'Yitro', 'Mishpatim', 'Terumah', 'Tetzaveh', 'Ki Tisa', 'Vayakhel',
    'Pekudei', 'Vayikra', 'Tzav', 'Shmini', 'Tazria', 'Metzora', 'Achrei Mot', 'Kedoshim',
    'Emor', 'Behar', 'Bechukotai', 'Bamidbar', 'Nasso', "Beha'alotcha", "Sh'lach",
    'Korach', 'Chukat', 'Balak', 'Pinchas', 'Matot', 'Masei', 'Devarim', 'Vaetchanan',
    'Eikev', "Re'eh", 'Shoftim', 'Ki Teitzei', 'Ki Tavo', 'Nitzavim', 'Vayeilech',
    "Ha'Azinu", 'V\'Zot HaBerachah']

# Hebraeische Namen in der Reihenfolge von PARASHOT (fuer Kolumnentitel)
PARASHOT_HE = [
    'בראשית', 'נח', 'לך לך', 'וירא', 'חיי שרה', 'תולדות', 'ויצא', 'וישלח', 'וישב', 'מקץ',
    'ויגש', 'ויחי', 'שמות', 'וארא', 'בא', 'בשלח', 'יתרו', 'משפטים', 'תרומה', 'תצוה',
    'כי תשא', 'ויקהל', 'פקודי', 'ויקרא', 'צו', 'שמיני', 'תזריע', 'מצורע', 'אחרי מות',
    'קדושים', 'אמור', 'בהר', 'בחקותי', 'במדבר', 'נשא', 'בהעלותך', 'שלח לך', 'קרח', 'חקת',
    'בלק', 'פינחס', 'מטות', 'מסעי', 'דברים', 'ואתחנן', 'עקב', 'ראה', 'שופטים', 'כי תצא',
    'כי תבוא', 'נצבים', 'וילך', 'האזינו', 'וזאת הברכה']

# --- Zeichenklassen -----------------------------------------------------------
HEB_LETTER = 'א-ת'
MARKS = '֑-ׇֽֿׁׂׅׄ'   # Nikud + Teamim
MAQAF = '־'
NIKUD_RE = re.compile('[' + MARKS + ']')
TAG_RE = re.compile(r'<[^>]+>')
QUOTE_MAP = str.maketrans({'״': '"', '”': '"', '“': '"', '„': '"',
                           '׳': "'", '’': "'", '‘': "'"})
WORD_RE = re.compile('[' + HEB_LETTER + MARKS + '"\'׳״“”‘’]+')


# Dicta Nakdan (keepmetagim=true) markiert Lesemuetter der Plene-Schreibung mit
# Meteg auf dem ו/י (קֹוֽדֶם). Fuer Satz, Vergleich und Vorlage zaehlt die Marke nicht.
PLENE_RE = re.compile('([\u05D5\u05D9])\u05BD(?![\u0591-\u05C7])')


def ohne_plene_marke(text):
    return PLENE_RE.sub(r'\1', text or '')


def strip_tags(s):
    return TAG_RE.sub('', s or '')


def strip_nikud(s):
    return NIKUD_RE.sub('', s or '')


def visible_length(s):
    """Wie visibleLength() im BIC-JSX: trim(stripTags(s)).length."""
    return len(strip_tags(s).strip())


def norm_quotes(s):
    return (s or '').translate(QUOTE_MAP)


def skeleton(word):
    """Konsonantenskelett eines Worts: ohne Nikud/Teamim, Anfuehrungszeichen
    vereinheitlicht und am Rand entfernt. Grundlage jeder Kollation."""
    w = norm_quotes(strip_nikud(unicodedata.normalize('NFC', word or '')))
    return w.strip('"\'')


def words(text):
    """Hebraeische Woerter (mit Gershajim/Geresch im Wort) eines Klartexts.
    Maqaf trennt Woerter."""
    t = strip_tags(text or '').replace(MAQAF, ' ')
    out = []
    for m in WORD_RE.finditer(t):
        sk = skeleton(m.group(0))
        if re.search('[' + HEB_LETTER + ']', sk):
            out.append(m.group(0))
    return out


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha(path):
    data = Path(path).read_bytes()
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


# --- Netz (nur auf ausdruecklichen Wunsch) -----------------------------------
def http_get(url, timeout=60, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers=headers or {
        'User-Agent': 'od-yosef-chai-pipeline/1.0'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def download_sefaria(url, dest):
    raw = http_get(url, timeout=120)
    json.loads(raw.decode('utf-8'))           # nur gueltiges JSON ablegen
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    Path(dest).write_bytes(raw)
    return dest


# --- Werkmodell ---------------------------------------------------------------
def he_title_for(key, he):
    if key in PARASHOT:
        return 'פרשת ' + he
    return he


def load_werk(path=None):
    """Sefaria-JSON -> Werkmodell.

    {'meta': {...}, 'abschnitte': [
        {'ord', 'key', 'he', 'he_title', 'tiefe', 'parascha',
         'halachot': [{'n', 'ref', 'leer', 'absaetze': [{'ref', 'html'}]}]}]}
    """
    path = Path(path or SOURCE_JSON)
    d = json.loads(path.read_text(encoding='utf-8'))
    nodes = (d.get('schema') or {}).get('nodes') or []
    he_of = {n.get('enTitle'): n.get('heTitle') for n in nodes}
    text = d['text']
    abschnitte = []
    for ord_, (key, val) in enumerate(text.items(), start=1):
        he = he_of.get(key) or key
        tiefe = 1 if (val and all(isinstance(x, str) for x in val)) else 2
        halachot = []
        if tiefe == 1:
            for i, p in enumerate(val, start=1):
                ref = '{} {}'.format(key, i)
                halachot.append({'n': i, 'ref': ref, 'leer': not strip_tags(p).strip(),
                                 'absaetze': [{'ref': ref, 'html': p}]})
        else:
            for i, h in enumerate(val, start=1):
                abs_ = [{'ref': '{} {}:{}'.format(key, i, j), 'html': p}
                        for j, p in enumerate(h or [], start=1)]
                leer = not any(strip_tags(a['html']).strip() for a in abs_)
                halachot.append({'n': i, 'ref': '{} {}'.format(key, i), 'leer': leer,
                                 'absaetze': abs_})
        abschnitte.append({'ord': ord_, 'key': key, 'he': he,
                           'he_title': he_title_for(key, he), 'tiefe': tiefe,
                           'parascha': key in PARASHOT, 'halachot': halachot})
    meta = {k: d.get(k) for k in ('title', 'heTitle', 'versionTitle', 'versionSource',
                                  'language', 'license', 'versionNotes')}
    meta['datei'] = str(path)
    meta['sha256'] = sha256_file(path)
    meta['schema_reihenfolge'] = [n.get('enTitle') for n in nodes]
    meta['text_reihenfolge'] = list(text.keys())
    return {'meta': meta, 'abschnitte': abschnitte}


def iter_absaetze(werk):
    for a in werk['abschnitte']:
        for h in a['halachot']:
            for p in h['absaetze']:
                if strip_tags(p['html']).strip():
                    yield a, h, p


def absatz_index(werk):
    """ref -> (abschnitt, halacha, absatz) fuer alle nichtleeren Absaetze."""
    return {p['ref']: (a, h, p) for a, h, p in iter_absaetze(werk)}


def segment_he(h, texts=None):
    """<he> eines Segments: Absaetze der Halacha, durch Zeilenwechsel getrennt,
    wie die mehrzeiligen Chapter-Bloecke der Ben-Ish-Chai-Quelle.
    texts: optional ref -> Ersatztext (z. B. vokalisierte Fassung)."""
    parts = []
    for p in h['absaetze']:
        if not strip_tags(p['html']).strip():
            continue
        parts.append((texts or {}).get(p['ref'], p['html']).strip())
    return '\n'.join(parts)


GLIEDERUNG = HERE / 'gliederung.json'


def lade_gliederung(path=None):
    """Lektoratsentscheidungen zur Bandgliederung (gliederung.json):
    'teilen' zerlegt eine Sefaria-Halacha absatzweise in mehrere Segmente
    (eigenes n, optional eigener Abschnittstitel), 'unterabschnitte' gibt einem
    JSON-Abschnitt den Titel, unter dem er im Druck steht."""
    path = Path(path or GLIEDERUNG)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding='utf-8'))


def pruefe_gliederung(werk, gl):
    halachot = {h['ref']: h for a in werk['abschnitte'] for h in a['halachot']}
    keys = {a['key'] for a in werk['abschnitte']}
    for t in gl.get('teilen', []):
        h = halachot.get(t['ref'])
        if h is None:
            raise SystemExit('gliederung.json: Halacha nicht gefunden: ' + t['ref'])
        voll = [i for i, p in enumerate(h['absaetze'], start=1) if strip_tags(p['html']).strip()]
        teile = [i for x in t['teile'] for i in x['absaetze']]
        if sorted(teile) != voll or len(teile) != len(set(teile)) or teile != sorted(teile):
            raise SystemExit('gliederung.json: Teile von {} muessen die Absaetze {} genau einmal und '
                             'in Reihenfolge abdecken (angegeben: {})'.format(t['ref'], voll, teile))
        for x in t['teile']:
            if not isinstance(x.get('n'), int) or x['n'] < 0:
                raise SystemExit('gliederung.json: n fehlt oder ungueltig in ' + t['ref'])
    for u in gl.get('unterabschnitte', []):
        if u['abschnitt'] not in keys or u.get('unter') not in keys:
            raise SystemExit('gliederung.json: unbekannter Abschnitt in {}'.format(u))
        if not u.get('abschnitt_he'):
            raise SystemExit('gliederung.json: abschnitt_he fehlt fuer ' + u['abschnitt'])
    return True


def _ref_bereich(ref, nums):
    return '{}:{}'.format(ref, nums[0]) if len(nums) == 1 else '{}:{}–{}'.format(ref, nums[0], nums[-1])


def build_segments(werk, texts=None, gliederung=None):
    """Segmente des Bandes. gliederung=None liest gliederung.json,
    gliederung={} liefert die reine Sefaria-Gliederung."""
    gl = lade_gliederung() if gliederung is None else gliederung
    if gl:
        pruefe_gliederung(werk, gl)
    teil_map = {t['ref']: t for t in gl.get('teilen', [])}
    unter = {u['abschnitt']: u for u in gl.get('unterabschnitte', [])}
    segs, g = [], 0

    def neu(a, sec_he, n, ref, absz, rolle):
        nonlocal g
        g += 1
        he = '\n'.join((texts or {}).get(p['ref'], p['html']).strip() for p in absz
                       if strip_tags(p['html']).strip())
        segs.append({'id': '{}{:07d}'.format(ID_PREFIX, g), 'global': g, 'n': n,
                     'abschnitt': a['key'], 'section_he': sec_he,
                     'ref': '{}, {}'.format(WERK_EN, ref), 'rolle': rolle,
                     'absaetze': sum(1 for p in absz if strip_tags(p['html']).strip()),
                     'he': he, 'he_chars': visible_length(he)})

    for a in werk['abschnitte']:
        sec_he = unter[a['key']]['abschnitt_he'] if a['key'] in unter else a['he_title']
        for h in a['halachot']:
            if h['leer']:
                continue
            t = teil_map.get(h['ref'])
            if t:
                for x in t['teile']:
                    absz = [h['absaetze'][i - 1] for i in x['absaetze']]
                    ref = _ref_bereich(h['ref'], x['absaetze']) if a['tiefe'] == 2 else h['ref']
                    neu(a, x.get('abschnitt_he', sec_he), x['n'], ref, absz, x.get('rolle', ''))
            else:
                neu(a, sec_he, h['n'], h['ref'], h['absaetze'],
                    'unter ' + unter[a['key']]['unter'] if a['key'] in unter else '')
    return segs


# --- Dateiformen wie im Buchmanager --------------------------------------------
def xml_escape(s):
    return (str(s or '').replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;').replace('"', '&quot;'))


def protect_cdata(s):
    return '<![CDATA[' + str(s or '').replace(']]>', ']]]]><![CDATA[>') + ']]>'


def write_bic_text(path, text):
    """writeUTF8() des JSX: BOM + Windows-Zeilenenden."""
    text = str(text or '').replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\r\n')
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8-sig', newline='') as fh:
        fh.write(text)


def write_tsv(path, header, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write('\t'.join(header) + '\r\n')
        for r in rows:
            fh.write('\t'.join(re.sub(r'[\t\r\n]+', ' ', str(x if x is not None else ''))
                               for x in r) + '\r\n')


def read_tsv(path):
    lines = Path(path).read_text(encoding='utf-8-sig').splitlines()
    lines = [l for l in lines if l.strip() and not l.lstrip().startswith('#')]
    if not lines:
        return []
    head = lines[0].split('\t')
    out = []
    for l in lines[1:]:
        cells = l.split('\t')
        cells += [''] * (len(head) - len(cells))
        out.append({h: c.strip() for h, c in zip(head, cells)})
    return out


def write_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding='utf-8')


def parse_range(spec, maximum=None):
    """'1-25,30' -> [1..25, 30]"""
    out = []
    for part in (spec or '').split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            a, b = part.split('-', 1)
            a = int(a)
            b = int(b) if b.strip() else (maximum or a)
            out.extend(range(a, b + 1))
        else:
            out.append(int(part))
    return out


# --- Pipeline v3.2.1 aus dem Repository-ZIP ------------------------------------
def import_pipeline(path=None):
    """Macht by_parse/by_glossary der freigegebenen Pipeline v3.2.1 importierbar,
    ohne den Code zu kopieren. path: ZIP (Vorgabe) oder entpackter Ordner."""
    path = Path(path or PIPELINE_ZIP)
    if path.is_file():
        if git_blob_sha(path) != PIPELINE_ZIP_BLOB:
            raise SystemExit('Pipeline-ZIP weicht von v3.2.1 ab: ' + str(path))
        with zipfile.ZipFile(path) as z:
            root = sorted({n.split('/')[0] for n in z.namelist()})[0]
        entry = str(path) + '/' + root
    else:
        entry = str(path)
    if entry not in sys.path:
        sys.path.insert(0, entry)
    import by_parse      # noqa: F401
    import by_glossary   # noqa: F401
    return entry


# --- Textkorrekturen nach Scan (Gegenstueck zu den BY-Quellkorrekturen) -------
TEXTKORREKTUREN = HERE / 'textkorrekturen.json'


def lade_textkorrekturen(path=None):
    """{"korrekturen": [{"ref": "Bereshit 1:2", "alt": "..", "neu": "..",
    "scan_seq": 123, "grund": ".."}]}. Jede Korrektur braucht Scanbeleg und
    Grund; die JSON-Quelldatei selbst bleibt unveraendert (Regel 45)."""
    path = Path(path or TEXTKORREKTUREN)
    if not path.exists():
        return []
    d = json.loads(path.read_text(encoding='utf-8'))
    fixes = d.get('korrekturen', []) if isinstance(d, dict) else d
    for fx in fixes:
        for k in ('ref', 'alt', 'neu', 'scan_seq', 'grund'):
            if k not in fx or fx[k] in ('', None):
                raise SystemExit('Textkorrektur ohne "{}": {}'.format(k, fx))
    return fixes


def wende_textkorrekturen(werk, fixes):
    idx = absatz_index(werk)
    log = []
    for fx in fixes:
        if fx['ref'] not in idx:
            raise SystemExit('Textkorrektur: Absatz nicht gefunden: ' + fx['ref'])
        p = idx[fx['ref']][2]
        if p['html'].count(fx['alt']) != 1:
            raise SystemExit('Textkorrektur {}: "alt" kommt nicht genau einmal vor'.format(fx['ref']))
        p['html'] = p['html'].replace(fx['alt'], fx['neu'], 1)
        log.append('{} · Scan S. {} · {}'.format(fx['ref'], fx['scan_seq'], fx['grund']))
    werk['meta']['textkorrekturen'] = log
    return log


def load_werk_korrigiert(path=None, korrekturen=None):
    werk = load_werk(path)
    wende_textkorrekturen(werk, lade_textkorrekturen(korrekturen))
    return werk
