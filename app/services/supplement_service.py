from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supplements import Supplement
from app.schemas.supplements import SupplementCreate, SupplementUpdate

from app.repository.supplement_repository import SupplementRepository

from app.exceptions import (
    SupplementNotFoundError,
    SupplementAlreadyExistsError,
)


class SupplementService:

    def __init__(self):
        self.supplement_repo = SupplementRepository()

    # =========================
    # CREATE
    # =========================

    async def create_supplement(
        self,
        db: AsyncSession,
        data: SupplementCreate,
    ) -> Supplement:

        if await self.supplement_repo.exists_by_name(
            db,
            data.name,
        ):
            raise SupplementAlreadyExistsError(
                data.name
            )

        supplement = Supplement(
            name=data.name,
            description=data.description,
            category=data.category,
        )

        self.supplement_repo.create(
            db,
            supplement,
        )

        await db.commit()
        await db.refresh(supplement)

        return supplement

    # =========================
    # GET BY ID
    # =========================

    async def get_by_id(
        self,
        db: AsyncSession,
        supplement_id: int,
    ) -> Supplement:

        supplement = await self.supplement_repo.get_by_id(
            db,
            supplement_id,
        )

        if not supplement:
            raise SupplementNotFoundError(
                supplement_id
            )

        return supplement

    # =========================
    # GET ALL
    # =========================

    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Supplement]:

        return await self.supplement_repo.get_all(
            db,
            skip,
            limit,
        )

    # =========================
    # UPDATE
    # =========================

    async def update_supplement(
        self,
        db: AsyncSession,
        supplement_id: int,
        data: SupplementUpdate,
    ) -> Supplement:

        supplement = await self.get_by_id(
            db,
            supplement_id,
        )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "name" in update_data:

            existing = await self.supplement_repo.get_by_name(
                db,
                update_data["name"],
            )

            if existing and existing.id != supplement_id:
                raise SupplementAlreadyExistsError(
                    update_data["name"]
                )

        for key, value in update_data.items():
            setattr(
                supplement,
                key,
                value,
            )

        self.supplement_repo.update(
            supplement
        )

        await db.commit()
        await db.refresh(supplement)

        return supplement

    # =========================
    # DELETE
    # =========================

    async def delete_supplement(
        self,
        db: AsyncSession,
        supplement_id: int,
    ) -> None:

        supplement = await self.get_by_id(
            db,
            supplement_id,
        )

        await self.supplement_repo.delete(
            db,
            supplement,
        )

        await db.commit()