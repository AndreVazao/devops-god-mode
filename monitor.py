import requests
import time
import os

URL = os.getenv("APP_HEALTH_URL")

def check():
    try:
        r = requests.get(URL, timeout=5)
        return r.status_code == 200
    except:
        return False

def run():
    print("📡 Monitor started")

    fails = 0

    while True:
        ok = check()

        if ok:
            fails = 0
            print("✅ healthy")
        else:
            fails += 1
            print("❌ fail", fails)

        if fails >= 3:
            print("🚨 triggering rollback")
            import rollback
            rollback.run()
            fails = 0 # Reset after triggering rollback to avoid infinite loop of rollbacks if it takes time to recover

        time.sleep(10)

if __name__ == "__main__":
    run()
