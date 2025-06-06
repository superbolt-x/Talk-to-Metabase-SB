# Combo Chart Visualization Settings Documentation

## Overview

Combo charts combine multiple visualization types (lines, bars, areas) in a single chart, often with dual Y-axes to compare metrics with different scales. This documentation covers the essential settings for customizing combo chart appearance and behavior.

## Core Settings

### Card-Level Settings

```json
{
  "card.title": "Sales & Order Volume Trends",
  "card.description": "Revenue (bars) and order count (line)",
  "card.hide_empty": true
}
```

### Required Configuration

```json
{
  "graph.dimensions": ["created_at"],
  "graph.metrics": ["sum_of_total", "count"]
}
```

**Required Fields**:
- `graph.dimensions` - X-axis dimensions (1-3 fields)
- `graph.metrics` - Y-axis metrics (different series to combine)

## Series Configuration

### Individual Series Settings

The key to combo charts is configuring each series with different display types:

```json
{
  "series_settings": {
    "sum_of_total": {
      "display": "bar",
      "axis": "left",
      "color": "#509EE3",
      "name": "Revenue"
    },
    "count": {
      "display": "line",
      "axis": "right",
      "color": "#88BF4D",
      "name": "Order Count",
      "line.marker_enabled": true,
      "line.interpolate": "linear"
    }
  }
}
```

**Display Types**:
- `"bar"` - Bar series
- `"line"` - Line series
- `"area"` - Area series

**Axis Assignment**:
- `"left"` - Left Y-axis (primary)
- `"right"` - Right Y-axis (secondary)

### Line Series Options

```json
{
  "line.interpolate": "linear|cardinal|step-before|step-after",
  "line.marker_enabled": true,
  "line.missing": "interpolate|zero|none"
}
```

## Dual Axes Configuration

### Auto-Split Axes

```json
{
  "graph.y_axis.auto_split": true
}
```

When enabled, automatically creates dual axes for series with different scales.

### Manual Axis Configuration

```json
{
  "graph.y_axis.scale": "linear|log|pow",
  "graph.y_axis.title_text": "Revenue ($)",
  "graph.y_axis.auto_range": true,
  "graph.y_axis.min": 0,
  "graph.y_axis.max": 100000
}
```

### X-Axis Settings

```json
{
  "graph.x_axis.scale": "linear|timeseries|ordinal|log|pow",
  "graph.x_axis.title_text": "Month",
  "graph.x_axis.axis_enabled": true|"compact"|"rotate-45"|"rotate-90"
}
```

## Stacking Options

For bar and area series:

```json
{
  "stackable.stack_type": null|"stacked"|"normalized"
}
```

- `null` - No stacking (default)
- `"stacked"` - Stack compatible series
- `"normalized"` - Percentage stacking

## Visual Options

### Value Display

```json
{
  "graph.show_values": true,
  "graph.label_value_frequency": "fit|all",
  "graph.label_value_formatting": "auto|compact|full",
  "graph.show_stack_values": "total|series|all"
}
```

### Goal Lines

```json
{
  "graph.goal_value": 100000,
  "graph.goal_label": "Target Revenue",
  "graph.show_goal": true
}
```

### Tooltips

```json
{
  "graph.tooltip_type": "series_comparison|default",
  "graph.tooltip_columns": ["additional_field"]
}
```

### Trend Lines

```json
{
  "graph.show_trendline": true
}
```

## Series Order and Visibility

```json
{
  "graph.series_order": [
    {
      "key": "revenue",
      "enabled": true,
      "color": "#509EE3",
      "name": "Total Revenue"
    },
    {
      "key": "orders",
      "enabled": true,
      "color": "#88BF4D",
      "name": "Order Count"
    }
  ]
}
```

## Column Formatting

```json
{
  "column_settings": {
    "[\"name\",\"sum_of_total\"]": {
      "number_style": "currency",
      "currency": "USD",
      "currency_style": "symbol",
      "decimals": 0
    },
    "[\"name\",\"count\"]": {
      "number_style": "decimal",
      "decimals": 0,
      "suffix": " orders"
    }
  }
}
```

## Click Behaviors

```json
{
  "click_behavior": {
    "type": "crossfilter",
    "parameterMapping": {
      "quarter_filter": {
        "id": "quarter_filter",
        "source": {
          "type": "column",
          "id": "quarter",
          "name": "Quarter"
        },
        "target": {
          "type": "parameter",
          "id": "quarter_filter"
        }
      }
    }
  }
}
```

## Complete Examples

### Revenue and Orders Over Time

```json
{
  "card.title": "Sales & Order Volume Trends",
  "graph.dimensions": ["created_at"],
  "graph.metrics": ["sum_of_total", "count"],
  "graph.x_axis.title_text": "Month",
  "graph.y_axis.title_text": "Revenue ($)",
  "graph.y_axis.auto_split": true,
  "series_settings": {
    "sum_of_total": {
      "display": "bar",
      "axis": "left",
      "color": "#509EE3",
      "name": "Revenue"
    },
    "count": {
      "display": "line",
      "axis": "right",
      "color": "#88BF4D",
      "name": "Order Count",
      "line.marker_enabled": true
    }
  },
  "column_settings": {
    "[\"name\",\"sum_of_total\"]": {
      "number_style": "currency",
      "currency": "USD",
      "decimals": 0
    }
  }
}
```

### Multi-Series Performance Dashboard

```json
{
  "card.title": "Quarterly Performance",
  "graph.dimensions": ["quarter"],
  "graph.metrics": ["revenue", "profit", "expenses"],
  "series_settings": {
    "revenue": {
      "display": "bar",
      "axis": "left",
      "color": "#509EE3"
    },
    "profit": {
      "display": "line",
      "axis": "left",
      "color": "#84BB4C",
      "line.marker_enabled": true
    },
    "expenses": {
      "display": "area",
      "axis": "left",
      "color": "#ED6E6E"
    }
  },
  "graph.goal_value": 100000,
  "graph.goal_label": "Target Revenue",
  "graph.show_goal": true
}
```

### Bar-Line Combination with Stacking

```json
{
  "graph.dimensions": ["region"],
  "graph.metrics": ["current_sales", "previous_sales", "growth_rate"],
  "stackable.stack_type": "stacked",
  "series_settings": {
    "current_sales": {
      "display": "bar",
      "axis": "left",
      "color": "#509EE3"
    },
    "previous_sales": {
      "display": "bar", 
      "axis": "left",
      "color": "#88BF4D"
    },
    "growth_rate": {
      "display": "line",
      "axis": "right",
      "color": "#F9CF48",
      "line.marker_enabled": true
    }
  }
}
```

## Common Patterns

### Revenue vs Quantity
```json
{
  "graph.dimensions": ["date"],
  "graph.metrics": ["revenue", "quantity"],
  "series_settings": {
    "revenue": {"display": "bar", "axis": "left"},
    "quantity": {"display": "line", "axis": "right"}
  }
}
```

### Actual vs Target vs Trend
```json
{
  "graph.dimensions": ["month"],
  "graph.metrics": ["actual", "target", "trend"],
  "series_settings": {
    "actual": {"display": "bar", "axis": "left"},
    "target": {"display": "line", "axis": "left"},
    "trend": {"display": "area", "axis": "left"}
  }
}
```

### KPI Dashboard
```json
{
  "graph.dimensions": ["period"],
  "graph.metrics": ["sales", "conversion_rate"],
  "graph.y_axis.auto_split": true,
  "series_settings": {
    "sales": {"display": "bar", "axis": "left"},
    "conversion_rate": {"display": "line", "axis": "right"}
  }
}
```