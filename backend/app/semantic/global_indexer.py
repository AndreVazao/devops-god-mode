import os
from app.semantic.semantic_brain import load_index, save_index, add_many_to_index
from app.config import settings

REPOS_PATH = settings.REPOS_PATH

def index_all():
    if not os.path.exists(REPOS_PATH):
        print(f"Warning: REPOS_PATH {REPOS_PATH} does not exist.")
        return

    index = load_index()
    items_to_add = []

    for root, dirs, files in os.walk(REPOS_PATH):
        for file in files:
            if file.endswith((".py", ".js", ".ts", ".md")):
                path = os.path.join(root, file)

                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()

                    if content.strip():
                        items_to_add.append((path, content))

                except Exception as e:
                    print(f"Error reading {path}: {e}")
                    continue

    if items_to_add:
        print(f"Indexing {len(items_to_add)} files...")
        add_many_to_index(index, items_to_add)
        save_index(index)
        print("Indexing complete.")

if __name__ == "__main__":
    index_all()
