# Row Chart Visualization Settings Documentation

## Overview

Row charts (horizontal bar charts) display data using horizontal bars where the length represents the value. They're particularly useful for comparing categories with long names or when you have many categories to display.

## Core Settings

### Card-Level Settings

```json
{
  "card.title": "Top Products by Sales",
  "card.description": "Horizontal bar chart showing product performance",
  "card.hide_empty": true
}
```

### Required Configuration

```json
{
  "graph.dimensions": ["product_name"],
  "graph.metrics": ["total_sales"]
}
```

**Required Fields**:
- `graph.dimensions` - Y-axis dimensions (categories, 1-2 fields)
- `graph.metrics` - X-axis metrics (measures displayed as bar length)

## Axes Configuration

### X-Axis (Values)

```json
{
  "graph.x_axis.scale": "linear|log|pow",
  "graph.x_axis.title_text": "Sales Revenue",
  "graph.x_axis.auto_range": true,
  "graph.x_axis.min": 0,
  "graph.x_axis.max": 100000,
  "graph.x_axis.unpin_from_zero": false
}
```

### Y-Axis (Categories)

```json
{
  "graph.y_axis.scale": "ordinal",
  "graph.y_axis.title_text": "Product",
  "graph.y_axis.axis_enabled": true|"compact"|"rotate-45"|"rotate-90"
}
```

## Stacking Options

```json
{
  "stackable.stack_type": null|"stacked"|"normalized"
}
```

- `null` - Side-by-side bars for multiple series
- `"stacked"` - Stack bars horizontally
- `"normalized"` - Stack bars as percentages

## Value Display

### Show Values on Bars

```json
{
  "graph.show_values": true,
  "graph.label_value_frequency": "fit|all",
  "graph.label_value_formatting": "auto|compact|full"
}
```

### Stack Value Display

```json
{
  "graph.show_stack_values": "total|series|all"
}
```

## Series Configuration

### Individual Series Settings

```json
{
  "series_settings": {
    "total_sales": {
      "display": "bar",
      "color": "#509EE3",
      "name": "Sales"
    }
  }
}
```

### Series Order and Visibility

```json
{
  "graph.series_order": [
    {
      "key": "revenue",
      "enabled": true,
      "color": "#84BB4C",
      "name": "Revenue"
    },
    {
      "key": "expenses",
      "enabled": true,
      "color": "#ED6E6E",
      "name": "Expenses"
    }
  ]
}
```

## Category Management

For charts with many categories:

```json
{
  "graph.max_categories_enabled": true,
  "graph.max_categories": 10,
  "graph.other_category_color": "#CCCCCC"
}
```

## Goal Lines

```json
{
  "graph.goal_value": 50000,
  "graph.goal_label": "Target",
  "graph.show_goal": true
}
```

## Visual Options

### Tooltips

```json
{
  "graph.tooltip_type": "series_comparison|default",
  "graph.tooltip_columns": ["additional_field"]
}
```

### Legend

```json
{
  "legend.is_reversed": false
}
```

## Column Formatting

```json
{
  "column_settings": {
    "[\"name\",\"total_sales\"]": {
      "number_style": "currency",
      "currency": "USD",
      "currency_style": "symbol",
      "decimals": 0
    },
    "[\"name\",\"product_name\"]": {
      "column_title": "Product"
    }
  }
}
```

## Click Behaviors

```json
{
  "click_behavior": {
    "type": "link",
    "linkType": "dashboard",
    "targetId": 42,
    "parameterMapping": {
      "product_filter": {
        "id": "product_filter",
        "source": {
          "type": "column",
          "id": "product_name",
          "name": "Product Name"
        },
        "target": {
          "type": "parameter",
          "id": "product_filter"
        }
      }
    }
  }
}
```

## Complete Examples

### Simple Product Performance

```json
{
  "card.title": "Top Products by Sales",
  "graph.dimensions": ["product_name"],
  "graph.metrics": ["total_sales"],
  "graph.x_axis.title_text": "Sales Revenue",
  "graph.y_axis.title_text": "Product",
  "graph.show_values": true,
  "graph.label_value_formatting": "compact",
  "series_settings": {
    "total_sales": {
      "color": "#509EE3",
      "name": "Sales"
    }
  },
  "column_settings": {
    "[\"name\",\"total_sales\"]": {
      "number_style": "currency",
      "currency": "USD",
      "decimals": 0
    }
  }
}
```

### Department Performance Comparison

```json
{
  "card.title": "Department Performance",
  "graph.dimensions": ["department"],
  "graph.metrics": ["revenue", "expenses"],
  "stackable.stack_type": "stacked",
  "graph.show_values": true,
  "graph.show_stack_values": "total",
  "graph.max_categories_enabled": true,
  "graph.max_categories": 10,
  "series_settings": {
    "revenue": {
      "color": "#84BB4C",
      "name": "Revenue"
    },
    "expenses": {
      "color": "#ED6E6E",
      "name": "Expenses"
    }
  },
  "graph.goal_value": 50000,
  "graph.goal_label": "Target",
  "graph.show_goal": true
}
```

### Regional Sales with Categories

```json
{
  "graph.dimensions": ["region"],
  "graph.metrics": ["q1_sales", "q2_sales"],
  "graph.max_categories_enabled": true,
  "graph.max_categories": 8,
  "graph.other_category_color": "#CCCCCC",
  "series_settings": {
    "q1_sales": {
      "color": "#509EE3",
      "name": "Q1 Sales"
    },
    "q2_sales": {
      "color": "#88BF4D",
      "name": "Q2 Sales"
    }
  }
}
```

## Common Patterns

### Top N Analysis
```json
{
  "graph.dimensions": ["category"],
  "graph.metrics": ["value"],
  "graph.max_categories_enabled": true,
  "graph.max_categories": 10
}
```

### Performance vs Target
```json
{
  "graph.dimensions": ["department"],
  "graph.metrics": ["actual_sales"],
  "graph.goal_value": 75000,
  "graph.show_goal": true
}
```

### Multi-Metric Comparison
```json
{
  "graph.dimensions": ["team"],
  "graph.metrics": ["current_month", "previous_month"],
  "stackable.stack_type": null
}
```