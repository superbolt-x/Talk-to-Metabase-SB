# Metabase Card Parameters Documentation

This document provides comprehensive guidance for working with parameters on native SQL cards in Metabase. Parameters allow users to create interactive filters and dynamic queries that can be customized without editing the SQL code directly.

## Overview

Card parameters in Metabase are automatically generated from template tags in native SQL queries. While parameters can be manually specified via the API, **Metabase typically regenerates parameters automatically based on the `dataset_query.native.template-tags` content**.

### Key Concepts

1. **Template Tags**: SQL-level placeholders that exist within the query text (e.g., `{{variable_name}}`)
2. **Parameters**: UI-level interactive controls that collect user input and feed values to template tags
3. **Automatic Generation**: Metabase automatically creates parameters when template tags are detected in SQL queries
4. **Slug Generation**: Parameter slugs are automatically generated from names - never specify manually
5. **ID Management**: For new parameters, omit ID (auto-generated). For existing parameters, include existing ID.

## Template Tag Syntax

### Variable Tags (Parameters)
```sql
SELECT * FROM orders WHERE status = {{order_status}}
```
- Creates interactive parameter controls
- Users can set values through the UI
- Supports different data types (text, number, date, field filters)

### Optional Filters
```sql
SELECT * FROM products 
WHERE true 
[[AND category = {{category}}]] 
[[AND price > {{min_price}}]]
```
- Square brackets create optional filter sections
- Users can toggle these filters on/off
- Combines with regular template tags for flexible querying

### Snippet References
```sql
SELECT *, {{snippet: common-fields}} FROM table_name
```
- References reusable SQL snippets
- Does not create parameters (snippets are text substitution)

## Parameter Types and Template Tag Mapping

| Template Tag Type | Parameter Type | UI Widget | Description |
|-------------------|----------------|-----------|-------------|
| `text` | `category` | Text input with autocomplete | Default for all new template tags |
| `number` | `number/=` | Number input | For numeric parameters |
| `date` | `date/single` | Date picker | For date parameters |
| `dimension` (Field Filter) | Various | Field-specific widgets | For advanced field filtering |

### Important Notes

- **ALL template tags start as `text` type by default** - there is no automatic type inference
- Template tags are automatically generated from parameters when using the API
- Parameter slugs are automatically generated from names and cannot be manually specified
- For updates, existing parameter IDs must be provided to maintain consistency

## Parameter Structure

### New Parameters (Creation)

```json
{
  "name": "Order Status",
  "type": "category",
  "default": "pending",
  "required": false
}
```

**Auto-generated fields:**
- `id`: Unique UUID-style identifier
- `slug`: URL-friendly identifier from name (e.g., "order_status")
- `target`: Links to template tag (e.g., `["variable", ["template-tag", "order_status"]]`)

### Existing Parameters (Updates)

```json
{
  "id": "existing-parameter-id",  // Must include existing ID
  "name": "Updated Order Status",
  "type": "string/=",
  "default": "active"
}
```

**Required for updates:**
- `id`: Must match existing parameter ID
- Other fields will be updated as specified

## Parameter Types Reference

### String Parameters
- `category`: Basic text input with autocomplete (default)
- `string/=`: Exact match dropdown/input
- `string/!=`: Not equal to
- `string/contains`: Contains text
- `string/does-not-contain`: Does not contain text  
- `string/starts-with`: Starts with text
- `string/ends-with`: Ends with text

### Number Parameters
- `number/=`: Exact number match
- `number/!=`: Not equal to number
- `number/between`: Number range
- `number/>=`: Greater than or equal
- `number/<=`: Less than or equal

### Date Parameters
- `date/single`: Single date picker
- `date/range`: Date range picker
- `date/relative`: Relative dates (last 30 days, etc.)
- `date/month-year`: Month/year picker
- `date/quarter-year`: Quarter/year picker
- `date/all-options`: All date options combined

### Special Parameters
- `id`: For ID/primary key fields
- `boolean/=`: Boolean true/false
- `temporal-unit`: Time bucketing options

## Value Sources

Parameters can get their values from different sources:

### Default Behavior (null)
```json
{
  "values_source_type": null
}
```
Metabase determines values automatically

### Static List
```json
{
  "values_source_type": "static-list",
  "values_source_config": {
    "values": ["Option 1", "Option 2", "Option 3"]
  }
}
```

### From Another Card
```json
{
  "values_source_type": "card",
  "values_source_config": {
    "card_id": 123,
    "value_field": ["field", 456, null],
    "label_field": ["field", 457, null]
  }
}
```

## Examples

### Basic Text Parameter (New)
```json
{
  "name": "Order Status",
  "type": "category", 
  "default": "pending"
}
```

**Generated fields:**
- `id`: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
- `slug`: "order_status"
- `target`: ["variable", ["template-tag", "order_status"]]

**SQL Query:**
```sql
SELECT * FROM orders WHERE status = {{order_status}}
```

### Number Range Parameter (New)
```json
{
  "name": "Price Range",
  "type": "number/between",
  "default": [10, 100]
}
```

**SQL Query:**
```sql
SELECT * FROM products WHERE price BETWEEN {{price_range}}
```

### Date Filter Parameter (New)
```json
{
  "name": "Created Date",
  "type": "date/all-options",
  "default": "past30days"
}
```

**SQL Query:**
```sql
SELECT * FROM orders WHERE {{created_date}}
```

### Multi-Select Parameter with Static Values (New)
```json
{
  "name": "Product Categories",
  "type": "string/=",
  "isMultiSelect": true,
  "values_source_type": "static-list",
  "values_source_config": {
    "values": ["Electronics", "Books", "Clothing"]
  }
}
```

**SQL Query:**
```sql
SELECT * FROM products WHERE category IN ({{product_categories}})
```

### Updating Existing Parameter
```json
{
  "id": "existing-param-uuid",  // Must include existing ID
  "name": "Updated Order Status Filter",
  "type": "string/=",
  "isMultiSelect": true,
  "values_source_type": "static-list",
  "values_source_config": {
    "values": ["pending", "processing", "shipped", "delivered", "cancelled"]
  }
}
```

## API Usage Patterns

### Creating Card with Parameters

```python
parameters = [
    {
        "name": "Date Range",
        "type": "date/all-options", 
        "default": "past30days"
    },
    {
        "name": "Status Filter",
        "type": "string/=",
        "isMultiSelect": true,
        "values_source_type": "static-list",
        "values_source_config": {
            "values": ["active", "pending", "cancelled"]
        }
    }
]

create_card(
    database_id=1,
    query="""
    SELECT * FROM orders 
    WHERE {{date_range}}
    [[AND status IN ({{status_filter}})]]
    """,
    name="Order Analysis",
    parameters=parameters
)
```

### Updating Card Parameters

```python
# First, get existing card to see current parameter IDs
existing_card = get_card_definition(card_id=123)

# Update with existing IDs for parameters you want to keep/modify
updated_parameters = [
    {
        "id": "existing-date-param-id",  # Keep existing date parameter
        "name": "Updated Date Filter",
        "type": "date/range",  # Change type
        "default": ["2024-01-01", "2024-12-31"]
    },
    {
        # New parameter (no ID) 
        "name": "Customer Type",
        "type": "category",
        "default": "all"
    }
]

update_card(
    id=123,
    parameters=updated_parameters
)
```

## Best Practices

### 1. Parameter Naming
```python
# Good - descriptive names
"Date Range"
"Customer Status" 
"Product Category"

# Avoid - technical names
"date_filter"
"param1"
"filter_var"
```

### 2. Provide Sensible Defaults
```json
{
  "default": "past30days",  // For date parameters
  "default": "active",      // For status parameters  
  "default": 10            // For limit parameters
}
```

### 3. Use Optional Filters for Flexibility
```sql
SELECT * FROM products 
WHERE price > 0
[[AND category = {{category}}]]
[[AND brand = {{brand}}]]
[[AND price BETWEEN {{price_min}} AND {{price_max}}]]
```

### 4. Handle Parameter Updates Carefully
```python
# When updating parameters:
# 1. Get current card definition first
# 2. Include existing IDs for parameters you want to keep
# 3. Omit IDs for new parameters
# 4. Parameters not included will be removed
```

## Common Patterns

### 1. Dashboard-Style Filtering
```sql
SELECT 
  date_trunc('day', created_at) as date,
  COUNT(*) as orders,
  SUM(total) as revenue
FROM orders 
WHERE true
  [[AND created_at >= {{start_date}}]]
  [[AND created_at <= {{end_date}}]]
  [[AND status = {{order_status}}]]
  [[AND customer_type = {{customer_type}}]]
GROUP BY 1
ORDER BY 1
```

### 2. Performance Optimization
```sql
SELECT * FROM large_table 
WHERE indexed_column = {{required_filter}}  -- Always required
  [[AND other_column = {{optional_filter}}]]  -- Optional
LIMIT {{limit}}  -- Prevent runaway queries
```

### 3. Multi-Tenant Filtering
```sql
SELECT * FROM data_table
WHERE tenant_id = {{tenant_id}}  -- Security filter
  [[AND category IN ({{categories}})]]
  [[AND {{date_filter}}]]
```

## Validation Rules

### Required Fields
- `name`: Must be non-empty string
- `type`: Must be valid parameter type

### Auto-Generated Fields
- `id`: Generated UUID for new parameters
- `slug`: Generated from name (snake_case)
- `target`: Generated based on slug

### Business Rules
- No duplicate names within the same card
- No duplicate IDs within the same card
- Required parameters must have non-empty default values
- Certain parameter types cannot use `isMultiSelect=true`

## Troubleshooting

### Parameters Not Appearing
1. Check SQL syntax for template tags
2. Verify template tags match parameter slugs
3. Ensure parameters have valid targets

### Parameter Values Not Working  
1. Verify parameter type matches expected data type
2. Check default values are valid for the parameter type
3. Ensure SQL query uses correct template tag syntax

### Update Issues
1. Always include existing IDs for parameters you want to keep
2. Use `get_card_definition` to see current parameter structure
3. Remember that parameters not included in update will be removed

### Template Tag Generation
The system automatically generates template tags from parameters:
- Parameter slug becomes template tag name
- Parameter type determines template tag type
- Parameter ID links parameter to template tag

This documentation provides a comprehensive foundation for working with card parameters in the Talk to Metabase MCP server. The automatic ID and slug generation, combined with proper template tag linking, ensures parameters work seamlessly with Metabase's native SQL functionality.
