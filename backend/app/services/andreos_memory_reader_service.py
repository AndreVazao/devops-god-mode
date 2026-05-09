import os
from typing import Dict

BASE_PATH = "memory/vault/AndreOS/02_PROJETOS/GOD_MODE"

FILES = [
    "MEMORIA_MESTRE.md",
    "DECISOES.md",
    "ARQUITETURA.md",
    "BACKLOG.md",
    "HISTORICO.md",
    "ULTIMA_SESSAO.md"
]

class AndreOSMemoryReaderService:
    def read_memory(self) -> Dict[str, str]:
        data = {}

        for f in FILES:
            path = os.path.join(BASE_PATH, f)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as file:
                    data[f] = file.read()
            else:
                data[f] = ""

        return data

andreos_memory_reader_service = AndreOSMemoryReaderService()
