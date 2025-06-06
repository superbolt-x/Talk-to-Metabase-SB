# Line Chart Visualization Settings Documentation

## Overview

Line charts display data as connected points over a continuous scale, typically showing trends over time. This documentation covers the essential settings for customizing line chart appearance and behavior.

## Core Settings

### Card-Level Settings

```json
{
  "card.title": "Monthly Revenue Trend",
  "card.description": "Revenue trends over time",
  "card.hide_empty": true
}
```

### Required Configuration

```json
{
  "graph.dimensions": ["created_at"],
  "graph.metrics": ["total_revenue", "total_profit"]
}
```

**Required Fields**:
- `graph.dimensions` - X-axis dimensions (1-2 fields, usually dates or categories)
- `graph.metrics` - Y-axis metrics (data series to plot)

## Axes Configuration

### X-Axis Settings

```json
{
  "graph.x_axis.scale": "timeseries|linear|ordinal|log|pow",
  "graph.x_axis.title_text": "Month",
  "graph.x_axis.axis_enabled": true,
  "graph.x_axis.labels_enabled": true
}
```

### Y-Axis Settings

```json
{
  "graph.y_axis.scale": "linear|log|pow",
  "graph.y_axis.title_text": "Amount ($)",
  "graph.y_axis.auto_range": true,
  "graph.y_axis.min": 0,
  "graph.y_axis.max": 100000,
  "graph.y_axis.auto_split": false,
  "graph.y_axis.unpin_from_zero": false
}
```

## Series Configuration

### Individual Series Settings

```json
{
  "series_settings": {
    "total_revenue": {
      "display": "line|bar|area",
      "color": "#509EE3",
      "name": "Revenue",
      "axis": "left|right",
      "line.interpolate": "linear|cardinal|step-before|step-after",
      "line.marker_enabled": true,
      "line.missing": "interpolate|zero|none"
    }
  }
}
```

### Series Order and Visibility

```json
{
  "graph.series_order": [
    {
      "key": "North",
      "enabled": true,
      "color": "#509EE3",
      "name": "North Region"
    },
    {
      "key": "South",
      "enabled": false,
      "color": "#88BF4D"
    }
  ]
}
```

## Visual Options

### Data Labels and Values

```json
{
  "graph.show_values": true,
  "graph.label_value_frequency": "fit|all",
  "graph.label_value_formatting": "auto|compact|full",
  "graph.show_trendline": true
}
```

### Tooltips

```json
{
  "graph.tooltip_type": "series_comparison|default",
  "graph.tooltip_columns": ["additional_field"]
}
```

### Stacking (for area effects)

```json
{
  "stackable.stack_type": null|"stacked"|"normalized"
}
```

## Goal Lines

```json
{
  "graph.goal_line": {
    "value": 50000,
    "label": "Target Revenue",
    "color": "#ED6E6E"
  }
}
```

## Column Formatting

Format values in tooltips and labels:

```json
{
  "column_settings": {
    "[\"name\",\"total_revenue\"]": {
      "number_style": "currency",
      "currency": "USD",
      "currency_style": "symbol",
      "decimals": 0
    },
    "[\"name\",\"created_at\"]": {
      "date_style": "MMM YYYY"
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
      "date_param": {
        "id": "date_param",
        "source": {
          "type": "column",
          "id": "created_at",
          "name": "Created At"
        },
        "target": {
          "type": "parameter",
          "id": "date_param"
        }
      }
    }
  }
}
```

## Complete Example

```json
{
  "card.title": "Monthly Revenue Trend",
  "graph.dimensions": ["created_at"],
  "graph.metrics": ["total_revenue", "total_profit"],
  "graph.x_axis.title_text": "Month",
  "graph.y_axis.title_text": "Amount ($)",
  "graph.x_axis.scale": "timeseries",
  "graph.show_trendline": true,
  "series_settings": {
    "total_revenue": {
      "display": "line",
      "color": "#509EE3",
      "name": "Revenue",
      "line.interpolate": "linear",
      "line.marker_enabled": true
    },
    "total_profit": {
      "display": "line",
      "color": "#88BF4D",
      "name": "Profit",
      "line.marker_enabled": true
    }
  },
  "column_settings": {
    "[\"name\",\"total_revenue\"]": {
      "number_style": "currency",
      "currency": "USD",
      "decimals": 0
    }
  },
  "graph.goal_line": {
    "value": 50000,
    "label": "Target",
    "color": "#ED6E6E"
  }
}
```

## Common Patterns

### Time Series Chart
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
  "graph.dimensions": ["month"],
  "graph.metrics": ["revenue", "expenses"],
  "graph.y_axis.auto_split": true
}
```

### Categorical Line Chart
```json
{
  "graph.dimensions": ["category"],
  "graph.metrics": ["performance"],
  "graph.x_axis.scale": "ordinal"
}
```