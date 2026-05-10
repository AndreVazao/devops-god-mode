import time
import requests
import os

RELAY_URL = os.getenv("RELAY_URL")
TOKEN = os.getenv("RELAY_TOKEN")

def pull_tasks():
    headers = {}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    r = requests.get(f"{RELAY_URL}/pull-tasks", headers=headers)
    return r.json().get("tasks", [])


def push_result(result):
    headers = {}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    requests.post(f"{RELAY_URL}/push-result", json=result, headers=headers)


def execute(task):
    print("Executar:", task)

    if task.get("action") == "ping":
        return {"status": "pong"}

    if task.get("action") == "run_code":
        try:
            # Note: exec() is dangerous, used here as requested for the prototype
            exec(task["code"])
            return {"status": "done"}
        except Exception as e:
            return {"error": str(e)}

    if task.get("action") == "chat":
        return {"type": "chat_response", "message": f"PC recebeu: {task.get('message')}"}

    return {"status": "unknown"}


def loop():
    print(f"Worker ligado ao relay: {RELAY_URL}")

    while True:
        try:
            tasks = pull_tasks()

            for t in tasks:
                result = execute(t)
                push_result(result)

        except Exception as e:
            print("Erro:", e)

        time.sleep(2)


if __name__ == "__main__":
    if not RELAY_URL:
        print("Erro: RELAY_URL não configurada.")
    else:
        loop()
