"""Custom exceptions for Weather Dashboard application.

This module defines all custom exceptions used throughout the application
to provide better error handling and debugging capabilities.
"""


class WeatherDashboardError(Exception):
    """Base exception class for Weather Dashboard application."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        """Initialize the exception.
        
        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
            details: Optional dictionary with additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def __str__(self) -> str:
        """Return string representation of the exception."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class DependencyInjectionError(WeatherDashboardError):
    """Exception raised when dependency injection fails."""
    
    def __init__(self, message: str, service_name: str = None):
        """Initialize the exception.
        
        Args:
            message: Error message
            service_name: Name of the service that failed to inject
        """
        super().__init__(message, "DI_ERROR")
        self.service_name = service_name


class ConfigurationError(WeatherDashboardError):
    """Exception raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, config_key: str = None, config_value: str = None):
        """Initialize the exception.
        
        Args:
            message: Error message
            config_key: Configuration key that caused the error
            config_value: Configuration value that caused the error
        """
        super().__init__(message, "CONFIG_ERROR")
        self.config_key = config_key
        self.config_value = config_value


class ValidationError(WeatherDashboardError):
    """Exception raised when data validation fails."""
    
    def __init__(self, message: str, field_name: str = None, field_value: str = None):
        """Initialize the exception.
        
        Args:
            message: Error message
            field_name: Name of the field that failed validation
            field_value: Value that failed validation
        """
        super().__init__(message, "VALIDATION_ERROR")
        self.field_name = field_name
        self.field_value = field_value


class ServiceError(WeatherDashboardError):
    """Exception raised when a service operation fails."""
    
    def __init__(self, message: str, service_name: str = None, operation: str = None):
        """Initialize the exception.
        
        Args:
            message: Error message
            service_name: Name of the service that failed
            operation: Operation that failed
        """
        super().__init__(message, "SERVICE_ERROR")
        self.service_name = service_name
        self.operation = operation


class WeatherAPIError(ServiceError):
    """Exception raised when weather API operations fail."""
    
    def __init__(self, message: str, api_name: str = None, status_code: int = None):
        """Initialize the exception.
        
        Args:
            message: Error message
            api_name: Name of the API that failed
            status_code: HTTP status code if applicable
        """
        super().__init__(message, "weather_api", "api_call")
        self.api_name = api_name
        self.status_code = status_code


class CacheError(ServiceError):
    """Exception raised when cache operations fail."""
    
    def __init__(self, message: str, cache_key: str = None, operation: str = None):
        """Initialize the exception.
        
        Args:
            message: Error message
            cache_key: Cache key that caused the error
            operation: Cache operation that failed (get, set, delete, etc.)
        """
        super().__init__(message, "cache_service", operation)
        self.cache_key = cache_key


class StorageError(ServiceError):
    """Exception raised when storage operations fail."""
    
    def __init__(self, message: str, storage_type: str = None, operation: str = None):
        """Initialize the exception.
        
        Args:
            message: Error message
            storage_type: Type of storage (file, database, etc.)
            operation: Storage operation that failed
        """
        super().__init__(message, "storage_service", operation)
        self.storage_type = storage_type


class UIError(WeatherDashboardError):
    """Exception raised when UI operations fail."""
    
    def __init__(self, message: str, component: str = None, action: str = None):
        """Initialize the exception.
        
        Args:
            message: Error message
            component: UI component that caused the error
            action: UI action that failed
        """
        super().__init__(message, "UI_ERROR")
        self.component = component
        self.action = action


class BusinessLogicError(WeatherDashboardError):
    """Exception raised when business logic validation fails."""
    
    def __init__(self, message: str, rule: str = None, context: dict = None):
        """Initialize the exception.
        
        Args:
            message: Error message
            rule: Business rule that was violated
            context: Additional context about the error
        """
        super().__init__(message, "BUSINESS_LOGIC_ERROR", context)
        self.rule = rule