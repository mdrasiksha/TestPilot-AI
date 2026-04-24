from __future__ import annotations

phone_to_user_map: dict[str, str] = {}
user_plans: dict[str, str] = {}


def normalize_phone(phone: str) -> str:
    return "".join(ch for ch in phone if ch.isdigit())


def save_phone_user_mapping(phone: str, user_id: str) -> None:
    normalized_phone = normalize_phone(phone)
    if normalized_phone and user_id:
        phone_to_user_map[normalized_phone] = user_id


def get_user_plan(user_id: str) -> str:
    return user_plans.get(user_id, "free")


def set_user_pro_by_phone(phone: str) -> str | None:
    normalized_phone = normalize_phone(phone)
    user_id = phone_to_user_map.get(normalized_phone)
    if user_id:
        user_plans[user_id] = "pro"
    return user_id
