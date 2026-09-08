"""Small stdio MCP client for the installed Unity relay; no guessed tool names."""
import argparse, json, queue, subprocess, threading, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--method', default='tools/list')
    parser.add_argument('--params', default='{}')
    parser.add_argument('--params-file')
    parser.add_argument('--code-file', help='Execute a C# command through discovered Unity_RunCommand')
    parser.add_argument('--output')
    parser.add_argument('--timeout', type=int, default=45)
    args = parser.parse_args()
    relay = Path.home() / '.unity/relay/relay_win.exe'
    proc = subprocess.Popen([str(relay), '--mcp', '--project-path', str(ROOT / 'hnp-game')],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW)
    messages = queue.Queue()
    def reader():
        for line in proc.stdout:
            try: messages.put(json.loads(line))
            except ValueError: pass
    threading.Thread(target=reader, daemon=True).start()
    def drain_errors():
        for _ in proc.stderr: pass
    threading.Thread(target=drain_errors, daemon=True).start()
    def send(msg):
        proc.stdin.write(json.dumps(msg) + '\n'); proc.stdin.flush()
    def request(ident, method, params):
        send(dict(jsonrpc='2.0', id=ident, method=method, params=params))
        deadline = time.monotonic() + args.timeout
        while time.monotonic() < deadline:
            try: msg = messages.get(timeout=min(1, max(.01, deadline-time.monotonic())))
            except queue.Empty: continue
            if msg.get('id') == ident: return msg
        raise TimeoutError(f'{method}: no response within {args.timeout}s; check Unity Pending Connections')
    try:
        init = request(1, 'initialize', dict(protocolVersion='2024-11-05', capabilities={},
                       clientInfo=dict(name='HNP Prototype Client', version='1.0.0')))
        if 'error' in init: raise RuntimeError(init['error'])
        send(dict(jsonrpc='2.0', method='notifications/initialized'))
        params = json.loads(Path(args.params_file).read_text(encoding='utf-8-sig') if args.params_file else args.params)
        if args.code_file:
            args.method = 'tools/call'
            params = dict(name='Unity_RunCommand', arguments=dict(Code=Path(args.code_file).read_text(encoding='utf-8-sig'), Title=Path(args.code_file).stem))
        result = request(2, args.method, params)
        formatted = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            target = ROOT / args.output
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(formatted, encoding='utf-8')
        print(formatted.encode('ascii', 'backslashreplace').decode() if not args.output else f'Saved {args.output}')
        body = result.get('result', {})
        failed = 'error' in result or body.get('isError', False)
        structured = body.get('structuredContent', {})
        failed |= structured.get('success') is False
        for item in body.get('content', []):
            if item.get('type') == 'text':
                try:
                    content = json.loads(item['text'])
                    failed |= isinstance(content, dict) and content.get('success') is False
                except (ValueError, KeyError): pass
        if failed:
            raise RuntimeError('MCP returned an error; inspect the saved response. The action did not pass.')
    finally:
        proc.terminate()
        proc.wait(timeout=5)

if __name__ == '__main__': main()
