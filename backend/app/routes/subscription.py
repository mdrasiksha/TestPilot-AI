from __future__ import annotations

import hashlib
import hmac
import json

from fastapi import APIRouter, Header, HTTPException, Request

from app.core.config import get_settings
from app.services.subscription_store import save_phone_user_mapping, set_user_pro_by_phone

router = APIRouter(tags=["subscription"])


@router.post("/save-user", summary="Save phone to user mapping")
async def save_user(payload: dict):
    user_id = str(payload.get("user_id") or "").strip()
    phone = str(payload.get("phone") or "").strip()

    if not user_id or not phone:
        raise HTTPException(status_code=400, detail="Missing user_id or phone")

    save_phone_user_mapping(phone=phone, user_id=user_id)
    return {"status": "ok"}


@router.post("/webhook", summary="Handle Razorpay webhook")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str | None = Header(default=None),
):
    settings = get_settings()
    raw_body = await request.body()

    if settings.razorpay_webhook_secret:
        expected = hmac.new(
            settings.razorpay_webhook_secret.encode("utf-8"),
            raw_body,
            hashlib.sha256,
        ).hexdigest()

        if not x_razorpay_signature or not hmac.compare_digest(expected, x_razorpay_signature):
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid webhook payload") from exc

    event = payload.get("event")
    if event == "payment.captured":
        payment = payload.get("payload", {}).get("payment", {}).get("entity", {})
        phone = str(payment.get("contact") or "").strip()
        upgraded_user_id = set_user_pro_by_phone(phone)

        if upgraded_user_id:
            print(f"User upgraded to PRO: {upgraded_user_id}")

    return {"status": "ok"}
