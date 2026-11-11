/* Authored controls for unchanged publication movies. File time is not biology time. */
(() => {
  'use strict';
  const videos = [...document.querySelectorAll('video[data-observed-controls]')];
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const pauseAll = () => videos.forEach(video => video.pause());
  videos.forEach((video, index) => {
    const name = video.dataset.observedName || 'Observed movie';
    const player = video.closest('.player') || video.parentElement;
    const group = document.createElement('div');
    group.className = 'observed-video-controls';
    group.setAttribute('role', 'group');
    group.setAttribute('aria-label', name + ' playback');
    const button = (label, action) => {
      const element = document.createElement('button');
      element.type = 'button';
      element.textContent = label;
      element.addEventListener('click', action);
      group.append(element);
      return element;
    };
    const duration = () => Number.isFinite(video.duration) && video.duration > 0 ? video.duration : 0;
    const seek = seconds => {
      video.pause();
      if (duration()) video.currentTime = Math.max(0, Math.min(duration(), seconds));
      update();
    };
    const play = () => video.play().catch(() => { video.pause(); update(); });
    const toggle = button('Play', () => video.paused || video.ended ? play() : video.pause());
    toggle.setAttribute('aria-label', 'Play ' + name);
    const replay = button('Replay', () => {
      seek(0);
      if (!motion.matches) play();
    });
    replay.setAttribute('aria-label', 'Replay ' + name);
    const previous = button('Previous 0.5 s', () => seek(video.currentTime - 0.5));
    previous.setAttribute('aria-label', name + ': previous 0.5 publisher seconds');
    const next = button('Next 0.5 s', () => seek(video.currentTime + 0.5));
    next.setAttribute('aria-label', name + ': next 0.5 publisher seconds');
    const label = document.createElement('label');
    const slider = document.createElement('input');
    slider.type = 'range'; slider.min = '0'; slider.max = '0'; slider.step = '1'; slider.value = '0';
    slider.id = 'observed-seek-' + index;
    slider.setAttribute('aria-label', name + ': seek in milliseconds');
    label.htmlFor = slider.id;
    label.textContent = 'Seek in milliseconds';
    label.append(slider);
    group.append(label);
    const output = document.createElement('output');
    output.setAttribute('aria-label', name + ' publisher file time');
    group.append(output);
    const help = document.createElement('p');
    help.className = 'observed-video-help';
    help.id = 'observed-video-help-' + index;
    help.textContent = 'Steps inspect 0.5 seconds in the publication file and pause playback. The source clock and nearby timing key explain experiment time; file steps are not acquisition intervals.';
    slider.setAttribute('aria-describedby', help.id);
    group.append(help);
    function update() {
      const end = duration(), current = Math.max(0, Math.min(end || 0, video.currentTime || 0));
      slider.max = String(Math.ceil(end * 1000));
      slider.value = String(Math.min(Number(slider.max), Math.round(current * 1000)));
      slider.disabled = !end; previous.disabled = !end; next.disabled = !end; replay.disabled = !end;
      output.value = current.toFixed(2) + ' / ' + (end ? end.toFixed(2) : '—') + ' publisher s';
      slider.setAttribute('aria-valuetext', current.toFixed(2) + ' of ' + (end ? end.toFixed(2) : 'unknown') + ' publisher seconds');
      const playing = !video.paused && !video.ended;
      toggle.textContent = playing ? 'Pause' : 'Play';
      toggle.setAttribute('aria-label', (playing ? 'Pause ' : 'Play ') + name);
    }
    slider.addEventListener('input', () => seek(Number(slider.value) / 1000));
    ['loadedmetadata', 'durationchange', 'timeupdate', 'seeked', 'play', 'pause', 'ended', 'error'].forEach(event => video.addEventListener(event, update));
    video.addEventListener('play', () => videos.forEach(other => { if (other !== video) other.pause(); }));
    video.autoplay = false; video.loop = false; video.pause();
    player.insertAdjacentElement('afterend', group);
    // Keep native controls as no-JS fallback; replace only once this group exists.
    video.controls = false;
    video.dataset.observedInitialized = 'true';
    document.querySelectorAll('[data-observed-legacy]').forEach(element => { element.hidden = true; });
    player.addEventListener('keydown', event => {
      if (event.target !== player || event.altKey || event.ctrlKey || event.metaKey) return;
      let left = player.scrollLeft, top = player.scrollTop;
      const maxX = Math.max(0, player.scrollWidth - player.clientWidth);
      const maxY = Math.max(0, player.scrollHeight - player.clientHeight);
      switch (event.key) {
        case 'ArrowLeft': left -= 60; break;
        case 'ArrowRight': left += 60; break;
        case 'ArrowUp': top -= 60; break;
        case 'ArrowDown': top += 60; break;
        case 'Home': left = 0; top = 0; break;
        case 'End': left = maxX; top = maxY; break;
        default: return;
      }
      event.preventDefault();
      player.scrollTo({left: Math.max(0, Math.min(maxX, left)), top: Math.max(0, Math.min(maxY, top)), behavior: 'instant'});
    });
    update();
  });
  document.querySelectorAll('[data-native]').forEach(button => button.addEventListener('click', () => {
    const video = document.getElementById(button.dataset.native + '-video');
    video?.closest('.player')?.focus();
  }));
  motion.addEventListener('change', pauseAll);
  document.addEventListener('visibilitychange', () => { if (document.hidden) pauseAll(); });
  window.addEventListener('beforeprint', pauseAll);
})();
