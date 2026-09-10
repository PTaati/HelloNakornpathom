"""Camera acceptance through actual browser pointer drags, not setter injection."""
import functools,http.server,json,sys,threading,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/.python'))
from playwright.sync_api import sync_playwright
OUT=ROOT/'reports/world'/time.strftime('world006-camera-%Y%m%d-%H%M%S');OUT.mkdir(parents=True)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'builds/world006/web')))
threading.Thread(target=server.serve_forever,daemon=True).start()
report={'status':'FAIL','physical_mobile':'NOT RUN','snapshots':{},'errors':[]};samples=[];motions=[];times=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True,args=['--enable-webgl','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  page=browser.new_page(viewport={'width':1280,'height':720})
  def log(m):
   if m.type=='error':report['errors'].append(m.text)
   if 'HNP004_QA {' in m.text:samples.append(json.loads(m.text.split('HNP004_QA ',1)[1]))
  def motionlog(m):
   if 'HNP006_QA {' in m.text:times.append(json.loads(m.text.split('HNP006_QA ',1)[1]))
   if 'HNP005_QA {' in m.text:motions.append(json.loads(m.text.split('HNP005_QA ',1)[1]))
  page.on('console',motionlog)
  page.on('console',log);page.on('pageerror',lambda e:report['errors'].append(str(e)))
  def snap(name):
   n=len(samples);page.evaluate("window.hnpGame.SendMessage('HNP World Game','LogCameraDiagnostics')")
   for _ in range(40):
    page.wait_for_timeout(100)
    if len(samples)>n:break
   assert len(samples)>n,'No camera diagnostics';report['snapshots'][name]=samples[-1];return samples[-1]
  def capture(name):page.screenshot(path=str(OUT/(name+'.png')))
  def drag(x,a,b):
   page.mouse.move(x,a);page.mouse.down();page.wait_for_timeout(120)
   for i in range(1,13):page.mouse.move(x,a+(b-a)*i/12);page.wait_for_timeout(50)
   page.mouse.up();page.wait_for_timeout(300)
  page.goto(f'http://127.0.0.1:{server.server_port}/');page.wait_for_function('!!window.hnpGame',timeout=180000);page.wait_for_timeout(3500)
  page.mouse.click(640,494,delay=160);page.wait_for_timeout(800)
  def motion(name):
   n=len(motions);page.evaluate("window.hnpGame.SendMessage('HNP World Game','LogMotionDiagnostics')")
   for _ in range(40):
    page.wait_for_timeout(100)
    if len(motions)>n:break
   assert len(motions)>n;report['snapshots'][name]=motions[-1];return motions[-1]
  initial=motion('still_initial');assert not initial['tip']
  page.keyboard.down('w');page.wait_for_timeout(1500);walk=motion('walk');assert 'Walk' in walk['clip'],walk['clip']
  page.mouse.click(1096,638,delay=160)
  for _ in range(12):
   page.wait_for_timeout(200);fast=motion('fast_walk')
   if fast['stateSpeed']>=5:break
  assert fast['clip']==walk['clip'] and abs(fast['stateSpeed']-5)<.001,fast['stateSpeed']
  page.keyboard.up('w')
  for _ in range(12):
   page.wait_for_timeout(250);idle=motion('stopped')
   if 'Still005' in idle['clip']:break
  assert 'Still005' in idle['clip'],idle['clip']
  page.wait_for_timeout(1500);idle2=motion('stopped_later')
  assert max(abs(a-b) for a,b in zip(idle['pose'],idle2['pose']))<.000001,'Skeleton moves while idle'
  capture('still');page.mouse.click(1096,638,delay=160)
  def clock(name):
   n=len(times);page.evaluate("window.hnpGame.SendMessage('HNP World Game','LogTimeDiagnostics')")
   for _ in range(40):
    page.wait_for_timeout(100)
    if len(times)>n:break
   assert len(times)>n;report['snapshots'][name]=times[-1];return times[-1]
  a=clock('clock_start');assert a['runSpeed']==27
  def movement_rate(name):
   page.keyboard.down('w');page.wait_for_timeout(250);p0=clock(name+'_start');page.wait_for_timeout(700);p1=clock(name+'_end');page.keyboard.up('w');page.wait_for_timeout(300)
   return sum((p1['player'][k]-p0['player'][k])**2 for k in ('x','z'))**.5/(p1['activeSeconds']-p0['activeSeconds'])
  walking=movement_rate('walk_rate');page.mouse.click(1096,638,delay=160);page.wait_for_timeout(300);running=movement_rate('run_rate');page.mouse.click(1096,638,delay=160)
  report['measured_speeds']={'walk':walking,'run':running};assert 4.3<walking<6.5 and 21.6<running<32.4,(walking,running)
  # Pause must not count wall time, and manual changes remain available.
  page.mouse.click(62,64,delay=160);page.wait_for_timeout(400);paused=clock('paused')
  page.wait_for_timeout(2200);paused2=clock('paused_later');assert paused['minutes']==paused2['minutes']
  capture('clock-menu');page.mouse.click(62,64,delay=160);page.wait_for_timeout(500)
  a=clock('cycle_start');seen_day=a['daylight']>.9;seen_night=a['daylight']<.1
  for i in range(13):
   page.wait_for_timeout(6000);b=clock('cycle_'+str(i))
   minutes=(b['minutes']-a['minutes'])%1440;elapsed=b['activeSeconds']-a['activeSeconds']
   assert abs(minutes/elapsed-10)<.03,(minutes,elapsed)
   assert sum((b['sunDirection'][k]-b['lightDirection'][k])**2 for k in ('x','y','z'))<.000001
   assert sum((b['sunDirection'][k]-b['skyDirection'][k])**2 for k in ('x','y','z'))<.000001
   seen_day|=b['daylight']>.9;seen_night|=b['daylight']<.1
   if i in (0,6,12):capture('cycle-'+str(i))
  assert seen_day and seen_night,'No automatic day/night transition'
  assert abs(a['sunDirection']['y']-b['sunDirection']['y'])>.2
  assert not report['errors'],report['errors'];report['status']='PASS';report['browser']=browser.version;browser.close()
finally:
 server.shutdown();(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(OUT);print(report['status'])
