import os

def _ensure_data_directory():
    """Tworzy folder data/, jeśli nie istnieje."""
    os.makedirs("data", exist_ok=True)