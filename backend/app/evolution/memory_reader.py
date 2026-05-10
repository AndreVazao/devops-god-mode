from app.services.andreos_memory_reader_service import andreos_memory_reader_service

def read_memory():
    """Reads the project memory using the existing AndreOS memory reader service."""
    return andreos_memory_reader_service.read_memory()
