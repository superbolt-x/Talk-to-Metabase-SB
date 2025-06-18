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
- Supports different data types (text, number, date)

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

### Important Notes

- **ALL template tags start as `text` type by default** - there is no automatic type inference
- Template tags are automatically generated from parameters when using the API
- Parameter slugs are automatically generated from names and cannot be manually specified
- For updates, existing parameter IDs must be provided to maintain consistency
- **Field filters are disabled** - only basic variable template tags are supported

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
  "type": "category",
  "default": "active"
}
```

**Required for updates:**
- `id`: Must match existing parameter ID
- Other fields will be updated as specified

## Parameter Types Reference

### Basic Parameter Types (Only)
- `category`: Basic text input with autocomplete (for text template tags)
- `number/=`: Exact number input (for number template tags)
- `date/single`: Single date picker (for date template tags)

**Note**: With field filters disabled, these are the only three parameter types available. All other parameter types have been removed to simplify the system.

## Value Sources

Parameters can get their values from different sources and display them in different UI widgets:

### Default Behavior (null)
```json
{
  "values_source_type": null,
  "values_query_type": "none"    // Creates text input box
}
```
Metabase determines values automatically - creates a simple text input box.

### Static List with Dropdown
```json
{
  "values_source_type": "static-list",
  "values_query_type": "list",     // Creates dropdown widget
  "values_source_config": {
    "values": ["Option 1", "Option 2", "Option 3"]
  }
}
```
Creates a **dropdown list** where users select from predefined options.

### Static List with Search Box
```json
{
  "values_source_type": "static-list",
  "values_query_type": "search",   // Creates search box widget
  "values_source_config": {
    "values": ["Option 1", "Option 2", "Option 3"]
  }
}
```
Creates a **search box** where users can type to filter through predefined options.

### UI Widget Types Summary

| `values_query_type` | UI Widget | Use Case |
|---------------------|-----------|----------|
| `"none"` | Text input box | Free text entry, no predefined values |
| `"list"` | Dropdown | Small set of options, easy selection |
| `"search"` | Search box | Large set of options, searchable |

### Important Rule
**When `values_source_config` is provided, `values_query_type` must be either `"list"` or `"search"`, never `"none"`.**

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

### Number Parameter (New)
```json
{
  "name": "Price Limit",
  "type": "number/=",
  "default": 100
}
```

**SQL Query:**
```sql
SELECT * FROM products WHERE price <= {{price_limit}}
```

### Date Parameter (New)
```json
{
  "name": "Created Date",
  "type": "date/single",
  "default": "2024-01-01"
}
```

**SQL Query:**
```sql
SELECT * FROM orders WHERE created_at >= {{created_date}}
```

### Multi-Select Parameter with Static Values (New)
```json
{
  "name": "Product Categories",
  "type": "category",
  "default": ["Electronics"],
  "isMultiSelect": true,
  "values_source_type": "static-list",
  "values_query_type": "list",
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
  "type": "category",
  "default": ["pending"],
  "isMultiSelect": true,
  "values_source_type": "static-list",
  "values_query_type": "list",
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
        "name": "Date Filter",
        "type": "date/single", 
        "default": "2024-01-01"
    },
    {
        "name": "Status Filter",
        "type": "category",
        "default": ["active"],
        "isMultiSelect": true,
        "values_source_type": "static-list",
        "values_query_type": "list",
        "values_source_config": {
            "values": ["active", "pending", "cancelled"]
        }
    }
]

create_card(
    database_id=1,
    query="""
    SELECT * FROM orders 
    WHERE created_at >= {{date_filter}}
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
        "type": "date/single",
        "default": "2024-06-01"
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
  "default": "2024-01-01",  // For date parameters
  "default": "active",      // For category parameters  
  "default": 10            // For number parameters
}
```

### 3. Use Optional Filters for Flexibility
```sql
SELECT * FROM products 
WHERE price > 0
[[AND category = {{category}}]]
[[AND brand = {{brand}}]]
[[AND price <= {{price_limit}}]]
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
  [[AND created_at >= {{date_filter}}]]
```

## Validation Rules

### Required Fields
- `type`: Must be one of: category, number/=, date/single
- `name`: Parameter name that links to SQL template tag (must match {{tag_name}} in your SQL)
- `default`: Default value for the parameter (REQUIRED - see Default Values section below)

### Auto-Generated Fields
- `id`: Generated UUID for new parameters
- `slug`: Generated from name (snake_case)
- `target`: Generated based on slug (always variable target)

### Business Rules
- No duplicate names within the same card
- No duplicate IDs within the same card
- Required parameters must have non-empty default values
- All parameters use variable targets (field filters disabled)
- **When `values_source_config` is provided, `values_query_type` must be `"list"` or `"search"`, never `"none"`**

## Default Values - Critical Requirement

**IMPORTANT**: All parameters MUST have default values in this simplified system.

### Why Default Values Are Required

In Metabase SQL queries, parameters can be used in two ways:

1. **Direct usage** (requires default): `SELECT * FROM orders WHERE status = {{status}}`
2. **Optional usage** (default not required): `SELECT * FROM orders WHERE true [[AND status = {{status}}]]`

Since this simplified system assumes **direct usage**, all parameters must have default values or queries will fail when no value is provided.

### SQL Query Patterns

```sql
-- ✅ CORRECT: Direct usage with default values required
SELECT * FROM orders 
WHERE status = {{order_status}}        -- Must have default: "pending"
  AND date >= {{start_date}}           -- Must have default: "2024-01-01"
LIMIT {{limit}}                        -- Must have default: 100
```

```sql
-- ❌ INCORRECT: This pattern would require optional syntax (not supported in simplified system)
SELECT * FROM orders 
WHERE true
  [[AND status = {{order_status}}]]    -- Optional syntax - not supported
  [[AND date >= {{start_date}}]]       -- Optional syntax - not supported
```

### Default Value Examples

```json
{
  "name": "order_status",
  "type": "category",
  "default": "pending"           // ✅ String default
},
{
  "name": "min_price",
  "type": "number/=",
  "default": 0                   // ✅ Number default
},
{
  "name": "start_date",
  "type": "date/single",
  "default": "2024-01-01"        // ✅ Date string default
},
{
  "name": "categories",
  "type": "category",
  "isMultiSelect": true,
  "default": ["Electronics"]     // ✅ Array default for multi-select
}
```

### What Happens Without Defaults

If a parameter lacks a default value:
- The SQL query will fail with substitution errors
- Users must provide values before running the query
- Dashboard filters won't work properly
- Query execution will be blocked

### Best Practices for Defaults

1. **Choose sensible defaults**: Pick values that make the query useful immediately
2. **Consider data distribution**: Use common/typical values as defaults
3. **Match data types**: Ensure defaults match the expected SQL data type
4. **Test your defaults**: Verify the query works with default values

## Troubleshooting

### Parameters Not Appearing
1. Check SQL syntax for template tags
2. Verify template tags match parameter slugs
3. Ensure parameters have valid targets (should be variable targets only)

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
- Parameter type determines template tag type (text/number/date)
- Parameter ID links parameter to template tag
- All targets are variable targets (no field filters)

## Limitations

With the simplified parameter system:
- **No field filters**: Only basic variable template tags are supported
- **Limited parameter types**: Only category, number/=, and date/single
- **No complex filtering**: No string contains, date ranges, number ranges, etc.
- **Simplified targets**: All parameters use variable targets only

This simplified approach focuses on basic interactivity while maintaining ease of use and reducing complexity.

This documentation provides a comprehensive foundation for working with the simplified card parameters in the Talk to Metabase MCP server. The automatic ID and slug generation, combined with proper template tag linking, ensures parameters work seamlessly with Metabase's native SQL functionality.
