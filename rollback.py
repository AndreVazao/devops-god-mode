import subprocess

def run():
    print("↩️ Rolling back to previous commit")

    subprocess.run(["git", "reset", "--hard", "HEAD~1"])
    subprocess.run(["git", "push", "--force"])
