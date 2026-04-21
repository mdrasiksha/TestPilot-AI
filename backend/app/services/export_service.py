import io
import json
from typing import Any

import pandas as pd
from fastapi import HTTPException, status


class ExportService:
    def _normalize_input(self, test_cases: Any) -> list[dict[str, Any]]:
        if isinstance(test_cases, str):
            try:
                parsed_payload = json.loads(test_cases)
            except json.JSONDecodeError as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid JSON payload for test cases.",
                ) from exc
        else:
            parsed_payload = test_cases

        if isinstance(parsed_payload, dict):
            return [parsed_payload]

        if isinstance(parsed_payload, list):
            return [item if isinstance(item, dict) else {"value": item} for item in parsed_payload]

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test cases must be a JSON object or array.",
        )

    def to_csv_bytes(self, test_cases: Any) -> bytes:
        normalized_payload = self._normalize_input(test_cases)

        dataframe = pd.json_normalize(normalized_payload)
        buffer = io.StringIO()
        dataframe.to_csv(buffer, index=False)
        return buffer.getvalue().encode("utf-8")


export_service = ExportService()
