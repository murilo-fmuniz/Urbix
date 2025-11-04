import json
from pathlib import Path
from typing import List, Dict, Any, Optional

class Database:
    def __init__(self):
        self.db_path = Path(__file__).parent / "data" / "db.json"
        
    def read_db(self) -> Dict[str, Any]:
        with open(self.db_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    def write_db(self, data: Dict[str, Any]) -> None:
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    def get_all_indicators(self) -> List[Dict[str, Any]]:
        db = self.read_db()
        return db["indicators"]
        
    def get_indicator_by_id(self, indicator_id: int) -> Optional[Dict[str, Any]]:
        indicators = self.get_all_indicators()
        return next((ind for ind in indicators if ind["id"] == indicator_id), None)
        
    def add_indicator(self, indicator: Dict[str, Any]) -> Dict[str, Any]:
        db = self.read_db()
        # Auto-increment ID
        max_id = max([ind["id"] for ind in db["indicators"]], default=0)
        indicator["id"] = max_id + 1
        db["indicators"].append(indicator)
        self.write_db(db)
        return indicator

db = Database()