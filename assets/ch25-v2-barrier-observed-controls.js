/* Full source plate only: no crop, overlay or image modification. */
(() => {
  'use strict';
  const viewport = document.getElementById('plate-viewport');
  const native = document.getElementById('native');
  const fit = document.getElementById('fit');
  const setNative = value => {
    viewport.classList.toggle('native', value);
    native.setAttribute('aria-pressed', String(value));
    fit.setAttribute('aria-pressed', String(!value));
    viewport.scrollTo({left: 0, top: 0, behavior: 'instant'});
    viewport.focus();
  };
  native.addEventListener('click', () => setNative(true));
  fit.addEventListener('click', () => setNative(false));
  viewport.addEventListener('keydown', event => {
    if (event.target !== viewport || event.altKey || event.ctrlKey || event.metaKey) return;
    let left = viewport.scrollLeft, top = viewport.scrollTop;
    switch (event.key) {
      case 'ArrowLeft': left -= 60; break;
      case 'ArrowRight': left += 60; break;
      case 'ArrowUp': top -= 60; break;
      case 'ArrowDown': top += 60; break;
      case 'Home': left = 0; top = 0; break;
      case 'End': left = viewport.scrollWidth; top = viewport.scrollHeight; break;
      case 'PageUp': top -= viewport.clientHeight * .9; break;
      case 'PageDown': top += viewport.clientHeight * .9; break;
      default: return;
    }
    event.preventDefault();
    viewport.scrollTo({left: Math.max(0, Math.min(viewport.scrollWidth - viewport.clientWidth, left)),
      top: Math.max(0, Math.min(viewport.scrollHeight - viewport.clientHeight, top)), behavior: 'instant'});
  });
})();
