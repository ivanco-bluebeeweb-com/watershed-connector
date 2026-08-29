"""Read layer + activity-data-record writes for Watershed Connector.

Activity data record create/update is included in v1 (unlike some
sibling connectors' write-deferral pattern) because it is Watershed's
own primary documented API use case per PREPARATION.md.
"""
from __future__ import annotations

import json

from imperal_sdk import ActionResult

import watershed_client as ws
from app import chat
from handlers_connection import resolve_or_error
from schemas import (
    ListFootprintsParams, FootprintList,
    GetFootprintParams, FootprintDetail,
    ListDatasetsParams, DatasetList,
    ListActivityDataRecordsParams, ActivityDataRecordList,
    ListSupplierDataRequestsParams, SupplierDataRequestList,
    ListReportsParams, ReportList,
    CreateActivityDataRecordParams, UpdateActivityDataRecordParams, WriteResult,
)


@chat.function(
    "list_footprints",
    "List computed emissions footprints on the connected Watershed account.",
    action_type="read", chain_callable=True, data_model=FootprintList,
)
async def list_footprints(ctx, params: ListFootprintsParams) -> ActionResult:
    """List footprints."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if not conn:
        return err
    data = await ws.request(ctx, conn, "GET", "/v1/footprints", params={"limit": params.limit}, action="list footprints")
    rows = data.get("footprints", data) if isinstance(data, dict) else data
    rows = rows if isinstance(rows, list) else []
    return ActionResult.ok(FootprintList(count=len(rows), footprints=rows))


@chat.function(
    "get_footprint",
    "Read one computed emissions footprint in full by its Watershed footprint id.",
    action_type="read", chain_callable=True, data_model=FootprintDetail,
)
async def get_footprint(ctx, params: GetFootprintParams) -> ActionResult:
    """Read one footprint."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if not conn:
        return err
    data = await ws.request(ctx, conn, "GET", f"/v1/footprints/{params.footprint_id}", action="get footprint")
    return ActionResult.ok(FootprintDetail(footprint=data if isinstance(data, dict) else {}))


@chat.function(
    "list_datasets",
    "List datasets (activity data collections) configured on the connected Watershed account.",
    action_type="read", chain_callable=True, data_model=DatasetList,
)
async def list_datasets(ctx, params: ListDatasetsParams) -> ActionResult:
    """List datasets."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if not conn:
        return err
    data = await ws.request(ctx, conn, "GET", "/v1/datasets", params={"limit": params.limit}, action="list datasets")
    rows = data.get("datasets", data) if isinstance(data, dict) else data
    rows = rows if isinstance(rows, list) else []
    return ActionResult.ok(DatasetList(count=len(rows), datasets=rows))


@chat.function(
    "list_activity_data_records",
    "List activity data records (raw emissions activity data, e.g. utility bills, travel, spend) inside one "
    "Watershed dataset.",
    action_type="read", chain_callable=True, data_model=ActivityDataRecordList,
)
async def list_activity_data_records(ctx, params: ListActivityDataRecordsParams) -> ActionResult:
    """List activity data records in a dataset."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if not conn:
        return err
    data = await ws.request(
        ctx, conn, "GET", f"/v1/datasets/{params.dataset_id}/records",
        params={"limit": params.limit}, action="list activity data records",
    )
    rows = data.get("records", data) if isinstance(data, dict) else data
    rows = rows if isinstance(rows, list) else []
    return ActionResult.ok(ActivityDataRecordList(dataset_id=params.dataset_id, count=len(rows), records=rows))


@chat.function(
    "list_supplier_data_requests",
    "List supplier data requests (Watershed's supplier engagement campaign items) on the connected account.",
    action_type="read", chain_callable=True, data_model=SupplierDataRequestList,
)
async def list_supplier_data_requests(ctx, params: ListSupplierDataRequestsParams) -> ActionResult:
    """List supplier data requests."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if not conn:
        return err
    data = await ws.request(ctx, conn, "GET", "/v1/supplier_data_requests", params={"limit": params.limit}, action="list supplier data requests")
    rows = data.get("requests", data) if isinstance(data, dict) else data
    rows = rows if isinstance(rows, list) else []
    return ActionResult.ok(SupplierDataRequestList(count=len(rows), requests=rows))


@chat.function(
    "list_reports",
    "List climate/ESG reports (GHG Protocol/CDP/TCFD-aligned) on the connected Watershed account.",
    action_type="read", chain_callable=True, data_model=ReportList,
)
async def list_reports(ctx, params: ListReportsParams) -> ActionResult:
    """List reports."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if not conn:
        return err
    data = await ws.request(ctx, conn, "GET", "/v1/reports", params={"limit": params.limit}, action="list reports")
    rows = data.get("reports", data) if isinstance(data, dict) else data
    rows = rows if isinstance(rows, list) else []
    return ActionResult.ok(ReportList(count=len(rows), reports=rows))


@chat.function(
    "create_activity_data_record",
    "Create a new activity data record (e.g. a utility bill, travel record, or spend-based estimate) inside "
    "a Watershed dataset -- Watershed's core way to ingest new emissions activity data.",
    action_type="write", chain_callable=True, data_model=WriteResult,
    event="watershed-connector.create_activity_data_record", effects=["create:resource"],
)
async def create_activity_data_record(ctx, params: CreateActivityDataRecordParams) -> ActionResult:
    """Create an activity data record."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if not conn:
        return err
    try:
        fields = json.loads(params.fields_json) if params.fields_json else {}
    except (TypeError, ValueError):
        return ActionResult.error("fields_json must be valid JSON.", code="WATERSHED_VALIDATION_FAILED")
    data = await ws.request(
        ctx, conn, "POST", f"/v1/datasets/{params.dataset_id}/records",
        json_body=fields, action="create activity data record",
    )
    rid = data.get("id", "") if isinstance(data, dict) else ""
    return ActionResult.ok(WriteResult(id=rid, dataset_id=params.dataset_id, status="created"))


@chat.function(
    "update_activity_data_record",
    "Update selected field values of an existing activity data record. Only the fields in fields_json change.",
    action_type="write", chain_callable=True, data_model=WriteResult,
    event="watershed-connector.update_activity_data_record", effects=["update:resource"],
)
async def update_activity_data_record(ctx, params: UpdateActivityDataRecordParams) -> ActionResult:
    """Update an activity data record."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if not conn:
        return err
    try:
        fields = json.loads(params.fields_json) if params.fields_json else {}
    except (TypeError, ValueError):
        return ActionResult.error("fields_json must be valid JSON.", code="WATERSHED_VALIDATION_FAILED")
    await ws.request(
        ctx, conn, "PATCH", f"/v1/datasets/{params.dataset_id}/records/{params.record_id}",
        json_body=fields, action="update activity data record",
    )
    return ActionResult.ok(WriteResult(id=params.record_id, dataset_id=params.dataset_id, status="updated"))
