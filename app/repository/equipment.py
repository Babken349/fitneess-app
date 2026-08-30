from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.exercise import Equipment


class EquipmentRepository:
    
    def get_by_id(self, db: Session, equipment_id: int) -> Equipment | None:
        stmt = select(Equipment).where(Equipment.id == equipment_id)
        return db.execute(stmt).scalar_one_or_none()

    def get_by_name(self, db: Session, name: str) -> Equipment | None:
        stmt = select(Equipment).where(Equipment.name == name)
        return db.execute(stmt).scalar_one_or_none()