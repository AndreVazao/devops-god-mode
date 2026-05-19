import sys
from fastapi.testclient import TestClient
sys.path.insert(0, r'c:/ProgramasGodMode/devops-god-mode/backend')
import main
client = TestClient(main.app)
paths = ['/health', '/app/home', '/api/system/config', '/api/home-control-surface/package', '/api/home-visual-shell/package']
for path in paths:
    r = client.get(path)
    print(path, r.status_code, r.headers.get('content-type', '')[:50])
    if r.status_code != 200:
        print('BODY:', r.text[:400])
