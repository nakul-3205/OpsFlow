from fastapi import Request
from fastapi.responses import JSONResponse
from error_handler import APIException
from logger_service.logger import setup_logger

logger = setup_logger()

async def api_exception_handler(request: Request, exc: APIException):

    logger.error(f"Error: {exc.message} | Path: {request.url.path} | Details: {exc.details}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "details": exc.details
        }
    )
