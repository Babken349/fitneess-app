import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool
from yookassa import Configuration, Payment as YooKassaPayment

from app.models.payment import Payment
from app.models.users import User
from app.repository.payment import PaymentRepository
from app.core.config import settings


class PaymentService:

    PREMIUM_PRICE = Decimal("499.00")
    PREMIUM_DAYS = 30

    def __init__(self):
        self.payment_repo = PaymentRepository()

        Configuration.account_id = settings.YOOKASSA_SHOP_ID
        Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    async def create_payment(
        self,
        db: AsyncSession,
        user: User,
    ) -> dict:

        amount = self.PREMIUM_PRICE

        # SDK yookassa блокирующий, выносим в поток, чтобы не вешать event loop
        yookassa_payment = await run_in_threadpool(
            YooKassaPayment.create,
            {
                "amount": {
                    "value": str(amount),
                    "currency": "RUB",
                },
                "capture": True,
                "confirmation": {
                    "type": "redirect",
                    "return_url": settings.YOOKASSA_RETURN_URL,
                },
                "description": "Premium на 30 дней",
                "metadata": {
                    "user_id": str(user.id),
                },
            },
            str(uuid.uuid4()),
        )

        payment = Payment(
            user_id=user.id,
            payment_id=yookassa_payment.id,
            amount=amount,
            currency="RUB",
            status=yookassa_payment.status,
            description="Premium на 30 дней",
        )

        self.payment_repo.create(db, payment)

        await db.commit()
        await db.refresh(payment)

        return {
            "payment_id": yookassa_payment.id,
            "amount": amount,
            "currency": "RUB",
            "status": yookassa_payment.status,
            "confirmation_url": (
                yookassa_payment.confirmation.confirmation_url
            ),
        }