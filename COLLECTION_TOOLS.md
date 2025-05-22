# Collection Tools Overview

SuperMetabase now provides two specialized collection tools that work together to provide efficient collection exploration and content viewing.

## Tools

### 1. `explore_collection_tree`
**Purpose**: Navigate the collection hierarchy  
**Shows**: Only child collections + comprehensive content summary  
**Use case**: When you want to browse through the collection structure

**Example Call**:
```json
{
  "name": "explore_collection_tree",
  "arguments": {
    "collection_id": 123
  }
}
```

**Response**:
```json
{
  "collection_id": 123,
  "child_collections": [
    {"id": 456, "name": "Marketing", "model": "collection"},
    {"id": 789, "name": "Sales", "model": "collection"}
  ],
  "content_summary": {
    "dashboard": 18,
    "card": 15,
    "collection": 12,
    "dataset": 3,
    "timeline": 0,
    "snippet": 2,
    "pulse": 1,
    "metric": 0
  }
}
```

### 2. `view_collection_contents`
**Purpose**: View all items in a collection  
**Shows**: All direct children items (with optional filtering)  
**Use case**: When you want to see what's actually inside a collection

**Example Call**:
```json
{
  "name": "view_collection_contents", 
  "arguments": {
    "collection_id": 123,
    "models": ["dashboard", "card"]  // Optional filter
  }
}
```

**Response**:
```json
{
  "collection_id": 123,
  "items": [
    {"id": 101, "name": "Q4 Revenue", "model": "dashboard"},
    {"id": 102, "name": "Sales Analysis", "model": "card"},
    {"id": 103, "name": "Customer Data", "model": "dataset"}
  ],
  "content_summary": {
    "dashboard": 18,
    "card": 15,
    "collection": 12,
    "dataset": 3,
    "timeline": 0,
    "snippet": 2,
    "pulse": 1,
    "metric": 0
  }
}
```

## Typical Usage Flow

1. **Start exploring**: Use `explore_collection_tree` at root level (`collection_id: null`)
2. **Navigate deeper**: Use `explore_collection_tree` with specific collection IDs to see subcollections
3. **View contents**: Use `view_collection_contents` when you want to see all items in a collection
4. **Filter content**: Use `view_collection_contents` with `models` parameter to see specific types

## Key Features

- **Always shows comprehensive summary**: Both tools provide counts for all 8 model types
- **Database filtering**: Database items are automatically filtered out  
- **Simplified responses**: Only essential fields (id, name, model, location) are included
- **Flexible filtering**: `view_collection_contents` supports optional model type filtering
- **Consistent structure**: Both tools use the same response patterns for easy integration

## Model Types Supported

- `dashboard` - Interactive dashboards
- `card` - Questions/queries
- `collection` - Sub-collections  
- `dataset` - Models/datasets
- `timeline` - Timeline events
- `snippet` - SQL snippets
- `pulse` - Automated reports
- `metric` - Business metrics
