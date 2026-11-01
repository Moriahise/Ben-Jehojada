"""Independent, read-only protected-field and English checks. Usage: python verify_master.py INPUT OUTPUT REPORT.json"""
import sys,re,json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path

def verify(source,dest):
 a=Path(source).read_bytes();b=Path(dest).read_bytes();A=ET.fromstring(a);B=ET.fromstring(b)
 sa=list(A.iter('segment'));sb=list(B.iter('segment'));issues=[];details=[]
 def issue(sid,msg):issues.append({'id':sid,'problem':msg})
 field=re.compile(rb'(<(en|band_en)>)(.*?)(</\2>)',re.S)
 mask=lambda x:field.sub(lambda m:m[1]+b'ENGLISH_CONTENT'+m[4],x)
 protected=mask(a)==mask(b)
 if not protected:issue('DOCUMENT','Bytes outside en/band_en differ')
 if len(sa)!=len(sb):issue('DOCUMENT','Segment count differs')
 if [s.attrib for s in sa]!=[s.attrib for s in sb]:issue('DOCUMENT','IDs, attributes or order differ')
 expected={'en':0,'band_en':0};filled={'en':0,'band_en':0};unchanged_prefilled=0
 heb=re.compile(r'[\u0590-\u05ff\ufb1d-\ufb4f]');badname=re.compile(r'\b(?:God|YHWH|Yahweh|Jehovah|Adonai)\b',re.I)
 for x,y in zip(sa,sb):
  sid=x.get('id');e=y.findtext('en') or '';band=y.findtext('band_en') or '';bh=x.findtext('band_he') or ''
  for key in ['he','band_he']:
   if x.findtext(key)!=y.findtext(key):issue(sid,key+' differs')
  for key in ['en','band_en']:
   old=x.findtext(key) or '';new=y.findtext(key) or ''
   if old.strip():
    unchanged_prefilled+=int(old==new)
    if old!=new:issue(sid,'Prefilled '+key+' changed')
   else:
    expected[key]+=1
    if new.strip():filled[key]+=1
    else:issue(sid,'Empty '+key)
  if heb.search(band):issue(sid,'Hebrew in band_en')
  if re.search(r'<\s*/?fn\b',band):issue(sid,'Footnote in band_en')
  if badname.search(e+' '+band):issue(sid,'Forbidden Divine Name spelling')
  if re.search(r'Bible:|Tanach:|```|\[TRAKTAT\]|\[NR\]|„',e+' '+band):issue(sid,'Forbidden placeholder, heading or markup')
  if re.search(r'\b(?:Senlake|Dicta|HE lemma|band)\b',e,re.I):issue(sid,'Workshop note in English')
  lemma=re.findall(r'<lemma>(.*?)</lemma>',e,re.S);hl=re.findall(r'<lemma>(.*?)</lemma>',x.findtext('he') or '',re.S)
  if len(lemma)!=len(hl):issue(sid,'Lemma count differs')
  for l in lemma:
   if l not in band:issue(sid,'Lemma is not verbatim in band_en')
  if (x.findtext('he') or '').lstrip().startswith('<lemma>') and not e.lstrip().startswith('<lemma>'):issue(sid,'Lemma moved')
  if bh.count('…')!=band.count('…') or bh.strip().startswith('…')!=band.strip().startswith('…') or bh.strip().endswith('…')!=band.strip().endswith('…'):issue(sid,'Ellipses differ')
  stack=[]
  for m in re.finditer(r'<(/?)(\w+)([^>]*)>',e):
   close,tag,attrs=m.groups()
   if tag=='br' and not close:continue
   if attrs.strip() or tag not in {'lemma','fn','b','i','small','sup'}:issue(sid,'Unknown inner tag/attribute: '+m[0])
   if close:
    if not stack or stack[-1]!=tag:issue(sid,'Unbalanced inner tags: '+tag)
    if stack:stack.pop()
   else:
    if tag=='fn' and 'fn' in stack:issue(sid,'Nested footnote')
    stack.append(tag)
  if stack:issue(sid,'Unclosed inner tags')
  details.append({'id':sid,'n':y.get('n'),'daf':y.get('daf'),'ref':y.get('ref'),'en_filled':bool(e.strip()),'band_en_filled':bool(band.strip()),'lemma_verbatim':all(l in band for l in lemma),'english_footnotes':e.count('<fn>'),'he_protected':x.findtext('he')==y.findtext('he'),'band_he_protected':x.findtext('band_he')==y.findtext('band_he')})
 # Compare every element and attribute after hiding only the two allowed texts.
 for root in [A,B]:
  for elem in root.iter():
   if elem.tag in ['en','band_en']:elem.text='ENGLISH_CONTENT'
 if ET.tostring(A)!=ET.tostring(B):issue('DOCUMENT','XML structure/protected fields differ')
 titles=[(t.tag,t.text) for t in ET.fromstring(b).iter() if t.tag in ['he_title','en_title']]
 if any(heb.search(text or '') for tag,text in titles if tag=='en_title'):issue('DOCUMENT','Hebrew in English heading')
 result={'source':str(source),'output':str(dest),'input_sha256':hashlib.sha256(a).hexdigest(),'output_sha256':hashlib.sha256(b).hexdigest(),'input_bytes':len(a),'output_bytes':len(b),'segment_count':len(sb),'expected_empty_fields':expected,'filled_fields':filled,'original_prefilled_fields_preserved':unchanged_prefilled,'protected_bytes_identical':protected,'protected_mask_sha256':hashlib.sha256(mask(a)).hexdigest(),'heading_count_he':sum(tag=='he_title' for tag,text in titles),'heading_count_en':sum(tag=='en_title' for tag,text in titles),'all_lemmas_verbatim':all(d['lemma_verbatim'] for d in details),'english_footnotes':sum(d['english_footnotes'] for d in details),'issues':issues,'segments':details,'status':'PASS' if not issues else 'FAIL'}
 return result

if __name__=='__main__':
 result=verify(sys.argv[1],sys.argv[2]);Path(sys.argv[3]).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='segments'},ensure_ascii=False,indent=2));sys.exit(bool(result['issues']))
