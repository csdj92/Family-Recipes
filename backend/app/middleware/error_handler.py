from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

async def error_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except SQLAlchemyError as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Database error occurred: {str(e)}"}
        ) 