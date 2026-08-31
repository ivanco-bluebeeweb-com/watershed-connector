"""Connection management for Watershed Connector: connect/disconnect/list.

Static Bearer API key -- verified synchronously against a harmless read
endpoint at connect time. No refresh logic needed (no expiry).
"""
from __future__ import annotations

import json
import uuid

from imperal_sdk import ActionResult

import watershed_client as ws
from app import chat
from schemas import (
    NoParams,
    ConnectWatershedParams,
    ProviderConnection, ProviderConnectionList,
    DisconnectWatershedParams, DeleteResult,
)

_SECRET_NAME = "watershed_connections"


async def _load_connections(ctx) -> list[dict]:
    raw = await ctx.secrets.get(_SECRET_NAME)
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except (TypeError, ValueError):
        return []
    return data if isinstance(data, list) else []


async def _save_connections(ctx, connections: list[dict]) -> None:
    await ctx.secrets.set(_SECRET_NAME, json.dumps(connections))


async def resolve_connection(ctx, connection_id: str = "") -> dict | None:
    connections = await _load_connections(ctx)
    if not connections:
        return None
    if connection_id:
        for c in connections:
            if c.get("id") == connection_id:
                return c
        return None
    return connections[0]


async def resolve_or_error(ctx, connection_id: str = ""):
    conn = await resolve_connection(ctx, connection_id)
    if not conn:
        return None, ActionResult.error(
            "No Watershed connection found. Connect Watershed first.",
            code="WATERSHED_NOT_CONNECTED",
        )
    return conn, None


@chat.function(
    "connect_watershed",
    "Connect your own Watershed account by saving your API key (from Organization Settings > API), after "
    "checking it actually works.",
    action_type="write", chain_callable=True, data_model=ProviderConnection,
    event="watershed-connector.connect_watershed", effects=["create:connection"],
)
async def connect_watershed(ctx, params: ConnectWatershedParams) -> ActionResult:
    """Verify and save a Watershed API key."""
    check = await ws.verify_key(params.api_key)
    if not check.get("ok"):
        return ActionResult.error(check.get("message", "Could not verify the Watershed API key."), code=check.get("code", "WATERSHED_UNAUTHORIZED"))
    connections = await _load_connections(ctx)
    conn_id = str(uuid.uuid4())
    connections.append({"id": conn_id, "label": params.label, "api_key": params.api_key})
    await _save_connections(ctx, connections)
    return ActionResult.success(ProviderConnection(id=conn_id, label=params.label or "Watershed connection"), summary="Watershed connected.")


@chat.function(
    "list_connections",
    "List the connected Watershed accounts.",
    action_type="read", chain_callable=True, data_model=ProviderConnectionList,
)
async def list_connections(ctx, params: NoParams) -> ActionResult:
    """List saved Watershed connections."""
    connections = await _load_connections(ctx)
    rows = [ProviderConnection(id=c.get("id", ""), label=c.get("label") or "Watershed connection") for c in connections]
    return ActionResult.success(ProviderConnectionList(connections=rows), summary="Connections listed.")


@chat.function(
    "disconnect_watershed",
    "Disconnect a Watershed account: deletes the saved API key. Nothing in Watershed itself is changed.",
    action_type="write", chain_callable=True, data_model=DeleteResult,
    event="watershed-connector.disconnect_watershed", effects=["delete:connection"],
)
async def disconnect_watershed(ctx, params: DisconnectWatershedParams) -> ActionResult:
    """Delete a saved Watershed connection."""
    connections = await _load_connections(ctx)
    remaining = [c for c in connections if c.get("id") != params.connection_id]
    if len(remaining) == len(connections):
        return ActionResult.error("That Watershed connection was not found.", code="WATERSHED_NOT_CONNECTED")
    await _save_connections(ctx, remaining)
    return ActionResult.success(DeleteResult(deleted=True, id=params.connection_id), summary="Watershed disconnected.")
