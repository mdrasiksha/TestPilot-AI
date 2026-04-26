# Razorpay SaaS Demo (FastAPI + HTML)

This project includes a simple Razorpay test-mode integration for a SaaS-style paywall.

## Project structure

- `backend/main.py` - FastAPI backend with Razorpay integration.
- `frontend/index.html` - Basic UI with Razorpay Checkout flow.

## Environment variables

Create `backend/.env` and add test keys:

```env
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_test_secret
```

> Do not commit real keys.

## Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

Required packages include:
- fastapi
- uvicorn
- razorpay
- python-dotenv

## Run backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Run frontend

Open `frontend/index.html` in your browser.

## API behavior

- `POST /create-order`
  - Creates Razorpay order for ₹99 (`amount=9900`, `currency=INR`).
  - Returns `order_id`, `amount`, `currency`, and `key_id`.
  - If env keys missing, returns: `Razorpay keys are not configured`.

- `POST /verify-payment`
  - Verifies signature using `razorpay_order_id`, `razorpay_payment_id`, `razorpay_signature`.
  - Prevents duplicate verification for same payment id.
  - On success marks user paid (`is_paid = true`).

- `POST /generate`
  - Free users: allowed up to 5 times.
  - Paid users: unlimited.
  - After limit returns `Upgrade to Pro`.

- `GET /user-state`
  - Returns current in-memory user status.

## Payment flow

1. Click **🚀 Upgrade to Pro**.
2. Frontend calls `/create-order`.
3. Razorpay checkout opens.
4. On payment success frontend calls `/verify-payment`.
5. Backend verifies signature and unlocks unlimited usage.

## Security notes

- Razorpay secret key stays in backend env variables only.
- Frontend uses only `RAZORPAY_KEY_ID`.
- Signature verification is done on backend before enabling paid access.
