# Metabase Card Filters Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Variable Types](#variable-types)
4. [Configuration Guide](#configuration-guide)
5. [JSON Schemas](#json-schemas)
6. [Implementation Examples](#implementation-examples)
7. [Validation & Best Practices](#validation--best-practices)

---

## Overview

Card filters enable interactive parameters in Metabase native SQL queries, allowing users to dynamically filter results through UI controls. This document covers implementation through the POST `/api/card/` endpoint.

### Key Benefits
- **Interactive Dashboards**: Enable dynamic filtering across cards
- **User-Friendly Queries**: Transform static SQL into interactive reports  
- **Type Safety**: Automatic validation and appropriate UI controls
- **Performance**: Efficient parameter substitution and caching

---

## Architecture

### Dual Structure Design

Metabase uses two interconnected structures for card filters:

| Structure | Purpose | Scope |
|-----------|---------|-------|
| **Template Tags** | SQL placeholders for parameter substitution | Backend/Query execution |
| **Parameters** | UI controls for user input collection | Frontend/User interface |

### Data Flow
```
User Input → Parameter → Template Tag → SQL Substitution → Query Execution
```

### Linking Mechanism
Parameters connect to template tags through:
- **Shared UUID**: Both structures use the same `id` field
- **Target Mapping**: Parameters reference template tags via `target` array
- **Name Consistency**: Parameter `slug` matches template tag `name`

### ID Generation
Each template tag requires a unique UUID that links it to its corresponding parameter:

- **Format**: Standard UUID v4 format (e.g., `"b9d76a9e-46b7-4c73-a6d6-3645384cbf78"`)
- **Generation**: Client-side generation using `crypto.randomUUID()` or similar
- **Uniqueness**: Must be unique across all template tags in the card
- **Persistence**: Same ID maintained across template tag and parameter updates
- **Linking**: Parameter `id` field must exactly match template tag `id` field

---

## Variable Types

### Type System Overview

| Variable Type | Default Parameter Type | Default UI | Manual Setup Required |
|---------------|----------------------|------------|---------------------|
| **Text** | `category` | Text input with autocomplete | No - auto-created |
| **Number** | `number/=` | Number input | Yes - user must change type |
| **Date** | `date/single` | Date picker | Yes - user must change type |
| **Field Filter** | Varies by field | Field-specific widget | Yes - user must map to field |

### 1. Text Variables
**Default for all new template tags**

- **Template Tag Type**: `"text"`
- **Parameter Type**: `"category"`
- **Use Cases**: String values, categories, status filters, granularity settings
- **UI Options**: Input box, search box, dropdown list
- **Value Sources**: Manual input, custom list, model/question

### 2. Number Variables
**Manually configured by user**

- **Template Tag Type**: `"number"`
- **Parameter Type**: `"number/="`
- **Use Cases**: Limits, IDs, quantities, thresholds
- **UI Options**: Number input, dropdown list
- **Value Sources**: Manual input, custom numeric list

### 3. Date Variables
**Manually configured by user**

- **Template Tag Type**: `"date"`
- **Parameter Type**: `"date/single"`
- **Use Cases**: Date filters, time ranges
- **UI Options**: Date picker (various configurations)
- **Value Sources**: Date picker interface

### 4. Field Filter Variables
**Advanced filtering mapped to database columns**

- **Template Tag Type**: `"dimension"`
- **Parameter Type**: Determined by field type and widget choice
- **Use Cases**: Column-specific filtering with appropriate operators
- **UI Options**: Field-appropriate widgets
- **Value Sources**: Connected fields, custom lists

---

## Configuration Guide

### UI Interface Configuration

#### Text Variables
| Interface | Values Query Type | Use Case | Configuration Required |
|-----------|-------------------|----------|----------------------|
| **Input Box** | `"none"` | Free text entry | None |
| **Search Box** | `"search"` | Searchable suggestions | Card source or custom list |
| **Dropdown List** | `"list"` | Fixed options | Custom list or card source |

#### Number Variables
| Interface | Values Query Type | Use Case | Configuration Required |
|-----------|-------------------|----------|----------------------|
| **Input Box** | `"none"` | Free numeric entry | None |
| **Dropdown List** | `"list"` | Fixed numeric options | Custom numeric list |

#### Field Filter Variables
Interface automatically determined by:
- **Field Type**: String, numeric, or date field
- **Widget Choice**: User-selected filter operation
- **Value Source**: Connected fields or custom lists

### Default Value Configuration

Default values must match the expected format for each parameter type. The format varies significantly based on the parameter type and widget configuration:

#### Text/Category Parameters
```json
{
  "default": "day"               // Simple string value
}
{
  "default": "week"              // Another string example
}
{
  "default": null                // No default value
}
```

#### Number Parameters
```json
{
  "default": 100                 // Single numeric value
}
{
  "default": 0                   // Zero is valid
}
{
  "default": null                // No default value
}
```

#### Date Parameters (Single Date)
```json
{
  "default": "2025-06-08"        // ISO 8601 date string (YYYY-MM-DD)
}
{
  "default": null                // No default value
}
```

#### Field Filter Parameters

**String Field Filters:**
```json
{
  "default": "active"            // String value for exact match
}
{
  "default": null                // No default value
}
```

**Numeric Field Filters:**

*Single Value Operations (=, !=, >=, <=):*
```json
{
  "default": [10]                // Array with single number
}
{
  "default": [100]               // Another single value example
}
{
  "default": [999]               // Larger number example
}
```

*Between Operations:*
```json
{
  "default": [10, 100]           // Array with min and max values
}
```

**Date Field Filters:**

*Single Date:*
```json
{
  "default": "2025-06-08"        // ISO date string
}
```

*Date Range:*
```json
{
  "default": "2025-06-01~2025-06-08"    // Range with tilde separator
}
```

*Open-Ended Ranges:*
```json
{
  "default": "~2025-06-08"       // Before date (no start)
}
{
  "default": "2025-06-01~"       // After date (no end)
}
```

*Relative Date Values:*

**Past Periods:**
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

**Past Periods with Offset:**
```json
{
  "default": "past1weeks-from-2weeks"    // 1 week, starting 2 weeks ago
}
{
  "default": "past3days-from-1weeks"     // 3 days, starting 1 week ago
}
```

**Future Periods:**
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

**Future Periods with Offset:**
```json
{
  "default": "next1hours-from-2hours"    // 1 hour, starting 2 hours from now
}
{
  "default": "next1days-from-1weeks"     // 1 day, starting 1 week from now
}
```

**Current Period Shortcuts:**
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

**Examples:**
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

### Value Source Configuration
```json
{
  "values_query_type": "none"
}
```
- **UI**: Basic input field
- **Use Case**: Free-form entry
- **Configuration**: None required

#### 1. Manual Input (None)
```json
{
  "values_query_type": "list",
  "values_source_type": "static-list",
  "values_source_config": {
    "values": ["option1", "option2", "option3"]
  }
}
```
- **UI**: Dropdown with predefined options
- **Use Case**: Fixed set of known values
- **Configuration**: Array of string values

#### 2. Custom List (Static)
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
- **Configuration**: Card ID and column reference

#### 3. Model/Question Source (Dynamic)
```json
{
  "values_source_type": "card",
  "values_source_config": {
    "values": [],
    "field_id": 123
  }
}
```
- **UI**: Field-appropriate widget
- **Use Case**: Direct field value population
- **Configuration**: Automatic from field mapping

#### 4. Connected Fields (Field Filters Only)

#### String Field Widgets
| Widget Type | Parameter Type | Operator | Use Case |
|-------------|----------------|----------|----------|
| **String** | `string/=` | Exact match | Precise filtering |
| **String is not** | `string/!=` | Exclude match | Negative filtering |
| **String contains** | `string/contains` | Partial match | Text search |
| **String does not contain** | `string/does-not-contain` | Exclude partial | Negative text search |
| **String starts with** | `string/starts-with` | Prefix match | Beginning patterns |
| **String ends with** | `string/ends-with` | Suffix match | Ending patterns |

#### Numeric Field Widgets
| Widget Type | Parameter Type | Operator | Use Case |
|-------------|----------------|----------|----------|
| **Equal to** | `number/=` | Exact match | Specific values |
| **Not equal to** | `number/!=` | Exclude value | Negative filtering |
| **Between** | `number/between` | Range filter | Value ranges |
| **Greater than or equal** | `number/>=` | Minimum value | Lower bounds |
| **Less than or equal** | `number/<=` | Maximum value | Upper bounds |

#### Date Field Widgets
| Widget Type | Parameter Type | Interface | Use Case |
|-------------|----------------|-----------|----------|
| **Month and Year** | `date/month-year` | Month/year picker | Monthly reports |
| **Quarter and Year** | `date/quarter-year` | Quarter/year picker | Quarterly analysis |
| **Single Date** | `date/single` | Single date picker | Specific dates |
| **Date Range** | `date/range` | Start/end picker | Date ranges |
| **Relative Date** | `date/relative` | Relative options | Dynamic dates |
| **All Options** | `date/all-options` | Comprehensive picker | Maximum flexibility |

---

## JSON Schemas

### Template Tags Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Metabase Template Tags",
  "type": "object",
  "patternProperties": {
    "^[a-zA-Z0-9_]+$": {
      "type": "object",
      "properties": {
        "type": {
          "type": "string",
          "enum": ["text", "number", "date", "dimension", "snippet", "card"],
          "description": "Template tag type - all new variables default to 'text'"
        },
        "name": {
          "type": "string",
          "pattern": "^[a-zA-Z0-9_]+$",
          "description": "Variable name from SQL template tag"
        },
        "id": {
          "type": "string",
          "format": "uuid",
          "description": "Unique identifier linking to parameter"
        },
        "display-name": {
          "type": "string",
          "description": "Human-readable name for UI display"
        },
        "required": {
          "type": "boolean",
          "default": false,
          "description": "Whether parameter value is mandatory"
        },
        "default": {
          "oneOf": [
            {"type": "string"},
            {"type": "number"},
            {"type": "array"},
            {"type": "null"}
          ],
          "description": "Default value - format depends on parameter type"
        },
        "widget-type": {
          "type": "string",
          "description": "Override default parameter widget type",
          "enum": [
            "category", "string/=", "string/!=", "string/contains", 
            "string/does-not-contain", "string/starts-with", "string/ends-with",
            "number/=", "number/!=", "number/between", "number/>=", "number/<=",
            "date/single", "date/range", "date/month-year", "date/quarter-year",
            "date/relative", "date/all-options", "none"
          ]
        },
        "dimension": {
          "type": "array",
          "description": "Field mapping for dimension type template tags",
          "items": [
            {"type": "string", "enum": ["field"]},
            {"type": "integer", "description": "Field ID"},
            {"type": ["object", "null"], "description": "Field options"}
          ],
          "minItems": 3,
          "maxItems": 3
        }
      },
      "required": ["type", "name", "id"],
      "additionalProperties": false,
      "allOf": [
        {
          "if": {"properties": {"type": {"const": "dimension"}}},
          "then": {"required": ["dimension"]}
        }
      ]
    }
  },
  "additionalProperties": false
}
```

### Parameters Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Metabase Parameters",
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "id": {
        "type": "string",
        "format": "uuid",
        "description": "Links to template tag ID"
      },
      "type": {
        "type": "string",
        "enum": [
          "category", "string/=", "string/!=", "string/contains",
          "string/does-not-contain", "string/starts-with", "string/ends-with",
          "number/=", "number/!=", "number/between", "number/>=", "number/<=",
          "date/single", "date/range", "date/month-year", "date/quarter-year", 
          "date/relative", "date/all-options"
        ],
        "description": "UI widget type"
      },
      "target": {
        "type": "array",
        "description": "Links parameter to template tag",
        "oneOf": [
          {
            "description": "Variable target for basic template tags",
            "items": [
              {"type": "string", "enum": ["variable"]},
              {
                "type": "array",
                "items": [
                  {"type": "string", "enum": ["template-tag"]},
                  {"type": "string", "description": "Template tag name"}
                ],
                "minItems": 2,
                "maxItems": 2
              }
            ],
            "minItems": 2,
            "maxItems": 2
          },
          {
            "description": "Dimension target for field filter template tags",
            "items": [
              {"type": "string", "enum": ["dimension"]},
              {
                "type": "array", 
                "items": [
                  {"type": "string", "enum": ["template-tag"]},
                  {"type": "string", "description": "Template tag name"}
                ],
                "minItems": 2,
                "maxItems": 2
              }
            ],
            "minItems": 2,
            "maxItems": 2
          }
        ]
      },
      "name": {
        "type": "string",
        "description": "UI label text"
      },
      "slug": {
        "type": "string",
        "pattern": "^[a-zA-Z0-9_]+$",
        "description": "URL-friendly parameter name"
      },
      "required": {
        "type": "boolean",
        "default": false,
        "description": "UI validation requirement"
      },
      "default": {
        "oneOf": [
          {"type": "string"},
          {"type": "number"},
          {"type": "array"},
          {"type": "null"}
        ],
        "description": "Default UI value"
      },
      "values_query_type": {
        "type": "string",
        "enum": ["none", "list", "search"],
        "description": "How values are populated in UI"
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
                "items": {"type": "string"},
                "description": "Static list of values"
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
          },
          {
            "description": "Connected field configuration",
            "properties": {
              "values": {
                "type": "array",
                "description": "Connected field values"
              },
              "field_id": {
                "type": "integer",
                "description": "Connected field ID"
              }
            },
            "additionalProperties": true
          }
        ]
      }
    },
    "required": ["id", "type", "target", "name", "slug"],
    "additionalProperties": false,
    "allOf": [
      {
        "if": {
          "properties": {
            "values_query_type": {"enum": ["list", "search"]}
          }
        },
        "then": {
          "required": ["values_source_type", "values_source_config"]
        }
      }
    ]
  }
}
```

---

## Implementation Examples

### Basic Examples

#### Example 1: Simple Text Input
```json
{
  "dataset_query": {
    "type": "native",
    "native": {
      "query": "SELECT * FROM users WHERE status = {{user_status}}",
      "template-tags": {
        "user_status": {
          "type": "text",
          "name": "user_status",
          "id": "uuid-1",
          "display-name": "User Status",
          "required": false,
          "default": null
        }
      }
    }
  },
  "parameters": [
    {
      "id": "uuid-1",
      "type": "category", 
      "target": ["variable", ["template-tag", "user_status"]],
      "name": "User Status",
      "slug": "user_status",
      "required": false,
      "values_query_type": "none"
    }
  ]
}
```

#### Example 2: Number Parameter
```json
{
  "dataset_query": {
    "type": "native",
    "native": {
      "query": "SELECT * FROM products LIMIT {{row_limit}}",
      "template-tags": {
        "row_limit": {
          "type": "number",
          "name": "row_limit",
          "id": "uuid-2",
          "display-name": "Row Limit", 
          "required": true,
          "default": 100
        }
      }
    }
  },
  "parameters": [
    {
      "id": "uuid-2",
      "type": "number/=",
      "target": ["variable", ["template-tag", "row_limit"]],
      "name": "Row Limit",
      "slug": "row_limit",
      "required": true,
      "default": 100,
      "values_query_type": "none"
    }
  ]
}
```

#### Example 3: Date Parameter
```json
{
  "dataset_query": {
    "type": "native",
    "native": {
      "query": "SELECT * FROM orders WHERE created_at >= {{start_date}}",
      "template-tags": {
        "start_date": {
          "type": "date",
          "name": "start_date",
          "id": "uuid-3",
          "display-name": "Start Date",
          "required": false,
          "default": null
        }
      }
    }
  },
  "parameters": [
    {
      "id": "uuid-3", 
      "type": "date/single",
      "target": ["variable", ["template-tag", "start_date"]],
      "name": "Start Date",
      "slug": "start_date",
      "required": false,
      "values_query_type": "none"
    }
  ]
}
```

### Advanced Examples

#### Example 4: Text with Custom List
```json
{
  "dataset_query": {
    "type": "native", 
    "native": {
      "query": "SELECT * FROM orders WHERE status = {{order_status}}",
      "template-tags": {
        "order_status": {
          "type": "text",
          "name": "order_status", 
          "id": "uuid-4",
          "display-name": "Order Status",
          "required": false,
          "default": null
        }
      }
    }
  },
  "parameters": [
    {
      "id": "uuid-4",
      "type": "category",
      "target": ["variable", ["template-tag", "order_status"]],
      "name": "Order Status",
      "slug": "order_status", 
      "required": false,
      "values_query_type": "list",
      "values_source_type": "static-list",
      "values_source_config": {
        "values": ["pending", "shipped", "delivered", "cancelled"]
      }
    }
  ]
}
```

#### Example 5: Text with Model Source
```json
{
  "dataset_query": {
    "type": "native",
    "native": {
      "query": "SELECT * FROM products WHERE category = {{product_category}}",
      "template-tags": {
        "product_category": {
          "type": "text",
          "name": "product_category",
          "id": "uuid-5", 
          "display-name": "Product Category",
          "required": false,
          "default": null
        }
      }
    }
  },
  "parameters": [
    {
      "id": "uuid-5",
      "type": "category",
      "target": ["variable", ["template-tag", "product_category"]],
      "name": "Product Category", 
      "slug": "product_category",
      "required": false,
      "values_query_type": "search",
      "values_source_type": "card",
      "values_source_config": {
        "card_id": 54417,
        "value_field": ["field", "category_name", {"base-type": "type/Text"}]
      }
    }
  ]
}
```

### Field Filter Examples

#### Example 6: String Field Filter
```json
{
  "dataset_query": {
    "type": "native",
    "native": {
      "query": "SELECT * FROM orders WHERE {{customer_filter}}",
      "template-tags": {
        "customer_filter": {
          "type": "dimension",
          "name": "customer_filter",
          "id": "uuid-6",
          "display-name": "Customer Filter",
          "dimension": ["field", 123, null],
          "widget-type": "string/="
        }
      }
    }
  },
  "parameters": [
    {
      "id": "uuid-6",
      "type": "string/=",
      "target": ["dimension", ["template-tag", "customer_filter"]],
      "name": "Customer Filter",
      "slug": "customer_filter",
      "values_source_type": "card",
      "values_source_config": {
        "values": [],
        "field_id": 123
      }
    }
  ]
}
```

#### Example 7: Numeric Range Filter
```json
{
  "dataset_query": {
    "type": "native",
    "native": {
      "query": "SELECT * FROM products WHERE {{price_filter}}",
      "template-tags": {
        "price_filter": {
          "type": "dimension",
          "name": "price_filter", 
          "id": "uuid-7",
          "display-name": "Price Filter",
          "dimension": ["field", 456, null],
          "widget-type": "number/between"
        }
      }
    }
  },
  "parameters": [
    {
      "id": "uuid-7",
      "type": "number/between",
      "target": ["dimension", ["template-tag", "price_filter"]],
      "name": "Price Filter",
      "slug": "price_filter"
    }
  ]
}
```

#### Example 8: Date Filter with All Options
```json
{
  "dataset_query": {
    "type": "native",
    "native": {
      "query": "SELECT * FROM orders WHERE {{date_filter}}",
      "template-tags": {
        "date_filter": {
          "type": "dimension",
          "name": "date_filter",
          "id": "uuid-8", 
          "display-name": "Date Filter",
          "dimension": ["field", 789, null],
          "widget-type": "date/all-options"
        }
      }
    }
  },
  "parameters": [
    {
      "id": "uuid-8",
      "type": "date/all-options",
      "target": ["dimension", ["template-tag", "date_filter"]],
      "name": "Date Filter",
      "slug": "date_filter"
    }
  ]
}
```

---

## Validation & Best Practices

### Validation Rules

#### Template Tag Validation
- **Name Pattern**: Must match `^[a-zA-Z0-9_]+$`
- **Type Defaults**: All new variables default to `"text"` type
- **Required Fields**: 
  - `"dimension"` type requires `dimension` field
  - `"snippet"` type requires `snippet-name` field
  - `"card"` type requires `card-id` field
- **ID Format**: Must be valid UUID

#### Parameter Validation
- **Target Mapping**: Must correctly reference template tag
- **Type Compatibility**: Parameter type must match template tag capabilities
- **Value Source Logic**: 
  - `values_query_type: "list"` requires `values_source_config`
  - `values_query_type: "search"` requires card reference
  - `values_query_type: "none"` should not have `values_source_config`

#### Cross-Validation
- **ID Consistency**: Template tag ID must match parameter ID exactly
- **ID Format**: Must be valid UUID v4 format
- **ID Uniqueness**: IDs must be unique within the card's template tags
- **Name Consistency**: Template tag name should match parameter slug
- **Target Accuracy**: Parameter target must correctly reference template tag
- **Database Consistency**: Field filters must reference fields from query's database

### Best Practices

#### Naming Conventions
- Use descriptive, snake_case names for template tags
- Keep display names user-friendly and concise
- Ensure slug matches template tag name exactly

#### ID Management
- Generate UUIDs client-side using `crypto.randomUUID()` or equivalent
- Maintain consistent IDs between template tags and parameters
- Ensure ID uniqueness within each card
- Preserve IDs when updating existing parameters

#### Performance Optimization
- Use static lists for small, fixed value sets (< 100 items)
- Use card sources for dynamic or large value sets
- Avoid field filters on high-cardinality fields without search

#### User Experience
- Set sensible defaults for required parameters
- Choose appropriate widgets based on expected value count
- Use search boxes for high-cardinality value sources
- Group related parameters logically in UI

#### Error Prevention
- Validate field references before saving
- Ensure referenced cards/models remain accessible
- Test parameter behavior with various input types
- Verify SQL syntax with parameter substitution

#### Security Considerations
- Validate all parameter inputs to prevent SQL injection
- Ensure field filters respect database permissions
- Limit value source queries to prevent performance issues
- Use appropriate parameter types to enforce data validation