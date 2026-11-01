# -*- coding: utf-8 -*-
"""
Unabhaengige Gegenpruefung einer Ben-Yehoyada-Banddatei gegen die beiden
Quelldateien (Senlake-Rohdatei und Dicta haser). Nutzt bewusst NICHT die
Pipeline-Funktionen, sondern liest beide Rohdateien selbst ein.

  A  Struktur      IDs lueckenlos, n/daf je Absatz wie in Senlake, Daf-Titel
  B  Hebraeisch    <he> (ohne <fn>, ohne Tags) == Senlake-Absatz (ohne
                   <small>[...]</small>-Erklaerungen, ohne Tags)
  C  Kopfband      <band_he> ist ein zusammenhaengender Wortausschnitt genau
                   des Dicta-Segments, das ref nennt; ohne ref == Lemma
  D  Fussnoten     kein Markup im <fn>, Kuerzel steht unmittelbar davor
  E  EN-Felder     frischer Master: <band_en>/<en> leer; --uebersetzt: gefuellt
  F  Tags          <b>/</b> im <he> ausgeglichen, hoechstens ein <lemma>
  G  Lemma-Liste   HINWEIS, kein Befund: Lemmata, die die Pipeline aus mehreren
                   fetten Stuecken zusammengesetzt hat — zur Sichtpruefung, ob
                   ein Lemma zu lang geraten ist (Kommentar statt Talmudzitat)

Rueckgabe-Code: 0 = A bis F ohne Befund, 1 = Befunde vorhanden.

    python3 by_gegenpruefung.py BAND.txt SENLAKE.txt DICTA.txt [--json out.json] [--uebersetzt]
                                [--quellkorrektur quellkorrekturen/<Traktat>.json]

--quellkorrektur (v3.2.1): dieselbe Korrekturdatei wie im Pipelinelauf. Die
"alt"/"neu"-Ersetzungen werden auf die eingelesenen Senlake-Absaetze angewandt;
eine Korrektur, die mehr als Tags und Leerraum aendert, ist ein Befund in A.

Entstanden beim Yoma-Lauf 2026-10-05; gilt fuer jeden Traktat und jeden Band:
Segment BYH-000n wird mit dem n-ten Senlake-Absatz verglichen (Band 02 ff.
beginnen also mitten in der Datei). --uebersetzt: fuer einen uebersetzten
Band-Master (EN_FERTIG) prueft E, dass <band_en>/<en> GEFUELLT sind und
<band_en> weder <fn> noch hebraeische Zeichen enthaelt.
"""
import html, json, re, sys

SEG = re.compile(r'<segment\s+([^>]*)>\s*\r?\n(.*?)\r?\n</segment>', re.S)
ATTR = re.compile(r'(\w+)="([^"]*)"')
SECTION = re.compile(r'<he_title>(.*?)</he_title>\s*\r?\n<en_title>(.*?)</en_title>')
NIKUD = re.compile(r'[֑-ׇ]')
HEB_VAL = {'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
           'י': 10, 'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60, 'ע': 70, 'פ': 80,
           'צ': 90, 'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400}


def field(body, k):
    m = re.search(r'<%s>(?:<!\[CDATA\[(.*?)\]\]>|(.*?))</%s>' % (k, k), body, re.S)
    if not m:
        return None
    return m.group(1) if m.group(1) is not None else m.group(2)


def chars(s):
    """Vergleichsform: nur sichtbare Zeichen, ohne jeden Leerraum."""
    return re.sub(r'\s+', '', s or '')


def senlake_paragraphs(path):
    out, cur, seq = [], None, 0
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\r\n')
        m = re.match(r'^Daf\s+(\S+)\s*$', line)
        if m:
            cur, seq = m.group(1), 0
            continue
        if cur is None or not line.strip():
            continue
        seq += 1
        out.append((cur, seq, line.strip()))
    return out


def senlake_text(para):
    # Senlake-Erklaerungen [..] sind Zusatz der Ausgabe, nicht Ben-Yehoyada-Text.
    s = re.sub(r'<small>\s*\[(?:(?!</small>)[^\]])*\]\s*([.,:;]?)\s*</small>', r'\1', para)
    # Nur die bekannten Senlake-Tags entfernen. Ein kaputtes Tag wie "<b>מַר<, וזה"
    # (Pesachim) bleibt so im Vergleichstext stehen und faellt in B auf, statt
    # wie im Tag-Muster der Pipeline samt Text zu verschwinden.
    s = re.sub(r'</?(?:b|br|small)>', '', s)
    s = s.replace('<', '')
    # Maskierte Tag-Reste ("&lt;b&gt; אַתָּה חוֹנֵןb&gt;", Bava Kamma 3b) sind kein Text.
    s = re.sub(r'/?b?(?:&lt;|&gt;)(?:[/b]*(?:&lt;|&gt;))*/?', '', s)
    return s


def dicta(path):
    out, cur = {}, None
    rx = re.compile(r'^\s*\*{2,}\s*דף\s+([א-ת"״׳\']+?)\s*([.:])\s*\*{2,}\s*$')
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\r\n')
        m = rx.match(line)
        if m:
            n = sum(HEB_VAL.get(c, 0) for c in m.group(1))
            cur = '%d%s' % (n, 'a' if m.group(2) == '.' else 'b')
            out.setdefault(cur, [])
            continue
        t = line.strip()
        if cur is None or not t or t in {"גמ'", 'גמ׳', "מתני'", 'מתני׳', 'הדרן', 'מתניתין', 'גמרא'}:
            continue
        out[cur].append(re.sub(r'<[^>]+>', '', t))
    return out


def daf_title_he(daf):
    m = re.match(r'^(\d+)([ab])$', daf)
    n, out = int(m.group(1)), ''
    for v, c in sorted(((v, c) for c, v in HEB_VAL.items()), reverse=True):
        while n >= v:
            out += c
            n -= v
    out = out.replace('יה', 'טו').replace('יו', 'טז')
    return 'דף {} {}'.format(out, 'ע"א' if m.group(2) == 'a' else 'ע"ב')


def _nur_text(s):
    s = re.sub(r'</?(?:b|br|small)>', '', s).replace('<', '')
    s = re.sub(r'/?b?(?:&lt;|&gt;)(?:[/b]*(?:&lt;|&gt;))*/?', '', s)
    return re.sub(r'\s+', '', s)


def apply_quellkorrektur(paras, path, befunde):
    """Wendet die "alt"/"neu"-Korrekturen auf die Absaetze an (eigene Umsetzung,
    unabhaengig von by_parse). "lemma_ende" aendert den Text nicht."""
    d = json.load(open(path, encoding='utf-8'))
    fixes = d.get('korrekturen', d) if isinstance(d, dict) else d
    pos = {(daf, seq): i for i, (daf, seq, _p) in enumerate(paras)}
    n = 0
    for fx in fixes:
        if 'alt' not in fx:
            continue
        i = pos.get((fx['daf'], int(fx['n'])))
        if i is None or paras[i][2].count(fx['alt']) != 1:
            befunde.append('Quellkorrektur {}.{}: Absatz/Suchtext nicht eindeutig'.format(fx['daf'], fx['n']))
            continue
        daf, seq, p = paras[i]
        q = p.replace(fx['alt'], fx['neu'])
        if _nur_text(q) != _nur_text(p):
            befunde.append('Quellkorrektur {}.{}: aendert Text, nicht nur Tags'.format(fx['daf'], fx['n']))
            continue
        paras[i] = (daf, seq, q)
        n += 1
    return n


def main(band, senlake, dicta_path, json_out=None, uebersetzt=False, quellkorrektur=None):
    raw = open(band, encoding='utf-8-sig').read()
    segs = [(dict(ATTR.findall(m.group(1))), m.group(2)) for m in SEG.finditer(raw)]
    paras = senlake_paragraphs(senlake)
    qk_befunde = []
    n_qk = apply_quellkorrektur(paras, quellkorrektur, qk_befunde) if quellkorrektur else 0
    src_raw = open(senlake, encoding='utf-8').read()
    kaputt = [m.start() for m in re.finditer(r'<', src_raw)
              if not re.match(r'<(?:/?b|br|/?small)>', src_raw[m.start():m.start() + 8])]
    tal = dicta(dicta_path)
    res = {k: [] for k in 'ABCDEFG'}
    res['A'].extend(qk_befunde)
    stats = {'segmente': len(segs), 'senlake_absaetze': len(paras),
             'senlake_kaputte_tags': len(kaputt),
             'senlake_maskiertes_markup': len(re.findall(r'&lt;|&gt;', src_raw)),
             'quellkorrekturen_angewandt': n_qk}

    # A Struktur — Segment BYH-000n gehoert zum n-ten Senlake-Absatz.
    first = int(re.sub(r'\D', '', segs[0][0].get('id', '0')) or 0) if segs else 1
    if first < 1 or first - 1 + len(segs) > len(paras):
        res['A'].append('Band reicht ueber die {} Senlake-Absaetze hinaus'.format(len(paras)))
    paras = paras[first - 1:first - 1 + len(segs)]
    stats['senlake_absaetze_im_band'] = len(paras)
    for i, ((a, _b), (daf, seq, _p)) in enumerate(zip(segs, paras), start=first):
        if a.get('id') != 'BYH-{:07d}'.format(i):
            res['A'].append('{}: ID statt BYH-{:07d}'.format(a.get('id'), i))
        if a.get('daf') != daf or a.get('n') != str(seq):
            res['A'].append('{}: daf/n {} {} statt {} {}'.format(a.get('id'), a.get('daf'), a.get('n'), daf, seq))
    titles = SECTION.findall(raw)
    dafs_used = []
    for _d, _s, _p in paras:
        if not dafs_used or dafs_used[-1] != _d:
            dafs_used.append(_d)
    want = [(daf_title_he(d), 'Daf ' + d) for d in dafs_used]
    if titles != want:
        res['A'].append('Daf-Titel weichen ab ({} statt {})'.format(len(titles), len(want)))
    stats['dafim'] = len(titles)

    # B Hebraeisch vollstaendig
    exact = 0
    for (a, b), (_d, _s, p) in zip(segs, paras):
        he = field(b, 'he') or ''
        he_txt = html.unescape(re.sub(r'<[^>]+>', '', re.sub(r'<fn>.*?</fn>', '', he)))
        src = senlake_text(p)
        # Fuehrende Satzzeichen-Reste trennt die Pipeline bewusst vom Lemma ab
        # ("<b> .</b> <b>...</b>", Yoma 22b) — sie zaehlen nicht als Abweichung.
        if chars(he_txt).lstrip('.,:;') == chars(src).lstrip('.,:;'):
            exact += 1
        else:
            x, y = chars(he_txt).lstrip('.,:;'), chars(src).lstrip('.,:;')
            k = 0
            while k < min(len(x), len(y)) and x[k] == y[k]:
                k += 1
            res['B'].append({'id': a.get('id'), 'pos': k,
                             'band': x[max(0, k - 25):k + 25], 'senlake': y[max(0, k - 25):k + 25],
                             'len_band': len(x), 'len_senlake': len(y)})
    stats['he_wortgleich'] = exact

    # C Kopfband aus Dicta
    ok_c, fallback, freitext = 0, 0, 0
    for a, b in segs:
        bh = (field(b, 'band_he') or '').strip()
        ref = a.get('ref', '')
        if not ref:
            lm = re.search(r'<lemma>(.*?)</lemma>', field(b, 'he') or '', re.S)
            if not lm and not bh:
                freitext += 1          # Freitext ohne Lemma: kein Kopfband ist richtig
            elif lm and chars(html.unescape(lm.group(1))) == chars(bh):
                fallback += 1
            else:
                res['C'].append('{}: ohne ref, Kopfband != Lemma'.format(a.get('id')))
            continue
        m = re.match(r'^.+ (\d+[ab]):(\d+)$', ref)
        if not m or m.group(1) not in tal or int(m.group(2)) > len(tal[m.group(1)]):
            res['C'].append('{}: ref {} nicht in Dicta'.format(a.get('id'), ref))
            continue
        segw = tal[m.group(1)][int(m.group(2)) - 1].split()
        bw = [w for w in bh.split() if w != '…']
        n = len(bw)
        hit = any(segw[j:j + n] == bw for j in range(0, len(segw) - n + 1))
        if hit:
            ok_c += 1
        else:
            res['C'].append('{}: Kopfband kein Wortausschnitt aus {}'.format(a.get('id'), ref))
        if m.group(1) != a.get('daf'):
            stats.setdefault('ref_nachbarblatt', []).append('{} daf={} ref={}'.format(a.get('id'), a.get('daf'), ref))
    stats['kopfband_aus_dicta'] = ok_c
    stats['kopfband_lemma_rueckfall'] = fallback
    stats['freitext_ohne_kopfband'] = freitext

    # D Fussnoten
    nfn = 0
    for a, b in segs:
        he = field(b, 'he') or ''
        for m in re.finditer(r'<fn>(.*?)</fn>', he, re.S):
            nfn += 1
            note = m.group(1)
            if '&lt;' in note or '<' in note or ']' in note:
                res['D'].append('{}: Markup im <fn>: {}'.format(a.get('id'), note[:60]))
            if ' = ' in note:
                tok = html.unescape(note.split(' = ', 1)[0])
                before = html.unescape(re.sub(r'<[^>]+>', '', he[:m.start()]))
                if not before.endswith(tok):
                    res['D'].append('{}: <fn> {} steht nicht hinter dem Kuerzel'.format(a.get('id'), tok))
        if '<fn>' in re.sub(r'<fn>.*?</fn>', '', he, flags=re.S):
            res['D'].append('{}: verschachtelte <fn>'.format(a.get('id')))
    stats['fussnoten'] = nfn

    # E Uebersetzungsfelder: frischer Master leer, EN_FERTIG gefuellt
    for a, b in segs:
        for k in ('band_en', 'en'):
            v = field(b, k)
            if v is None:
                res['E'].append('{}: <{}> fehlt'.format(a.get('id'), k))
            elif uebersetzt and not v.strip():
                res['E'].append('{}: <{}> leer'.format(a.get('id'), k))
            elif not uebersetzt and v.strip():
                res['E'].append('{}: <{}> nicht leer'.format(a.get('id'), k))
        bev = field(b, 'band_en') or ''
        if uebersetzt and ('<fn>' in bev or re.search(r'[\u0590-\u05FF]', bev)):
            res['E'].append('{}: <band_en> mit <fn> oder hebraeischen Zeichen'.format(a.get('id')))

    # F Tags
    for a, b in segs:
        he = field(b, 'he') or ''
        nl = he.count('<lemma>')
        if (he.count('<b>') != he.count('</b>') or nl > 1
                or (nl == 0 and (field(b, 'band_he') or '').strip())):
            res['F'].append('{}: <b> {} / </b> {} / <lemma> {}'.format(
                a.get('id'), he.count('<b>'), he.count('</b>'), nl))
        # Maskiertes Markup erschiene im Satz als sichtbares "<b>".
        m = re.search(r'&lt;|&gt;', re.sub(r'<fn>.*?</fn>', '', he, flags=re.S))
        if m:
            res['F'].append('{}: maskiertes Markup im Text: {}'.format(
                a.get('id'), he[max(0, m.start() - 20):m.end() + 20]))

    # G Lemma-Sichtliste (HINWEIS): laenger als das erste fette Stueck in Senlake
    for (a, b), (_d, _s, p) in zip(segs, paras):
        lm = re.search(r'<lemma>(.*?)</lemma>', field(b, 'he') or '', re.S)
        f1 = re.match(r'\s*<b>(.*?)</b>', p, re.S)
        if not lm or not f1:
            continue
        lem = re.sub(r'<[^>]+>', '', html.unescape(lm.group(1)))
        if len(chars(lem)) > len(chars(senlake_text(f1.group(1))).lstrip('.,:;')):
            res['G'].append('{}: {}'.format(a.get('id'), re.sub(r'\s+', ' ', lem)[:160]))
    stats['lemma_mehrteilig'] = len(res['G'])

    names = {'A': 'Struktur', 'B': 'Hebraeischer Text vollstaendig', 'C': 'Kopfband aus Dicta',
             'D': 'Fussnoten', 'E': 'Uebersetzungsfelder', 'F': 'Tag-Ausgleich',
             'G': 'Lemma-Sichtliste (HINWEIS)'}
    print('== GEGENPRUEFUNG ==', band)
    for k, v in stats.items():
        if isinstance(v, list):
            print('{:26s}: {}'.format(k, len(v)))
            for x in v:
                print('      ' + x)
        else:
            print('{:26s}: {}'.format(k, v))
    for k in 'ABCDEF':
        print('{} {:32s}: {}'.format(k, names[k], 'OK' if not res[k] else '{} Befund(e)'.format(len(res[k]))))
        for x in res[k][:40]:
            print('      ', x)
    print('G {:32s}: {} Lemma(ta) aus mehreren fetten Stuecken — bitte ansehen'.format(
        names['G'], len(res['G'])))
    for x in res['G']:
        print('       ', x)
    if json_out:
        json.dump({'stats': stats, 'befunde': res}, open(json_out, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
    return 0 if not any(res[k] for k in 'ABCDEF') else 1


if __name__ == '__main__':
    a = sys.argv[1:]
    j = None
    ueb = '--uebersetzt' in a
    a = [x for x in a if x != '--uebersetzt']
    qk = None
    if '--quellkorrektur' in a:
        k = a.index('--quellkorrektur')
        qk = a[k + 1]
        a = a[:k] + a[k + 2:]
    if '--json' in a:
        j = a[a.index('--json') + 1]
        a = a[:a.index('--json')]
    sys.exit(main(a[0], a[1], a[2], j, ueb, qk))
