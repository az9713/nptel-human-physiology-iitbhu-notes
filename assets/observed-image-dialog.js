/* Layout adapter for source-image dialogs. Existing gallery handlers own images, pan and focus. */
(() => {
  'use strict';
  const dialog = document.getElementById('enlargement');
  if (!dialog) return;
  const fit = document.getElementById('fit');
  const native = document.getElementById('native');
  const close = document.getElementById('close');
  const viewport = dialog.querySelector('.viewport');
  if (!fit || !native || !close) return;
  const setFit = (value) => dialog.classList.toggle('observed-fit', value);
  document.querySelectorAll('[data-enlarge]').forEach((button) => {
    button.addEventListener('click', () => setFit(false));
  });
  native.addEventListener('click', () => {
    setFit(false);
    // Return keyboard navigation to the restored native-size scroll region.
    if (viewport) viewport.focus();
  });
  fit.addEventListener('click', () => setFit(true));
  close.addEventListener('click', () => setFit(false));
  dialog.addEventListener('close', () => setFit(false));
  if (viewport) viewport.addEventListener('keydown', (event) => {
    if (event.target !== viewport || event.altKey || event.ctrlKey || event.metaKey) return;
    if (dialog.classList.contains('observed-fit')) return;
    let left = viewport.scrollLeft, top = viewport.scrollTop;
    const maxX = Math.max(0, viewport.scrollWidth - viewport.clientWidth);
    const maxY = Math.max(0, viewport.scrollHeight - viewport.clientHeight);
    switch (event.key) {
      case 'ArrowLeft': left -= 60; break;
      case 'ArrowRight': left += 60; break;
      case 'ArrowUp': top -= 60; break;
      case 'ArrowDown': top += 60; break;
      case 'Home': left = 0; top = 0; break;
      case 'End': left = maxX; top = maxY; break;
      case 'PageUp': top -= viewport.clientHeight * .9; break;
      case 'PageDown': top += viewport.clientHeight * .9; break;
      default: return;
    }
    event.preventDefault();
    viewport.scrollTo({left:Math.max(0,Math.min(maxX,left)),
      top:Math.max(0,Math.min(maxY,top)),behavior:'instant'});
  });
})();
