"""
Custom exceptions and error handlers for BeachWaste AI.
"""
from fastapi import HTTPException, status

class BeachWasteException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class ModelNotTrainedError(BeachWasteException):
    def __init__(self, model_name: str):
        super().__init__(
            detail=f"Model '{model_name}' has not been trained or no valid weights found. Please initiate training first.",
            status_code=status.HTTP_404_NOT_FOUND
        )

class InsufficientDataError(BeachWasteException):
    def __init__(self, beach_name: str, required_records: int, available_records: int):
        super().__init__(
            detail=f"Insufficient historical data for '{beach_name}'. Minimum required is {required_records} monthly observations, but only {available_records} are available.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

class DatasetValidationError(BeachWasteException):
    def __init__(self, errors: list):
        super().__init__(
            detail=f"Dataset validation failed: {'; '.join(errors)}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
