"""Actual Web input + read-only shrine diagnostics; desktop is not physical mobile."""
import functools, hashlib, http.server, json, sys, threading, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/.python'))
from playwright.sync_api import sync_playwright
BUILD=ROOT/(sys.argv[1] if len(sys.argv)>1 else 'builds/world010-r1/web')
OUT=ROOT/'reports/world'/time.strftime('world010-shrine-%Y%m%d-%H%M%S');OUT.mkdir(parents=True)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(BUILD)))
threading.Thread(target=server.serve_forever,daemon=True).start()
report=dict(status='FAIL',physical_mobile='NOT RUN',build=str(BUILD),wasm_sha256=hashlib.sha256((BUILD/'Build/web.wasm').read_bytes()).hexdigest(),snapshots={},errors=[])
samples={k:[] for k in ('HNP006_QA','HNP008_QA','HNP010_QA')}
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
   assert len(values)>n,(key,method)
   report['snapshots'][label]=values[-1];return values[-1]
  def click(x,y):page.mouse.click(x,y,delay=140);page.wait_for_timeout(300)
  def capture(name):page.screenshot(path=str(OUT/(name+'.png')))
  def drag(dx,dy):
   page.mouse.move(900,500);page.mouse.down();page.wait_for_timeout(100)
   for i in range(1,13):page.mouse.move(900+dx*i/12,500+dy*i/12);page.wait_for_timeout(45)
   page.mouse.up();page.wait_for_timeout(400)
  page.goto(f'http://127.0.0.1:{server.server_port}/')
  page.wait_for_function('!!window.hnpGame',timeout=180000);page.wait_for_timeout(3000);click(640,494)
  # Sprint only the long central road; finish the approach at walking speed.
  page.keyboard.down('w');page.keyboard.press('Shift')
  for _ in range(40):
   page.wait_for_timeout(250);pos=snap('road_approach')
   if pos['player']['x']>=-20:break
  page.keyboard.up('w');page.wait_for_timeout(5500)
  page.keyboard.down('w')
  for _ in range(45):
   page.wait_for_timeout(150);pos=snap('shrine_approach')
   if pos['player']['x']>=19:break
  page.keyboard.up('w');page.wait_for_timeout(400)
  assert 19<=pos['player']['x']<30,pos['player']
  # Offset from central statue/photo axis so the avatar does not cover the image.
  page.keyboard.down('d');page.wait_for_timeout(650);page.keyboard.up('d')
  drag(-65,-140);capture('shrine-day')
  day=snap('photo_day','HNP010_QA','LogShrineDiagnostics')
  assert day['enabled'] and day['unlit'] and day['texture']!='MISSING',day
  assert abs(day['aspect']-387/792)<.002,day
  click(62,64);clock=snap('menu')
  if clock['daylight']>.5:click(206,198)
  click(62,64);page.wait_for_timeout(700);capture('shrine-night')
  night=snap('photo_night','HNP010_QA','LogShrineDiagnostics')
  assert night['enabled'] and night['unlit'] and night['texture']==day['texture'],night
  lights=snap('night_lights','HNP008_QA','LogNightDiagnostics')
  assert lights['night']>.99 and lights['monumentProfile']=='light-profile'
  page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(700);capture('shrine-portrait')
  snap('photo_portrait','HNP010_QA','LogShrineDiagnostics')
  assert not report['errors'],report['errors']
  report['browser']=browser.version;report['status']='PASS';browser.close()
finally:
 server.shutdown();(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(OUT);print(report['status'])
