from __future__ import annotations

import hashlib
import hmac
import json
import os

import razorpay
from fastapi import APIRouter, HTTPException, Request
from collections import Counter
from fastapi.responses import JSONResponse

from app.services.analytics_store import get_all_events, track_event
from app.services.subscription_store import (
    get_user,
    get_user_plan,
    set_user_pro,
    upsert_user,
    user_to_dict,
)

router = APIRouter(tags=["subscription"])


@router.post("/analytics-event", summary="Track analytics event")
async def analytics_event(payload: dict):
    event = str(payload.get("event") or "").strip()
    allowed_events = {"upgrade_clicked", "payment_started", "payment_success", "payment_failed"}

    if event not in allowed_events:
        raise HTTPException(status_code=400, detail="Invalid analytics event")

    track_event(event)
    return {"status": "ok"}


@router.get("/analytics-summary", summary="Payment analytics summary")
async def analytics_summary():
    events = get_all_events()
    counter = Counter([e.event for e in events])

    upgrade = counter.get("upgrade_clicked", 0)
    started = counter.get("payment_started", 0)
    success = counter.get("payment_success", 0)
    failed = counter.get("payment_failed", 0)

    conversion = 0
    if started > 0:
        conversion = (success / started) * 100

    return {
        "upgrade_clicked": upgrade,
        "payment_started": started,
        "payment_success": success,
        "payment_failed": failed,
        "conversion_rate": round(conversion, 2),
    }


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


@router.post("/create-payment-link", summary="Create Razorpay payment link")
async def create_payment_link(payload: dict):
    user_id = str(payload.get("user_id") or "").strip()
    email = str(payload.get("email") or "").strip().lower() or "customer@testpilot.ai"

    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")

    user = get_user(user_id)
    if user and user.is_paid:
        return {
            "short_url": "",
            "payment_link_url": "",
            "message": "User already on pro plan",
        }

    if user and user.email:
        email = user.email
    elif not user:
        upsert_user(user_id=user_id, email=email)

    track_event("payment_started")

    razorpay_key_id = os.getenv("RAZORPAY_KEY_ID", "")
    razorpay_key_secret = os.getenv("RAZORPAY_KEY_SECRET", "")

    if not razorpay_key_id or not razorpay_key_secret:
        raise HTTPException(status_code=500, detail="Razorpay keys are not configured")

    client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))
    options = {
        "amount": 9900,
        "currency": "INR",
        "description": "TestPilot AI Pro Plan",
        "customer": {"email": email},
        "notify": {"email": True},
        "callback_method": "get",
        "callback_url": "https://testpilotai.app/payment-success.html",
        "reference_id": user_id,
        "notes": {
            "user_id": user_id,
            "plan": "pro",
        },
    }

    try:
        payment_link = client.payment_link.create(data=options)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create payment link: {exc}") from exc

    short_url = payment_link.get("short_url")
    if not short_url:
        raise HTTPException(status_code=500, detail="Payment link short_url not found in Razorpay response")

    return {
        "short_url": short_url,
        "payment_link_url": short_url,
        "payment_link_id": payment_link.get("id"),
    }


@router.post("/webhook", summary="Razorpay webhook")
async def razorpay_webhook(request: Request):
    webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")
    if not webhook_secret:
        raise HTTPException(status_code=500, detail="Razorpay webhook secret is not configured")

    raw_body = await request.body()
    received_signature = request.headers.get("X-Razorpay-Signature", "")

    expected_signature = hmac.new(
        webhook_secret.encode("utf-8"), raw_body, hashlib.sha256
    ).hexdigest()

    if not received_signature or not hmac.compare_digest(expected_signature, received_signature):
        print("Invalid Razorpay webhook signature")
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Webhook JSON parse error: {exc}")
        raise HTTPException(status_code=400, detail="Invalid webhook payload") from exc

    event = payload.get("event")

    if event == "payment_link.paid":
        entity = ((payload.get("payload") or {}).get("payment_link") or {}).get("entity") or {}
        reference_id = entity.get("reference_id")
        notes = entity.get("notes") or {}
        user_id = str(reference_id or notes.get("user_id") or "").strip()

        if user_id:
            user = get_user(user_id)
            if not user:
                upsert_user(user_id=user_id, email="")
                user = get_user(user_id)

            if user and not user.is_paid:
                set_user_pro(user_id)
                track_event("payment_success")
        else:
            print("payment_link.paid webhook missing user_id in notes")

    return JSONResponse(status_code=200, content={"status": "ok"})
