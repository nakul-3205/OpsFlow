from fastapi import FastAPI
from config.database_conn import conn
from config.settings import settings
from logger_service.logger import setup_logger
from core.error_handler import APIException
from fastapi.responses import JSONResponse
from fastapi.requests import Request


app = FastAPI()
logger=setup_logger()
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
app.add_exception_handler(APIException,api_exception_handler)


@app.get("/")
async def root():
    return {"status": "OpsFlow Auth Service Running"}
