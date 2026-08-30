from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.exercise import router as exercise_router 
from app.api.v1.supplements import router as supplements_router
from app.api.v1.workout_day import router as workout_day_router
from app.api.v1.workout_exercise import router as workout_exercise_router
from app.api.v1.workout_program import router as workout_program_router
from app.api.v1.workout_session import router as workout_session_router
from app.api.v1.exercise_log import router as exercise_log_router
from app.api.v1.set_log import router as set_log_router
from app.api.v1.body_weight import router as body_weights_router
from app.api.v1.body_measurement import router as body_measurements_router
from app.api.v1.progress_photo import router as progress_photos_router
from app.exceptions import AppError
from app.api.v1.achievement import router as achievements_router
from app.api.v1.user_achievement import router as user_achievements_router
from app.api.v1.friendship import router as friendship_router
from app.api.v1.supplement_intake import router as supplement_intake_router
from app.api.v1.password_reset import router as password_reset_router
from app.api.v1.email_verification import router as email_verification_router
from app.api.v1.test_email import router as test_email_router


app = FastAPI(
    title="Fitness App API",
    description="API для фитнес‑приложения (трекинг, тренировки, добавки, друзья, достижения)",
    version="0.1.0",
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)},
    )


# Auth & Users
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])

# Email & Password
app.include_router(
    email_verification_router,
    prefix="/api/v1/email-verification",
    tags=["Email verification"],
)
app.include_router(
    password_reset_router,
    prefix="/api/v1/password-reset",
    tags=["Password reset"],
)
app.include_router(
    test_email_router,
    prefix="/api/v1/test",
    tags=["Test email"],
)

# Exercises & Workouts
app.include_router(exercise_router, prefix="/api/v1/exercises", tags=["Exercises"])
app.include_router(workout_day_router, prefix="/api/v1/workout-days", tags=["Workout days"])
app.include_router(workout_exercise_router, prefix="/api/v1/workout-exercises", tags=["Workout exercises"])
app.include_router(workout_program_router, prefix="/api/v1/workout-programs", tags=["Workout programs"])
app.include_router(workout_session_router, prefix="/api/v1/workout-sessions", tags=["Workout sessions"])
app.include_router(exercise_log_router, prefix="/api/v1/exercise-logs", tags=["Exercise logs"])
app.include_router(set_log_router, prefix="/api/v1/set-logs", tags=["Set logs"])

# Body tracking
app.include_router(body_weights_router, prefix="/api/v1/weight", tags=["Body weight"])
app.include_router(body_measurements_router, prefix="/api/v1/measurement", tags=["Body measurement"])
app.include_router(progress_photos_router, prefix="/api/v1/photo", tags=["Progress photo"])

# Supplements
app.include_router(supplements_router, prefix="/api/v1/supplements", tags=["Supplements"])
app.include_router(supplement_intake_router, prefix="/api/v1/supplement-intake", tags=["Supplement intake"])

# Achievements & Friendship
app.include_router(achievements_router, prefix="/api/v1/achievements", tags=["Achievements"])
app.include_router(user_achievements_router, prefix="/api/v1/user-achievements", tags=["User achievements"])
app.include_router(friendship_router, prefix="/api/v1/friendship", tags=["Friendship"])