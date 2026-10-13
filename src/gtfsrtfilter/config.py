"""Load and validate the service configuration."""
from pathlib import Path
from typing import Any, Literal
import yaml
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator

class AppConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    host: str = "0.0.0.0"
    port: int = Field(default=8080, ge=1, le=65535)

class EntityConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    type: Literal["service-alerts", "trip-updates", "vehicle-positions"]
    source: HttpUrl = Field(alias="from")
    to: str
    filters: list[dict[str, Any]] = Field(default_factory=list)

    @field_validator("to")
    @classmethod
    def validate_path(cls, value: str) -> str:
        if not value.startswith("/") or "?" in value or "#" in value:
            raise ValueError("to must be an absolute HTTP path without query or fragment")
        return value

    @field_validator("filters")
    @classmethod
    def validate_filters(cls, value: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for entry in value:
            if not isinstance(entry, dict) or len(entry) != 1:
                raise ValueError("each filter must be a mapping with exactly one key")
            key, pattern = next(iter(entry.items()))
            if key not in {"agency_id", "route_id", "route_type", "stop_id", "trip_id", "vehicle_id", "include", "exclude"}:
                raise ValueError(f"unknown filter: {key}")
            if not isinstance(pattern, (str, int)) or isinstance(pattern, bool):
                raise ValueError(f"filter {key} must be a string or integer")
        return value

    @model_validator(mode="after")
    def validate_supported(self):
        supported = {
            "service-alerts": {"agency_id", "route_id", "route_type", "stop_id", "trip_id"},
            "trip-updates": {"route_id", "trip_id", "stop_id"},
            "vehicle-positions": {"route_id", "trip_id", "vehicle_id", "include", "exclude"},
        }
        for entry in self.filters:
            key = next(iter(entry))
            if key not in supported[self.type]:
                raise ValueError(f"{key} is not supported for {self.type}")
        return self

class Config(BaseModel):
    model_config = ConfigDict(extra="forbid")
    app: AppConfig = Field(default_factory=AppConfig)
    entities: list[EntityConfig]

    @model_validator(mode="after")
    def unique_paths(self):
        paths = [entity.to for entity in self.entities]
        if len(paths) != len(set(paths)):
            raise ValueError("entity destination paths must be unique")
        return self

def load_config(path: str | Path) -> Config:
    with Path(path).open(encoding="utf-8") as stream:
        raw = yaml.safe_load(stream)
    if not isinstance(raw, dict):
        raise ValueError("configuration must be a YAML mapping")
    return Config.model_validate(raw)
