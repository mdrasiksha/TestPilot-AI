import json
from typing import Any


class ExportService:
    def to_json(self, payload: Any) -> str:
        return json.dumps(payload, ensure_ascii=False, indent=2)


export_service = ExportService()
