"""Inspect real browser layout and deterministic animation controls; not science acceptance."""
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    out = ROOT/'work'/'browser'
    out.mkdir(parents=True, exist_ok=True)
    report = {'scope': 'reader scaffold and secretory-traffic interaction pilot only',
              'science_acceptance': False, 'layouts': [], 'animation': {}}
    with sync_playwright() as runtime:
        browser = runtime.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(reduced_motion='reduce')
        page = context.new_page()
        errors = []
        requests = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: requests.append(request.url) if request.url.startswith(('http:', 'https:')) else None)
        for name in ['index.html', 'source-map.html', 'references.html', 'code-lab.html',
                     'assets/secretory-traffic-pilot.html']:
            for width in [1440, 650, 390]:
                page.set_viewport_size({'width': width, 'height': 1000})
                page.goto((ROOT/name).as_uri(), wait_until='load')
                page.wait_for_timeout(100)
                dimensions = page.evaluate('({width:innerWidth, scroll:document.documentElement.scrollWidth})')
                assert dimensions['scroll'] <= dimensions['width'] + 1, (name, width, dimensions)
                screenshot = f"{Path(name).stem}-{width}.png"
                page.screenshot(path=str(out/screenshot), full_page=True)
                report['layouts'].append({'file': name, 'width': width,
                                          'horizontal_overflow': False, 'screenshot': screenshot})
        page.goto((ROOT/'assets'/'secretory-traffic-pilot.html').as_uri())
        assert page.evaluate('window.getVisualState().playing') is False
        states = [page.evaluate('(t)=>window.renderFrame(t)', t) for t in [0, 3, 6, 9, 12]]
        assert len({round(state['x'], 4) for state in states}) == 5
        assert [s['phase'] for s in states] == [1, 2, 3, 4, 5]
        for seconds in [0, 3, 6, 9, 12]:
            page.evaluate('(t)=>window.renderFrame(t)', seconds)
            page.screenshot(path=str(out/f'traffic-t{seconds:02d}.png'), full_page=True)
        page.locator('#progress').evaluate("el=>{el.value='600';el.dispatchEvent(new Event('input',{bubbles:true}));}")
        assert page.evaluate('window.getVisualState().time') == 6
        page.locator('#speed').select_option('2')
        assert page.evaluate('window.getVisualState().rate') == 2
        page.locator('#play').click()
        page.wait_for_timeout(250)
        assert page.evaluate('window.getVisualState().time') > 6
        page.locator('#play').click()
        assert page.evaluate('window.getVisualState().playing') is False
        page.locator('#restart').click()
        assert page.evaluate('window.getVisualState().time') == 0
        report['animation'] = {'sampled_states': states, 'reduced_motion_initially_paused': True,
                               'scrubbing': 'pass', 'speed_control': 'pass', 'play_pause': 'pass', 'restart': 'pass'}
        report['page_errors'] = errors
        report['initial_remote_requests'] = requests
        assert not errors, errors
        assert not requests, requests
        browser.close()
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(f"PASS: {len(report['layouts'])} layouts; five distinct temporal states; controls; offline load; no page errors")


if __name__ == '__main__':
    main()
