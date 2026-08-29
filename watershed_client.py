"""Thin HTTP client for the Watershed Platform API.

Static Bearer API key -- no OAuth. Same "fail()-dict + ClientFail
exception" shape as every other connector this session's *_client.py.
"""
from __future__ import annotations

from typing import Any

import httpx

API_BASE = "https://api.watershedclimate.com"

WATERSHED_NOT_CONNECTED = "WATERSHED_NOT_CONNECTED"
WATERSHED_UNAUTHORIZED = "WATERSHED_UNAUTHORIZED"
WATERSHED_FORBIDDEN = "WATERSHED_FORBIDDEN"
WATERSHED_NOT_FOUND = "WATERSHED_NOT_FOUND"
WATERSHED_RATE_LIMITED = "WATERSHED_RATE_LIMITED"
WATERSHED_BACKEND_ERROR = "WATERSHED_BACKEND_ERROR"
WATERSHED_VALIDATION_FAILED = "WATERSHED_VALIDATION_FAILED"

_MESSAGES = {
    WATERSHED_NOT_CONNECTED: "No Watershed connection found. Connect Watershed first.",
    WATERSHED_UNAUTHORIZED: "Watershed rejected the API key as invalid.",
    WATERSHED_FORBIDDEN: "Watershed rejected this request -- the connected account lacks permission for this resource.",
    WATERSHED_NOT_FOUND: "That Watershed record was not found.",
    WATERSHED_RATE_LIMITED: "Watershed rate-limited this request. Try again shortly.",
    WATERSHED_BACKEND_ERROR: "Watershed's API returned an error.",
    WATERSHED_VALIDATION_FAILED: "Watershed rejected the request as invalid.",
}


class ClientFail(Exception):
    def __init__(self, payload: dict):
        self.payload = payload
        super().__init__(payload.get("message", "Watershed request failed"))


def fail(code: str, detail: str = "") -> dict:
    msg = _MESSAGES.get(code, "Watershed request failed.")
    if detail:
        msg = f"{msg} ({detail})"
    return {"ok": False, "code": code, "message": msg}


async def verify_key(api_key: str) -> dict:
    """Verify an API key works by calling a harmless read endpoint."""
    if not api_key:
        return fail(WATERSHED_VALIDATION_FAILED, "api_key is required")
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(
            f"{API_BASE}/v1/footprints",
            headers={"Authorization": f"Bearer {api_key}"},
            params={"limit": 1},
        )
    if resp.status_code == 401:
        return fail(WATERSHED_UNAUTHORIZED)
    if resp.status_code == 403:
        return fail(WATERSHED_FORBIDDEN)
    if resp.status_code >= 500:
        return fail(WATERSHED_BACKEND_ERROR, f"status {resp.status_code}")
    if resp.status_code >= 400:
        return fail(WATERSHED_VALIDATION_FAILED, f"status {resp.status_code}")
    return {"ok": True}


def _check_status(resp: httpx.Response, action: str) -> Any:
    if resp.status_code == 401:
        raise ClientFail(fail(WATERSHED_UNAUTHORIZED, action))
    if resp.status_code == 403:
        raise ClientFail(fail(WATERSHED_FORBIDDEN, action))
    if resp.status_code == 404:
        raise ClientFail(fail(WATERSHED_NOT_FOUND, action))
    if resp.status_code == 429:
        raise ClientFail(fail(WATERSHED_RATE_LIMITED, action))
    if resp.status_code >= 500:
        raise ClientFail(fail(WATERSHED_BACKEND_ERROR, f"{action}: status {resp.status_code}"))
    if resp.status_code >= 400:
        raise ClientFail(fail(WATERSHED_VALIDATION_FAILED, f"{action}: {resp.text[:300]}"))
    if not resp.content:
        return {}
    try:
        return resp.json()
    except ValueError:
        return {}


async def request(ctx, conn: dict, method: str, path: str, *, params: dict | None = None,
                   json_body: dict | None = None, action: str = "request") -> Any:
    api_key = conn.get("api_key", "")
    if not api_key:
        raise ClientFail(fail(WATERSHED_NOT_CONNECTED))
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.request(
            method, f"{API_BASE}{path}",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            params=params, json=json_body,
        )
    return _check_status(resp, action)
