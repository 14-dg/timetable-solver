import logging
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.exceptions.crud_exceptions import (
    ObjectAlreadyExistsException,
    ObjectNotFoundException,
)

logger = logging.getLogger(__name__)


class ErrorResponse(BaseModel):
    error: str
    code: str
    timestamp: datetime = datetime.now(UTC)
    path: str
    details: dict[str, Any] | None = None


async def http_exception_handler(request: Request, exc: HTTPException):
    error_response = ErrorResponse(
        error=exc.detail,
        code=f"HTTP_{exc.status_code}",
        path=request.url.path
    )

    if exc.status_code >= 500:
        logger.error(f"Server error at {request.url.path}: {exc.detail}")
    else:
        logger.error(f"Client error at {request.url.path}: {exc.detail}")

    return JSONResponse(
        content=jsonable_encoder(error_response),
        status_code=exc.status_code
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):

    field_errors = {f"Field: {error["loc"]}": f"Error: {error["msg"]}" for error in exc.errors()}

    error_response = ErrorResponse(
        error="Request validation failed",
        code="VALIDATION_ERROR",
        path=request.url.path,
        details=field_errors,
    )

    logger.error(f"Validation error at {request.url}: {field_errors}")
    
    return JSONResponse(
        content=jsonable_encoder(error_response),
        status_code=400,
    )


async def object_not_found_exception_handler(request: Request, exc: ObjectNotFoundException):
    error_response = ErrorResponse(
        error=exc.message,
        code=exc.code,
        path=request.url.path,
        details=exc.details,
    )

    logger.error(f"ObjectNotFoundException at {error_response.path}: {exc}")
    
    return JSONResponse(
        content=jsonable_encoder(error_response),
        status_code=404,
    )


async def object_already_exists_exception_handler(request: Request, exc: ObjectAlreadyExistsException):
    error_response = ErrorResponse(
        error=exc.message,
        code=exc.code,
        path=request.url.path,
        details=exc.details
    )

    logger.error(f"ObjectNotFoundException at {error_response.path}: {exc}")

    return JSONResponse(
        content=jsonable_encoder(error_response),
        status_code=409,
    )


async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler for unexpected exceptions.
    Logs the full traceback but returns a safe message to clients.
    """
    
    logger.error(
        f"Unhandled exception at {request.url}:\n {exc}"
    )

    error_response = ErrorResponse(
        error="An internal error occurred",
        code="INTERNAL_ERROR",
        path=str(request.url.path)
    )

    return JSONResponse(
        content=jsonable_encoder(error_response),
        status_code=500,
    )


def add_app_exception_handlers(app: FastAPI):
    app.add_exception_handler(exc_class_or_status_code=HTTPException, handler=http_exception_handler) # type: ignore
    app.add_exception_handler(exc_class_or_status_code=RequestValidationError, handler=validation_exception_handler) # type: ignore
    app.add_exception_handler(exc_class_or_status_code=ObjectNotFoundException, handler=object_not_found_exception_handler) # type: ignore
    app.add_exception_handler(exc_class_or_status_code=ObjectAlreadyExistsException, handler=object_already_exists_exception_handler) # type: ignore
    app.add_exception_handler(exc_class_or_status_code=Exception, handler=global_exception_handler)