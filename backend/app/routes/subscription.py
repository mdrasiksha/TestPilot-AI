from __future__ import annotations

import hashlib
import hmac
import json

import razorpay
from fastapi import APIRouter, Header, HTTPException, Request

from app.core.config import get_settings
from app.services.subscription_store import (
    get_user,
    get_user_plan,
    set_user_pro,
    upsert_user,
    user_to_dict,
)

router = APIRouter(tags=["subscription"])


@router.post("/auth/login", summary="Login or signup with email")
async def login(payload: dict):
    user_id = str(payload.get("user_id") or "").strip()
    email = str(payload.get("email") or "").strip().lower()

    if not user_id or not email:
        raise HTTPException(status_code=400, detail="Missing user_id or email")

    user = upsert_user(user_id=user_id, email=email)
    return {"status": "ok", "user": user_to_dict(user)}


@router.get("/user/{user_id}", summary="Get user profile")
async def get_profile(user_id: str):
    user = get_user(user_id)
    if not user:
        return {
            "user": {
                "user_id": user_id,
                "email": "",
                "plan": get_user_plan(user_id),
            }
        }

    return {"user": user_to_dict(user)}


@router.post("/create-order", summary="Create Razorpay order")
async def create_order(payload: dict):
    settings = get_settings()
    user_id = str(payload.get("user_id") or "").strip()

    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")

    if not settings.razorpay_key_id or not settings.razorpay_key_secret:
        raise HTTPException(status_code=500, detail="Razorpay keys are not configured")

    client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))
    options = {
        "amount": 29900,
        "currency": "INR",
        "receipt": f"receipt_{user_id}",
        "notes": {
            "user_id": user_id,
        },
    }

    try:
        order = client.order.create(data=options)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create order: {exc}") from exc

    return order


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
        notes = payment.get("notes") or {}
        user_id = str(notes.get("user_id") or "").strip()

        if user_id:
            set_user_pro(user_id)

    return {"status": "ok"}
