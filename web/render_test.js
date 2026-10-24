const S=require('./signrender.js'),fs=require('fs');S.setFontMetrics(JSON.parse(fs.readFileSync('fontmetrics.json')));
// réutilise les cas de test.js
const src=fs.readFileSync('test.js','utf8');const CASES=eval('(function(){const S={};'+src.split("const M =")[1].split('// Référence')[0].replace(/^/,'const M =')+';return CASES})()');
let html='<html><body style="margin:0;background:#ccd;font:12px sans-serif">';
for(const id of ['c01','c03','c04','c06','c07','c08','c09','c11']){const {comp,errors}=S.composer(CASES[id]);const g=S.geometrie(comp);const r=S.renderSVG(comp,g);fs.writeFileSync('out_'+id+'.svg',r.svg);
 html+='<div style="display:inline-block;margin:6px;vertical-align:top"><div>'+id+' '+(r.warn.join(';'))+'</div>'+r.svg+'</div>';}
fs.writeFileSync('sheet.html',html+'</body></html>');
