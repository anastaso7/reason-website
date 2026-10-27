import re, json, os, sys, shutil, html
from PIL import Image
SITE=(os.environ.get('SITE_URL') or 'https://YOUR-DOMAIN.gr').rstrip('/')
R='../reason'; OUT='dist'
src=open(R+'/project/Main.dc.html').read()
vals=json.load(open('vals.json'))
shutil.rmtree(OUT,ignore_errors=True); os.makedirs(OUT+'/img'); os.makedirs(OUT+'/el')

# ---- images: blob id -> file by byte size
sizes={12916:'mark',8854:'wordmark',303865:'reason-gym-petralona-personal-training.jpg',372142:'reason-gym-petralona-athens-space.jpg',315843:'reason-gym-dumbbells-arched-window.jpg',365978:'reason-gym-plants-corner.jpg',212897:'reason-gym-showers.jpg',163731:'reason-gym-coffee-corner.jpg',255274:'reason-gym-24-7-sign.jpg',181047:'reason-open-gym-poster.jpg',329459:'reason-gym-power-rack.jpg',425857:'reason-gym-lunge-training.jpg',275500:'reason-gym-cable-machine-window.jpg'}
byname={}
for fn in os.listdir(R+'/assets'):
    p=R+'/assets/'+fn; sz=os.path.getsize(p)
    if sz in sizes: byname[sizes[sz]]=p
blob={}
ids={'1074ece099442bd1eda6fadcd3344454':12916,'547aff9dc08813eaf2dec66f1d5289f5':8854,'e07082efffe27bebbd48e81dd6f98cdf':303865,'835c9aab291456239d38a33dfa450239':372142,'75ee525c9391be74403673d0460b9c91':315843,'643091f27a24e9d7df5c4a3522041887':365978,'47962f3b552f5d654b3487c8f914072f':212897,'3a619f1c894cf9f05e837615c1847379':163731,'c2547dc1553740a95a799ceeccc8bccf':255274,'e1f87baeee6a1b6a907b467658492240':181047,'6e95c1c142719a7d09eee44b4b5a67db':329459,'a6f000d37c6b972b08818f9cd3772db8':425857,'7ac3e0a8a4b9381f2f15b7b17317df3f':275500}
for i,sz in ids.items(): blob[i]=sizes[sz]
for k,v in blob.items():
    if k in ('1074ece099442bd1eda6fadcd3344454','547aff9dc08813eaf2dec66f1d5289f5'):
        name=v+'.png'; shutil.copy(byname[v],OUT+'/img/'+name)
        blob[k]=name
    else:
        im=Image.open(byname[v]).convert('RGB'); im.thumbnail((1600,1600)); im.save(OUT+'/img/'+v,quality=82,optimize=True,progressive=True)
# favicons
fav=Image.open('fav.png'); fav.save(OUT+'/favicon.png'); fav.resize((32,32),Image.LANCZOS).save(OUT+'/favicon-32.png'); 
Image.open('fav.png').resize((180,180),Image.LANCZOS).save(OUT+'/apple-touch-icon.png')

# ---- template
body=re.search(r'</helmet>(.*?)</x-dc>',src,re.S).group(1)
css=re.search(r'<style>(.*?)</style>',src,re.S).group(1)
for k,v in blob.items(): body=body.replace('/_blob/'+k,'/img/'+v)
body=body.replace(' lang="{{htmlLang}}"','')

def lookup(ctx,path):
    cur=None
    parts=path.strip().split('.')
    if parts[0] in ctx: cur=ctx[parts[0]]
    else: raise KeyError(path)
    for p in parts[1:]: cur=cur[p]
    return cur
TAGRE=re.compile(r'<(/?)sc-(for|if)\b([^>]*)>')
def subst(t,ctx):
    def r(m):
        v=lookup(ctx,m.group(1))
        if isinstance(v,bool): v='true' if v else 'false'
        return html.escape(str(v),quote=False)
    return re.sub(r'\{\{\s*([\w.]+)\s*\}\}',r,t)
def render(text,ctx):
    out=''; pos=0
    while True:
        m=TAGRE.search(text,pos)
        if not m: out+=subst(text[pos:],ctx); break
        out+=subst(text[pos:m.start()],ctx)
        assert not m.group(1),text[m.start()-80:m.start()+80]
        depth=1; j=m.end()
        while depth:
            n=TAGRE.search(text,j); assert n
            depth+= -1 if n.group(1) else 1; j=n.end()
        inner=text[m.end():n.start()]; attrs=m.group(3); kind=m.group(2)
        if kind=='for':
            lst=lookup(ctx,re.search(r'list="\{\{(.*?)\}\}"',attrs).group(1)); var=re.search(r'as="(\w+)"',attrs).group(1)
            for i,it in enumerate(lst):
                it=dict(it); it['_i']=i
                out+=render(inner,{**ctx,var:it})
        else:
            expr=re.search(r'value="\{\{(.*?)\}\}"',attrs).group(1).strip()
            panel={'isOpenTab':'open','isGroupsTab':'groups','isPersonalTab':'personal'}
            if expr in panel:
                out+='<div class="panel" data-panel="%s"%s>'%(panel[expr],'' if expr=='isOpenTab' else ' hidden')+render(inner,ctx)+'</div>'
            elif expr=='f.open':
                f=ctx['f']; out+='<div class="faq-a"%s>'%('' if f['open'] else ' hidden')+render(inner,ctx)+'</div>'
            else:
                try: ok=lookup(ctx,expr)
                except KeyError: ok=False
                if ok: out+=render(inner,ctx)
        pos=n.end()
    return out

def page(lang):
    v=dict(vals[lang]); t=v['t']
    b=body
    # lang toggle -> links
    b=re.sub(r'<button onClick="\{\{setEn\}\}"[^>]*>EN</button>','<a class="lang" href="/" hreflang="en" lang="en" aria-label="English"%s>EN</a>'%(' aria-current="true"' if lang=='en' else ''),b)
    b=re.sub(r'<button onClick="\{\{setEl\}\}"[^>]*>ΕΛ</button>','<a class="lang" href="/el/" hreflang="el" lang="el" aria-label="Ελληνικά"%s>ΕΛ</a>'%(' aria-current="true"' if lang=='el' else ''),b)
    for fn,key,lab in [('setOpen','open','tab1'),('setGroups','groups','tab2'),('setPersonal','personal','tab3')]:
        b=re.sub(r'<button onClick="\{\{%s\}\}"[^>]*>'%fn,'<button class="tab" data-tab="%s" aria-selected="%s">'%(key,'true' if key=='open' else 'false'),b)
    b=b.replace('<div style="display:inline-flex;flex-wrap:wrap;gap:6px;margin-top:36px;background:#EBE2D0;padding:6px;border-radius:28px">','<div role="tablist" style="display:inline-flex;flex-wrap:wrap;gap:6px;margin-top:36px;background:#EBE2D0;padding:6px;border-radius:28px">')
    b=b.replace('onClick="{{f.toggle}}" aria-expanded="{{f.open}}"','class="faq-q" aria-expanded="{{f.open}}"')
    html_body=render(b,v)
    assert '{{' not in html_body, re.findall(r'.{60}\{\{.{30}',html_body)[:3]
    # lazy images except first three
    cnt=[0]
    def lz(m):
        cnt[0]+=1
        return m.group(0) if cnt[0]<=4 else m.group(0).replace('<img ','<img loading="lazy" decoding="async" ',1)
    html_body=re.sub(r'<img [^>]*>',lz,html_body)
    path='/' if lang=='en' else '/el/'
    url=SITE+path
    title=t_title[lang]; desc=t_desc[lang]
    faq={"@context":"https://schema.org","@type":"FAQPage","inLanguage":lang,"mainEntity":[{"@type":"Question","name":f['q'],"acceptedAnswer":{"@type":"Answer","text":f['a']}} for f in v['faqs']]}
    biz={"@context":"https://schema.org","@type":["ExerciseGym","SportsActivityLocation"],"@id":SITE+"/#gym","name":"Reason Fitness Concept","url":url,
     "description":desc,"telephone":"+30 698 564 2282","priceRange":"€15–€550","image":SITE+"/img/reason-gym-petralona-athens-space.jpg","logo":SITE+"/img/mark.png",
     "address":{"@type":"PostalAddress","streetAddress":"Pandorou 36","addressLocality":"Athens","addressNeighborhood":"Petralona","postalCode":"118 53","addressCountry":"GR"},
     "hasMap":"https://www.google.com/maps/search/?api=1&query=Reason+Fitness+Concept+Pandorou+36+Athens",
     "openingHoursSpecification":{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],"opens":"00:00","closes":"23:59"},
     "knowsLanguage":["en","el"],
     "makesOffer":[{"@type":"Offer","name":"Open Gym drop-in","price":"20","priceCurrency":"EUR"},{"@type":"Offer","name":"Group class (single)","price":"15","priceCurrency":"EUR"},{"@type":"Offer","name":"Personal session","price":"30","priceCurrency":"EUR"},{"@type":"Offer","name":"Semi-personal session (2 people)","price":"40","priceCurrency":"EUR"}],
     "sameAs":["https://www.instagram.com/reason.concept/","https://www.getyourguide.com/athens-l91/athens-open-gym-access-at-reason-fitness-concept-t1303870","https://www.airbnb.com/services/7073539"]}
    e=lambda s: html.escape(s,quote=True)
    ld=lambda o:'<script type="application/ld+json">'+json.dumps(o,ensure_ascii=False)+'</script>'
    head=f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en" href="{SITE}/">
<link rel="alternate" hreflang="el" href="{SITE}/el/">
<link rel="alternate" hreflang="x-default" href="{SITE}/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Reason Fitness Concept">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/img/reason-gym-petralona-athens-space.jpg">
<meta property="og:locale" content="{'en_GB' if lang=='en' else 'el_GR'}">
<meta property="og:locale:alternate" content="{'el_GR' if lang=='en' else 'en_GB'}">
<meta name="twitter:card" content="summary_large_image">
<meta name="geo.region" content="GR-I"><meta name="geo.placename" content="Petralona, Athens">
<meta name="theme-color" content="#F6F0E4">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,300;0,500;1,300&family=Source+Serif+4:ital,wght@0,300;0,500;1,300&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
{ld(biz)}
{ld(faq)}
<style>{css}
.tab{{border:0;cursor:pointer;font-family:Inter,system-ui,sans-serif;font-size:15px;font-weight:600;padding:12px 22px;border-radius:999px;min-height:44px;background:transparent;color:#26262A}}
.tab[aria-selected=true]{{background:#2B3490;color:#fff}}
.lang{{display:inline-flex;align-items:center;font-size:13px;font-weight:600;padding:0 14px;border-radius:999px;min-height:36px;color:#26262A}}
.lang[aria-current=true]{{background:#2B3490;color:#fff}}
.faq-q:focus-visible,.tab:focus-visible,a:focus-visible{{outline:2px solid #2B3490;outline-offset:3px}}
[hidden]{{display:none!important}}
html{{scroll-behavior:smooth}}
@media (prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}
</style>
</head>
<body>
'''
    js='''<script>
document.querySelectorAll('.tab').forEach(function(b){b.addEventListener('click',function(){
document.querySelectorAll('.tab').forEach(function(x){x.setAttribute('aria-selected',x===b?'true':'false')});
document.querySelectorAll('.panel').forEach(function(p){p.hidden=p.getAttribute('data-panel')!==b.getAttribute('data-tab')});});});
document.querySelectorAll('.faq-q').forEach(function(q){q.addEventListener('click',function(){
var a=q.parentNode.querySelector('.faq-a'),open=q.getAttribute('aria-expanded')==='true';
document.querySelectorAll('.faq-q').forEach(function(x){x.setAttribute('aria-expanded','false');x.querySelector('span:last-child').textContent='+';x.parentNode.querySelector('.faq-a').hidden=true});
if(!open){q.setAttribute('aria-expanded','true');q.querySelector('span:last-child').textContent='\\u2212';a.hidden=false}});});
</script>
</body></html>'''
    return head+html_body+js

t_title={'en':'Reason Fitness Concept | 24/7 Open Gym & Strength Training in Petralona, Athens','el':'Reason Fitness Concept | 24/7 Open Gym και Strength & Conditioning στα Πετράλωνα, Αθήνα'}
t_desc={'en':'24/7 Open Gym and Strength & Conditioning small-group and personal training in Petralona, Athens. Max 3 people in the Open Gym, up to 6 in classes. First group session free. Pandorou 36.',
 'el':'Open Gym 24/7 και ομαδικά ή personal Strength & Conditioning στα Πετράλωνα, Αθήνα. Το πολύ 3 άτομα στο Open Gym, έως 6 στις ομάδες. Η πρώτη ομαδική δωρεάν. Πανδώρου 36.'}
open(OUT+'/index.html','w').write(page('en'))
open(OUT+'/el/index.html','w').write(page('el'))
open(OUT+'/robots.txt','w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
open(OUT+'/sitemap.xml','w').write(f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
<url><loc>{SITE}/</loc><xhtml:link rel="alternate" hreflang="en" href="{SITE}/"/><xhtml:link rel="alternate" hreflang="el" href="{SITE}/el/"/><xhtml:link rel="alternate" hreflang="x-default" href="{SITE}/"/></url>
<url><loc>{SITE}/el/</loc><xhtml:link rel="alternate" hreflang="en" href="{SITE}/"/><xhtml:link rel="alternate" hreflang="el" href="{SITE}/el/"/><xhtml:link rel="alternate" hreflang="x-default" href="{SITE}/"/></url>
</urlset>
''')
open(OUT+'/_headers','w').write('/img/*\n  Cache-Control: public, max-age=31536000, immutable\n/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n')
print('ok',[(f,os.path.getsize(OUT+'/'+f)) for f in ('index.html','el/index.html')])
