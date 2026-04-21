import json
from urllib import error, request

from app.core.config import get_settings


class JiraService:
    def fetch_jira_story(self, issue_id: str) -> str:
        settings = get_settings()
        url = f"{settings.jira_base_url.rstrip('/')}/rest/api/3/issue/{issue_id}"
        req = request.Request(
            url,
            headers={
                "Authorization": f"Bearer {settings.jira_api_token}",
                "Accept": "application/json",
            },
        )

        try:
            with request.urlopen(req, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise ValueError(f"Jira request failed ({exc.code}): {detail}") from exc
        except error.URLError as exc:
            raise ValueError(f"Unable to connect to Jira: {exc.reason}") from exc

        fields = payload.get("fields", {})
        summary = fields.get("summary", "").strip()
        description = self._extract_description(fields.get("description"))

        return f"Summary: {summary}\n\nDescription: {description}".strip()

    def _extract_description(self, description: object) -> str:
        if isinstance(description, str):
            return description.strip()

        if isinstance(description, dict):
            chunks: list[str] = []
            self._collect_text(description, chunks)
            return "\n".join(filter(None, chunks)).strip()

        return ""

    def _collect_text(self, node: object, chunks: list[str]) -> None:
        if isinstance(node, dict):
            text = node.get("text")
            if isinstance(text, str) and text.strip():
                chunks.append(text.strip())

            content = node.get("content")
            if isinstance(content, list):
                for item in content:
                    self._collect_text(item, chunks)

        elif isinstance(node, list):
            for item in node:
                self._collect_text(item, chunks)


jira_service = JiraService()
