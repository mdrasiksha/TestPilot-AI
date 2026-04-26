from __future__ import annotations

import hashlib
import hmac
import json
import os

import razorpay
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

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
        "callback_url": "https://test-pilot-ai-lemon.vercel.app/payment-success",
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
        notes = entity.get("notes") or {}
        user_id = str(notes.get("user_id") or "").strip()

        if user_id:
            user = get_user(user_id)
            if not user:
                upsert_user(user_id=user_id, email="")
                user = get_user(user_id)

            if user and not user.is_paid:
                set_user_pro(user_id)
        else:
            print("payment_link.paid webhook missing user_id in notes")

    return JSONResponse(status_code=200, content={"status": "ok"})
