from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment


class PaymentRepository:

    def create(self, db: AsyncSession, payment: Payment) -> Payment:
        db.add(payment)
        return payment

    async def get_by_id(self, db: AsyncSession, payment_id: int) -> Payment | None:
        stmt = select(Payment).where(Payment.id == payment_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_payment_id(
        self,
        db: AsyncSession,
        payment_id: str,
    ) -> Payment | None:
        stmt = select(Payment).where(Payment.payment_id == payment_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    def update(self, payment: Payment) -> Payment:
        return payment