from rest_framework.renderers import JSONRenderer


class StandardizedJSONRenderer(JSONRenderer):


    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None
        status_code = getattr(response, "status_code", 200)

        success = 200 <= status_code < 400

        # Default placeholders
        message = ""
        data_field = None
        error_details = None

        if isinstance(data, dict):
            if "message" in data and isinstance(data["message"], str):
                message = data.pop("message")

            # Handle different error scenarios
            if not success:
                if status_code == 400 and self._is_validation_error(data):
                    message = "Validation error occurred."
                    error_details = self._format_validation_error(data)
                else:
                    # Handle other error types (403, 401, 404, etc.)
                    if "detail" in data:
                        message = str(data["detail"])
                        error_details = data
                    else:
                        error_details = data
            else:
                data_field = data
        else:
            # Non-dict data (e.g. list, string, etc.)
            if success:
                data_field = data
            else:
                if isinstance(data, str):
                    message = data
                error_details = data

        standardized = {
            "success": success,
            "statusCode": status_code,
            "message": message,
        }

        if success:
            standardized["Data"] = data_field
        else:
            standardized["errorDetails"] = error_details

        return super().render(standardized, accepted_media_type, renderer_context)

    def _is_validation_error(self, data):
        if not isinstance(data, dict):
            return False
        
        for key, value in data.items():
            if key != "detail" and isinstance(value, (list, str)):
                return True
        return False

    def _format_validation_error(self, data):
        for field, errors in data.items():
            if field != "detail":
                if isinstance(errors, list) and errors:
                    error_message = str(errors[0])
                elif isinstance(errors, str):
                    error_message = errors
                else:
                    error_message = "Invalid value."
                
                return {
                    "field": field,
                    "message": error_message
                }
        
        return {
            "field": "unknown",
            "message": "Validation error occurred."
        } 