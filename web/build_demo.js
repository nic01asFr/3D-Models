// Assemble demo.html (autonome) à partir de demo.tpl.html + signrender.js + fontmetrics.json.
// Usage : node web/build_demo.js  -> web/demo.html
const fs = require('fs'), d = __dirname;
let lib = fs.readFileSync(d + '/signrender.js', 'utf8').replace(/\n$/, '');
// la démo met 'Source Sans 3' (chargée via Google Fonts) en tête de la pile de police du SVG
lib = lib.replace("\\'Noto Sans CJK JP\\',\\'Noto Sans\\',\\'Source Sans 3\\'", "\\'Source Sans 3\\',\\'Noto Sans CJK JP\\',\\'Noto Sans\\'");
const fm = JSON.stringify(JSON.parse(fs.readFileSync(d + '/fontmetrics.json', 'utf8')));
const out = fs.readFileSync(d + '/demo.tpl.html', 'utf8').replace('/*LIB*/', () => lib).replace('/*FM*/', () => fm);
fs.writeFileSync(d + '/demo.html', out);
console.log('demo.html', out.length, 'octets');
