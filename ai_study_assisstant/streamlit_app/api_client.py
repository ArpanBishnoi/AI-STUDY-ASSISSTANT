import requests
from requests.exceptions import ConnectionError as RequestsConnectionError

import api_client
from config import API_BASE_URL


class APIError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def _handle_response(response: requests.Response) -> dict:
    try:
        data = response.json()
    except ValueError:
        data = {}

    if response.ok:
        if isinstance(data, dict) and data.get("error"):
            raise APIError(str(data["error"]), response.status_code)
        return data

    detail = data.get("detail", response.text or "Request failed")
    if isinstance(detail, list):
        detail = "; ".join(str(item) for item in detail)
    raise APIError(str(detail), response.status_code)


def register(username: str, email: str, password: str) -> dict:
    response = requests.post(
        f"{API_BASE_URL}/Register",
        json={"username": username, "email": email, "password": password},
        timeout=30,
    )
    return _handle_response(response)


def login(email: str, password: str) -> dict:
    response = requests.post(
        f"{API_BASE_URL}/Login",
        json={"email": email, "password": password},
        timeout=30,
    )
    return _handle_response(response)


def get_profile(headers: dict) -> dict:
    response = requests.get(
        f"{API_BASE_URL}/profile",
        headers=headers,
        timeout=30,
    )
    return _handle_response(response)


def get_my_pdfs(headers: dict) -> list:
    response = requests.get(
        f"{API_BASE_URL}/my-pdfs",
        headers=headers,
        timeout=30,
    )
    data = _handle_response(response)
    return data.get("your pdfs are", [])


def get_pdf(pdf_id: int, headers: dict) -> list | None:
    response = requests.get(
        f"{API_BASE_URL}/pdf/{pdf_id}",
        headers=headers,
        timeout=30,
    )
    data = _handle_response(response)
    return data.get("here is your pdf")


def upload_pdf(headers: dict, file_bytes: bytes, filename: str) -> dict:
    response = requests.post(
        f"{API_BASE_URL}/upload-pdf",
        headers=headers,
        files={"file": (filename, file_bytes, "application/pdf")},
        timeout=120,
    )
    return _handle_response(response)


def delete_pdf(pdf_id: int, headers: dict) -> dict:
    response = requests.delete(
        f"{API_BASE_URL}/pdf/{pdf_id}",
        headers=headers,
        timeout=30,
    )
    return _handle_response(response)


def rename_pdf(pdf_id: int, new_title: str, headers: dict) -> dict:
    response = requests.put(
        f"{API_BASE_URL}/pdf/{pdf_id}/rename",
        headers=headers,
        params={"new_title": new_title},
        timeout=30,
    )
    return _handle_response(response)


def is_connection_error(exc: Exception) -> bool:
    return isinstance(exc, RequestsConnectionError)


def summarize_pdf(pdf_id: int, headers: dict) -> dict:
    response = requests.put(
        f"{API_BASE_URL}/SUMMARIZE_PDF",
        headers=headers,
        params={"pdf_id": pdf_id},
        timeout=120,
    )
    return _handle_response(response)
