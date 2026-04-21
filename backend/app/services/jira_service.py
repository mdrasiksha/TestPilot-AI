import base64
import json
from urllib import request
from urllib.error import HTTPError, URLError

from app.core.config import get_settings


class JiraService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _auth_header(self) -> str:
        token = f"{self.settings.jira_email}:{self.settings.jira_api_token}".encode("utf-8")
        return f"Basic {base64.b64encode(token).decode('utf-8')}"

    def create_issue(
        self, project_key: str, summary: str, description: str, issue_type: str = "Task"
    ) -> dict[str, str]:
        if not self.settings.jira_base_url:
            raise ValueError("Missing JIRA_BASE_URL in environment.")
        if not self.settings.jira_email:
            raise ValueError("Missing JIRA_EMAIL in environment.")
        if not self.settings.jira_api_token:
            raise ValueError("Missing JIRA_API_TOKEN in environment.")

        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": issue_type},
            }
        }

        jira_url = self.settings.jira_base_url.rstrip("/")
        req = request.Request(
            url=f"{jira_url}/rest/api/3/issue",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": self._auth_header(),
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=30) as response:
                body = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8")
            raise RuntimeError(f"Jira API error ({exc.code}): {detail}") from exc
        except URLError as exc:
            raise RuntimeError("Could not connect to Jira API.") from exc

        key = body.get("key")
        if not key:
            raise RuntimeError("Jira API did not return an issue key.")

        return {"key": key, "url": f"{jira_url}/browse/{key}"}


jira_service = JiraService()
