from sqlalchemy.orm import Session

from app.models.user_achievement import UserAchievement
from app.models.users import User
from app.repository.user_achievement import UserAchievementRepository
from app.repository.achievement import AchievementRepository

from app.exceptions import (
    AchievementNotFoundError,
    AchievementNotActiveError,
    UserAchievementNotFoundError,
    UserAlreadyHasAchievementError,
    ForbiddenError,
)


class UserAchievementService:
    def __init__(self):
        self.user_achievement_repo = UserAchievementRepository()
        self.achievement_repo = AchievementRepository()

    def award_achievement(
        self, db: Session, achievement_id: int, current_user: User
    ) -> UserAchievement:
        # Внутренний метод. НЕ выставляется в публичный API.
        # Будет вызываться автоматической системой достижений (Achievement Engine)
        # после проверки условий (завершённая тренировка, стрик, PR и т.д.).
        achievement = self.achievement_repo.get_by_id(db, achievement_id)
        if not achievement:
            raise AchievementNotFoundError(achievement_id)

        if not achievement.is_active:
            raise AchievementNotActiveError(achievement_id)

        if self.user_achievement_repo.exists(db, current_user.id, achievement_id):
            raise UserAlreadyHasAchievementError()

        user_achievement_db = UserAchievement(
            user_id=current_user.id,
            achievement_id=achievement_id,
        )

        new_user_achievement = self.user_achievement_repo.create(db, user_achievement_db)
        db.commit()
        db.refresh(new_user_achievement)
        return new_user_achievement

    def get_by_id(
        self, db: Session, user_achievement_id: int, current_user: User
    ) -> UserAchievement:
        user_achievement = self.user_achievement_repo.get_by_id(db, user_achievement_id)
        if not user_achievement:
            raise UserAchievementNotFoundError(user_achievement_id)

        if user_achievement.user_id != current_user.id:
            raise ForbiddenError()

        return user_achievement

    def get_my_achievements(
        self, db: Session, current_user: User, skip: int = 0, limit: int = 20
    ) -> list[UserAchievement]:
        return self.user_achievement_repo.get_by_user(db, current_user.id, skip, limit)

    def get_users_by_achievement(
        self, db: Session, achievement_id: int, skip: int = 0, limit: int = 20
    ) -> list[UserAchievement]:
        # Заготовка для будущего admin-эндпоинта. Публичного роута нет.
        return self.user_achievement_repo.get_by_achievement(db, achievement_id, skip, limit)