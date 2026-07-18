from pathlib import Path

from src.utils.config import DATA_DIR

class StateManager:
    
    def __init__(self) -> None:
        self.state_file = DATA_DIR / "state.json"
    
    def load(self):
        pass
    
    def save(self):
        pass
    
    def delete(self):
        pass