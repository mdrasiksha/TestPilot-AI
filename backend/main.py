import os
from typing import Any

import razorpay
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="Razorpay SaaS Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FREE_USAGE_LIMIT = 5
ORDER_AMOUNT_PAISE = 9900
ORDER_CURRENCY = "INR"

# In-memory user state (single demo user)
user = {
    "is_paid": False,
    "usage_count": 0,
    "last_verified_payment_id": None,
}


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class GenerateRequest(BaseModel):
    prompt: str | None = None


def get_razorpay_keys() -> tuple[str, str]:
    key_id = os.getenv("RAZORPAY_KEY_ID", "").strip()
    key_secret = os.getenv("RAZORPAY_KEY_SECRET", "").strip()

    if not key_id or not key_secret:
        raise HTTPException(status_code=500, detail="Razorpay keys are not configured")

    return key_id, key_secret


def get_razorpay_client() -> razorpay.Client:
    key_id, key_secret = get_razorpay_keys()
    return razorpay.Client(auth=(key_id, key_secret))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/user-state")
def user_state() -> dict[str, Any]:
    remaining = "unlimited" if user["is_paid"] else max(0, FREE_USAGE_LIMIT - user["usage_count"])
    return {
        "is_paid": user["is_paid"],
        "usage_count": user["usage_count"],
        "remaining": remaining,
    }


@app.post("/create-order")
def create_order() -> dict[str, Any]:
    client = get_razorpay_client()

    try:
        order = client.order.create(
            {
                "amount": ORDER_AMOUNT_PAISE,
                "currency": ORDER_CURRENCY,
                "receipt": "saas-upgrade-receipt",
                "notes": {"plan": "pro"},
            }
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create order: {exc}") from exc

    return {
        "order_id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"],
        "key_id": os.getenv("RAZORPAY_KEY_ID", "").strip(),
    }


@app.post("/verify-payment")
def verify_payment(payload: VerifyPaymentRequest) -> dict[str, Any]:
    client = get_razorpay_client()

    if payload.razorpay_payment_id == user.get("last_verified_payment_id"):
        return {
            "success": True,
            "message": "Payment already verified",
            "is_paid": user["is_paid"],
        }

    params = {
        "razorpay_order_id": payload.razorpay_order_id,
        "razorpay_payment_id": payload.razorpay_payment_id,
        "razorpay_signature": payload.razorpay_signature,
    }

    try:
        client.utility.verify_payment_signature(params)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid payment signature: {exc}") from exc

    user["is_paid"] = True
    user["last_verified_payment_id"] = payload.razorpay_payment_id

    return {"success": True, "message": "Payment verified", "is_paid": True}


@app.post("/generate")
def generate(_: GenerateRequest) -> dict[str, Any]:
    if user["is_paid"]:
        return {
            "allowed": True,
            "message": "Unlimited access",
            "usage_count": user["usage_count"],
            "is_paid": True,
        }

    if int(user["usage_count"]) < FREE_USAGE_LIMIT:
        user["usage_count"] = int(user["usage_count"]) + 1
        remaining = FREE_USAGE_LIMIT - int(user["usage_count"])
        return {
            "allowed": True,
            "message": "Free usage consumed",
            "usage_count": user["usage_count"],
            "remaining": remaining,
            "is_paid": False,
        }

    return {
        "allowed": False,
        "message": "Upgrade to Pro",
        "usage_count": user["usage_count"],
        "remaining": 0,
        "is_paid": False,
    }
