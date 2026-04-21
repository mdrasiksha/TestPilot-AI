from app.utils.parser import normalize_prompt


class AIService:
    def generate(self, prompt: str) -> str:
        clean_prompt = normalize_prompt(prompt)

        return f"""You are a Senior QA Architect specializing in risk-based testing and production-grade test design.

Task:
Generate comprehensive test cases for the provided feature or requirement context.

Source Context:
\"\"\"
{clean_prompt}
\"\"\"

Output Rules (mandatory):
1. Return ONLY valid JSON (no markdown, no comments, no prose outside JSON).
2. Follow the JSON schema exactly.
3. If any required detail is missing from the source context, do not invent facts.
4. Add assumptions only in the `assumptions` field and keep them minimal.
5. Use clear, executable, step-by-step test instructions.
6. Include realistic QA scenarios across happy path, negative, edge, integration, security, and usability where applicable.
7. Ensure each test case has a business and technical rationale via `coverage_tags`.

Priority Classification:
- P0: Critical business flow or security/compliance risk; release blocker.
- P1: Core functionality with high user impact; should be fixed before release.
- P2: Important but non-blocking behavior; medium impact.
- P3: Minor impact, cosmetic, or low-frequency scenario.

JSON Schema:
{{
  "feature": "string",
  "assumptions": ["string"],
  "coverage_summary": {{
    "in_scope": ["string"],
    "out_of_scope": ["string"],
    "risk_areas": ["string"]
  }},
  "test_cases": [
    {{
      "id": "TC-001",
      "title": "string",
      "priority": "P0|P1|P2|P3",
      "type": "functional|negative|edge|integration|security|usability|performance",
      "preconditions": ["string"],
      "test_data": ["string"],
      "steps": [
        {{
          "step_number": 1,
          "action": "string",
          "expected_result": "string"
        }}
      ],
      "postconditions": ["string"],
      "coverage_tags": ["string"],
      "automation_candidate": true,
      "notes": "string"
    }}
  ]
}}

Quality Gate Before Finalizing:
- JSON parses successfully.
- Every test case includes at least 3 steps.
- Every step has both `action` and `expected_result`.
- Priorities are distributed by risk (not all identical unless justified in notes).
- No placeholder terms like "TBD", "etc", "as needed", or "some data".
"""


ai_service = AIService()
