from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.exceptions import AppError

# Auth & Users
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router

# Email & Password
from app.api.v1.email_verification import router as email_verification_router
from app.api.v1.password_reset import router as password_reset_router
from app.api.v1.email import router as email_router

# Exercises & Workouts
from app.api.v1.exercise import router as exercise_router
from app.api.v1.workout_day import router as workout_day_router
from app.api.v1.workout_exercise import router as workout_exercise_router
from app.api.v1.workout_program import router as workout_program_router
from app.api.v1.workout_session import router as workout_session_router
from app.api.v1.exercise_log import router as exercise_log_router
from app.api.v1.set_log import router as set_log_router

# Body tracking
from app.api.v1.body_weight import router as body_weights_router
from app.api.v1.body_measurement import router as body_measurements_router
from app.api.v1.progress_photo import router as progress_photos_router

# Supplements
from app.api.v1.supplements import router as supplements_router
from app.api.v1.user_supplements import router as user_supplements_router
from app.api.v1.supplement_intake import router as supplement_intake_router
from app.api.v1.reminder import router as reminder_router

# Achievements & Friendship
from app.api.v1.achievement import router as achievements_router
from app.api.v1.user_achievement import router as user_achievements_router
from app.api.v1.friendship import router as friendship_router

# Calendar
from app.api.v1.calendar_availability import router as calendar_availability_router

# Payment
from app.api.v1.payment import router as payment_router

# Study
from app.api.v1.study_state import router as study_state_router
from app.api.v1.study_test_result import router as study_test_result_router

# Sleep & Research
from app.api.v1.sleep import router as sleep_router
from app.api.v1.research_analytics import router as research_analytics_router


app = FastAPI(
    title="Fitness App API",
    description="API для фитнес-приложения (трекинг, тренировки, добавки, друзья, достижения)",
    version="0.1.0",
)


# CORS: разрешаем браузерному фронтенду ходить в API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)},
        headers=exc.headers,
    )


# =========================================================
# Правило: если пути внутри роутера уже содержат название ресурса
# (например "/weights" или "/days/{id}"), prefix у роутера общий
# ("/api/v1" или "/api/v1/body"), чтобы слова не повторялись.
# =========================================================

# Auth & Users
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Auth"],
)

app.include_router(
    users_router,
    prefix="/api/v1/users",
    tags=["Users"],
)


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

# Тестовое письмо только в режиме отладки, в проде эндпоинта не будет
if getattr(settings, "DEBUG", False):
    app.include_router(
        email_router,
        prefix="/api/v1/dev",
        tags=["Dev"],
    )


# Exercises & Workouts
app.include_router(
    exercise_router,
    prefix="/api/v1/exercises",
    tags=["Exercises"],
)

# Внутри: /workout-programs/{id}/days..., /days/{id}...
app.include_router(
    workout_day_router,
    prefix="/api/v1",
    tags=["Workout days"],
)

# Внутри: /days/{id}/exercises, /workout-exercises/{id}
app.include_router(
    workout_exercise_router,
    prefix="/api/v1",
    tags=["Workout exercises"],
)

# Внутри: /workout-programs/...
app.include_router(
    workout_program_router,
    prefix="/api/v1",
    tags=["Workout programs"],
)

# Внутри: "", /me, /active, /{id}, /day/{id}
app.include_router(
    workout_session_router,
    prefix="/api/v1/workout-sessions",
    tags=["Workout sessions"],
)

# Внутри: /workout-sessions/{id}/exercises, /exercise-logs/{id}
app.include_router(
    exercise_log_router,
    prefix="/api/v1",
    tags=["Exercise logs"],
)

# Внутри: /exercise-logs/{id}/sets, /sets/{id}
app.include_router(
    set_log_router,
    prefix="/api/v1",
    tags=["Set logs"],
)


# Body tracking
# Внутри: /weights, /measurements, /photos
app.include_router(
    body_weights_router,
    prefix="/api/v1/body",
    tags=["Body weight"],
)

app.include_router(
    body_measurements_router,
    prefix="/api/v1/body",
    tags=["Body measurement"],
)

app.include_router(
    progress_photos_router,
    prefix="/api/v1/body",
    tags=["Progress photo"],
)


# Supplements
app.include_router(
    supplements_router,
    prefix="/api/v1/supplements",
    tags=["Supplements"],
)

# Внутри: /user-supplements, /user-supplements/{id}
app.include_router(
    user_supplements_router,
    prefix="/api/v1",
    tags=["User supplements"],
)

# Внутри: /supplement-intakes..., /user-supplements/{id}/intakes
app.include_router(
    supplement_intake_router,
    prefix="/api/v1",
    tags=["Supplement intake"],
)

# Внутри: /user-supplements/{id}/reminders, /supplement-reminders...
app.include_router(
    reminder_router,
    prefix="/api/v1",
    tags=["Reminders"],
)


# Achievements & Friendship
app.include_router(
    achievements_router,
    prefix="/api/v1/achievements",
    tags=["Achievements"],
)

app.include_router(
    user_achievements_router,
    prefix="/api/v1/user-achievements",
    tags=["User achievements"],
)

app.include_router(
    friendship_router,
    prefix="/api/v1/friendship",
    tags=["Friendship"],
)


# Calendar
app.include_router(
    calendar_availability_router,
    prefix="/api/v1/calendar",
    tags=["Calendar availability"],
)


# Payment
app.include_router(
    payment_router,
    prefix="/api/v1/payment",
    tags=["Payment"],
)


# Study (prefix внутри самих роутеров убран, он задаётся только здесь)
app.include_router(
    study_state_router,
    prefix="/api/v1/study-states",
    tags=["Study states"],
)

app.include_router(
    study_test_result_router,
    prefix="/api/v1/study-test-results",
    tags=["Study test results"],
)


# Sleep & Research
app.include_router(
    sleep_router,
    prefix="/api/v1/sleep",
    tags=["Sleep"],
)

app.include_router(
    research_analytics_router,
    prefix="/api/v1/research/analytics",
    tags=["Research Analytics"],
)