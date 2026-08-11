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

from app.exceptions import AppError


app = FastAPI()


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(exercise_router, prefix="/api/v1/exercises", tags=["Exercises"])
app.include_router(supplements_router, prefix="/api/v1/supplements", tags=["Supplements"])
app.include_router(workout_day_router, prefix="/api/v1/workout-days", tags=["Workout days"])
app.include_router(workout_exercise_router, prefix="/api/v1/workout-exercises", tags=["Workout exercises"])
app.include_router(workout_program_router, prefix="/api/v1/workout-programs", tags=["Workout programs"])
app.include_router(workout_session_router, prefix="/api/v1/workout-sessions", tags=["Workout sessions"])
app.include_router(exercise_log_router, prefix="/api/v1/exercise-logs", tags=["Exercise logs"])
app.include_router(set_log_router, prefix="/api/v1/set-logs", tags=["Set logs"])