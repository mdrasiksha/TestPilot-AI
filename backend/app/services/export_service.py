import json


class ExportService:
    def to_json(self, content: str) -> str:
        return json.dumps({"content": content}, ensure_ascii=False)


export_service = ExportService()
