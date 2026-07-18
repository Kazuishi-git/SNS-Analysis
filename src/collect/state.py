# JSONファイルに保存されたcollectorの状態を管理

from pathlib import Path
import json

from src.utils.config import DATA_DIR

class StateManager:
    # Load and Save collector state
    
    def __init__(self) -> None:
        self.state_file = DATA_DIR / "state.json"
    
    def load(self) -> dict | None:
        # Load the saved state.  Returns None if the state file does not exist.
        
        if not self.state_file.exists():
            return None
        
        with self.state_file.open("r", encoding="utf-8") as f:
            return json.load(f)
       
    
    def save(self, state: dict) -> None:
        # Save the current state.
        
        with self.state_file.open("w", encoding="utf-8") as f:
            json.dump(
                state,
                f,
                ensure_ascii=False,
                indent=4,
            )
    
    def delete(self):
        # Delete the saved state.
        
        if self.state_file.exists():
            self.state_file.unlink()