"""HNP003 real Unity Web player functional smoke; desktop viewports, not phones."""
import functools,http.server,json,sys,threading,time,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/.python'))
BUILD=ROOT/(sys.argv[1] if len(sys.argv)>1 else 'builds/world003-r3/web')
from playwright.sync_api import sync_playwright
OUT=ROOT/'reports/world'/time.strftime('world003-web-%Y%m%d-%H%M%S');OUT.mkdir(parents=True,exist_ok=True)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(BUILD)))
threading.Thread(target=server.serve_forever,daemon=True).start()
report={'physical_mobile':'NOT RUN','errors':[],'console_errors':[],'snapshots':{},'checks':[],'evidence':str(OUT),'build':str(BUILD),'wasm_sha256':hashlib.sha256((BUILD/'Build/web.wasm').read_bytes()).hexdigest()}
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True,args=['--enable-webgl','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  page=browser.new_page(viewport={'width':1280,'height':720},device_scale_factor=1);snapshots=[];logs=[]
  def console(m):
   logs.append(m.text)
   if m.type=='error':report['console_errors'].append(m.text)
   if 'HNP003_QA {' in m.text:
    try:snapshots.append(json.loads(m.text[m.text.index('HNP003_QA ')+10:].strip()))
    except Exception:pass
  page.on('console',console);page.on('pageerror',lambda e:report['errors'].append(str(e)))
  def capture(name):page.screenshot(path=str(OUT/(name+'.png')))
  def click(x,y):page.mouse.click(x,y,delay=160);page.wait_for_timeout(350)
  def snap(name):
   n=len(snapshots);page.evaluate("window.hnpGame.SendMessage('HNP World Game','LogDiagnostics')")
   for i in range(30):
    page.wait_for_timeout(100)
    if len(snapshots)>n:break
   assert len(snapshots)>n,'Missing Unity diagnostic response'
   report['snapshots'][name]=snapshots[-1];return snapshots[-1]
  page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded');page.wait_for_function('!!window.hnpGame',timeout=180000);page.wait_for_timeout(3500)
  assert page.locator('#fullscreen').count()==0;assert page.locator('#rotate').count()==0
  capture('welcome');click(640,494);page.wait_for_timeout(500);a=snap('start');capture('day')
  assert a['vehicles']==18 and a['birds']==12,(a['vehicles'],a['birds'])
  page.wait_for_timeout(4200);b=snap('actors_moving')
  dist=lambda x,y:sum((x[k]-y[k])**2 for k in ('x','y','z'))**.5
  assert all(dist(x,y)>.3 for x,y in zip(a['positions'],b['positions'])),'A car is stationary'
  assert all(dist(x,y)>.3 for x,y in zip(a['birdPositions'],b['birdPositions'])),'A bird is stationary'
  assert any(abs(x-y)>3 for x,y in zip(a['wingAngles'],b['wingAngles'])),'Wings not flapping'
  def road(v):
   x,z=v['x'],v['z'];return (-61<x<-12 and abs(z)<5) or (-18<x<110 and abs(abs(z)-58)<3.5) or (abs(x+13)<3.5 and abs(z)<63) or (abs(x-105)<3.5 and abs(z)<63)
  assert all(road(v) for v in a['positions']+b['positions']),'Traffic left mapped roads'
  report['checks'].append('PASS: 18 moving vehicles on mapped roads, 12 moving birds and changing wing poses')
  page.keyboard.down('w');page.wait_for_timeout(1600);walk=snap('walk');capture('walk');assert walk['animation']=='Walk',walk['animation']
  click(1096,638);page.wait_for_timeout(1200);run=snap('run');capture('run');assert run['animation']=='Run' and run['running'],run['animation']
  page.keyboard.up('w')
  # Wait for rendered Unity state, not wall-clock frames on software WebGL.
  for _ in range(12):
   page.wait_for_timeout(250);idle=snap('idle')
   if idle['animation']=='Idle':break
  capture('idle');assert idle['animation']=='Idle',idle['animation']
  page.wait_for_timeout(1000);idle2=snap('idle_stable');assert dist(idle['player'],idle2['player'])<.03,'Idle root drifts'
  click(1096,638);assert not snap('run_disabled')['running']
  report['checks'].append('PASS: walk, icon-toggle Run, stop Idle without root drift, run off')
  click(1164,82);assert snap('map_open')['paused'];capture('expanded-map');click(640,662);assert not snap('map_closed')['paused']
  click(62,64);assert snap('menu_open')['menu'];capture('settings');click(206,198);assert snap('night')['daylight']<.2;capture('night')
  click(206,294);assert snap('muted')['muted'];capture('muted');click(206,294);click(206,198);click(62,64)
  report['checks'].append('PASS: minimap opens/closes map; hidden settings toggle time and mute')
  page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(1100);capture('portrait');assert not snap('portrait')['paused']
  # Menu icon and expanded map in portrait, using the same responsive canvas scale.
  click(34,35);capture('portrait-settings');assert snap('portrait_menu')['menu'];click(34,35)
  click(332,44);capture('portrait-map');assert snap('portrait_map')['paused'];click(195,813)
  page.set_viewport_size({'width':844,'height':390});page.wait_for_timeout(1000);capture('landscape');assert not snap('restored')['paused']
  report['checks'].append('PASS: portrait gameplay/menu/map and landscape restoration')
  for i in range(8):
   page.wait_for_timeout(4000);traffic=snap('traffic_loop_'+str(i));assert all(road(v) for v in traffic['positions']),'Traffic left road during loop'
  report['checks'].append('PASS: additional 32-second moving traffic loop road-bound regression')
  assert not report['errors'],report['errors'];assert not report['console_errors'],report['console_errors']
  report['browser']=browser.version;report['status']='PASS';report['logs']=logs;browser.close()
except Exception as e:
 report['status']='FAIL';report['failure']=str(e);raise
finally:
 server.shutdown();(OUT/'report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8');print(str(OUT));print(report.get('status'),report.get('failure',''))
