# define Python user-defined exceptions
class ProtocolError(Exception):
    """
    Base class for other exceptions in protocol.py
    """
    pass


class IntegrityVerificationError(ProtocolError):
    """
    Raised when integrity verification fails
    """
    pass


class AuthenticationError(ProtocolError):
    """
    Raised when authentication fails"
    ""
    pass
