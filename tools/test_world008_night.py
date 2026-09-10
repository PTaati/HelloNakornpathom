"""Night lighting and real route collision checks; desktop Web, not physical mobile."""
import functools,http.server,json,sys,threading,time,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/.python'))
from playwright.sync_api import sync_playwright
BUILD=ROOT/(sys.argv[1] if len(sys.argv)>1 else 'builds/world008-r4/web');OUT=ROOT/'reports/world'/time.strftime('world008-night-%Y%m%d-%H%M%S');OUT.mkdir(parents=True)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(BUILD)));threading.Thread(target=server.serve_forever,daemon=True).start()
report={'status':'FAIL','physical_mobile':'NOT RUN','snapshots':{},'errors':[],'build':str(BUILD),'wasm_sha256':hashlib.sha256((BUILD/'Build/web.wasm').read_bytes()).hexdigest()};samples=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True,args=['--enable-webgl','--use-angle=swiftshader','--enable-unsafe-swiftshader']);page=browser.new_page(viewport={'width':1280,'height':720})
  def log(m):
   if m.type=='error':report['errors'].append(m.text)
   if 'HNP008_QA {' in m.text:samples.append(json.loads(m.text.split('HNP008_QA ',1)[1]))
  page.on('console',log);page.on('pageerror',lambda e:report['errors'].append(str(e)))
  def snap(name):
   n=len(samples);page.evaluate("window.hnpGame.SendMessage('HNP World Game','LogNightDiagnostics')")
   for _ in range(40):
    page.wait_for_timeout(100)
    if len(samples)>n:break
   assert len(samples)>n;report['snapshots'][name]=samples[-1];return samples[-1]
  def click(x,y):page.mouse.click(x,y,delay=160);page.wait_for_timeout(300)
  def capture(name):page.screenshot(path=str(OUT/(name+'.png')))
  page.goto(f'http://127.0.0.1:{server.server_port}/');page.wait_for_function('!!window.hnpGame',timeout=180000);page.wait_for_timeout(3500);click(640,494)
  day=snap('day');assert day['night']==0 and day['lit']==0 and day['collider'];capture('day')
  page.keyboard.down('w');page.wait_for_timeout(1600);click(1096,638);page.wait_for_timeout(1100);page.keyboard.up('w');page.wait_for_timeout(400);capture('approach-day')
  click(62,64);click(206,198)
  for _ in range(15):
   page.wait_for_timeout(150);night=snap('night_menu')
   if night['lit']>0:break
  assert night['night']>.99 and night['emission']>1.5;assert night['street']==10 and night['headlights']==36 and night['cabin']==18 and night['outlinedCars']==18;assert 3<=night['lit']<=15
  capture('night-menu');click(62,64);page.wait_for_timeout(700);capture('night-approach');a=snap('night')
  page.wait_for_timeout(2400);capture('night-traffic');b=snap('night_later');assert b['lit']>0
  page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(600);capture('night-portrait');page.set_viewport_size({'width':1280,'height':720});page.wait_for_timeout(500)
  # Actual approach: hold forward, sprint, and jump into the monument boundary.
  page.keyboard.down('w');page.keyboard.press('Space')
  for _ in range(25):
   page.keyboard.press('Shift');page.wait_for_timeout(500);probe=snap('approach_probe')
   if probe['player']['x']>24:break
  page.wait_for_timeout(2500);blocked=snap('blocked');capture('collision-boundary');assert blocked['player']['x']<30 and blocked['player']['x']>15,blocked['player']
  page.keyboard.press('Space');page.wait_for_timeout(1600);blocked2=snap('blocked_after_jump');page.keyboard.up('w');assert blocked2['player']['x']<30,blocked2['player']
  page.keyboard.down('s');page.wait_for_timeout(1000);page.keyboard.up('s');retreat=snap('retreat');assert retreat['player']['x']<blocked2['player']['x']-3,'Cannot retreat from boundary'
  click(62,64);click(206,198)
  for _ in range(15):
   page.wait_for_timeout(150);restored=snap('restored_day')
   if restored['lit']==0:break
  assert restored['night']==0 and restored['lit']==0;click(62,64)
  assert not report['errors'],report['errors'];report['browser']=browser.version;report['status']='PASS';browser.close()
finally:
 server.shutdown();(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(OUT);print(report['status'])
