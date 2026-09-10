"""Reference revision Web regression, using real input and read-only diagnostics."""
import functools, hashlib, http.server, json, sys, threading, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/.python'))
from playwright.sync_api import sync_playwright
BUILD = ROOT/(sys.argv[1] if len(sys.argv)>1 else 'builds/world009-r2/web')
OUT = ROOT/'reports/world'/time.strftime('world009-reference-%Y%m%d-%H%M%S')
OUT.mkdir(parents=True)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
server = http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(BUILD)))
threading.Thread(target=server.serve_forever,daemon=True).start()
report = dict(status='FAIL',physical_mobile='NOT RUN',build=str(BUILD),wasm_sha256=hashlib.sha256((BUILD/'Build/web.wasm').read_bytes()).hexdigest(),snapshots={},errors=[])
samples={k:[] for k in ('HNP004_QA','HNP005_QA','HNP006_QA','HNP008_QA')}
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True,args=['--enable-webgl','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  page=browser.new_page(viewport={'width':1280,'height':720})
  def log(m):
   if m.type=='error':report['errors'].append(m.text)
   for key,values in samples.items():
    if key+' {' in m.text:values.append(json.loads(m.text.split(key+' ',1)[1]))
  page.on('console',log);page.on('pageerror',lambda e:report['errors'].append(str(e)))
  def snap(label,key='HNP006_QA',method='LogTimeDiagnostics'):
   values=samples[key];n=len(values)
   page.evaluate('(m)=>window.hnpGame.SendMessage("HNP World Game",m)',method)
   for _ in range(40):
    page.wait_for_timeout(80)
    if len(values)>n:break
   assert len(values)>n
   report['snapshots'][label]=values[-1];return values[-1]
  def click(x,y):page.mouse.click(x,y,delay=140);page.wait_for_timeout(250)
  def capture(name):page.screenshot(path=str(OUT/(name+'.png')))
  def drag(x,y,dy):
   page.mouse.move(x,y);page.mouse.down();page.wait_for_timeout(100)
   for i in range(1,13):page.mouse.move(x,y+dy*i/12);page.wait_for_timeout(45)
   page.mouse.up();page.wait_for_timeout(400)
  page.goto(f'http://127.0.0.1:{server.server_port}/')
  page.wait_for_function('!!window.hnpGame',timeout=180000);page.wait_for_timeout(3000);click(640,494)
  capture('station')
  a=snap('clock_start');page.wait_for_timeout(1700);b=snap('clock_end')
  rate=((b['minutes']-a['minutes'])%1440)/(b['activeSeconds']-a['activeSeconds']);report['minutes_per_second']=rate
  assert abs(rate-10)<.03
  assert sum((b['sunDirection'][k]-b['lightDirection'][k])**2 for k in ('x','y','z'))<.000001
  assert sum((b['sunDirection'][k]-b['skyDirection'][k])**2 for k in ('x','y','z'))<.000001
  page.keyboard.down('w')
  for _ in range(35):
   page.keyboard.press('Shift');page.wait_for_timeout(350);pos=snap('approach')
   if pos['player']['x']>=-15:break
  page.keyboard.up('w');assert -15<=pos['player']['x']<8,pos['player']
  page.wait_for_timeout(500)
  idle=snap('idle','HNP005_QA','LogMotionDiagnostics');page.wait_for_timeout(900)
  later=snap('idle_later','HNP005_QA','LogMotionDiagnostics')
  assert 'Still005' in idle['clip'] and not idle['tip']
  assert max(abs(x-y) for x,y in zip(idle['pose'],later['pose']))<.000001
  # Approach framing is achieved by a pointer drag, not a camera or player setter.
  drag(970,535,-330);capture('front-day')
  click(1164,82);capture('expanded-map');click(640,662)
  click(62,64);paused=snap('menu_paused');page.wait_for_timeout(800);paused2=snap('menu_paused_later')
  assert paused['minutes']==paused2['minutes']
  if paused2['daylight']>.5:click(206,198)
  click(62,64);page.wait_for_timeout(600);capture('front-night')
  night=snap('night','HNP008_QA','LogNightDiagnostics');assert night['night']>.99 and 3<=night['lit']<=15
  if 'world009' in str(BUILD):assert night['monumentProfile']=='light-profile' and night['templeRenderers']>0,night
  page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(600);capture('portrait-night')
  click(332,44);capture('portrait-map');click(195,813)
  page.set_viewport_size({'width':1280,'height':720});page.wait_for_timeout(600)
  # Look straight overhead using several pointer drags; existing 90-degree range must survive.
  for _ in range(3):drag(970,500,-290)
  sky=snap('sky','HNP004_QA','LogCameraDiagnostics');capture('sky')
  assert sky['pitch']<=-89.9 and sky['forward']['y']>.999
  assert not report['errors'],report['errors']
  report['browser']=browser.version;report['status']='PASS';browser.close()
finally:
 server.shutdown();(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(OUT);print(report['status'])
