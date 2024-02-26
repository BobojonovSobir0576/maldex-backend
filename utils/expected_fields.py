from utils.responses import bad_request_response

def check_required_key(request, expected_fields):
    received_fields = set(request.data.keys())
    unexpected_fields = received_fields - expected_fields
    if unexpected_fields:
        return unexpected_fields