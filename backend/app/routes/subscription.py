from __future__ import annotations

import os
from urllib.parse import urlencode

import razorpay
from fastapi import APIRouter, HTTPException
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
    print("Request received:", payload)
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
    if user and user.email:
        email = user.email
    elif not user:
        upsert_user(user_id=user_id, email=email)

    razorpay_key_id = os.getenv("RAZORPAY_KEY_ID", "")
    razorpay_key_secret = os.getenv("RAZORPAY_KEY_SECRET", "")
    frontend_url = os.getenv("FRONTEND_URL", "https://your-frontend-url")

    if not razorpay_key_id or not razorpay_key_secret:
        raise HTTPException(status_code=500, detail="Razorpay keys are not configured")

    client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))
    options = {
        "amount": 99900,
        "currency": "INR",
        "description": "TestPilot AI Pro Plan",
        "customer": {"email": email},
        "notify": {"email": True},
        "callback_method": "get",
        "callback_url": f"{frontend_url.rstrip('/')}/payment-success",
        "notes": {
            "user_id": user_id,
        },
    }

    try:
        payment_link = client.payment_link.create(data=options)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create payment link: {exc}") from exc

    payment_link_url = payment_link.get("short_url") or payment_link.get("payment_link")
    if not payment_link_url:
        raise HTTPException(status_code=500, detail="Payment link URL not found in Razorpay response")

    return {
        "payment_link_url": payment_link_url,
        "payment_link_id": payment_link.get("id"),
    }


@router.get("/payment-success", summary="Handle Razorpay payment success callback")
async def payment_success(payment_id: str = "", payment_link_id: str = "", status: str = ""):
    if not payment_link_id:
        raise HTTPException(status_code=400, detail="Missing payment_link_id")

    if status == "paid":
        razorpay_key_id = os.getenv("RAZORPAY_KEY_ID", "")
        razorpay_key_secret = os.getenv("RAZORPAY_KEY_SECRET", "")
        if not razorpay_key_id or not razorpay_key_secret:
            raise HTTPException(status_code=500, detail="Razorpay keys are not configured")

        client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))
        try:
            payment_link = client.payment_link.fetch(payment_link_id)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Failed to verify payment link: {exc}") from exc

        notes = payment_link.get("notes") or {}
        user_id = str(notes.get("user_id") or "").strip()
        if user_id:
            set_user_pro(user_id)
            return {"status": "ok", "message": "Payment verified and user upgraded", "user_id": user_id}

    query_string = urlencode(
        {"payment_id": payment_id, "payment_link_id": payment_link_id, "status": status}
    )
    return {"status": "pending", "message": "Payment not confirmed", "details": query_string}
