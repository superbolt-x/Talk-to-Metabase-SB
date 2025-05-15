"""
Data models for Metabase entities.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class MetabaseEntity(BaseModel):
    """Base class for all Metabase entities."""
    
    id: int
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        """Pydantic config."""
        
        populate_by_name = True
        extra = "allow"


class Dashboard(MetabaseEntity):
    """Metabase Dashboard model."""
    
    collection_id: Optional[int] = None
    collection_name: Optional[str] = None
    creator_id: Optional[int] = None
    parameters: List[Dict[str, Any]] = Field(default_factory=list)
    ordered_cards: List[Dict[str, Any]] = Field(default_factory=list)


class Card(MetabaseEntity):
    """Metabase Card (Question) model."""
    
    collection_id: Optional[int] = None
    collection_name: Optional[str] = None
    database_id: Optional[int] = None
    table_id: Optional[int] = None
    dataset_query: Dict[str, Any] = Field(default_factory=dict)
    display: str = "table"
    visualization_settings: Dict[str, Any] = Field(default_factory=dict)
    creator_id: Optional[int] = None


class Collection(MetabaseEntity):
    """Metabase Collection model."""
    
    location: Optional[str] = None
    namespace: Optional[str] = None
    slug: Optional[str] = None
    color: Optional[str] = None
    personal_owner_id: Optional[int] = None
    parent_id: Optional[int] = None


class Database(MetabaseEntity):
    """Metabase Database model."""
    
    engine: str
    features: List[str] = Field(default_factory=list)
    is_sample: bool = False
    is_on_demand: bool = False
    tables: List[Dict[str, Any]] = Field(default_factory=list)


class Table(MetabaseEntity):
    """Metabase Table model."""
    
    db_id: int
    schema: Optional[str] = None
    display_name: str
    fields: List[Dict[str, Any]] = Field(default_factory=list)
    field_values: Optional[Dict[str, Any]] = None


class Field(BaseModel):
    """Metabase Field model."""
    
    id: int
    name: str
    display_name: str
    description: Optional[str] = None
    base_type: str
    semantic_type: Optional[str] = None
    has_field_values: Optional[str] = None
    fingerprint: Optional[Dict[str, Any]] = None


class QueryResults(BaseModel):
    """Metabase Query Results model."""
    
    rows: List[List[Any]] = Field(default_factory=list)
    columns: List[str] = Field(default_factory=list)
    cols: List[Dict[str, Any]] = Field(default_factory=list)
    data: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    context: Optional[str] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    json_query: Optional[Dict[str, Any]] = None
