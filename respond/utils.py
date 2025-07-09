from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


# ======  standardized API response format =======>>
def get_standardized_response(success=True, message="", data=None, status_code=200, error_details=None):
    response_data = {
        "success": success,
        "message": message
    }
    
    if success:
        response_data["statusCode"] = status_code
        if data is not None:
            response_data["Data"] = data
    else:
        if error_details:
            response_data["errorDetails"] = error_details
    
    return Response(response_data, status=status_code)


#=======  success response =========>>
def success_response(message="", data=None, status_code=200):
    return get_standardized_response(
        success=True,
        message=message,
        data=data,
        status_code=status_code
    )


# ===== error response ===========>>
def error_response(message="", error_details=None, status_code=400):
    return get_standardized_response(
        success=False,
        message=message,
        error_details=error_details,
        status_code=status_code
    )


# ==== validation error response from serializer errors ===>>
def validation_error_response(serializer_errors):
    first_field = list(serializer_errors.keys())[0]
    first_error = serializer_errors[first_field][0] if isinstance(serializer_errors[first_field], list) else serializer_errors[first_field]
    
    return Response(serializer_errors, status=status.HTTP_400_BAD_REQUEST)

# ======== Unauthorized and Forbidden responses ===========>>
def unauthorized_response(message="Unauthorized access."):
    return error_response(
        message=message,
        error_details="Authentication credentials were not provided or are invalid.",
        status_code=status.HTTP_401_UNAUTHORIZED
    )

# ======= Forbidden response ===========>>
def forbidden_response(message="You do not have permission to perform this action."):
    return error_response(
        message=message,
        error_details="You must have the required permissions to access this resource.",
        status_code=status.HTTP_403_FORBIDDEN
    )


def not_found_response(message="Resource not found."):
    return error_response(
        message=message,
        error_details="The requested resource does not exist.",
        status_code=status.HTTP_404_NOT_FOUND
    )

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
        'token_type': 'Bearer'
    } 