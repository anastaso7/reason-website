# Cookie consent (Consent Mode v2, default denied) + Google Tag Manager loaded only after acceptance.
import os
GTM_ID = os.environ.get('GTM_ID','GTM-NJPQRCB5')
TXT = {
 'en': dict(msg='We use cookies to measure visits and improve our site and ads. You can accept or decline.',acc='Accept',dec='Decline',more='Privacy Policy',priv='/privacy/',set='Cookie settings'),
 'el': dict(msg='Χρησιμοποιούμε cookies για να μετράμε τις επισκέψεις και να βελτιώνουμε το site και τις διαφημίσεις μας. Μπορείς να αποδεχτείς ή να απορρίψεις.',acc='Αποδοχή',dec='Απόρριψη',more='Πολιτική απορρητου',priv='/el/privacy/',set='Ρυθμίσεις cookies'),
}
def head():
    return ('<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}'
            "gtag('consent','default',{ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',analytics_storage:'denied',wait_for_update:500});"
            "gtag('set','ads_data_redaction',true);</script>")
def body(lang):
    t=TXT[lang]
    return f'''<div id="cc" role="dialog" aria-live="polite" aria-label="Cookies" hidden>
<p>{t['msg']} <a href="{t['priv']}">{t['more']}</a></p>
<div class="cc-b"><button type="button" id="cc-dec">{t['dec']}</button><button type="button" id="cc-acc">{t['acc']}</button></div></div>
<style>
#cc{{position:fixed;left:16px;right:16px;bottom:16px;z-index:100;max-width:560px;margin:0 auto;background:#FBF7EE;color:#26262A;border:1px solid #E4DAC7;border-radius:22px;padding:18px 20px;box-shadow:0 18px 40px rgba(38,38,42,.18);font:400 14px/1.55 Inter,system-ui,sans-serif}}
#cc[hidden]{{display:none}}#cc p{{margin:0 0 14px}}#cc a{{color:#2B3490}}
.cc-b{{display:flex;gap:10px}}.cc-b button{{flex:1;min-height:44px;border-radius:999px;border:1.5px solid #26262A;background:transparent;color:#26262A;font:600 14px Inter,system-ui,sans-serif;cursor:pointer}}
.cc-b button:focus-visible{{outline:2px solid #2B3490;outline-offset:3px}}
</style>
<script>
(function(){{
var KEY='rc_consent',GTM='{GTM_ID}',loaded=false,el=document.getElementById('cc');
function get(){{try{{return localStorage.getItem(KEY)}}catch(e){{return null}}}}
function set(v){{try{{localStorage.setItem(KEY,v)}}catch(e){{}}}}
function load(){{if(loaded)return;loaded=true;
(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s);j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer',GTM);}}
function grant(){{gtag('consent','update',{{ad_storage:'granted',ad_user_data:'granted',ad_personalization:'granted',analytics_storage:'granted'}});load();}}
function deny(){{gtag('consent','update',{{ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',analytics_storage:'denied'}});}}
var c=get();if(c==='granted')grant();else if(c!=='denied')el.hidden=false;
document.getElementById('cc-acc').onclick=function(){{set('granted');el.hidden=true;grant();}};
document.getElementById('cc-dec').onclick=function(){{set('denied');el.hidden=true;deny();}};
var pl=document.querySelector('a[href$="privacy/"]');
if(pl&&pl.parentNode){{var s=document.createElement('a');s.href='#';s.textContent='{t['set']}';s.style.cssText='border-bottom:1px solid #5E5A52';s.onclick=function(e){{e.preventDefault();el.hidden=false;}};pl.parentNode.appendChild(document.createTextNode(' \\u00b7 '));pl.parentNode.appendChild(s);}}
document.addEventListener('click',function(e){{var a=e.target.closest&&e.target.closest('a[href]');if(!a)return;var h=a.getAttribute('href')||'',ev=null;
if(h.indexOf('ig.me/')>-1)ev='book_click';else if(h.indexOf('instagram.com')>-1)ev='instagram_click';else if(h.indexOf('tel:')===0)ev='phone_click';else if(h.indexOf('mailto:')===0)ev='email_click';
else if(h.indexOf('fitbook')>-1)ev='member_login_click';else if(h.indexOf('share.google')>-1||h.indexOf('maps')>-1)ev='maps_click';else if(h.indexOf('getyourguide')>-1||h.indexOf('airbnb')>-1)ev='listing_click';
if(ev)window.dataLayer.push({{event:ev,link_url:h,page_language:document.documentElement.lang}});}});
}})();
</script>'''
