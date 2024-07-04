from http.client import METHOD_NOT_ALLOWED
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError, MethodNotAllowed
from http import HTTPStatus
from typing import Any
from rest_framework.views import Response
# def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response:

def custom_exception_handler(exc, context):
    """Custom API exception handler."""

    # Call REST framework's default exception handler first,
    # to get the standard error response.
    #import pdb; pdb.set_trace();
    response = exception_handler(exc, context)
    if response is not None:
        # Using the description's of the HTTPStatus class as error message.
        # import pdb; pdb.set_trace();
        exception_class=exc.__class__.__name__
        http_code_to_message = {v.value: v.description for v in HTTPStatus}
        status_code = response.status_code
        
        if "InvalidToken" in exception_class and exc.status_code==401:
            response.data={
                "error": {
                    "statusCode": status_code,
                    "message": "Token is invalid or expired",
                }
            }
            return response
        elif "NotAuthenticated" in exception_class:
            response.data={
                "error": {
                    "statusCode": status_code,
                    "message": "Authentication credentials were not provided.",
                }
            }
            return response
        elif "PermissionDenied" in exception_class:
            response.data={
                "error": {
                    "statusCode": status_code,
                    "message": "You do not have permission to perform this action.",
                }
            }
            return response
        elif "AuthenticationFailed" in exception_class:
            response.data={
                "error": {
                    "statusCode": status_code,
                    "message": "User not found with this details.",
                }
            }
            return response
        elif "ValidationError" in exception_class:
            for key, value in response.data.items():
                if 'error' in key:
                    response.data={
                        "error": {
                            "statusCode": status_code,
                            "message": response.data['error'][0]
                        }
                    }
                    return response
            response.data={
                "error": {
                    "statusCode": status_code,
                    "message": "One or more parameter values are invalid!!",
                    "details": response.data,
                }
            }
            return response
        elif "NotFound" in exception_class:
            response.data={
                "error": {
                    "statusCode": status_code,
                    "message": ["Resource does not exists at the given URL."],
                }
            }
            return response
        elif "ParseError" in exception_class:
            response.data={
                "error": {
                    "statusCode": status_code,
                    "message": response.data['detail'],
                }
            }
            return response
        elif "MethodNotAllowed" in exception_class:
            response.data={
                "error": {
                    "statusCode": status_code,
                    "message": response.data['detail'],
                }
            }
            return response
        else:
            error_payload = {
                "error": {
                    "statusCode": status_code,
                    "message": response.data,
                }
            }
            error = error_payload["error"]

            error["statusCode"] = status_code
            error["message"] = http_code_to_message[status_code]
            error["details"] = response.data
            response.data = error_payload
        return response