import os

def chunk_code(file_path, max_lines=40):
    chunks = []

    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return []

    for i in range(0, len(lines), max_lines):
        chunk = "".join(lines[i:i+max_lines])

        chunks.append({
            "file": file_path,
            "start_line": i,
            "content": chunk
        })

    return chunks
