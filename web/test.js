// Tests : parité JS vs Python (dir_regles.py de production), règles, performance, scénario « lecture OCR ».
const S = require('./signrender.js'); const fs = require('fs');
S.setFontMetrics(JSON.parse(fs.readFileSync(__dirname + '/fontmetrics.json')));
const M = (t, p = 'autre', d = null, l = false) => ({ texte: t, pole: p, distance_km: d, local: l });
const A = { reseau: 'autoroutier', vitesse: 110, support: 'portique' }, O = { reseau: 'autre', vitesse: 50, eloignement_m: 10 };
const CASES = {
  c01: { type: 'D21a', contexte: { reseau: 'autre', vitesse: 90, support: 'sol', eloignement_m: 10 }, registres: [{ fond: 'vert', fleche: 'g', mentions: [M('Marseille', 'agglo', 28), M('Aubagne', 'agglo', 12)] }, { fond: 'blanc', fleche: 'g', mentions: [M('Gémenos', 'autre', 4.3)] }] },
  c02: { type: 'D21b', contexte: O, registres: [{ fond: 'vert', fleche: 'g', mentions: [M('Marseille', 'agglo')] }] },
  c03: { type: 'D31', contexte: A, registres: [{ fond: 'vert', fleche: 'hd', mentions: [M('Toulon', 'agglo', 65), M('Marseille', 'agglo', 28)] }, { fond: 'blanc', fleche: null, mentions: [M('Sortie 12')] }] },
  c04: { type: 'D42', contexte: A, registres: [{ fond: 'vert', fleche: 'h', mentions: [M('Toulon', 'agglo', 65), M('Aix-en-Provence', 'agglo', 35), M('Marseille', 'agglo', 28)] }] },
  c05: { type: 'D61a', contexte: A, registres: [{ fond: 'vert', fleche: null, mentions: [M('Marseille', 'agglo', 12)] }] },
  c06: { type: 'Da31a', contexte: A, registres: [{ fond: 'vert', fleche: null, mentions: [M('Toulon', 'agglo', 65)], voies: 2, sortie: true }] },
  c07: { type: 'D44', contexte: A, registres: [{ fond: 'bleu', fleche: 'd', mentions: [M('Aire de la Crau', 'autre', 2)] }] },
  c08: { type: 'D21a', contexte: O, registres: [{ fond: 'blanc', fleche: 'd', mentions: [M('Centre-ville', 'autre', 0.3, true)] }] },
  c09: { type: 'D21a', contexte: { reseau: 'autre', vitesse: 70, eloignement_m: 60, presignal: false }, registres: [{ fond: 'vert', fleche: 'd', mentions: [M('Marseille', 'agglo', 28)] }] },
  c10: { type: 'D21a', contexte: { reseau: 'autoroutier', vitesse: 130, support: 'sol' }, registres: [{ fond: 'vert', fleche: 'd', mentions: [M("L'Isle-sur-la-Sorgue", 'agglo', 7.4), M('Saint-Rémy-de-Provence', 'autre', 3.2)] }] },
  c11: { type: 'D21a', contexte: O, registres: [{ fond: 'bleu', fleche: 'g', mentions: [M('Aire', 'autre', 2)] }, { fond: 'vert', fleche: 'g', mentions: [M('Nice', 'agglo', 30)] }, { fond: 'jaune', fleche: 'g', mentions: [M('Déviation', 'autre', 1)] }] },
  x01: { type: 'D21a', contexte: O, registres: [{ fond: 'blanc', fleche: 'g', mentions: [M('Gémenos', 'autre', 4)] }, { fond: 'vert', fleche: 'g', mentions: [M('Marseille', 'agglo', 28)] }] },
  x02: { type: 'D21b', contexte: O, registres: [{ fond: 'vert', fleche: 'g', mentions: [M('Marseille', 'agglo', 28)] }] },
  x03: { type: 'D21a', contexte: O, registres: [{ fond: 'vert', fleche: 'g', mentions: [M('Marseille', 'agglo')] }] },
  x04: { type: 'D21a', contexte: O, registres: [{ fond: 'vert', fleche: 'g', mentions: [M('A', 'agglo', 9), M('B', 'agglo', 8), M('C', 'agglo', 7), M('D', 'agglo', 6), M('E', 'agglo', 5)] }] },
  x05: { type: 'D21a', contexte: O, registres: [{ fond: 'vert', fleche: 'g', mentions: [M('Aubagne', 'agglo', 12), M('Marseille', 'agglo', 28)] }] },
  x06: { type: 'D21a', contexte: { reseau: 'autre', vitesse: 130 }, registres: [{ fond: 'vert', fleche: 'g', mentions: [M('Marseille', 'agglo', 28)] }] },
};
// Référence produite par dir_regles.py / composition.py (production)
const REF = JSON.parse(fs.readFileSync(__dirname + '/ref.json'));
let ok = 0, ko = 0; const fails = [];
for (const [id, spec] of Object.entries(CASES)) {
  const r = REF[id]; const { comp, errors } = S.composer(spec);
  if (r.err) { if (errors.length === 1 && errors[0] === r.err) ok++; else { ko++; fails.push([id, 'erreur attendue: ' + r.err, 'obtenu: ' + JSON.stringify(errors)]); } continue; }
  if (errors.length) { ko++; fails.push([id, 'erreur inattendue', errors]); continue; }
  const g = S.geometrie(comp);
  const mine = { hb: comp.hb_mm, hc: comp.registres.map(x => x.hc_mm), m: comp.registres.map(x => x.mentions.map(m => [m.texte, m.dist])), W: Math.round(g.largeur * 1e6) / 1e6, H: Math.round(g.hauteur * 1e6) / 1e6, rows: g.registres.map(x => Math.round(x.h * 1e6) / 1e6) };
  const same = JSON.stringify([mine.hb, mine.hc, mine.m, mine.rows]) === JSON.stringify([r.hb, r.hc, r.m, r.rows]) && Math.abs(mine.W - r.W) < 1e-3 && Math.abs(mine.H - r.H) < 1e-3;
  if (same) ok++; else { ko++; fails.push([id, r, mine]); }
}
console.log('PARITE JS/Python : %d identiques, %d écarts sur %d cas', ok, ko, Object.keys(CASES).length);
fails.forEach(x => console.log(' ÉCART', JSON.stringify(x)));

// perf
const t0 = process.hrtime.bigint(); const N = 5000;
for (let i = 0; i < N; i++) { const { comp } = S.composer(CASES.c01); const g = S.geometrie(comp); S.renderSVG(comp, g); }
console.log('PERF : %s ms / panneau (composition + géométrie + SVG)', (Number(process.hrtime.bigint() - t0) / 1e6 / N).toFixed(3));

// scénario « OCR » : lectures bruitées -> diagnostic + correction automatique
const ocr = [
  ['blocs inversés + distances croissantes', { type: 'D21a', contexte: O, registres: [{ fond: 'blanc', fleche: 'g', mentions: [M('Gémenos', 'autre', 4.3)] }, { fond: 'vert', fleche: 'g', mentions: [M('Aubagne', 'agglo', 12), M('Marseille', 'agglo', 28)] }] }],
  ['D21b lu avec distance', CASES.x02],
  ['vitesse hors table', CASES.x06],
];
for (const [n, s] of ocr) {
  const d = S.composer(s); const c = S.corriger(s); const d2 = S.composer(c.spec);
  console.log('OCR « %s » : %d erreur(s) -> corrections %j -> après : %d erreur(s) %j', n, d.errors.length, c.log, d2.errors.length, d2.errors);
}
// largeur de texte : apostrophe typographique (bug repéré côté Blender : avance 1000 dans Noto CJK)
console.log('apostrophe ’ vs \' : %s vs %s (m, cap 0.1)', S.textWidth('d’art', 0.1).toFixed(4), S.textWidth("d'art", 0.1).toFixed(4));
if (ko) process.exit(1);
