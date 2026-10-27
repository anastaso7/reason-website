const fs=require('fs');
const src=fs.readFileSync('../reason/project/Main.dc.html','utf8');
const m=src.match(/<script type="text\/x-dc" data-dc-script[^>]*>([\s\S]*?)<\/script>/);
const code='class DCLogic{}\n'+m[1]+'\nreturn Component;';
const C=new Function(code)();
const out={};
for(const lang of ['en','el']){
  const c=new C(); c.props={accent:'#2B3490'}; c.state={lang};
  const v=c.renderVals();
  out[lang]=JSON.parse(JSON.stringify(v,(k,x)=>typeof x==='function'?undefined:x));
}
fs.writeFileSync('vals.json',JSON.stringify(out,null,1));
console.log(Object.keys(out.en).join(','), out.el.faqs.length, out.el.days.length);
