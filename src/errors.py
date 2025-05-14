"""
Centralized error handling for the booking application.
This module defines custom exceptions used throughout the application.
"""
from typing import Dict, Any, Optional
from fastapi import HTTPException, status

class ApplicationError(Exception):
    """Base error class for application errors"""
    def __init__(
        self, 
        message: str, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ResourceNotFoundError(ApplicationError):
    """Error raised when a requested resource is not found"""
    def __init__(self, resource_type: str, identifier: Any):
        super().__init__(
            message=f"{resource_type} with identifier {identifier} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource_type": resource_type, "identifier": identifier}
        )

class UnauthorizedError(ApplicationError):
    """Error raised for authentication failures"""
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class ConflictError(ApplicationError):
    """Error raised for resource conflicts"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )

class ValidationError(ApplicationError):
    """Error raised for validation failures"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )

def handle_application_error(error: ApplicationError):
    """Convert application errors to FastAPI HTTP exceptions"""
    raise HTTPException(
        status_code=error.status_code,
        detail={"message": error.message, "details": error.details}
    )