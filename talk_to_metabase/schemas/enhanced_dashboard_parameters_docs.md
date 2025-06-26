# Enhanced Dashboard Parameters Documentation

## Overview

Enhanced dashboard parameters provide comprehensive support for all Metabase dashboard filter types with automatic ID generation, intelligent defaults, and complete validation.

## Key Features

- **Name-Based Identification**: Parameters identified by name, IDs generated automatically
- **Complete Type Support**: All dashboard parameter types supported
- **Multi-Select Support**: Where applicable (string/=, number/=, id, location)
- **Automatic Processing**: sectionId, slug, and configuration generated automatically
- **Comprehensive Validation**: JSON schema + business rule validation
- **Value Sources**: Static lists, card sources, and connected values

## Parameter Types

### Text Parameters
**String-based filtering with various comparison operators**

- `string/=` - Exact match (supports multi-select)
- `string/!=` - Not equal to (supports multi-select)
- `string/contains` - Contains text (supports multi-select)
- `string/does-not-contain` - Does not contain text (supports multi-select)
- `string/starts-with` - Starts with text (supports multi-select)
- `string/ends-with` - Ends with text (supports multi-select)

### Number Parameters
**Numeric filtering with comparison and range operators**

- `number/=` - Equal to (supports multi-select)
- `number/!=` - Not equal to (supports multi-select)
- `number/between` - Between two values (no multi-select, requires array default)
- `number/>=` - Greater than or equal to (no multi-select)
- `number/<=` - Less than or equal to (no multi-select)

### Date Parameters
**Date-based filtering with various picker configurations**

- `date/single` - Single date picker
- `date/range` - Date range picker  
- `date/month-year` - Month and year picker
- `date/quarter-year` - Quarter and year picker
- `date/relative` - Relative date picker
- `date/all-options` - Comprehensive date picker with all options

**Note**: Date parameters do not support multi-select

### Special Parameters

#### Time Grouping (`temporal-unit`)
**Temporal aggregation control with predefined units**

- **Required Field**: `temporal_units` array
- **Available Units**: 
  - Absolute: `minute`, `hour`, `day`, `week`, `month`, `quarter`, `year`
  - Relative: `minute-of-hour`, `hour-of-day`, `day-of-week`, `day-of-month`, `day-of-year`, `week-of-year`, `month-of-year`, `quarter-of-year`

#### ID Parameters (`id`)
**Identifier-based filtering optimized for IDs**

- **Multi-Select**: Supported
- **Use Cases**: Primary keys, foreign keys, unique identifiers

#### Location Parameters
**Geographic filtering with location-specific handling**

- **Type**: `string/=` with `sectionId: "location"`
- **Multi-Select**: Supported
- **Use Cases**: Geographic filtering, address matching

## Value Sources

### Static Lists (`"type": "static"`)
**Predefined list of values**

```json
{
  "values_source": {
    "type": "static",
    "values": ["option1", "option2", "option3"]
  }
}
```

### Card Sources (`"type": "card"`)
**Values from another card/model with search functionality**

```json
{
  "values_source": {
    "type": "card",
    "card_id": 12345,
    "value_field": "column_name",
    "label_field": "display_column_name"
  }
}
```

### Connected Values (`"type": "connected"`)
**Values connected to parameter context**

```json
{
  "values_source": {
    "type": "connected"
  }
}
```

## Default Value Formats

### Text Parameters
**Single Value:**
```json
{"default": "active"}
```

**Multiple Values:**
```json
{"default": ["active", "pending"]}
```

### Number Parameters
**Single Value:**
```json
{"default": 100}
```

**Multiple Values:**
```json
{"default": [10, 50, 100]}
```

**Range (number/between):**
```json
{"default": [10, 100]}
```

### Date Parameters
**Single Date:**
```json
{"default": "2025-06-08"}
```

**Date Range:**
```json
{"default": "2025-06-01~2025-06-08"}
```

**Relative Dates:**
```json
{"default": "past30days"}
{"default": "past1weeks"}
{"default": "thismonth"}
```

### Time Grouping Parameters
```json
{"default": "day"}
{"default": "month"}
{"default": "hour-of-day"}
```

### Location Parameters
```json
{"default": ["New York"]}
{"default": ["New York", "San Francisco"]}
```

### ID Parameters
```json
{"default": "12345"}
{"default": 12345}
{"default": ["12345", "67890"]}
```

## Complete Examples

### Basic Text Filter
```json
{
  "name": "Status Filter",
  "type": "string/=",
  "default": "active",
  "values_source": {
    "type": "static",
    "values": ["active", "inactive", "pending"]
  }
}
```

### Multi-Select Category Filter
```json
{
  "name": "Categories",
  "type": "string/=",
  "isMultiSelect": true,
  "default": ["electronics", "books"],
  "values_source": {
    "type": "static",
    "values": ["electronics", "books", "clothing", "home"]
  }
}
```

### Number Range Filter
```json
{
  "name": "Price Range",
  "type": "number/between",
  "default": [10, 1000]
}
```

### Date Range Filter
```json
{
  "name": "Date Range",
  "type": "date/range",
  "default": "past30days"
}
```

### Time Grouping Parameter
```json
{
  "name": "Time Breakdown",
  "type": "temporal-unit",
  "default": "day",
  "temporal_units": ["hour", "day", "week", "month", "quarter"]
}
```

### Location Filter
```json
{
  "name": "Locations",
  "type": "string/=",
  "sectionId": "location",
  "isMultiSelect": true,
  "default": ["New York"],
  "values_source": {
    "type": "static",
    "values": ["New York", "San Francisco", "Chicago", "Boston"]
  }
}
```

### ID Filter with Card Source
```json
{
  "name": "User IDs",
  "type": "id",
  "isMultiSelect": false,
  "values_source": {
    "type": "card",
    "card_id": 98765,
    "value_field": "user_id",
    "label_field": "user_name"
  }
}
```

### Required Parameter
```json
{
  "name": "Department",
  "type": "string/=",
  "required": true,
  "default": "sales",
  "values_source": {
    "type": "static",
    "values": ["sales", "marketing", "engineering"]
  }
}
```

## Validation Rules

### Required Fields
- `name`: Parameter name (cannot be 'tab')
- `type`: Parameter type from supported list

### Automatic Processing
- `id`: Generated as 8-character alphanumeric if not provided
- `sectionId`: Auto-determined from type unless overridden
- `slug`: Generated from name

### Business Rules
- **Unique Names**: Parameter names must be unique within dashboard
- **Multi-Select Support**: Only available for `string/=`, `number/=`, `id`, and location
- **Temporal Units**: Required for `temporal-unit` parameters
- **Required Parameters**: Must have non-null default values
- **Default Format**: Must match parameter type and multi-select setting
- **Card References**: Validated for accessibility and field existence

### Multi-Select Restrictions
**Supported:**
- All string parameter types (`string/=`, `string/!=`, `string/contains`, `string/does-not-contain`, `string/starts-with`, `string/ends-with`)
- Number equality types (`number/=`, `number/!=`)
- `id`
- Location parameters (uses `string/=` with `sectionId: "location"`)

**Not Supported:**
- All date parameters (`date/single`, `date/range`, `date/month-year`, `date/quarter-year`, `date/relative`, `date/all-options`)
- `temporal-unit`
- Number range/comparison parameters (`number/between`, `number/>=`, `number/<=`)

## Usage Guidelines

### Best Practices
1. **Use descriptive names** - they become the UI labels
2. **Set sensible defaults** - improves user experience
3. **Choose appropriate types** - match expected data patterns
4. **Enable multi-select judiciously** - only when multiple values make sense
5. **Validate card sources** - ensure referenced cards exist and have run

### Performance Considerations
- **Static lists**: Best for < 50 items, stable values
- **Card sources**: Best for dynamic data, > 50 items
- **Connected values**: Best for context-dependent values

### Common Patterns
- **Category filters**: Use `string/=` with static values
- **Date ranges**: Use `date/range` or `date/all-options`
- **Time grouping**: Use `temporal-unit` for chart aggregation control
- **Geographic data**: Use location parameters with static or card values
- **ID lookups**: Use `id` type with card sources for large lists

## Error Prevention

### Parameter Configuration
- Always provide default values for required parameters
- Use array format for multi-select defaults
- Ensure temporal_units array for temporal-unit parameters
- Validate card accessibility before using as value source

### Type Selection
- Choose correct parameter type for your data
- Don't enable multi-select for incompatible types
- Use number/between for ranges, not multi-select number/=
- Use appropriate date picker for your use case

### Value Sources
- Verify card sources have result metadata (have been run)
- Check field names exist in referenced cards
- Use static lists for small, stable value sets
- Use card sources for dynamic or large value sets

This documentation provides complete specifications for implementing enhanced dashboard parameters with proper validation, multi-select support, and all parameter types available in Metabase dashboard contexts.