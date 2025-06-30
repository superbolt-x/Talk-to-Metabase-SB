# Card Parameters Documentation

## Overview

Card parameters provide comprehensive filtering capabilities for Metabase cards, supporting both simple variable filters and advanced field filters that connect directly to database columns.

## 🔑 Critical Distinction: Variable vs Field Filters

### **Simple Variable Filters** (category, number/=, date/single)
- **SQL Usage**: `WHERE column = {{variable_name}}`
- **How it works**: The parameter value gets substituted directly into your SQL
- **You control**: Column name, operator, and SQL structure
- **User provides**: Just the value
- **Example SQL**: `WHERE status = {{order_status}}` → becomes `WHERE status = 'pending'` (quotes included automatically)

### **Field Filters** (string/=, number/between, date/range, etc.)
- **SQL Usage**: `WHERE {{field_filter_name}}`
- **How it works**: Field filters are replaced with BOOLEAN VALUES (true/false) indicating if the condition is met
- **Metabase controls**: Column name, operator, formatting, and SQL structure
- **User provides**: Just the value(s)
- **Example SQL**: `WHERE {{customer_filter}}` → becomes `WHERE true` or `WHERE false` (boolean result)

### **Key Rule**: 
- ✅ **Simple filters**: `WHERE column = {{variable}}`
- ✅ **Field filters**: `WHERE {{field_filter}}`
- ❌ **Never**: `WHERE column = {{field_filter}}` (field filters are booleans, not values!)
- ❌ **Never**: `WHERE column = '{{variable}}'` (don't add extra quotes to text parameters)

## ⚠️ CRITICAL: Common AI Assistant Mistakes to AVOID

### ❌ **WRONG: Adding quotes around parameters**
```sql
-- DON'T DO THIS - WRONG!
CASE 
    WHEN '{{metric_type}}' = 'spend' THEN spend    -- ❌ Extra quotes!
    WHEN '{{metric_type}}' = 'impressions' THEN impressions
END

-- DON'T DO THIS - WRONG!
WHERE channel = '{{channel_param}}'               -- ❌ Double quotes!

-- DON'T DO THIS - WRONG!
WHERE customer_name = {{customer_filter}}         -- ❌ Field filter used as value!
```

### ✅ **CORRECT: Parameters substitute with proper formatting**
```sql
-- CORRECT - Simple variable parameters
CASE 
    WHEN {{metric_type}} = 'spend' THEN spend      -- ✅ No extra quotes!
    WHEN {{metric_type}} = 'impressions' THEN impressions
END

-- CORRECT - Text parameter already includes quotes
WHERE channel = {{channel_param}}                  -- ✅ {{channel_param}} becomes 'Google'

-- CORRECT - Field filter as boolean condition
WHERE {{customer_filter}}                          -- ✅ Becomes true/false
```

## 🎯 How Parameter Substitution Actually Works

### Simple Variable Filters
Parameters substitute their **actual values** with proper formatting:

- **Text parameter**: `{{channel}}` → `'Google'` (quotes included automatically)
- **Number parameter**: `{{limit}}` → `100` (no quotes)
- **Date parameter**: `{{start_date}}` → `'2024-01-01'` (quotes included automatically)

### Field Filters
Parameters substitute **boolean values** indicating if the condition is met:

- `{{customer_filter}}` → `true` (if customer matches filter) or `false`
- `{{date_range}}` → `true` (if date is in range) or `false`
- `{{spend_range}}` → `true` (if spend is in range) or `false`

**Field filters are NOT replaced with the actual filter condition - they become boolean evaluations!**

### **⚡ Performance Tip**: 
**Use field filters instead of multiple simple date filters!**
- ❌ **Less optimal**: `WHERE date >= {{start_date}} AND date <= {{end_date}}`
- ✅ **Much better**: `WHERE {{date_range_filter}}` (single field filter with date/range type)

## Complete SQL Examples

### ✅ **Complete Correct Example**
```sql
SELECT 
    date,
    channel,
    spend,
    impressions,
    CASE 
        WHEN {{metric_type}} = 'spend' THEN spend           -- ✅ Simple variable, no extra quotes
        WHEN {{metric_type}} = 'impressions' THEN impressions
        ELSE spend
    END as selected_metric
FROM reporting.marketing_data
WHERE 1=1
    AND date >= {{start_date}}           -- ✅ Simple date filter (becomes '2024-01-01')
    AND date <= {{end_date}}             -- ✅ Simple date filter
    AND granularity = {{granularity}}    -- ✅ Simple category filter (becomes 'day')
    [[AND {{channel_filter}}]]           -- ✅ Field filter (becomes true/false)
    [[AND {{spend_range}}]]              -- ✅ Field filter (becomes true/false)
ORDER BY date DESC
```

### ❌ **What NOT to do**
```sql
-- DON'T DO THIS:
SELECT * FROM orders 
WHERE customer_name = {{customer_filter}}  -- ❌ Wrong! Field filter is boolean, not a value

-- DON'T DO THIS:
SELECT * FROM orders
WHERE {{start_date}}                       -- ❌ Wrong! Simple variable used as boolean condition

-- DON'T DO THIS:
WHERE status = '{{order_status}}'          -- ❌ Wrong! Double-quoting text parameter

-- DON'T DO THIS:
CASE WHEN '{{metric}}' = 'spend'           -- ❌ Wrong! Extra quotes around parameter
```

### Parameter Configurations

**For the correct SQL above:**

```json
[
  {
    "name": "start_date",
    "type": "date/single",        // Simple filter - just the value
    "default": "2024-01-01"
  },
  {
    "name": "granularity", 
    "type": "category",           // Simple filter - just the value
    "default": "day",
    "ui_widget": "dropdown",
    "values_source": {
      "type": "static",
      "values": ["day", "week", "month"]
    }
  },
  {
    "name": "channel_filter",
    "type": "string/=",           // Field filter - complete condition  
    "field": {
      "database_id": 195,
      "table_id": 49974,
      "field_id": 50705156        // Maps to 'channel' column
    },
    "ui_widget": "dropdown"
  },
  {
    "name": "spend_range",
    "type": "number/between",     // Field filter - complete condition
    "field": {
      "database_id": 195, 
      "table_id": 49974,
      "field_id": 50705153        // Maps to 'spend' column
    },
    "default": [100, 10000]
  }
]
```

### Simple Filters (Variable Targets)

Simple filters work with template tags in SQL queries (e.g., `{{variable_name}}`).

#### Category Parameters (`type: "category"`)
Text-based filtering with various UI options.

**Basic Example:**
```json
{
  "name": "order_status",
  "type": "category",
  "default": "pending"
}
```

**With Dropdown Options:**
```json
{
  "name": "order_status", 
  "type": "category",
  "default": "pending",
  "ui_widget": "dropdown",
  "values_source": {
    "type": "static",
    "values": ["pending", "shipped", "delivered", "cancelled"]
  }
}
```

**With Search from Model:**
```json
{
  "name": "product_category",
  "type": "category", 
  "default": "Electronics",
  "ui_widget": "search",
  "values_source": {
    "type": "card",
    "card_id": 54417,
    "value_field": "category_name"
  }
}
```

#### Number Parameters (`type: "number/="`)
Numeric filtering with input or dropdown options.

**Basic Example:**
```json
{
  "name": "price_limit",
  "type": "number/=",
  "default": 100
}
```

**With Dropdown Options:**
```json
{
  "name": "row_limit",
  "type": "number/=", 
  "default": 50,
  "ui_widget": "dropdown",
  "values_source": {
    "type": "static",
    "values": [10, 25, 50, 100, 500]
  }
}
```

#### Date Parameters (`type: "date/single"`)
Single date selection.

**Example:**
```json
{
  "name": "start_date",
  "type": "date/single",
  "default": "2024-01-01"
}
```

### Field Filter Parameters

Field filters connect directly to database columns and provide advanced filtering operations.

#### String Field Filters

**String Equals (`type: "string/="`):**
```json
{
  "name": "customer_filter",
  "type": "string/=",
  "field": {
    "database_id": 195,
    "table_id": 50112,
    "field_id": 50705149
  },
  "ui_widget": "dropdown",
  "values_source": {
    "type": "connected"
  }
}
```

**String Contains (`type: "string/contains"`):**
```json
{
  "name": "name_search",
  "type": "string/contains",
  "field": {
    "database_id": 195,
    "table_id": 50112, 
    "field_id": 50705150
  },
  "ui_widget": "search",
  "values_source": {
    "type": "connected"
  }
}
```

**Available String Filter Types:**
- `"string/="` - String equals
- `"string/!="` - String is not equal
- `"string/contains"` - String contains 
- `"string/does-not-contain"` - String does not contain
- `"string/starts-with"` - String starts with
- `"string/ends-with"` - String ends with

#### Numeric Field Filters

**Number Equals (`type: "number/="`):**
```json
{
  "name": "spend_equals",
  "type": "number/=",
  "field": {
    "database_id": 195,
    "table_id": 50112,
    "field_id": 50705151
  },
  "default": 1000
}
```

**Number Between (`type: "number/between"`):**
```json
{
  "name": "spend_range",
  "type": "number/between", 
  "field": {
    "database_id": 195,
    "table_id": 50112,
    "field_id": 50705151
  },
  "default": [100, 5000]
}
```

**Available Numeric Filter Types:**
- `"number/="` - Equals
- `"number/!="` - Not equal to
- `"number/between"` - Between (inclusive)
- `"number/>="` - Greater than or equal to
- `"number/<="` - Less than or equal to

#### Date Field Filters

**Date Range (`type: "date/range"`):**
```json
{
  "name": "date_range",
  "type": "date/range",
  "field": {
    "database_id": 195,
    "table_id": 50112,
    "field_id": 50705150
  },
  "default": "2024-01-01~2024-12-31"
}
```

**All Date Options (`type: "date/all-options"`):**
```json
{
  "name": "created_date",
  "type": "date/all-options",
  "field": {
    "database_id": 195,
    "table_id": 50112,
    "field_id": 50705150
  },
  "default": "past30days"
}
```

**Available Date Filter Types:**
- `"date/single"` - Single date picker
- `"date/range"` - Date range picker
- `"date/relative"` - Relative date options (past X days, etc.)
- `"date/all-options"` - Comprehensive date picker with all options
- `"date/month-year"` - Month and year picker
- `"date/quarter-year"` - Quarter and year picker

## UI Widget Options

### For Simple Filters

#### Category Parameters
- **`"input"`** (default): Free text input box
- **`"dropdown"`**: Select from predefined list (requires `values_source`)
- **`"search"`**: Search box with suggestions (requires `values_source`)

#### Number Parameters  
- **`"input"`** (default): Number input box
- **`"dropdown"`**: Select from predefined numbers (requires `values_source`)

#### Date Parameters
- Date picker (no widget options)

### For Field Filters

#### String Field Filters
- **`"dropdown"`** (default): Select from field values 
- **`"search"`**: Search field values

#### Numeric Field Filters
- Input boxes appropriate for the filter type (automatically determined)

#### Date Field Filters  
- Date picker with options based on filter type (automatically determined)

## Value Source Configuration

### Static Lists (`type: "static"`)
Provide a fixed list of options.

```json
{
  "values_source": {
    "type": "static",
    "values": ["option1", "option2", "option3"]
  }
}
```

### Card/Model Sources (`type: "card"`)
Get values from another card or model.

```json
{
  "values_source": {
    "type": "card", 
    "card_id": 54417,
    "value_field": "category_name",
    "label_field": "category_display_name"  // Optional
  }
}
```

### Connected Fields (`type: "connected"`)  
Use actual values from the connected database field (field filters only).

```json
{
"values_source": {
"type": "connected"
}
}
```

**Important**: For connected field filters, Metabase automatically populates values from the database field. The API uses `values_source_type: null` and `values_source_config: {}` to indicate this.

## Default Value Formats

### Simple Filters
- **Category**: String value (`"pending"`)
- **Number**: Numeric value (`100`)
- **Date**: ISO date string (`"2024-01-01"`)

### Field Filters

#### String Field Filters
- **Single value**: String (`"Electronics"`)

#### Numeric Field Filters
- **Single value operations** (`=`, `!=`, `>=`, `<=`): Array with one number (`[100]`)
- **Between operations**: Array with two numbers (`[10, 100]`)

#### Date Field Filters
- **Single date**: ISO date string (`"2024-01-01"`)
- **Date range**: Range string (`"2024-01-01~2024-12-31"`)
- **Relative dates**: Relative string (`"past30days"`, `"thismonth"`)

### Relative Date Examples
```json
{
  "default": "past3days"        // Previous 3 days
}
{
  "default": "past1weeks"       // Previous 1 week  
}
{
  "default": "past1months"      // Previous 1 month
}
{
  "default": "thisyear"         // Current year
}
{
  "default": "next1hours"       // Next 1 hour
}
```

## Complete Examples

### E-commerce Order Filtering
```json
[
  {
    "name": "order_status",
    "type": "category",
    "display_name": "Order Status",
    "default": "pending",
    "ui_widget": "dropdown", 
    "values_source": {
      "type": "static",
      "values": ["pending", "processing", "shipped", "delivered", "cancelled"]
    }
  },
  {
    "name": "customer_filter",
    "type": "string/contains",
    "display_name": "Customer Name Contains",
    "field": {
      "database_id": 195,
      "table_id": 50112,
      "field_id": 50705149
    },
    "ui_widget": "search",
    "values_source": {
      "type": "connected"
    }
  },
  {
    "name": "order_total_range", 
    "type": "number/between",
    "display_name": "Order Total",
    "field": {
      "database_id": 195,
      "table_id": 50112,
      "field_id": 50705151
    },
    "default": [50, 1000]
  },
  {
    "name": "order_date",
    "type": "date/all-options",
    "display_name": "Order Date", 
    "field": {
      "database_id": 195,
      "table_id": 50112,
      "field_id": 50705150
    },
    "default": "past30days"
  }
]
```

### Marketing Campaign Analysis
```json
[
  {
    "name": "date_granularity",
    "type": "category",
    "display_name": "Date Granularity",
    "default": "day",
    "ui_widget": "dropdown",
    "values_source": {
      "type": "static", 
      "values": ["day", "week", "month", "quarter"]
    }
  },
  {
    "name": "campaign_channel",
    "type": "string/=",
    "display_name": "Marketing Channel",
    "field": {
      "database_id": 195,
      "table_id": 50112,
      "field_id": 50705149
    },
    "ui_widget": "dropdown",
    "values_source": {
      "type": "connected"
    }
  },
  {
    "name": "min_spend",
    "type": "number/>=", 
    "display_name": "Minimum Spend",
    "field": {
      "database_id": 195,
      "table_id": 50112,
      "field_id": 50705151
    },
    "default": [1000]
  },
  {
    "name": "analysis_period",
    "type": "date/range",
    "display_name": "Analysis Period",
    "field": {
      "database_id": 195,
      "table_id": 50112, 
      "field_id": 50705150
    },
    "default": "2024-01-01~2024-12-31"
  }
]
```

## Usage Notes

1. **Automatic Processing**: All UUIDs, template tags, targets, and slugs are generated automatically
2. **Name Requirements**: Parameter names must start with a letter and contain only letters, numbers, and underscores
3. **Field Validation**: Field references are validated against the database to ensure they exist
4. **Widget Compatibility**: UI widgets are validated for compatibility with parameter types
5. **Template Tag Generation**: Template tags are automatically created and linked to parameters
6. **SQL Integration**: Use parameter names in SQL queries as `{{parameter_name}}` or `[[AND condition = {{parameter_name}}]]`

## Error Prevention

The system includes comprehensive validation to prevent common errors:
- Field existence validation
- Parameter type and widget compatibility checking  
- Required field validation based on parameter type
- Default value format validation
- Duplicate parameter name detection
- UI widget requirement validation (dropdown/search need value sources)
