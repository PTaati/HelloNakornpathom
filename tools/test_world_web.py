"""Real desktop Chromium smoke test; viewport emulation is not physical mobile QA."""
import functools, http.server, json, sys, threading, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/world'/time.strftime('web-test-%Y%m%d-%H%M%S')
OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'tools/.python'))
from playwright.sync_api import sync_playwright

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(ROOT/'builds/web')))
threading.Thread(target=server.serve_forever,daemon=True).start()
report={'evidence':str(OUT),'physical_mobile':'NOT RUN','errors':[],'console_errors':[],'logs':[],'checks':[]}
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True,
                                 args=['--enable-webgl','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        page=browser.new_page(viewport={'width':1280,'height':720},device_scale_factor=1)
        page.on('pageerror',lambda e:report['errors'].append(str(e)))
        page.on('console',lambda m:report['console_errors'].append(m.text) if m.type=='error' else None)
        page.on('console',lambda m:report['logs'].append(m.text))
        started=time.monotonic()
        page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
        page.wait_for_function('!!window.hnpGame',timeout=180000)
        report['load_seconds']=round(time.monotonic()-started,2)
        report['checks'].append('Unity WebAssembly instance started')
        page.wait_for_timeout(3500)
        page.screenshot(path=str(OUT/'web-welcome.png'))
        page.mouse.click(640,462,delay=120)
        page.wait_for_timeout(1000)
        page.keyboard.down('w'); page.wait_for_timeout(2200)
        page.screenshot(path=str(OUT/'web-walking.png'))
        page.keyboard.up('w'); page.wait_for_timeout(600)
        page.screenshot(path=str(OUT/'web-idle.png'))
        page.keyboard.press('Space'); page.wait_for_timeout(500)
        page.screenshot(path=str(OUT/'web-desktop.png'))
        report['checks'].append('Start, WASD and jump inputs delivered; screenshot for visual verification')
        page.keyboard.press('m'); page.wait_for_timeout(500)
        page.screenshot(path=str(OUT/'web-map.png'))
        page.keyboard.press('m')
        page.mouse.click(1156,240,delay=120); page.wait_for_timeout(700)
        page.screenshot(path=str(OUT/'web-night.png'))
        page.mouse.click(1156,240,delay=120); page.wait_for_timeout(300)
        page.mouse.click(1238,240,delay=120); page.wait_for_timeout(300)
        page.screenshot(path=str(OUT/'web-muted.png'))
        page.mouse.click(1238,240,delay=120); page.wait_for_timeout(300)
        report['checks'].append('TIME and SOUND inputs delivered; night and mute screenshots for visual verification')
        page.set_viewport_size({'width':844,'height':390})
        page.wait_for_timeout(800)
        page.screenshot(path=str(OUT/'web-landscape.png'))
        assert not page.locator('#rotate').is_visible()
        page.mouse.move(67,324); page.mouse.down(); page.mouse.move(67,286)
        page.wait_for_timeout(1400); page.mouse.up()
        page.mouse.move(550,180); page.mouse.down(); page.mouse.move(660,180,steps=12); page.mouse.up()
        page.wait_for_timeout(700)
        page.screenshot(path=str(OUT/'web-pad-look.png'))
        report['checks'].append('On-screen movement pad and camera drag delivered with mouse; physical multitouch NOT RUN')
        page.set_viewport_size({'width':390,'height':844})
        page.wait_for_timeout(500)
        assert not page.locator('#rotate').is_visible()
        page.screenshot(path=str(OUT/'web-portrait.png'))
        page.set_viewport_size({'width':844,'height':390})
        page.wait_for_timeout(500)
        assert not page.locator('#rotate').is_visible()
        report['checks'].append('Portrait playable canvas and landscape restoration PASS')
        assert not report['errors'],report['errors']
        report['browser']=browser.version
        report['status']='AUTOMATED PASS; visual inspection required'
        browser.close()
except Exception as e:
    report['status']='FAIL';report['failure']=str(e)
    raise
finally:
    server.shutdown()
    (OUT/'web-smoke.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))
