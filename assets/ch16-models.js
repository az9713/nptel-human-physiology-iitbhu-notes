/* Original synthetic bookkeeping, not a nephron or patient solver. */
(function (root) {
  'use strict';
  const api = {
    flow(rbf, hct, gfr) {
      if (![rbf, hct, gfr].every(Number.isFinite) || rbf <= 0 || hct < 0 || hct >= 1 || gfr < 0 || gfr > rbf * (1 - hct)) throw Error('Incompatible flow inputs');
      const rpf = rbf * (1 - hct);
      return {rbf, rpf, cells: rbf * hct, gfr, ff: gfr / rpf, efferentPlasma: rpf - gfr, efferentBlood: rbf - gfr};
    },
    pressure(pgc, pbs, oncoticBlood, oncoticCapsule, kf) {
      if (![pgc,pbs,oncoticBlood,oncoticCapsule,kf].every(Number.isFinite) || kf < 0) throw Error('Invalid pressure inputs');
      const nfp = pgc - pbs - oncoticBlood + oncoticCapsule;
      return {nfp, signedFlux: kf * nfp};
    },
    resistance(ra, re, pa = 100, pv = 10) {
      if (![ra,re,pa,pv].every(Number.isFinite) || ra <= 0 || re <= 0 || pa <= pv) throw Error('Finite positive resistances and inlet pressure above outlet required');
      const q = (pa - pv) / (ra + re);
      return {q, pgc: pv + q * re};
    },
    state(mode, phase) {
      const f = Math.max(0, Math.min(1, phase));
      if (mode === 'filtration') return {phase:f, pbs:15 + 5*f, ...api.pressure(55,15+5*f,30,0,12.5)};
      if (mode === 'resistance') return {phase:f, afferent:api.resistance(1+f,1), efferent:api.resistance(1,1+f)};
      return {phase:f, step:Math.min(3,Math.floor(f*4))};
    }
  };
  if (typeof module !== 'undefined') module.exports = api;
  else root.Ch16 = api;
})(typeof window === 'undefined' ? globalThis : window);
