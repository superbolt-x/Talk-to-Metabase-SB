# Table Visualization Settings Documentation

## Overview

Table visualizations display data in a structured tabular format. This documentation covers the essential settings for customizing table appearance and behavior.

## Core Settings

### Card-Level Settings

```json
{
  "card.title": "Monthly Sales Report",
  "card.description": "Sales performance by region",
  "card.hide_empty": true
}
```

### Column Configuration

Controls which columns are displayed and their order:

```json
{
  "table.columns": [
    {
      "name": "region",
      "fieldRef": ["field", 123, null],
      "enabled": true
    },
    {
      "name": "calculated_profit",
      "fieldRef": ["expression", "Profit Margin"],
      "enabled": false
    }
  ]
}
```

**Field Reference Types**:
- `["field", field_id, options]` - Database field
- `["expression", "expression_name"]` - Custom expression
- `["aggregation", index]` - Aggregation result

## Column Formatting

### Column Settings Structure

Use `column_settings` with specific column reference keys:

```json
{
  "column_settings": {
    "[\"ref\",[\"field\",124,null]]": {
      "column_title": "Total Sales",
      "number_style": "currency",
      "currency": "USD",
      "decimals": 2
    },
    "[\"name\",\"Profit Margin\"]": {
      "column_title": "Profit %",
      "number_style": "percent",
      "decimals": 1
    }
  }
}
```

### Number Formatting

```json
{
  "number_style": "currency|percent|decimal|scientific",
  "currency": "USD",
  "currency_style": "symbol|code|name",
  "decimals": 2,
  "prefix": "$",
  "suffix": " USD",
  "show_mini_bar": true
}
```

### Date/Time Formatting

```json
{
  "date_style": "YYYY-MM-DD|MM/DD/YYYY|DD/MM/YYYY|MMMM D, YYYY",
  "time_style": "HH:mm|HH:mm:ss|h:mm A|h:mm:ss A"
}
```

## Conditional Formatting

Apply formatting based on column values:

```json
{
  "table.column_formatting": [
    {
      "columns": ["sales_total"],
      "type": "single",
      "operator": ">",
      "value": 10000,
      "color": "#84BB4C",
      "highlight_row": false
    }
  ]
}
```

**Operators**: `>`, `<`, `>=`, `<=`, `=`, `!=`, `is-null`, `not-null`

## Click Behaviors

### Table-Level Click Behavior

```json
{
  "click_behavior": {
    "type": "link",
    "linkType": "dashboard",
    "targetId": 456
  }
}
```

### Column-Specific Click Behavior

```json
{
  "column_settings": {
    "[\"ref\",[\"field\",123,null]]": {
      "click_behavior": {
        "type": "link",
        "linkType": "url",
        "linkTemplate": "https://example.com/details/{{column:region}}"
      }
    }
  }
}
```

**Click Types**: `crossfilter`, `link`, `none`
**Link Types**: `question`, `dashboard`, `url`

## Complete Example

```json
{
  "card.title": "Sales Performance",
  "table.columns": [
    {
      "name": "region",
      "fieldRef": ["field", 101, null],
      "enabled": true
    },
    {
      "name": "sales_total",
      "fieldRef": ["field", 102, null],
      "enabled": true
    }
  ],
  "column_settings": {
    "[\"ref\",[\"field\",102,null]]": {
      "column_title": "Total Sales",
      "number_style": "currency",
      "currency": "USD",
      "decimals": 0,
      "show_mini_bar": true
    }
  },
  "table.column_formatting": [
    {
      "columns": ["sales_total"],
      "type": "single",
      "operator": ">",
      "value": 50000,
      "color": "#84BB4C"
    }
  ]
}
```

## Column Reference Keys

- Database fields: `[\"ref\",[\"field\",field_id,null]]`
- Expressions: `[\"name\",\"column_name\"]`
- Get field IDs using `get_table_query_metadata` tool