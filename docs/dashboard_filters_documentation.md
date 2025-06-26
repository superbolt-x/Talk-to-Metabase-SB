# Metabase Dashboard Filters Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Parameter Types](#parameter-types)
4. [Configuration Guide](#configuration-guide)
5. [JSON Schema](#json-schema)
6. [Implementation Examples](#implementation-examples)
7. [Validation & Best Practices](#validation--best-practices)

---

## Overview

Dashboard filters enable interactive parameters in Metabase dashboards, allowing users to filter multiple cards simultaneously through shared UI controls. Unlike card filters, dashboard parameters are created independently and linked to cards later through field mappings.

### Key Benefits
- **Cross-Card Filtering**: Filter multiple dashboard cards with a single parameter
- **Centralized Control**: Manage filtering logic at the dashboard level
- **Flexible Mapping**: Link parameters to different fields across various cards
- **User Experience**: Consistent filtering interface across dashboard

### Key Differences from Card Filters
- **No Template Tags**: Dashboard parameters exist independently of SQL queries
- **Post-Creation Linking**: Parameters are created first, then mapped to card fields
- **Different ID Format**: Uses shorter numeric-style IDs instead of UUIDs
- **Additional Parameter Types**: Time grouping, Date picker, Location, and ID types
- **Enhanced Multi-Select**: Built-in support for multiple value selection

---

## Architecture

### Single Structure Design

Dashboard filters use a simpler architecture than card filters:

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| **Parameters Array** | Standalone parameter definitions | Added to dashboard JSON |
| **Field Mappings** | Links parameters to card fields | Configured after parameter creation |

### Data Flow
```
User Input → Dashboard Parameter → Field Mappings → Card Queries → Results
```

### ID Generation
Dashboard parameters use a different ID format:
- **Format**: Short alphanumeric strings
- **Length**: Exactly 8 characters
- **Characters**: Alphanumeric (letters and numbers)
- **Generation**: Client-side generation using random alphanumeric strings
- **Uniqueness**: Must be unique within the dashboard

---

## Parameter Types

### Type System Overview

| Parameter Type | Type Values | Section ID | Multi-Select Support | Use Cases |
|----------------|-------------|------------|---------------------|-----------|
| **Text** | `string/=`, `string/!=`, `string/contains`, `string/does-not-contain`, `string/starts-with`, `string/ends-with` | `string` | ✅ Yes | String filtering, categories |
| **Number** | `number/=`, `number/!=`, `number/between`, `number/>=`, `number/<=` | `number` | ✅ Yes | Numeric filtering, ranges |
| **Date** | `date/single`, `date/range`, `date/month-year`, `date/quarter-year`, `date/relative`, `date/all-options` | `date` | ❌ No | Date filtering, time ranges |
| **Time Grouping** | `temporal-unit` | `temporal-unit` | ❌ No | Temporal aggregation control |
| **Location** | `string/=` | `location` | ✅ Yes | Geographic filtering |
| **ID** | `id` | `id` | ✅ Yes | Identifier filtering |

### 1. Text Parameters
**String-based filtering with various comparison operators**

- **Type Values**: 
  - `"string/="` - Exact match
  - `"string/!="` - Not equal to
  - `"string/contains"` - Contains text
  - `"string/does-not-contain"` - Does not contain text
  - `"string/starts-with"` - Starts with text
  - `"string/ends-with"` - Ends with text
- **Section ID**: `"string"`
- **Multi-Select**: Available (`isMultiSelect: true/false`)
- **Use Cases**: Categories, status values, text matching with various operators
- **Value Sources**: Custom lists, model/question sources
- **Default Format**: String or array for multi-select

### 2. Number Parameters
**Numeric filtering with comparison and range operators**

- **Type Values**:
  - `"number/="` - Equal to
  - `"number/!="` - Not equal to  
  - `"number/between"` - Between two values
  - `"number/>="` - Greater than or equal to
  - `"number/<="` - Less than or equal to
- **Section ID**: `"number"`
- **Multi-Select**: Available (`isMultiSelect: true/false`)
- **Use Cases**: Numeric ranges, quantities, comparisons
- **Value Sources**: Custom lists, model/question sources
- **Default Format**: Number or array for multi-select and ranges

### 3. Date Parameters
**Date-based filtering with various picker configurations**

- **Type Values**:
  - `"date/single"` - Single date picker
  - `"date/range"` - Date range picker
  - `"date/month-year"` - Month and year picker
  - `"date/quarter-year"` - Quarter and year picker
  - `"date/relative"` - Relative date picker
  - `"date/all-options"` - Comprehensive date picker with all options
- **Section ID**: `"date"`
- **Multi-Select**: Not available
- **Use Cases**: Date filtering, time periods, various temporal granularities
- **Value Sources**: Date picker interface
- **Default Format**: ISO date strings or relative date expressions

### 4. Time Grouping Parameters
**Temporal aggregation control with predefined units**

- **Type Value**: `"temporal-unit"`
- **Section ID**: `"temporal-unit"`
- **Multi-Select**: Not available
- **Use Cases**: Controlling time-based grouping in charts
- **Value Sources**: Predefined temporal units only
- **Available Units**:
  - **Absolute**: `minute`, `hour`, `day`, `week`, `month`, `quarter`, `year`
  - **Relative**: `minute-of-hour`, `hour-of-day`, `day-of-week`, `day-of-month`, `day-of-year`, `week-of-year`, `month-of-year`, `quarter-of-year`

### 5. Location Parameters
**Geographic filtering with location-specific handling**

- **Type Value**: `"string/="`
- **Section ID**: `"location"`
- **Multi-Select**: Available (`isMultiSelect: true/false`)
- **Use Cases**: Geographic filtering, address matching
- **Value Sources**: Custom lists, model/question sources
- **Default Format**: String or array for multi-select

### 6. ID Parameters
**Identifier-based filtering optimized for IDs**

- **Type Value**: `"id"`
- **Section ID**: `"id"`
- **Multi-Select**: Available (`isMultiSelect: true/false`)
- **Use Cases**: Primary keys, foreign keys, unique identifiers
- **Value Sources**: Custom lists, model/question sources
- **Default Format**: String, number, or array for multi-select

---

## Configuration Guide

### Multi-Select Configuration

Dashboard parameters support multi-select functionality for applicable types:

#### Single Value Selection
```json
{
  "isMultiSelect": false
}
```
- **UI**: Dropdown or input allowing one selection
- **Default**: Single value
- **Use Case**: When only one value should be selected

#### Multiple Value Selection
```json
{
  "isMultiSelect": true
}
```
- **UI**: Multi-select dropdown or checkbox interface
- **Default**: Array of values
- **Use Case**: When filtering should include multiple values

#### Supported Types for Multi-Select
- **Text** (`string/=`)
- **Number** (`number/=`)
- **Location** (`string/=`)
- **ID** (`id`)

#### Not Supported for Multi-Select
- **Date** (all date types)
- **Time Grouping** (`temporal-unit`)
- **Date Picker** (all date picker types)

### Value Source Configuration

Dashboard parameters support fewer value source options than card filters:

#### 1. Manual Input (None)
```json
{
  "values_query_type": "none"
}
```
- **UI**: Basic input field
- **Use Case**: Free-form entry
- **Available For**: All parameter types

#### 2. Custom List (Static)
```json
{
  "values_source_type": "static-list",
  "values_source_config": {
    "values": [
      ["option1"],
      ["option2"], 
      ["option3"]
    ]
  }
}
```
- **UI**: Dropdown with predefined options
- **Use Case**: Fixed set of known values
- **Available For**: Text, Number, Location, ID
- **Format**: Array of arrays, each containing a single value

#### 3. Model/Question Source (Dynamic)
```json
{
  "values_query_type": "search",
  "values_source_type": "card",
  "values_source_config": {
    "card_id": 12345,
    "value_field": ["field", "column_name", {"base-type": "type/Text"}]
  }
}
```
- **UI**: Search box with dynamic suggestions
- **Use Case**: Large or changing value sets
- **Available For**: Text, Number, Location, ID

#### 4. Time Grouping (Predefined Units)
```json
{
  "temporal_units": ["minute", "hour", "day", "week"]
}
```
- **UI**: Dropdown with selected temporal units
- **Use Case**: Controlling time aggregation granularity
- **Available For**: Time Grouping parameters only

### Default Value Configuration

Default values follow specific formats based on parameter type and multi-select settings. Dashboard parameters support the same comprehensive default value formats as card filters:

#### Text Parameters
**Single Value:**
```json
{
  "default": "active"
}
```

**Multiple Values:**
```json
{
  "default": ["active", "pending"]
}
```

#### Number Parameters
**Single Value:**
```json
{
  "default": 100
}
{
  "default": 0                   // Zero is valid
}
```

**Multiple Values:**
```json
{
  "default": [10, 50, 100]
}
```

**Range Operations (number/between):**
```json
{
  "default": [10, 100]           // Array with min and max values
}
```

#### Date Parameters
**Single Date:**
```json
{
  "default": "2025-06-08"        // ISO 8601 date string (YYYY-MM-DD)
}
```

**Date Range:**
```json
{
  "default": "2025-06-01~2025-06-08"    // Range with tilde separator
}
```

**Open-Ended Ranges:**
```json
{
  "default": "~2025-06-08"       // Before date (no start)
}
{
  "default": "2025-06-01~"       // After date (no end)
}
```

**Relative Date Values:**

*Past Periods:*
```json
{
  "default": "past3days"         // Previous 3 days
}
{
  "default": "past1weeks"        // Previous 1 week
}
{
  "default": "past1months"       // Previous 1 month
}
{
  "default": "past1quarters"     // Previous 1 quarter
}
{
  "default": "past1years"        // Previous 1 year
}
```

*Past Periods with Offset:*
```json
{
  "default": "past1weeks-from-2weeks"    // 1 week, starting 2 weeks ago
}
{
  "default": "past3days-from-1weeks"     // 3 days, starting 1 week ago
}
```

*Future Periods:*
```json
{
  "default": "next1hours"        // Next 1 hour
}
{
  "default": "next1days"         // Next 1 day
}
{
  "default": "next1weeks"        // Next 1 week
}
{
  "default": "next1months"       // Next 1 month
}
```

*Future Periods with Offset:*
```json
{
  "default": "next1hours-from-2hours"    // 1 hour, starting 2 hours from now
}
{
  "default": "next1days-from-1weeks"     // 1 day, starting 1 week from now
}
```

*Current Period Shortcuts:*
```json
{
  "default": "thisyear"          // Current year
}
{
  "default": "thismonth"         // Current month
}
{
  "default": "thisweek"          // Current week
}
{
  "default": "thisday"           // Today
}
{
  "default": "thishour"          // Current hour
}
```

#### Time Grouping Parameters
```json
{
  "default": "day"               // Absolute temporal units
}
{
  "default": "month"
}
{
  "default": "quarter"
}
{
  "default": "hour-of-day"       // Relative temporal units
}
{
  "default": "day-of-week"
}
{
  "default": "month-of-year"
}
```

#### Location Parameters
**Single Location:**
```json
{
  "default": ["New York"]        // Note: Array format even for single value
}
```

**Multiple Locations:**
```json
{
  "default": ["New York", "San Francisco", "Chicago"]
}
```

#### ID Parameters
**Single ID:**
```json
{
  "default": "12345"             // String format
}
{
  "default": 12345               // Numeric format
}
```

**Multiple IDs:**
```json
{
  "default": ["12345", "67890"]  // String array
}
{
  "default": [12345, 67890]      // Numeric array
}
```

#### Relative Date Format Specification

The relative date format follows this pattern:
```
{direction}{amount}{unit}[-from-{offset}{offsetUnit}]
```

**Components:**
- **Direction**: `past`, `next`, or `this`
- **Amount**: Number (1, 2, 3, etc.)
- **Unit**: `minutes`, `hours`, `days`, `weeks`, `months`, `quarters`, `years`
- **Offset** (optional): `-from-{amount}{unit}` to specify starting point

**Complete Examples:**
```json
{
  "default": "past30minutes"                    // Last 30 minutes
}
{
  "default": "past2hours"                       // Last 2 hours  
}
{
  "default": "past7days"                        // Last 7 days
}
{
  "default": "past4weeks"                       // Last 4 weeks
}
{
  "default": "past6months"                      // Last 6 months
}
{
  "default": "past2quarters"                    // Last 2 quarters
}
{
  "default": "past3years"                       // Last 3 years
}
{
  "default": "next15minutes-from-1hours"        // 15 min, starting 1 hour from now
}
{
  "default": "past1months-from-3months"         // 1 month, starting 3 months ago
}
```

#### No Default Value
For any parameter type, use `null` to indicate no default:
```json
{
  "default": null                // User must provide value
}
```

---

## JSON Schema

### Dashboard Parameters Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Metabase Dashboard Parameters",
  "type": "object",
  "properties": {
    "parameters": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9]{8}$",
            "description": "8-character alphanumeric parameter ID"
          },
          "name": {
            "type": "string",
            "description": "Human-readable parameter name"
          },
          "slug": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9_]+$",
            "description": "URL-friendly parameter name"
          },
          "type": {
            "type": "string",
            "enum": [
              "string/=", "string/!=", "string/contains", "string/does-not-contain",
              "string/starts-with", "string/ends-with", "number/=", "number/!=", 
              "number/between", "number/>=", "number/<=", "date/single", 
              "date/range", "date/month-year", "date/quarter-year", 
              "date/relative", "date/all-options", "temporal-unit", "id"
            ],
            "description": "Parameter widget type"
          },
          "sectionId": {
            "type": "string",
            "enum": ["string", "number", "date", "location", "temporal-unit", "id"],
            "description": "Parameter category for UI grouping"
          },
          "required": {
            "type": "boolean",
            "default": false,
            "description": "Whether parameter value is required"
          },
          "default": {
            "oneOf": [
              {"type": "string"},
              {"type": "number"},
              {"type": "array"},
              {"type": "null"}
            ],
            "description": "Default value - format depends on type and multi-select"
          },
          "isMultiSelect": {
            "type": "boolean",
            "description": "Enable multiple value selection"
          },
          "values_query_type": {
            "type": "string",
            "enum": ["none", "list", "search"],
            "description": "How values are populated"
          },
          "values_source_type": {
            "type": "string",
            "enum": ["static-list", "card"],
            "description": "Source of parameter values"
          },
          "values_source_config": {
            "type": "object",
            "description": "Configuration for value source",
            "oneOf": [
              {
                "description": "Static list configuration",
                "properties": {
                  "values": {
                    "type": "array",
                    "items": {
                      "type": "array",
                      "items": {"type": "string"},
                      "minItems": 1,
                      "maxItems": 1
                    },
                    "description": "Static list of values as array of arrays"
                  }
                },
                "required": ["values"],
                "additionalProperties": false
              },
              {
                "description": "Card source configuration",
                "properties": {
                  "card_id": {
                    "type": "integer",
                    "description": "Source card/model ID"
                  },
                  "value_field": {
                    "type": "array",
                    "items": [
                      {"type": "string", "enum": ["field"]},
                      {"type": "string", "description": "Column name"},
                      {
                        "type": "object",
                        "properties": {
                          "base-type": {
                            "type": "string",
                            "description": "Field base type"
                          }
                        }
                      }
                    ],
                    "minItems": 3,
                    "maxItems": 3,
                    "description": "Field reference for values"
                  }
                },
                "required": ["card_id", "value_field"],
                "additionalProperties": false
              }
            ]
          },
          "temporal_units": {
            "type": "array",
            "items": {
              "type": "string",
              "enum": [
                "minute", "hour", "day", "week", "month", "quarter", "year",
                "minute-of-hour", "hour-of-day", "day-of-week", "day-of-month",
                "day-of-year", "week-of-year", "month-of-year", "quarter-of-year"
              ]
            },
            "description": "Available temporal units for time grouping parameters"
          }
        },
        "required": ["id", "name", "slug", "type", "sectionId"],
        "additionalProperties": false,
        "allOf": [
          {
            "if": {"properties": {"type": {"const": "temporal-unit"}}},
            "then": {"required": ["temporal_units"]}
          },
          {
            "if": {
              "properties": {
                "type": {"enum": ["string/=", "number/=", "id"]}
              }
            },
            "then": {
              "properties": {
                "isMultiSelect": {"type": "boolean"}
              }
            }
          },
          {
            "if": {
              "properties": {
                "sectionId": {"const": "location"}
              }
            },
            "then": {
              "properties": {
                "type": {"const": "string/="},
                "isMultiSelect": {"type": "boolean"}
              }
            }
          }
        ]
      }
    }
  },
  "required": ["parameters"],
  "additionalProperties": false
}
```

---

## Implementation Examples

### Basic Parameter Examples

#### Example 1: Simple Text Parameter
```json
{
  "parameters": [
    {
      "id": "69707443",
      "name": "Status Filter",
      "slug": "status_filter",
      "type": "string/=",
      "sectionId": "string",
      "required": false,
      "isMultiSelect": false,
      "values_query_type": "none"
    }
  ]
}
```

#### Example 2: Multi-Select Text Parameter with Custom List
```json
{
  "parameters": [
    {
      "id": "a1b2c3d4",
      "name": "Categories",
      "slug": "categories",
      "type": "string/=",
      "sectionId": "string",
      "required": false,
      "isMultiSelect": true,
      "default": ["electronics", "books"],
      "values_source_type": "static-list",
      "values_source_config": {
        "values": [
          ["electronics"],
          ["books"],
          ["clothing"],
          ["home"]
        ]
      }
    }
  ]
}
```

#### Example 3: Number Parameter with Multi-Select
```json
{
  "parameters": [
    {
      "id": "n9m8x7z6",
      "name": "Product IDs",
      "slug": "product_ids", 
      "type": "number/=",
      "sectionId": "number",
      "required": true,
      "isMultiSelect": true,
      "default": [100, 200],
      "values_source_type": "card",
      "values_source_config": {
        "card_id": 54321,
        "value_field": ["field", "product_id", {"base-type": "type/Integer"}]
      }
    }
  ]
}
```

#### Example 4: Date Parameter
```json
{
  "parameters": [
    {
      "id": "d5e6f7g8",
      "name": "Date Range",
      "slug": "date_range",
      "type": "date/range",
      "sectionId": "date",
      "required": false,
      "default": "past30days",
      "values_query_type": "none"
    }
  ]
}
```

### Advanced Parameter Examples

#### Example 5: Time Grouping Parameter
```json
{
  "parameters": [
    {
      "id": "f6bf5587",
      "name": "Time Grouping",
      "slug": "time_grouping",
      "type": "temporal-unit",
      "sectionId": "temporal-unit",
      "required": true,
      "default": "day",
      "temporal_units": ["minute", "hour", "day", "week", "month"]
    }
  ]
}
```

#### Example 6: Location Parameter
```json
{
  "parameters": [
    {
      "id": "ea777f91",
      "name": "Location",
      "slug": "location",
      "type": "string/=",
      "sectionId": "location",
      "required": false,
      "isMultiSelect": true,
      "default": ["New York"],
      "values_source_type": "static-list",
      "values_source_config": {
        "values": [
          ["New York"],
          ["San Francisco"],
          ["Chicago"],
          ["Boston"]
        ]
      }
    }
  ]
}
```

#### Example 7: ID Parameter
```json
{
  "parameters": [
    {
      "id": "bae9934a",
      "name": "User IDs",
      "slug": "user_ids",
      "type": "id",
      "sectionId": "id",
      "required": false,
      "isMultiSelect": false,
      "values_source_type": "card",
      "values_source_config": {
        "card_id": 98765,
        "value_field": ["field", "user_id", {"base-type": "type/Text"}]
      }
    }
  ]
}
```

#### Example 8: Complete Time Grouping Configuration
```json
{
  "parameters": [
    {
      "id": "h7i8j9k0",
      "name": "Time Breakdown",
      "slug": "time_breakdown",
      "type": "temporal-unit",
      "sectionId": "temporal-unit",
      "required": false,
      "default": "month",
      "temporal_units": [
        "day",
        "week", 
        "month",
        "quarter",
        "year",
        "day-of-week",
        "month-of-year"
      ]
    }
  ]
}
```

### Dashboard Integration Example

#### Complete Dashboard with Multiple Parameters
```json
{
  "parameters": [
    {
      "id": "str12345",
      "name": "Status",
      "slug": "status",
      "type": "string/=",
      "sectionId": "string",
      "required": false,
      "isMultiSelect": true,
      "default": ["active"],
      "values_source_type": "static-list",
      "values_source_config": {
        "values": [
          ["active"],
          ["inactive"],
          ["pending"]
        ]
      }
    },
    {
      "id": "num67890",
      "name": "Limit",
      "slug": "limit",
      "type": "number/=",
      "sectionId": "number",
      "required": true,
      "isMultiSelect": false,
      "default": 100,
      "values_query_type": "none"
    },
    {
      "id": "dat11111",
      "name": "Date Filter",
      "slug": "date_filter",
      "type": "date/all-options",
      "sectionId": "date",
      "required": false,
      "default": "past30days"
    },
    {
      "id": "tmp22222",
      "name": "Grouping",
      "slug": "grouping",
      "type": "temporal-unit",
      "sectionId": "temporal-unit",
      "required": false,
      "default": "day",
      "temporal_units": ["hour", "day", "week", "month"]
    }
  ]
}
```

---

## Validation & Best Practices

### Validation Rules

#### Parameter Validation
- **ID Format**: Must be exactly 8 character alphanumeric string
- **ID Uniqueness**: IDs must be unique within the dashboard
- **Type/Section Consistency**: `sectionId` must match parameter `type` category
- **Multi-Select Availability**: Only available for Text, Number, Location, and ID types
- **Time Grouping Requirements**: Must include `temporal_units` array
- **Value Source Logic**: Value source configuration must match parameter capabilities
- **Static List Format**: Values must be arrays of arrays `[["value1"], ["value2"]]`

#### Cross-Parameter Validation
- **Slug Uniqueness**: Parameter slugs should be unique within dashboard
- **Name Consistency**: Human-readable names should be descriptive and unique
- **Default Value Format**: Must match parameter type and multi-select setting

#### Type-Specific Validation
- **Time Grouping**: Must use valid temporal units from predefined list
- **Location**: Must use `string/=` type with `location` sectionId
- **ID**: Must use `id` type with `id` sectionId
- **Multi-Select**: Default values must be arrays when `isMultiSelect: true`

### Best Practices

#### ID Generation
- Generate 8-character alphanumeric IDs client-side
- Ensure uniqueness within dashboard scope
- Avoid special characters or spaces
- Use consistent format across all parameters

#### Parameter Design
- Use descriptive names that clearly indicate parameter purpose
- Choose appropriate parameter types for expected data
- Enable multi-select for parameters that benefit from multiple values
- Set sensible defaults to improve user experience

#### Performance Optimization
- Use static lists for small, fixed value sets
- Use card sources for dynamic or large value sets
- Limit the number of parameters per dashboard (5-10 recommended)
- Consider parameter interdependencies for user experience

#### User Experience
- Group related parameters logically
- Use consistent naming conventions across parameters
- Provide helpful default values
- Consider parameter order in the UI

#### Value Source Configuration
- **Static Lists**: Best for < 50 items, stable values
- **Card Sources**: Best for dynamic data, > 50 items
- **No Source**: Best for free-form input, unique values

#### Multi-Select Guidelines
- Enable for categorical data where multiple selections make sense
- Use single-select for mutually exclusive options
- Consider UI space when enabling multi-select
- Provide reasonable default selections

#### Error Prevention
- Validate referenced cards/models remain accessible
- Test parameter behavior across different browsers
- Verify parameter mappings work with intended cards
- Ensure parameter types match expected field types

#### Security Considerations
- Validate all parameter inputs to prevent injection attacks
- Ensure referenced models respect user permissions
- Limit value source queries to prevent performance issues
- Use appropriate parameter types to enforce data validation

This documentation provides complete specifications for implementing Metabase dashboard filters with proper validation, multi-select support, and the new parameter types available in dashboard contexts.