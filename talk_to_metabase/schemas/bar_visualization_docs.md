# Bar Chart Visualization Settings Documentation

## Overview

Bar charts display data using rectangular bars where the length of each bar is proportional to the value it represents. This documentation covers the essential settings for customizing bar chart appearance and behavior.

## Core Settings

### Card-Level Settings

```json
{
  "card.title": "Sales by Region",
  "card.description": "Quarterly sales performance",
  "card.hide_empty": true
}
```

### Required Configuration

```json
{
  "graph.dimensions": ["Region"],
  "graph.metrics": ["Total Sales", "Profit"]
}
```

**Required Fields**:
- `graph.dimensions` - X-axis dimensions (categories, 1-2 fields)
- `graph.metrics` - Y-axis metrics (measures to display as bars)

## Stacking Options

```json
{
  "stackable.stack_type": null|"stacked"|"normalized"
}
```

- `null` - Side-by-side bars for multiple series
- `"stacked"` - Stack bars on top of each other
- `"normalized"` - Stack bars as percentages (100% stacked)

## Axes Configuration

### X-Axis Settings

```json
{
  "graph.x_axis.scale": "ordinal|linear|timeseries|log|pow",
  "graph.x_axis.title_text": "Sales Region",
  "graph.x_axis.axis_enabled": true|"compact"|"rotate-45"|"rotate-90",
  "graph.x_axis.labels_enabled": true
}
```

### Y-Axis Settings

```json
{
  "graph.y_axis.scale": "linear|log|pow",
  "graph.y_axis.title_text": "Sales Amount ($)",
  "graph.y_axis.auto_range": true,
  "graph.y_axis.min": 0,
  "graph.y_axis.max": 100000,
  "graph.y_axis.auto_split": false,
  "graph.y_axis.unpin_from_zero": false
}
```

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

- `"total"` - Show total stack value only
- `"series"` - Show individual series values
- `"all"` - Show both individual and total values

## Series Configuration

### Individual Series Settings

```json
{
  "series_settings": {
    "Total Sales": {
      "display": "bar|line|area",
      "color": "#509EE3",
      "name": "Sales",
      "axis": "left|right"
    }
  }
}
```

### Series Order and Visibility

```json
{
  "graph.series_order": [
    {
      "key": "Revenue",
      "enabled": true,
      "color": "#509EE3",
      "name": "Total Revenue"
    },
    {
      "key": "Profit",
      "enabled": false,
      "color": "#88BF4D"
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
  "graph.other_category_color": "#CCCCCC",
  "graph.other_category_aggregation_fn": "sum|avg|count|min|max"
}
```

## Visual Options

### Tooltips

```json
{
  "graph.tooltip_type": "series_comparison|default",
  "graph.tooltip_columns": ["Product Name", "Sales Rep"]
}
```

### Trend Lines

```json
{
  "graph.show_trendline": true
}
```

## Column Formatting

```json
{
  "column_settings": {
    "[\"name\",\"Total Sales\"]": {
      "number_style": "currency",
      "currency": "USD",
      "currency_style": "symbol",
      "decimals": 0
    },
    "[\"name\",\"Region\"]": {
      "column_title": "Sales Region"
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
    "targetId": 123,
    "parameterMapping": {
      "region_filter": {
        "id": "region_filter",
        "source": {
          "type": "column",
          "id": "Region",
          "name": "Region"
        },
        "target": {
          "type": "parameter",
          "id": "region_filter"
        }
      }
    }
  }
}
```

## Complete Examples

### Simple Bar Chart

```json
{
  "card.title": "Sales by Region",
  "graph.dimensions": ["Region"],
  "graph.metrics": ["Total Sales"],
  "graph.show_values": true,
  "graph.x_axis.title_text": "Sales Region",
  "graph.y_axis.title_text": "Sales Amount ($)",
  "series_settings": {
    "Total Sales": {
      "color": "#509EE3",
      "name": "Sales"
    }
  },
  "column_settings": {
    "[\"name\",\"Total Sales\"]": {
      "number_style": "currency",
      "currency": "USD",
      "decimals": 0
    }
  }
}
```

### Stacked Bar Chart

```json
{
  "card.title": "Revenue vs Profit by Quarter",
  "graph.dimensions": ["Quarter"],
  "graph.metrics": ["Revenue", "Profit"],
  "stackable.stack_type": "stacked",
  "graph.show_values": true,
  "graph.show_stack_values": "series",
  "series_settings": {
    "Revenue": {
      "color": "#509EE3",
      "name": "Total Revenue"
    },
    "Profit": {
      "color": "#88BF4D",
      "name": "Net Profit"
    }
  }
}
```

### Horizontal Bar Chart with Rotated Labels

```json
{
  "graph.dimensions": ["Product Category"],
  "graph.metrics": ["Units Sold"],
  "graph.x_axis.axis_enabled": "rotate-45",
  "graph.show_values": true,
  "graph.label_value_formatting": "compact",
  "series_settings": {
    "Units Sold": {
      "color": "#F9CF48"
    }
  }
}
```

## Common Patterns

### Simple Category Comparison
```json
{
  "graph.dimensions": ["category"],
  "graph.metrics": ["value"],
  "graph.x_axis.scale": "ordinal"
}
```

### Time-Based Bar Chart
```json
{
  "graph.dimensions": ["date"],
  "graph.metrics": ["sales"],
  "graph.x_axis.scale": "timeseries"
}
```

### Multi-Series Comparison
```json
{
  "graph.dimensions": ["region"],
  "graph.metrics": ["current_year", "previous_year"],
  "stackable.stack_type": null
}
```