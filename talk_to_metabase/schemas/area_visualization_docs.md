# Area Chart Visualization Settings Documentation

## Overview

Area charts display data as filled areas under lines, typically used to show cumulative totals or part-to-whole relationships over time. They're excellent for visualizing trends and comparing multiple series with stacking.

## Core Settings

### Card-Level Settings

```json
{
  "card.title": "Revenue Over Time",
  "card.description": "Stacked area chart showing revenue trends by category",
  "card.hide_empty": true
}
```

### Required Configuration

```json
{
  "graph.dimensions": ["created_at"],
  "graph.metrics": ["electronics_revenue", "clothing_revenue", "books_revenue"]
}
```

**Required Fields**:
- `graph.dimensions` - X-axis dimensions (usually time series, 1-2 fields)
- `graph.metrics` - Y-axis metrics (data series to stack or overlay)

## Stacking Options

```json
{
  "stackable.stack_type": "stacked|normalized|null"
}
```

- `"stacked"` - Stack areas on top of each other (default for area charts)
- `"normalized"` - Stack as percentages (100% stacked)
- `null` - Overlay areas without stacking

## Axes Configuration

### X-Axis Settings

```json
{
  "graph.x_axis.scale": "linear|timeseries|ordinal|log|pow",
  "graph.x_axis.title_text": "Date",
  "graph.x_axis.axis_enabled": true|"compact"|"rotate-45"|"rotate-90",
  "graph.x_axis.labels_enabled": true
}
```

### Y-Axis Settings

```json
{
  "graph.y_axis.scale": "linear|log|pow",
  "graph.y_axis.title_text": "Revenue ($)",
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
    "electronics_revenue": {
      "display": "area",
      "color": "#509EE3",
      "name": "Electronics",
      "line.interpolate": "linear",
      "line.missing": "zero"
    },
    "clothing_revenue": {
      "display": "line",
      "color": "#88BF4D",
      "name": "Clothing",
      "line.marker_enabled": true,
      "line.interpolate": "cardinal"
    }
  }
}
```

**Display Types**:
- `"area"` - Filled area series
- `"line"` - Line overlay on area chart

**Interpolation Options**:
- `"linear"` - Straight lines between points
- `"cardinal"` - Smooth curves
- `"step-before"` - Step function before point
- `"step-after"` - Step function after point

**Missing Value Handling**:
- `"zero"` - Treat missing as zero (default for areas)
- `"interpolate"` - Interpolate between points
- `"none"` - Show gaps

## Visual Options

### Value Display

```json
{
  "graph.show_values": false,
  "graph.label_value_frequency": "fit|all",
  "graph.label_value_formatting": "auto|compact|full",
  "graph.show_stack_values": "total|series|all"
}
```

### Goal Lines

```json
{
  "graph.goal_value": 75000,
  "graph.goal_label": "Target Engagement",
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
      "key": "electronics_revenue",
      "enabled": true,
      "color": "#509EE3",
      "name": "Electronics"
    },
    {
      "key": "clothing_revenue",
      "enabled": true,
      "color": "#88BF4D",
      "name": "Clothing"
    }
  ]
}
```

## Column Formatting

```json
{
  "column_settings": {
    "[\"name\",\"electronics_revenue\"]": {
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
    "targetId": 89,
    "parameterMapping": {
      "date_filter": {
        "id": "date_filter",
        "source": {
          "type": "column",
          "id": "created_at",
          "name": "Date"
        },
        "target": {
          "type": "parameter",
          "id": "date_filter"
        }
      }
    }
  }
}
```

## Complete Examples

### Revenue Trends by Category

```json
{
  "card.title": "Revenue Over Time",
  "graph.dimensions": ["created_at"],
  "graph.metrics": ["electronics_revenue", "clothing_revenue", "books_revenue"],
  "graph.x_axis.title_text": "Date",
  "graph.y_axis.title_text": "Revenue ($)",
  "stackable.stack_type": "stacked",
  "graph.tooltip_type": "series_comparison",
  "series_settings": {
    "electronics_revenue": {
      "display": "area",
      "color": "#509EE3",
      "name": "Electronics",
      "line.interpolate": "linear"
    },
    "clothing_revenue": {
      "display": "area",
      "color": "#88BF4D",
      "name": "Clothing",
      "line.interpolate": "linear"
    },
    "books_revenue": {
      "display": "area",
      "color": "#F9CF48",
      "name": "Books",
      "line.interpolate": "linear"
    }
  },
  "column_settings": {
    "[\"name\",\"electronics_revenue\"]": {
      "number_style": "currency",
      "currency": "USD",
      "decimals": 0
    }
  }
}
```

### Website Traffic Analysis

```json
{
  "card.title": "Website Traffic Analysis",
  "graph.dimensions": ["date"],
  "graph.metrics": ["page_views", "unique_visitors"],
  "stackable.stack_type": "normalized",
  "graph.show_values": true,
  "graph.label_value_formatting": "compact",
  "graph.show_stack_values": "series",
  "series_settings": {
    "page_views": {
      "display": "area",
      "color": "#A989C5",
      "name": "Page Views"
    },
    "unique_visitors": {
      "display": "line",
      "color": "#EF8C8C",
      "name": "Unique Visitors",
      "line.marker_enabled": true,
      "line.interpolate": "cardinal"
    }
  },
  "graph.goal_value": 75,
  "graph.goal_label": "Target Engagement",
  "graph.show_goal": true
}
```

### Multi-Series Performance

```json
{
  "graph.dimensions": ["month"],
  "graph.metrics": ["sales", "marketing_spend", "leads"],
  "stackable.stack_type": "stacked",
  "graph.y_axis.auto_split": true,
  "series_settings": {
    "sales": {
      "display": "area",
      "color": "#509EE3"
    },
    "marketing_spend": {
      "display": "area",
      "color": "#ED6E6E"
    },
    "leads": {
      "display": "line",
      "color": "#88BF4D",
      "line.marker_enabled": true
    }
  }
}
```

## Common Patterns

### Time Series Accumulation
```json
{
  "graph.dimensions": ["date"],
  "graph.metrics": ["daily_revenue"],
  "stackable.stack_type": "stacked"
}
```

### Category Breakdown Over Time
```json
{
  "graph.dimensions": ["month"],
  "graph.metrics": ["category_a", "category_b", "category_c"],
  "stackable.stack_type": "normalized"
}
```

### Mixed Series Display
```json
{
  "graph.dimensions": ["period"],
  "graph.metrics": ["volume", "trend"],
  "series_settings": {
    "volume": {"display": "area"},
    "trend": {"display": "line", "line.marker_enabled": true}
  }
}
```