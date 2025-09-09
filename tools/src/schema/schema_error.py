class SchemaError(Exception):
    """Base exception for all schema-related errors.

    This exception is intended to be the parent class for more specific
    schema-related errors, such as missing keys or invalid values.
    Catching this exception will handle any type of schema issue.
    """
    def __init__(self, message: str) -> None:
        """
        Initializes the base SchemaError.

        Args:
            message (str): A clear, human-readable error message.
        """
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"SchemaError: {self.message}"

class SchemaKeyError(SchemaError):
    """
    Exception raised when a required key is missing from the schema.

    This exception should be used when a schema is missing a non-optional
    field or a specific dictionary key that is necessary for the program's
    functionality.
    """
    def __init__(self, message: str, key: str | None = None, field: str | None = None) -> None:
        """
        Initializes the SchemaKeyError.

        Args:
            message (str): A clear, human-readable error message.
            key (str | None): The name of the missing key, if applicable.
            field (str | None): The name of the field where the key is absent, if applicable.
        """
        self.key = key
        self.field = field
        
        super_message = message
        if key and field:
            super_message = f"Missing key '{key}' in field '{field}'. {message}"
        elif key:
            super_message = f"Missing key '{key}'. {message}"
        elif field:
            super_message = f"Missing a required key in field '{field}'. {message}"
        
        super().__init__(super_message)

    def __str__(self) -> str:
        base_message = f"SchemaKeyError: {self.message}"
        
        if self.key and self.field:
            return f"SchemaKeyError: Missing key '{self.key}' in field '{self.field}'. {self.message}"
        if self.key:
            return f"SchemaKeyError: Missing key '{self.key}'. {self.message}"
        if self.field:
            return f"SchemaKeyError: Missing key in field '{self.field}'. {self.message}"
        
        return base_message
    
class SchemaValueError(SchemaError):
    """
    Exception raised when a field's value is invalid.

    This exception should be used when a field exists in the schema but
    its value is of the wrong type, out of the expected range, or otherwise
    invalid according to the schema's rules.
    """
    def __init__(self, message: str, field: str | None = None, value=None) -> None:
        """
        Initializes the SchemaValueError.

        Args:
            message (str): A clear, human-readable error message.
            field (str | None): The name of the field with the invalid value, if applicable.
            value: The invalid value itself, for debugging and logging.
        """
        self.field = field
        self.value = value
        super().__init__(message)

    def __str__(self) -> str:
        value_str = f" with value '{self.value}'" if self.value is not None else ""
        if self.field:
            return f"SchemaValueError: Invalid value for field '{self.field}'{value_str}. {self.message}"
        return f"SchemaValueError: {self.message}"