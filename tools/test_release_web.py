"""HNP-RELEASE-20260913 Web journey E2E.

Uses real keyboard input and read-only Unity diagnostics.  Run with a local build
directory, a live URL, or both; desktop Playwright is explicitly not phone proof.
"""
import argparse, functools, hashlib, http.server, json, re, sys, threading, time, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/.python'))
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser()
parser.add_argument('target',nargs='?',default='builds/web-release-preflight/web',help='build directory or http(s) URL')
parser.add_argument('--live',action='store_true',help='target is live URL; no local server')
parser.add_argument('--prayer-x',type=float,default=463.53,help='scene-authoritative prayer X; record override in report')
parser.add_argument('--prayer-object',default='Phra Pathom Chedi v004 Flow Hero',help='exact Unity GameObject exposing LogPrayerDiagnostics')
parser.add_argument('--return-button',default='206,368',help='RETURN button coordinate in 1280x720 Canvas reference space (default follows current Settings layout)')
args=parser.parse_args(); target=args.target
OUT=ROOT/'reports/qa'/time.strftime('release-20260913-web-%Y%m%d-%H%M%S'); OUT.mkdir(parents=True,exist_ok=True)
server=None
def sha_local(build):
 wasm=next((build/'Build').glob('*.wasm'),None)
 return hashlib.sha256(wasm.read_bytes()).hexdigest() if wasm else None
is_live=args.live or target.startswith(('http://','https://'))
if is_live:
 url=target.rstrip('/')+'/'
 build_id='live:'+url; wasm_sha256=None
else:
 build=(ROOT/target).resolve(); assert build.is_dir(),build
 class Quiet(http.server.SimpleHTTPRequestHandler):
  def log_message(self,*x): pass
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(build)))
 threading.Thread(target=server.serve_forever,daemon=True).start()
 url=f'http://127.0.0.1:{server.server_port}/'; build_id=str(build); wasm_sha256=sha_local(build)
data_sha256=None
if not is_live:
 data=build/'Build'/'web.data'
 if data.exists(): data_sha256=hashlib.sha256(data.read_bytes()).hexdigest()
report={'task':'HNP-RELEASE-20260913','status':'FAIL','target':url,'build':build_id,'wasm_sha256':wasm_sha256,'data_sha256':data_sha256,'prayer_x':args.prayer_x,'prayer_object':args.prayer_object,'return_button_reference':args.return_button,'physical_mobile':'NOT RUN','snapshots':{},'checks':[],'errors':[],'evidence':str(OUT)}
samples={k:[] for k in ('HNP006_QA','HNP007_QA','HNP008_QA','HNP_PRAYER_QA','HNP005_QA')}
try:
 with sync_playwright() as p:
  # Exercise the Windows desktop build through hardware ANGLE.  SwiftShader is useful
  # for compatibility smoke tests, but its CPU speed is not a production frame-rate signal.
  browser=p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True,args=['--enable-webgl','--use-angle=d3d11'])
  page=browser.new_page(viewport={'width':844,'height':390},device_scale_factor=1)
  def console(m):
   if m.type=='error': report['errors'].append(m.text)
   for key,arr in samples.items():
    if key+' {' in m.text:
     try: arr.append(json.loads(m.text.split(key+' ',1)[1]))
     except Exception as e: report['errors'].append('diagnostic parse '+str(e))
  page.on('console',console); page.on('pageerror',lambda e:report['errors'].append(str(e)))
  def snap(label,key='HNP006_QA',method='LogTimeDiagnostics'):
   arr=samples[key]; n=len(arr)
   target=args.prayer_object if key=='HNP_PRAYER_QA' else 'HNP World Game'
   page.evaluate('(x)=>window.hnpGame.SendMessage(x[0],x[1])',[target,method])
   for _ in range(50):
    page.wait_for_timeout(80)
    if len(arr)>n: break
   assert len(arr)>n,(label,key,method)
   report['snapshots'][label]=arr[-1]; return arr[-1]
  def shot(name): page.screenshot(path=str(OUT/(name+'.png')))
  def tap(key):
   page.keyboard.down(key); page.wait_for_timeout(180); page.keyboard.up(key); page.wait_for_timeout(120)
  def start():
   page.mouse.click(page.viewport_size['width']//2,int(page.viewport_size['height']*.68),delay=120); page.wait_for_timeout(450)
   return snap('started')
  def travel(target_x):
   """Real W/Shift travel along authored +X route; no game state setters."""
   s=snap('travel_start'); deadline=time.monotonic()+90; last_x=s['player']['x']; stalled=0
   while s['player']['x'] < target_x:
    if time.monotonic()>deadline: shot('travel-timeout'); raise AssertionError(('travel timeout',s['player'],target_x))
    page.keyboard.down('w'); tap('Shift')
    for _ in range(32):
     page.wait_for_timeout(200); s=snap('travel')
     if s['player']['x']>=target_x: break
     stalled=stalled+1 if s['player']['x']<=last_x+.04 else 0; last_x=s['player']['x']
     if stalled>=10: shot('travel-stalled'); raise AssertionError(('travel stalled',s['player'],target_x))
    page.keyboard.up('w')
    if s['player']['x']>=target_x: break
    # Wait out cooldown without forward input, then produce a fresh Shift press.
    for _ in range(65):
     page.wait_for_timeout(160); r=snap('cooldown','HNP007_QA','LogSprintDiagnostics')
     if r['interactable']: break
   return s
  page.goto(url,wait_until='domcontentloaded'); page.wait_for_function('!!window.hnpGame',timeout=180000); page.wait_for_timeout(3500)
  report['webgl']=page.evaluate("""()=>{const c=document.querySelector('canvas');const g=c&&(c.getContext('webgl2')||c.getContext('webgl'));if(!g)return null;const d=g.getExtension('WEBGL_debug_renderer_info');return {renderer:d?g.getParameter(d.UNMASKED_RENDERER_WEBGL):g.getParameter(g.RENDERER),vendor:d?g.getParameter(d.UNMASKED_VENDOR_WEBGL):g.getParameter(g.VENDOR)};}""")
  if is_live:
   try: report['release_json']=page.evaluate("async()=>{let r=await fetch('release.json');return r.ok?await r.json():null}")
   except Exception as e: report['release_json_error']=str(e)
  ready=start(); assert not ready['paused']; shot('landscape-start')
  # CanvasScaler match=0 means reference-space coordinates scale from 1280px width.
  scale=page.viewport_size['width']/1280
  menu_x,menu_y=62*scale,64*scale
  # Current Settings: parent centre (206,290 from top); TIME local +78 and RETURN local -78.
  time_x,time_y=206*scale,212*scale
  # Use the actual settings button and TIME control; diagnostics only observe the result.
  page.mouse.click(menu_x,menu_y,delay=120); page.wait_for_timeout(250)
  page.mouse.click(time_x,time_y,delay=120); page.wait_for_timeout(250)
  page.mouse.click(menu_x,menu_y,delay=120); page.wait_for_timeout(300)
  night=snap('night-time'); assert night['daylight']<.2,night
  night_lights=snap('night-lights','HNP008_QA','LogNightDiagnostics'); shot('night')
  report['checks'].append('PASS: actual settings TIME control reaches night; read-only night diagnostics captured')
  # Actual minimap and BACK controls; no direct ToggleMap call.
  page.mouse.click(1164*scale,82*scale,delay=120); page.wait_for_timeout(250); opened=snap('map-open'); assert opened['paused']; shot('map-open')
  page.mouse.click(page.viewport_size['width']/2,page.viewport_size['height']-58*scale,delay=120); page.wait_for_timeout(250); assert not snap('map-close')['paused']; report['checks'].append('PASS: minimap opens/BACK closes map and pauses simulation')
  # Portrait requires the release rotate overlay and paused clock; desktop viewport is not a phone claim.
  page.set_viewport_size({'width':390,'height':844}); page.wait_for_timeout(800); portrait=snap('portrait-paused'); page.wait_for_timeout(900); portrait_later=snap('portrait-still-paused'); shot('portrait-rotate')
  assert portrait['paused'],portrait
  assert portrait_later['paused'] and portrait_later['activeSeconds']==portrait['activeSeconds'] and portrait_later['player']==portrait['player'],(portrait,portrait_later)
  assert page.locator('#rotate').count()>0,'missing rotate overlay'; assert page.locator('#rotate').is_visible(),'rotate overlay hidden'
  page.set_viewport_size({'width':844,'height':390}); page.wait_for_timeout(800); assert not snap('landscape-resumed')['paused']; shot('landscape-restored')
  report['checks'].append('PASS: portrait overlay is visible and game pauses; landscape resumes')
  # Keep the required night evidence above, then restore day through the same visible UI
  # so the route/prayer composition has an independently inspectable daylight frame.
  page.mouse.click(menu_x,menu_y,delay=120); page.wait_for_timeout(200)
  page.mouse.click(time_x,time_y,delay=120); page.wait_for_timeout(200)
  page.mouse.click(menu_x,menu_y,delay=120); page.wait_for_timeout(250)
  assert snap('day-restored')['daylight']>.5
  shot('day-restored')
  # Pointer drag is desktop touch emulation only; it supplements, never replaces, a physical-device result.
  move_x,move_y=102*scale,page.viewport_size['height']-106*scale
  before_touch=snap('touch-before'); page.mouse.move(move_x,move_y); page.mouse.down()
  for i in range(1,9):
   page.mouse.move(move_x,move_y-(68*scale*i/8)); page.wait_for_timeout(55)
  page.wait_for_timeout(650); page.mouse.up(); page.wait_for_timeout(300); after_touch=snap('touch-after')
  assert after_touch['player']['x']>before_touch['player']['x']+.4,(before_touch,after_touch)
  report['checks'].append('PASS: pointer/touch-emulated move pad advances player; physical mobile NOT RUN')
  # Direct authored +X road: cross bridge (>=130), then reach prayer vicinity. Target may be revised by scene owner; diagnostics prove actual path.
  bridge=travel(145); assert bridge['player']['x']>=145; shot('bridge-crossed')
  near=travel(args.prayer_x-4); assert near['player']['x']>=args.prayer_x-4; shot('prayer-approach')
  prayer=snap('prayer-near','HNP_PRAYER_QA','LogPrayerDiagnostics'); assert prayer['nearby'],prayer
  tap('e'); active=snap('prayer-active','HNP_PRAYER_QA','LogPrayerDiagnostics'); assert active['status']=='Active' and active['movementBlocked'],active
  # Map during prayer freezes prayer progress and movement; resume then complete once.
  page.mouse.click(1164*scale,82*scale,delay=120); page.wait_for_timeout(250); paused=snap('prayer-map-paused','HNP_PRAYER_QA','LogPrayerDiagnostics'); page.wait_for_timeout(900); paused2=snap('prayer-map-still','HNP_PRAYER_QA','LogPrayerDiagnostics')
  assert paused['paused'] and paused2['paused'] and paused['progress']==paused2['progress'],(paused,paused2)
  page.mouse.click(page.viewport_size['width']/2,page.viewport_size['height']-58*scale,delay=120); page.wait_for_timeout(3300); done=snap('prayer-complete','HNP_PRAYER_QA','LogPrayerDiagnostics')
  assert done['completedCount']==1 and not done['movementBlocked'],done; shot('prayer-complete')
  page.keyboard.down('s'); page.wait_for_timeout(1500); page.keyboard.up('s'); returned=snap('return-road')
  assert returned['player']['x'] < near['player']['x']-2,(near,returned)
  report['checks'].append('PASS: W/Shift route crosses bridge, E prayer freezes on map, completes once, movement returns and S travels back')
  # RETURN is deliberately exercised through the visible Settings menu, never via SendMessage.
  rx,ry=(float(v) for v in args.return_button.split(',',1))
  page.mouse.click(menu_x,menu_y,delay=120); page.wait_for_timeout(250)
  page.mouse.click(rx*scale,ry*scale,delay=120); page.wait_for_timeout(350); station=snap('return-button')
  assert abs(station['player']['x'])<1.0,station['player']; report['checks'].append('PASS: visible Settings RETURN button resets player')
  assert not report['errors'],report['errors']; report['browser']=browser.version; report['status']='PASS'; browser.close()
except Exception as e:
 report['status']='FAIL'; report['failure']=str(e)
finally:
 if server: server.shutdown()
 (OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print(OUT); print(report['status'],report.get('failure',''))
 if report['status']!='PASS': sys.exit(1)
