/* Native-size access and playback rate; source anatomy and time are unchanged. */
(() => {
  'use strict';
  document.querySelectorAll('button[data-size]').forEach(button => {
    button.addEventListener('click', () => {
      const target = document.getElementById(button.dataset.target);
      const viewport = target.closest('.source-view,.player');
      const native = button.dataset.size === 'native';
      viewport.classList.toggle('native-mode', native);
      document.querySelectorAll('button[data-size]').forEach(other => {
        if (other.dataset.target === button.dataset.target) {
          other.setAttribute('aria-pressed', String((other.dataset.size === 'native') === native));
        }
      });
      viewport.scrollTo({left: 0, top: 0, behavior: 'instant'});
      viewport.focus();
    });
  });
  document.querySelectorAll('select[data-rate]').forEach(select => {
    select.addEventListener('change', () => {
      document.getElementById(select.dataset.rate).playbackRate = Number(select.value);
    });
  });
  document.querySelectorAll('video[data-observed-name="Prepared brain surface rotation"]').forEach(video => {
    const group = video.closest('.player')?.nextElementSibling;
    const help = group?.classList.contains('observed-video-controls')
      ? group.querySelector('.observed-video-help') : null;
    if (help) help.textContent = 'Steps inspect 0.5 seconds of the publication camera movie and pause playback. File time describes the camera presentation; it has no physiological-time or acquisition-interval interpretation.';
  });
  document.querySelectorAll('[data-static-pan]').forEach(viewport => {
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
  });
})();
