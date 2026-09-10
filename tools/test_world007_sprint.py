"""Real browser input acceptance for sprint/cooldown; no gameplay setter calls."""
import functools,http.server,json,sys,threading,time,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/.python'))
from playwright.sync_api import sync_playwright
OUT=ROOT/'reports/world'/time.strftime('world007-sprint-%Y%m%d-%H%M%S');OUT.mkdir(parents=True)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'builds/world007/web')))
threading.Thread(target=server.serve_forever,daemon=True).start()
report={'status':'FAIL','physical_mobile':'NOT RUN','snapshots':{},'errors':[],'wasm_sha256':hashlib.sha256((ROOT/'builds/world007/web/Build/web.wasm').read_bytes()).hexdigest()};samples=[];motions=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True,args=['--enable-webgl','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  page=browser.new_page(viewport={'width':1280,'height':720})
  def log(m):
   if m.type=='error':report['errors'].append(m.text)
   if 'HNP007_QA {' in m.text:samples.append(json.loads(m.text.split('HNP007_QA ',1)[1]))
   if 'HNP005_QA {' in m.text:motions.append(json.loads(m.text.split('HNP005_QA ',1)[1]))
  page.on('console',log);page.on('pageerror',lambda e:report['errors'].append(str(e)))
  def snap(name,motion=False):
   values=motions if motion else samples;n=len(values);method='LogMotionDiagnostics' if motion else 'LogSprintDiagnostics'
   page.evaluate('(m)=>window.hnpGame.SendMessage("HNP World Game",m)',method)
   for _ in range(40):
    page.wait_for_timeout(70)
    if len(values)>n:break
   assert len(values)>n;report['snapshots'][name]=values[-1];return values[-1]
  def until(name,predicate):
   for _ in range(100):
    s=snap(name)
    if predicate(s):return s
    page.wait_for_timeout(100)
   raise AssertionError('Timeout: '+name)
  def click(x=1096,y=638):page.mouse.click(x,y,delay=100);page.wait_for_timeout(150)
  def capture(name):page.screenshot(path=str(OUT/(name+'.png')))
  page.goto(f'http://127.0.0.1:{server.server_port}/');page.wait_for_function('!!window.hnpGame',timeout=180000);page.wait_for_timeout(3500);click(640,494)
  ready=snap('ready');assert ready['interactable'] and not ready['ring']
  click();start=snap('active');assert start['running'] and not start['interactable'];assert 4.5<start['sprintEnds']-start['activeSeconds']<=5
  click();click();spam=snap('spam');assert spam['sprintEnds']==start['sprintEnds']
  until('near_end',lambda s:s['activeSeconds']>=s['sprintEnds']-3)
  page.keyboard.down('w')
  for _ in range(12):
   page.wait_for_timeout(100);fast=snap('fast_motion',True)
   if fast['stateSpeed']==5:break
  assert fast['stateSpeed']==5,fast['stateSpeed']
  cooldown=until('cooldown_start',lambda s:s['ring']);assert not cooldown['running'] and not cooldown['interactable'];assert abs(cooldown['cooldownEnds']-cooldown['sprintEnds']-5)<.000001
  for _ in range(12):
   page.wait_for_timeout(100);walk=snap('automatic_walk',True)
   if walk['stateSpeed']==1:break
  assert walk['stateSpeed']==1 and walk['clip']==fast['clip'];page.keyboard.up('w')
  click();page.keyboard.down('Shift');blocked=snap('blocked');assert not blocked['running'] and blocked['cooldownEnds']==cooldown['cooldownEnds']
  # Pause during cooldown, preserve remaining time and ring progress.
  click(62,64);paused=snap('paused');page.wait_for_timeout(1300);paused2=snap('paused_later');assert paused['activeSeconds']==paused2['activeSeconds'];assert paused['progress']==paused2['progress'];click(62,64)
  middle=until('ring_middle',lambda s:s['progress']>=.45);capture('cooldown-ring');assert middle['ring'] and .4<middle['progress']<1
  recovered=until('recovered',lambda s:s['interactable']);assert not recovered['running'] and not recovered['ring'];assert recovered['activeSeconds']>=cooldown['cooldownEnds'];assert recovered['activeSeconds']-cooldown['cooldownEnds']<.5
  page.wait_for_timeout(500);assert not snap('held_shift_no_restart')['running'];page.keyboard.up('Shift')
  # Fresh key press works, then renders ring correctly in portrait.
  page.keyboard.down('Shift');again=until('second_sprint',lambda s:s['running']);page.keyboard.up('Shift');assert again['sprintEnds']>start['sprintEnds']
  page.set_viewport_size({'width':390,'height':844});until('portrait_cooldown',lambda s:s['ring']);page.wait_for_timeout(1700);portrait=snap('portrait_ring');capture('portrait-ring');assert portrait['ring'] and not portrait['interactable']
  until('portrait_ready',lambda s:s['interactable']);click(287,789);assert until('portrait_tap_sprint',lambda s:s['running'])['running']
  assert not report['errors'],report['errors'];report['browser']=browser.version;report['status']='PASS';browser.close()
finally:
 server.shutdown();(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(OUT);print(report['status'])
