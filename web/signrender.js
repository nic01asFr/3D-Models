/* signrender.js — composition (règles IISR) + rendu SVG d'un panneau de direction, côté navigateur / Node.
   Port de dir_regles.py + composition.py (IISR 5e partie art. 81 C, 81-1, 83). Dimensions hors Hb/Hc = HYPOTHÈSES (NF P98-532 / Sétra non consultés). */
(function (root) {
  'use strict';
  const GAMMES = [100, 125, 160, 200, 250, 320];
  const HB = { autoroutier: { 70: 160, 90: 200, 110: 250, 130: 320 }, autre: { 50: 100, 70: 100, 90: 125 } };
  const CLAIR = ['blanc', 'jaune'];
  const ORDRE = ['bleu', 'vert', 'blanc', 'jaune'];
  const HYP = { hauteur_registre_sur_hc: 2.0, marge_h_sur_hc: 1.0, fleche_largeur_sur_hc: 2.5, liseré_sur_hc: 0.12 };
  const COL = { vert: '#00704A', bleu: '#00468C', blanc: '#F0F0EB', noir: '#141414', jaune: '#FFCC00', rouge: '#C8102E', marron: '#59341C' };
  let FM = null;
  function setFontMetrics(fm) { FM = fm; }

  // arrondi « banquier » comme Python round()
  function pyRound(x) { const f = Math.floor(x), d = x - f; if (d < 0.5) return f; if (d > 0.5) return f + 1; return f % 2 === 0 ? f : f + 1; }
  function arrondiDistanceKm(d) { if (d > 5) return pyRound(d); if (d >= 1) return pyRound(d * 2) / 2; return pyRound(d * 10) / 10; }
  function fmtDistance(d, local) {
    if (d === null || d === undefined) return null;
    if (local && d < 0.5) return pyRound(d * 1000 / 50) * 50 + ' m';
    return String(Number(arrondiDistanceKm(d).toPrecision(6))).replace('.', ',');
  }
  function casse(t, pole) { return ['agglo', 'pole_non_agglo', 'secondaire', 'rabattement'].includes(pole) ? t.toUpperCase() : t.charAt(0).toUpperCase() + t.slice(1); }

  function textWidth(t, cap) {
    if (!t) return 0;
    let a = 0;
    for (const ch of t) { const c = ch === '’' ? "'" : ch; const v = FM.adv[c]; a += (v === undefined ? 600 : v); }
    return (a / FM.upm) * cap / (FM.cap / FM.upm);
  }
  const gammePlus = (h, n) => GAMMES[Math.min(GAMMES.indexOf(h) + (n || 1), GAMMES.length - 1)];
  function hb(reseau, vitesse, support, type, eloignement, presignal) {
    const tab = HB[reseau]; if (!tab) throw new Error('réseau inconnu : ' + reseau);
    const v = Object.keys(tab).map(Number).sort((a, b) => a - b).find(s => vitesse <= s);
    if (v === undefined) throw new Error('Hb non défini par l’IISR pour ' + reseau + ' à ' + vitesse + ' km/h');
    let h = tab[v];
    if (['portique', 'potence', 'haut-mat'].includes(support)) h = Math.max(h, 250);
    if (type.startsWith('D2') && !type.startsWith('D29')) {
      if (!presignal) h = gammePlus(h, 1);
      if (eloignement > 50) h = gammePlus(h, 2); else if (eloignement >= 15) h = gammePlus(h, 1);
    }
    return h;
  }
  const hc = (h, fond) => CLAIR.includes(fond) ? h : gammePlus(h, 1);

  // règles de composition (composition.valider)
  function valider(p) {
    const err = []; const t = p.type || 'position';
    const cols = p.registres.map(r => r.couleur);
    const idx = cols.filter(c => ORDRE.includes(c)).map(c => ORDRE.indexOf(c));
    if (JSON.stringify(idx) !== JSON.stringify([...idx].sort((a, b) => a - b))) err.push('ordre des blocs de couleur (bleu, vert, blanc, jaune)');
    let tot = 0; const multic = new Set(cols).size > 1;
    for (const r of p.registres) {
      const ds = r.mentions.map(m => m.distance_km).filter(d => d !== null && d !== undefined);
      if (JSON.stringify(ds) !== JSON.stringify([...ds].sort((a, b) => b - a))) err.push('distances non décroissantes dans le bloc ' + r.couleur);
      const n = r.mentions.length; tot += n;
      if (['position', 'avancee', 'confirmation'].includes(t) && n > 4) err.push('plus de 4 mentions pour la couleur ' + r.couleur);
    }
    let lim = { presignalisation: 6, D42: 9, bifurcation: 4, portique: 12, D71: 3, filante_autoroutiere: 4 }[t];
    if (['position', 'avancee', 'confirmation'].includes(t) && multic) lim = 6;
    if (lim && tot > lim) err.push(tot + ' mentions > limite ' + lim + ' (' + t + ')');
    return err;
  }

  /** composer(spec) -> {comp, errors}. Ne lève pas : renvoie les non-conformités (mode « lecture OCR »). comp=null si Hb indéfini. */
  function composer(spec) {
    const c = spec.contexte || {}; const t = spec.type || 'D21a';
    const k3 = t.slice(0, 3);
    const typ = ['D21', 'D31', 'D41', 'D42', 'D61', 'D62'].includes(k3)
      ? ({ D21: 'position', D31: 'avancee', D41: 'presignalisation', D42: 'D42', D61: 'confirmation', D62: 'confirmation' })[k3]
      : (spec.regime || 'position');
    const errors = valider({ type: typ, registres: spec.registres.map(r => ({ couleur: r.fond, mentions: r.mentions })) });
    const dist = spec.registres.some(r => r.mentions.some(m => m.distance_km !== null && m.distance_km !== undefined));
    if (t === 'D21b' && dist) errors.push('D21b ne comporte pas d’indication de distance');
    if (t === 'D21a' && !dist) errors.push('D21a comporte une indication de distance');
    let h0;
    try { h0 = hb(c.reseau || 'autre', c.vitesse === undefined ? 50 : c.vitesse, c.support || 'sol', t, c.eloignement_m || 0, c.presignal === undefined ? true : c.presignal); }
    catch (e) { errors.push(e.message); return { comp: null, errors }; }
    const registres = spec.registres.map(r => {
      const H = hc(h0, r.fond);
      return { fond: r.fond, fleche: r.fleche || null, hc_mm: H, voies: r.voies || 0, sortie: !!r.sortie,
        mentions: r.mentions.map(m => ({ texte: casse(m.texte, m.pole || 'autre'), dist: fmtDistance(m.distance_km, !!m.local) })) };
    });
    return { comp: { type: t, hb_mm: h0, registres }, errors };
  }

  function geometrie(comp) {
    const k = HYP; let W = 0; const rows = [];
    for (const r of comp.registres) {
      const H = r.hc_mm / 1000; const h = k.hauteur_registre_sur_hc * H * Math.max(1, r.mentions.length);
      let w = 0;
      for (const m of r.mentions) w = Math.max(w, textWidth(m.texte, H) + (m.dist ? 1.4 * H + textWidth(m.dist, H) : 0));
      const fl = r.fleche;
      const fw = !fl ? 0 : (['h', 'b', 'hd', 'hg'].includes(fl) ? 1.1 * Math.min(0.8 * h, 4 * H) + H : 0.5 * h + 0.5 * H);
      w += 2 * k.marge_h_sur_hc * H + Math.max(fw, fl ? k.fleche_largeur_sur_hc * H : 0);
      const lanes = r.voies || 0; const lh = lanes ? 3.0 * H : 0;
      if (lanes) w = Math.max(w, lanes * 2.6 * H + 2 * k.marge_h_sur_hc * H);
      W = Math.max(W, w); rows.push({ r, h, H, lh, lanes });
    }
    return { largeur: W, hauteur: rows.reduce((s, x) => s + x.h + x.lh, 0),
      registres: rows.map(x => ({ h: x.h + x.lh, h_txt: x.h, lane_h: x.lh, voies: x.lanes, cap: x.H, registre: x.r })) };
  }

  /** Corrections automatiques proposées pour une lecture non conforme (tri des blocs et des distances). */
  function corriger(spec) {
    const s = JSON.parse(JSON.stringify(spec)); const log = [];
    const o = s.registres.map(r => ORDRE.indexOf(r.fond));
    const sorted = [...s.registres].sort((a, b) => ORDRE.indexOf(a.fond) - ORDRE.indexOf(b.fond));
    if (JSON.stringify(sorted) !== JSON.stringify(s.registres)) { s.registres = sorted; log.push('blocs réordonnés (bleu, vert, blanc, jaune)'); }
    for (const r of s.registres) {
      const before = JSON.stringify(r.mentions.map(m => m.distance_km));
      r.mentions.sort((a, b) => (b.distance_km ?? -1) - (a.distance_km ?? -1));
      if (before !== JSON.stringify(r.mentions.map(m => m.distance_km))) log.push('distances classées par ordre décroissant (' + r.fond + ')');
    }
    return { spec: s, log };
  }

  // ------------------------------------------------------------------ rendu SVG (unités : mm, y vers le bas)
  const f = x => (Math.round(x * 100) / 100);
  function offsetPoly(pts, d) {   // polygone convexe, sens anti-horaire (math), décalage vers l'intérieur de d
    const n = pts.length, L = [];
    for (let i = 0; i < n; i++) {
      const a = pts[i], b = pts[(i + 1) % n]; const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy);
      const nx = -dy / l, ny = dx / l; L.push([a[0] + nx * d, a[1] + ny * d, dx, dy]);
    }
    return pts.map((_, i) => {
      const p = L[(i + n - 1) % n], q = L[i]; const det = p[2] * q[3] - p[3] * q[2];
      const t = ((q[0] - p[0]) * q[3] - (q[1] - p[1]) * q[2]) / det; return [p[0] + p[2] * t, p[1] + p[3] * t];
    });
  }
  function arrowPts(s, deg) {
    const hw = s * 0.11, hh = s * 0.30, hl = s * 0.40;
    const base = [[-s / 2, -hw], [s / 2 - hl, -hw], [s / 2 - hl, -hh], [s / 2, 0], [s / 2 - hl, hh], [s / 2 - hl, hw], [-s / 2, hw]];
    const a = deg * Math.PI / 180, c = Math.cos(a), sn = Math.sin(a);
    return base.map(([x, y]) => [x * c - y * sn, x * sn + y * c]);
  }
  const DEG = { d: 0, g: 180, h: 90, b: -90, hd: 45, hg: 135 };
  const poly = (pts, fill, dx, dy) => '<polygon fill="' + fill + '" points="' + pts.map(p => f(p[0] + dx) + ',' + f(-(p[1]) + dy)).join(' ') + '"/>';
  function text(s, x, yc, cap, anchor, w, fill) {
    return '<text x="' + f(x) + '" y="' + f(yc + cap / 2) + '" font-size="' + f(cap / 0.733) + '" text-anchor="' + anchor + '" textLength="' + f(w) + '" lengthAdjust="spacingAndGlyphs" fill="' + fill + '" font-family="\'Noto Sans CJK JP\',\'Noto Sans\',\'Source Sans 3\',\'DejaVu Sans\',sans-serif">' + s.replace(/&/g, '&amp;').replace(/</g, '&lt;') + '</text>';
  }

  /** renderSVG(comp, geo) -> chaîne SVG. Retourne aussi les avertissements de mise en page (mention trop longue…). */
  function renderSVG(comp, geo, opts) {
    opts = opts || {}; const Wg = geo.largeur * 1000, Ht = geo.hauteur * 1000, pad = 20;
    let out = '', top = 0; const warn = [];
    for (const R of geo.registres) {
      const reg = R.registre, h = R.h * 1000, cap = R.cap * 1000, fond = reg.fond, fl = reg.fleche;
      const clair = CLAIR.includes(fond); const lis = Math.max(12, cap * 0.12);
      const txt = clair ? COL.noir : COL.blanc, colLis = clair ? COL.noir : COL.blanc;
      const cy = top + h / 2; top += h;     // centre du registre (svg)
      const cyM = -cy;                       // pour poly(): y math = -svg
      const marge = cap * 1.0;
      let x0, x1;
      const arrowshaped = fl === 'g' || fl === 'd';
      if (arrowshaped) {
        const p = Math.min(h * 0.5, Wg * 0.2), sens = fl === 'd' ? 0 : 180;
        let P = sens === 0 ? [[-Wg / 2, -h / 2], [Wg / 2 - p, -h / 2], [Wg / 2, 0], [Wg / 2 - p, h / 2], [-Wg / 2, h / 2]]
                          : [[Wg / 2, -h / 2], [-Wg / 2 + p, -h / 2], [-Wg / 2, 0], [-Wg / 2 + p, h / 2], [Wg / 2, h / 2]];
        if (sens === 180) P = P.slice().reverse();
        const I = offsetPoly(P, lis);
        out += poly(P, colLis, Wg / 2 + pad, cy) + poly(I, COL[fond], Wg / 2 + pad, cy);
        x0 = sens === 0 ? -Wg / 2 + marge : -Wg / 2 + p + marge; x1 = sens === 0 ? Wg / 2 - p - marge * 0.5 : Wg / 2 - marge;
      } else {
        out += '<rect x="' + f(pad) + '" y="' + f(cy - h / 2) + '" width="' + f(Wg) + '" height="' + f(h) + '" rx="10" fill="' + colLis + '"/>' +
               '<rect x="' + f(pad + lis) + '" y="' + f(cy - h / 2 + lis) + '" width="' + f(Wg - 2 * lis) + '" height="' + f(h - 2 * lis) + '" rx="5" fill="' + COL[fond] + '"/>';
        x0 = -Wg / 2 + marge; x1 = Wg / 2 - marge;
        if (fl && DEG[fl] !== undefined) { const al = Math.min(h * 0.8, 4 * cap); out += poly(arrowPts(al, DEG[fl]), txt, Wg / 2 - marge - al / 2 + Wg / 2 + pad, cy); x1 = Wg / 2 - marge - al * 1.1; }
      }
      const ms = reg.mentions, n = Math.max(1, ms.length), ht = R.h_txt * 1000;
      if (reg.voies) {
        const lh = R.lane_h * 1000, al = lh * 0.8;
        for (let k = 0; k < reg.voies; k++) { const deg = (reg.sortie && k === reg.voies - 1) ? -45 : -90; out += poly(arrowPts(al, deg), txt, Wg * (k + 0.5) / reg.voies + pad, cy + h / 2 - lh / 2); }
      }
      ms.forEach((m, i) => {
        const yc = (cy - h / 2) + ht * (i + 0.5) / n;
        let wt = textWidth(m.texte, cap), wd = m.dist ? textWidth(m.dist, cap) : 0;
        const dispo = (x1 - x0) - (m.dist ? 1.4 * cap : 0);
        let k = 1; if (wt + wd > dispo) { k = dispo / (wt + wd); warn.push('mention « ' + m.texte + ' » comprimée (' + Math.round(k * 100) + ' %)'); }
        out += text(m.texte, x0 + Wg / 2 + pad, yc, cap, 'start', wt * k, txt);
        if (m.dist) out += text(m.dist, x1 + Wg / 2 + pad, yc, cap, 'end', wd * k, txt);
      });
    }
    const svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + f(Wg + 2 * pad) + ' ' + f(Ht) + '" width="' + f((Wg + 2 * pad) / 4) + '" height="' + f(Ht / 4) + '">' + out + '</svg>';
    return { svg, warn };
  }

  // ------------------------------------------------------------------ signes simples : disque à valeur (B14) et panonceau textuel (M9)
  // Proportions = HYPOTHÈSES de dessin (bande rouge 10 % du diamètre, chiffres 40 % du diamètre) ; diamètres de gamme B : 450 / 650 / 850 / 1050 mm.
  const B_DIAM = { petite: 450, normale: 650, grande: 850, tres_grande: 1050 };
  const VALEURS_B14 = [5, 10, 15, 20, 30, 40, 45, 50, 60, 70, 80, 90, 100, 110, 130];
  /** renderDisqueValeur({valeur, gamme}) -> {svg, warn}. Disque B14 (fond blanc, bande rouge, valeur noire). */
  function renderDisqueValeur(o) {
    const warn = []; const v = String(o.valeur); const D = B_DIAM[o.gamme || 'normale'] || B_DIAM.normale;
    if (!/^\d+$/.test(v)) warn.push('valeur non numérique : ' + v);
    else if (!VALEURS_B14.includes(+v)) warn.push('valeur ' + v + ' km/h hors des valeurs usuelles (' + VALEURS_B14.join(', ') + ')');
    const R = D / 2, band = 0.1 * D, cap = 0.40 * D; let w = textWidth(v, cap), inner = 2 * (R - band) * 0.82;
    if (w > inner) { warn.push('valeur comprimée'); w = inner; }
    const svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + D + ' ' + D + '" width="' + f(D / 4) + '" height="' + f(D / 4) + '"><circle cx="' + R + '" cy="' + R + '" r="' + R + '" fill="' + COL.rouge + '"/><circle cx="' + R + '" cy="' + R + '" r="' + f(R - band) + '" fill="' + COL.blanc + '"/>' +
      text(v, R, R, cap, 'middle', w, COL.noir) + '</svg>';
    return { svg, warn };
  }
  /** renderPanonceauTexte({lignes, largeur_m, hauteur_m}) -> {svg, warn}. Panonceau M9 : fond blanc, filet noir, texte capitales noir. */
  function renderPanonceauTexte(o) {
    const warn = []; const L = (o.lignes || []).map(s => String(s).toUpperCase()); if (!L.length) warn.push('texte vide');
    if (L.length > 3) warn.push(L.length + ' lignes : lisibilité réduite au-delà de 3');
    const cap = 60, inter = cap * 0.6, marge = cap, fil = 10;
    const ws = L.map(s => textWidth(s, cap)), W = Math.max(...ws, cap) + 2 * marge, Ht = L.length * cap + (L.length - 1) * inter + 2 * marge;
    let out = '<rect x="0" y="0" width="' + f(W) + '" height="' + f(Ht) + '" rx="12" fill="' + COL.noir + '"/><rect x="' + fil + '" y="' + fil + '" width="' + f(W - 2 * fil) + '" height="' + f(Ht - 2 * fil) + '" rx="8" fill="' + COL.blanc + '"/>';
    L.forEach((s, i) => { out += text(s, W / 2, marge + cap / 2 + i * (cap + inter), cap, 'middle', ws[i], COL.noir); });
    return { svg: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + f(W) + ' ' + f(Ht) + '" width="' + f(W / 2) + '" height="' + f(Ht / 2) + '">' + out + '</svg>', warn };
  }

  const API = { renderDisqueValeur, renderPanonceauTexte, VALEURS_B14, composer, geometrie, renderSVG, corriger, valider, setFontMetrics, textWidth, fmtDistance, casse, hb, hc, COL, GAMMES };
  if (typeof module !== 'undefined' && module.exports) module.exports = API; else root.SignRender = API;
})(typeof self !== 'undefined' ? self : this);
