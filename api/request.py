import requests
from sentry_sdk.api import capture_exception

from utils.config import CONFIG
from utils.exception import BadRequest, UserNotConnected

BASE_URL = CONFIG["BASE_URL"]
TOKEN = CONFIG["TOKEN"]


def stringify_query_params(params=None):
    if params is None:
        params = {}
    params_length = len(params)
    if params_length == 0:
        return ""

    query_params = "?"
    param_at = 0
    for paramKey in params.keys():
        query_params += f"{paramKey}={params[paramKey]}"
        if param_at < params_length - 1:
            query_params += "&"
        param_at += 1

    return query_params


async def send_request(endpoint, method="GET", params={}, data=None, headers={}, logging=False):
    # Prevent double / between base url and endpoint
    if BASE_URL[-1] == "/":
        if endpoint[0] == "/":
            endpoint = endpoint[1:]

    # stringify query params
    query_params = stringify_query_params(params)

    # final request url
    url = BASE_URL + endpoint + query_params

    # merge default headers and custom ones
    final_headers = {"Content-Type": "application/vnd.api+json", "Token": TOKEN, "User-Type": "Bot", }
    final_headers.update(headers)

    # send request
    if logging:
        print(f"Request: {method} {url} {final_headers} {data}")
    try:
        request = requests.request(method=method, url=url, headers=final_headers, json=data)
    except Exception as e:
        capture_exception(e)
        raise BadRequest("Could not connect to backend", None)

    try:
        response = request.json()
    except ValueError:
        response = request.text

    if logging:
        print(f"Response: {request.status_code} {response}")

    if request.status_code >= 400 or request.status_code <= 600:
        request_info = {"endpoint": f"{method} {url}", "headers": headers, "response": response}
        capture_exception(Exception("Request Error", request_info))

    if 200 <= request.status_code < 300:
        return response
    if (
            type(response) == dict
            and response.get("data", {}).get("attributes", {}).get("error", "") == "user_not_active_web"
    ):
        raise UserNotConnected
    else:
        req_error_message = type(response) == dict and response.get("data", {}).get("attributes", {}).get("error", "")
        error_message = req_error_message or "API error"
        raise BadRequest(error_message, request)
