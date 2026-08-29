"""Pydantic params/result models for Watershed Connector.

All params models are module-scope (V17 federal invariant, same rule as
every other connector this session's schemas.py).
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class NoParams(BaseModel):
    """Explicit empty params model -- V17 disallows untyped handlers."""
    pass


class ConnectionScoped(BaseModel):
    connection_id: str = Field(
        "",
        description="Which connected Watershed account to use (see list_connections). Omit if only one is connected.",
    )


# ──────────────────────────────────────────────────────────────────────────
# Connection -- static Bearer API key, no OAuth
# ──────────────────────────────────────────────────────────────────────────


class ConnectWatershedParams(BaseModel):
    api_key: str = Field("", description="Your Watershed API key (from Organization Settings > API).")
    label: str = Field("", description="Optional friendly label for this connection, e.g. 'Acme Inc Watershed'.")


class ProviderConnection(BaseModel):
    id: str = ""
    label: str = ""


class ProviderConnectionList(BaseModel):
    connections: list[ProviderConnection] = Field(default_factory=list)


class DisconnectWatershedParams(BaseModel):
    connection_id: str = Field(description="Which connection to disconnect (see list_connections).")


class DeleteResult(BaseModel):
    deleted: bool = False
    id: str = ""


# ──────────────────────────────────────────────────────────────────────────
# Reads
# ──────────────────────────────────────────────────────────────────────────


class ListFootprintsParams(ConnectionScoped):
    limit: int = Field(50, ge=1, le=200, description="Maximum footprints to return.")


class FootprintList(BaseModel):
    count: int = 0
    footprints: list[dict] = Field(default_factory=list)


class GetFootprintParams(ConnectionScoped):
    footprint_id: str = Field(description="The Watershed footprint id.")


class FootprintDetail(BaseModel):
    footprint: dict = Field(default_factory=dict)


class ListDatasetsParams(ConnectionScoped):
    limit: int = Field(50, ge=1, le=200, description="Maximum datasets to return.")


class DatasetList(BaseModel):
    count: int = 0
    datasets: list[dict] = Field(default_factory=list)


class ListActivityDataRecordsParams(ConnectionScoped):
    dataset_id: str = Field(description="The Watershed dataset id to list activity data records from.")
    limit: int = Field(50, ge=1, le=200, description="Maximum records to return.")


class ActivityDataRecordList(BaseModel):
    dataset_id: str = ""
    count: int = 0
    records: list[dict] = Field(default_factory=list)


class ListSupplierDataRequestsParams(ConnectionScoped):
    limit: int = Field(50, ge=1, le=200, description="Maximum supplier data requests to return.")


class SupplierDataRequestList(BaseModel):
    count: int = 0
    requests: list[dict] = Field(default_factory=list)


class ListReportsParams(ConnectionScoped):
    limit: int = Field(50, ge=1, le=200, description="Maximum reports to return.")


class ReportList(BaseModel):
    count: int = 0
    reports: list[dict] = Field(default_factory=list)


# ──────────────────────────────────────────────────────────────────────────
# Writes
# ──────────────────────────────────────────────────────────────────────────


class CreateActivityDataRecordParams(ConnectionScoped):
    dataset_id: str = Field(description="The Watershed dataset id to add this activity data record to.")
    fields_json: str = Field(description="JSON object of the record's field values, matching the dataset's schema.")


class UpdateActivityDataRecordParams(ConnectionScoped):
    dataset_id: str = Field(description="The Watershed dataset id the record belongs to.")
    record_id: str = Field(description="The activity data record id to update.")
    fields_json: str = Field(description="JSON object of the field values to change. Only given fields change.")


class WriteResult(BaseModel):
    id: str = ""
    dataset_id: str = ""
    status: str = ""


# ──────────────────────────────────────────────────────────────────────────
# Reports
# ──────────────────────────────────────────────────────────────────────────


class GetEmissionsOverviewParams(ConnectionScoped):
    pass


class EmissionsOverviewReport(BaseModel):
    footprint_count: int = 0
    total_tco2e: float = 0.0
    by_scope: dict[str, float] = Field(default_factory=dict)
