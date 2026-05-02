from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta


@dataclass
class UserRecord:
    user_id: str
    email: str
    is_paid: bool = False
    plan: str = "free"
    plan_expiry: datetime | None = None


users: dict[str, UserRecord] = {}
usage_store: dict[str, dict[str, int | str]] = {}


def upsert_user(user_id: str, email: str) -> UserRecord:
    normalized_id = user_id.strip()
    normalized_email = email.strip().lower()

    existing = users.get(normalized_id)
    if existing:
        existing.email = normalized_email or existing.email
        return existing

    record = UserRecord(user_id=normalized_id, email=normalized_email, plan="free")
    users[normalized_id] = record
    return record


def get_user(user_id: str) -> UserRecord | None:
    return users.get(user_id.strip())


def get_user_plan(user_id: str) -> str:
    user = get_user(user_id)
    if not user:
        return "free"
    if user.plan_expiry and user.plan_expiry > datetime.utcnow():
        return "pro"
    if user.is_paid:
        return "pro"
    return user.plan


def set_user_plan(user_id: str, plan: str) -> UserRecord | None:
    user = get_user(user_id)
    if not user:
        return None
    user.plan = plan
    return user


def set_user_pro(user_id: str, duration_days: int = 30) -> UserRecord | None:
    user = get_user(user_id)
    if not user:
        return None
    user.is_paid = True
    user.plan = "pro"
    user.plan_expiry = datetime.utcnow() + timedelta(days=duration_days)
    return user


def user_to_dict(user: UserRecord) -> dict[str, str]:
    return asdict(user)
