# -*- coding: utf-8 -*-
"""
Abnahmepruefung einer Od-Yosef-Chai-Banddatei oder eines Translation_Batch
(Dateiform des Ben-Ish-Chai-/Od-Yosef-Chai-Buchmanagers).

    python3 oyc_validate.py --in Band_01_BILINGUAL_EN_FERTIG.txt --gegen Band_01_BILINGUAL.txt
    python3 oyc_validate.py --in Translation_Batch_01_OYH-…_EN_FERTIG.txt --gegen Band_01_BILINGUAL.txt
    python3 oyc_validate.py --in Band_01_BILINGUAL.txt                 (frischer Master)

FEHLER (blockierend, Rueckgabecode 1)
  Struktur   IDs, n, Reihenfolge, Zahl der Segmente, Abschnittsfolge wie im
             Ausgangsmaster; keine doppelten IDs
  Geschuetzt <he> und <he_title> zeichengleich (nach CDATA, Zeilenenden)
  EN         bei --fertig (Vorgabe bei Dateinamen *_EN_FERTIG*): jedes <en> und
             jedes <en_title> gefuellt; <en> nicht gleich <he>
  Titel      <en_title> ohne hebraeische Zeichen und ohne Tags; gleiche
             <he_title> nicht mit verschiedenen <en_title>
  Tags       in <en> nur b, i, small, sup, br; ausgeglichen; kein <fn>, kein
             <lemma> (der Buchmanager setzt sie nicht um)
  Verboten   YHWH, Yahweh, Jehovah, Adonai, "Bible:", "Tanach:", Markdown-Zaeune
PRUEFEN (nicht blockierend)
  Laengenverhaeltnis EN/HE ausserhalb 1,0–4,0 (Auslassung? Zusatz?)
  hoher Anteil hebraeischer Zeichen in <en>
  Segmente mit NEU-Kuerzeln aus dem Glossar (--glossar), zur Sichtpruefung
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

import oyc_common as C

SEC_RE = re.compile(r'<section>\s*<he_title>([\s\S]*?)</he_title>\s*<en_title>([\s\S]*?)</en_title>\s*</section>', re.I)
SEG_RE = re.compile(r'<segment\b([^>]*)>\s*<he>([\s\S]*?)</he>\s*<en>([\s\S]*?)</en>\s*</segment>', re.I)
ATTR_RE = re.compile(r'(\w+)=["\']([^"\']*)["\']')
HEB_RE = re.compile('[֐-׿]')
ERLAUBT = {'b', 'i', 'small', 'sup', 'br'}
VERBOTEN = [r'\bYHWH\b', r'\bYahweh\b', r'\bJehovah\b', r'\bAdonai\b', r'\bBible:', r'\bTanach:', r'```']


def restore_cdata(s):
    s = (s or '').strip()
    if s.startswith('<![CDATA[') and s.endswith(']]>'):
        s = s[9:-3].replace(']]]]><![CDATA[>', ']]>')
    return s


def xml_unescape(s):
    return (s or '').replace('&quot;', '"').replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')


def norm(s):
    return re.sub(r'\s+', ' ', (s or '').replace('\r\n', '\n').replace('\r', '\n')).strip()


def lese(path):
    raw = Path(path).read_text(encoding='utf-8-sig').replace('\r\n', '\n').replace('\r', '\n')
    ev = []
    for m in SEC_RE.finditer(raw):
        ev.append((m.start(), 'sec', restore_cdata(xml_unescape(m.group(1))), restore_cdata(xml_unescape(m.group(2)))))
    for m in SEG_RE.finditer(raw):
        a = dict(ATTR_RE.findall(m.group(1)))
        ev.append((m.start(), 'seg', a, restore_cdata(m.group(2)), restore_cdata(m.group(3))))
    ev.sort(key=lambda e: e[0])
    secs, segs, cur = [], [], None
    for e in ev:
        if e[1] == 'sec':
            cur = {'he': e[2], 'en': e[3]}
            secs.append(cur)
        else:
            segs.append({'id': e[2].get('id', ''), 'n': e[2].get('n', ''), 'he': e[3], 'en': e[4],
                         'sec_he': cur['he'] if cur else '', 'sec_en': cur['en'] if cur else ''})
    kopf = re.search(r'<(book|translation_batch)\b([^>]*)>', raw)
    planung = re.search(r'<planning\b([^>]*)/>', raw)
    return {'secs': secs, 'segs': segs, 'kopf': kopf.group(0) if kopf else '',
            'planung': dict(ATTR_RE.findall(planung.group(1))) if planung else {},
            'batch': bool(kopf and kopf.group(1) == 'translation_batch')}


def tags_pruefen(text):
    fehler = []
    stapel = []
    for m in re.finditer(r'<(/?)([A-Za-z]+)[^>]*?(/?)>', text):
        zu, name, selbst = m.group(1), m.group(2).lower(), m.group(3)
        if name not in ERLAUBT:
            fehler.append('Tag <{}> nicht erlaubt'.format(name))
            continue
        if name == 'br' or selbst:
            continue
        if zu:
            if not stapel or stapel[-1] != name:
                fehler.append('Tag </{}> ohne passendes oeffnendes Tag'.format(name))
            else:
                stapel.pop()
        else:
            stapel.append(name)
    if stapel:
        fehler.append('nicht geschlossen: ' + ', '.join('<{}>'.format(x) for x in stapel))
    return fehler


def pruefe(datei, gegen=None, fertig=None, glossar=None):
    d = lese(datei)
    F, P = [], []
    if fertig is None:
        fertig = '_EN_FERTIG' in Path(datei).name
    ids = [s['id'] for s in d['segs']]
    dup = [k for k, v in collections.Counter(ids).items() if v > 1]
    if dup:
        F.append('Doppelte IDs: ' + ', '.join(dup[:10]))
    if not d['segs']:
        F.append('Keine <segment>-Bloecke erkannt')
    ref = None
    if gegen:
        ref = lese(gegen)
        rmap = {s['id']: s for s in ref['segs']}
        rids = [s['id'] for s in ref['segs']]
        if d['batch']:
            fehlend = [i for i in ids if i not in rmap]
            if fehlend:
                F.append('IDs nicht im Master: ' + ', '.join(fehlend[:10]))
            pos = [rids.index(i) for i in ids if i in rmap]
            if pos != sorted(pos) or (pos and pos != list(range(pos[0], pos[0] + len(pos)))):
                F.append('Batch ist kein zusammenhaengender, geordneter Ausschnitt des Masters')
        else:
            if ids != rids:
                F.append('Segmentfolge weicht ab: {} statt {} Segmente; erste Abweichung bei {}'.format(
                    len(ids), len(rids), next((a for a, b in zip(ids, rids) if a != b), ids[len(rids):][:1] or rids[len(ids):][:1])))
            rsec = [s['he'] for s in ref['secs']]
            if [s['he'] for s in d['secs']] != rsec:
                F.append('Abschnittsfolge (<he_title>) weicht vom Master ab')
        for s in d['segs']:
            r = rmap.get(s['id'])
            if not r:
                continue
            if s['n'] != r['n']:
                F.append('{}: n="{}" statt "{}"'.format(s['id'], s['n'], r['n']))
            if norm(s['he']) != norm(r['he']):
                F.append('{}: <he> veraendert'.format(s['id']))
            if norm(s['sec_he']) != norm(r['sec_he']):
                F.append('{}: Abschnitt (<he_title>) veraendert oder verschoben'.format(s['id']))
            if norm(r['en']) and norm(s['en']) != norm(r['en']):
                F.append('{}: bereits gefuelltes <en> veraendert'.format(s['id']))
        rtit = {norm(s['he']): norm(s['en']) for s in ref['secs'] if norm(s['en'])}
        for s in d['secs']:
            if norm(s['he']) in rtit and norm(s['en']) != rtit[norm(s['he'])]:
                F.append('<en_title> zu "{}" veraendert (Master: "{}")'.format(s['he'], rtit[norm(s['he'])]))
    titel = {}
    for s in d['secs']:
        en = s['en']
        if fertig and not norm(en):
            F.append('<en_title> leer fuer "{}"'.format(s['he']))
        if HEB_RE.search(en):
            F.append('<en_title> mit hebraeischen Zeichen: "{}"'.format(en))
        if '<' in en:
            F.append('<en_title> mit Tags: "{}"'.format(en))
        if norm(en):
            if norm(s['he']) in titel and titel[norm(s['he'])] != norm(en):
                F.append('Widerspruechliche <en_title> fuer "{}"'.format(s['he']))
            titel[norm(s['he'])] = norm(en)
    neu = {}
    if glossar and Path(glossar).exists():
        for r in C.read_tsv(glossar):
            if 'NEU' in (r.get('status') or ''):
                neu[r['abbr']] = r.get('neu_stamm') or ''
    gefuellt = 0
    for s in d['segs']:
        en = s['en']
        if not norm(C.strip_tags(en)):
            if fertig:
                F.append('{}: <en> leer'.format(s['id']))
            continue
        gefuellt += 1
        if norm(en) == norm(s['he']):
            F.append('{}: <en> enthaelt den hebraeischen Text'.format(s['id']))
        for f in tags_pruefen(en):
            F.append('{}: {}'.format(s['id'], f))
        for v in VERBOTEN:
            if re.search(v, en):
                F.append('{}: verbotene Form {}'.format(s['id'], v.replace('\\b', '')))
        he_len = len(C.strip_nikud(C.strip_tags(s['he'])))
        en_len = len(C.strip_tags(en))
        if he_len and not 1.0 <= en_len / float(he_len) <= 4.0:
            P.append('{}: Laengenverhaeltnis EN/HE {:.2f} (HE {} / EN {} Zeichen)'.format(
                s['id'], en_len / float(he_len), he_len, en_len))
        z_he = len([z for z in s['he'].split('\n') if z.strip()])
        z_en = len([z for z in en.split('\n') if z.strip()])
        if z_he != z_en:
            P.append('{}: {} Absaetze im Hebraeischen, {} im Englischen (Trennung per Zeilenwechsel)'.format(
                s['id'], z_he, z_en))
        if re.search(r'<br\s*/?>', en):
            P.append('{}: <br> im Englischen – Absaetze wie im Hebraeischen per Zeilenwechsel trennen'.format(s['id']))
        hb = len(HEB_RE.findall(C.strip_nikud(en)))
        if en_len and hb / float(en_len) > 0.15:
            P.append('{}: {:.0f} % hebraeische Zeichen in <en>'.format(s['id'], 100.0 * hb / en_len))
        if neu:
            plain = C.strip_tags(s['he'])
            treffer = sorted({k for k in neu if re.search(r'(?<![א-ת"])' + re.escape(k) + r'(?![א-ת"])',
                                                           C.strip_nikud(plain))})
            if treffer:
                P.append('{}: NEU-Kuerzel {} – Aufloesung im Englischen sichten'.format(s['id'], ' '.join(treffer[:8])))
    return {'datei': str(datei), 'gegen': str(gegen) if gegen else None, 'segmente': len(d['segs']),
            'abschnitte': len(d['secs']), 'en_gefuellt': gefuellt, 'fertig_modus': fertig,
            'he_quelle': d['planung'].get('he_quelle', ''), 'fehler': F, 'pruefen': P}


def bericht(r):
    L = ['OD YOSEF CHAI · HALAKHOT · ABNAHMEPRUEFUNG', '',
         'Datei: {}'.format(r['datei']), 'Gegen: {}'.format(r['gegen'] or '– (ohne Master-Vergleich)'),
         'Segmente {} · Abschnitte {} · <en> gefuellt {} · Modus {}'.format(
             r['segmente'], r['abschnitte'], r['en_gefuellt'], 'EN_FERTIG' if r['fertig_modus'] else 'Master'),
         'HE-Quelle laut Banddatei: {}'.format(r['he_quelle'] or 'nicht vermerkt'), '',
         'FEHLER: {}'.format(len(r['fehler']))]
    L += ['  ' + x for x in r['fehler'][:300]]
    L += ['', 'PRUEFEN: {}'.format(len(r['pruefen']))] + ['  ' + x for x in r['pruefen'][:500]]
    return '\n'.join(L) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description='Abnahmepruefung Od Yosef Chai (Banddatei/Batch)')
    ap.add_argument('--in', dest='datei', required=True)
    ap.add_argument('--gegen', help='Ausgangsmaster (BILINGUAL.txt) fuer den Feldvergleich')
    ap.add_argument('--fertig', action='store_true', help='alle <en>/<en_title> muessen gefuellt sein')
    ap.add_argument('--master', action='store_true', help='frischer Master: leere <en> erlaubt')
    ap.add_argument('--glossar', default=str(C.HERE / 'out' / 'glossar' / (C.WERK_TAG + '_GLOSSAR.tsv')))
    ap.add_argument('--json', help='Ergebnis zusaetzlich als JSON')
    a = ap.parse_args(argv)
    fertig = True if a.fertig else (False if a.master else None)
    r = pruefe(a.datei, a.gegen, fertig, a.glossar)
    txt = bericht(r)
    print(txt)
    if a.json:
        Path(a.json).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    return 1 if r['fehler'] else 0


if __name__ == '__main__':
    sys.exit(main())
