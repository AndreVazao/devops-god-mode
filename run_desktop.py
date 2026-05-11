import subprocess
import webbrowser
import time
import sys

print("🚀 Starting God Mode...")

# iniciar backend
backend = subprocess.Popen([sys.executable, "-m", "backend.main"])

# esperar backend subir
time.sleep(3)

# abrir UI
webbrowser.open("http://127.0.0.1:8000/app/home")

print("✅ UI opened")
