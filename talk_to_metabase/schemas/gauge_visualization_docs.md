# Gauge Chart Visualization Settings Documentation

## Overview

Gauge charts display a single metric value on a circular or semi-circular scale, often with color-coded segments to indicate performance levels. They're perfect for KPIs, progress indicators, and performance dashboards.

## Core Settings

### Card-Level Settings

```json
{
  "card.title": "Customer Satisfaction Score",
  "card.description": "Current satisfaction rating",
  "card.hide_empty": true
}
```

### Required Configuration

```json
{
  "gauge.field": "satisfaction_score"
}
```

**Required Fields**:
- `gauge.field` - Field containing the value to display on the gauge

## Gauge Range

### Manual Range

```json
{
  "gauge.min": 0,
  "gauge.max": 100,
  "gauge.auto_range": false
}
```

### Auto Range

```json
{
  "gauge.auto_range": true
}
```

When enabled, automatically determines min/max from the data.

## Color Segments

### Segment Configuration

```json
{
  "gauge.segments": [
    {
      "min": 0,
      "max": 30,
      "color": "#ED6E6E",
      "label": "Poor"
    },
    {
      "min": 30,
      "max": 70,
      "color": "#F9CF48",
      "label": "Average"
    },
    {
      "min": 70,
      "max": 100,
      "color": "#84BB4C",
      "label": "Excellent"
    }
  ]
}
```

**Segment Properties**:
- `min` - Minimum value for this segment
- `max` - Maximum value for this segment
- `color` - Hex color code for the segment
- `label` - Optional descriptive label

## Display Options

### Value Display

```json
{
  "gauge.show_values": true
}
```

Controls whether to show the numeric value on the gauge.

## Value Formatting

```json
{
  "column_settings": {
    "[\"name\",\"satisfaction_score\"]": {
      "number_style": "percent",
      "decimals": 1,
      "suffix": "%"
    }
  }
}
```

### Number Formatting Options

```json
{
  "number_style": "decimal|currency|percent|scientific",
  "currency": "USD",
  "currency_style": "symbol",
  "decimals": 1,
  "prefix": "",
  "suffix": "%",
  "scale": 1
}
```

## Click Behaviors

```json
{
  "click_behavior": {
    "type": "link",
    "linkType": "dashboard",
    "targetId": 456,
    "parameterMapping": {
      "score_filter": {
        "id": "score_filter",
        "source": {
          "type": "column",
          "id": "satisfaction_score",
          "name": "Satisfaction Score"
        },
        "target": {
          "type": "parameter",
          "id": "score_filter"
        }
      }
    }
  }
}
```

## Complete Examples

### Customer Satisfaction Gauge

```json
{
  "card.title": "Customer Satisfaction Score",
  "gauge.field": "satisfaction_score",
  "gauge.min": 0,
  "gauge.max": 100,
  "gauge.show_values": true,
  "gauge.segments": [
    {
      "min": 0,
      "max": 30,
      "color": "#ED6E6E",
      "label": "Poor"
    },
    {
      "min": 30,
      "max": 70,
      "color": "#F9CF48",
      "label": "Average"
    },
    {
      "min": 70,
      "max": 100,
      "color": "#84BB4C",
      "label": "Excellent"
    }
  ],
  "column_settings": {
    "[\"name\",\"satisfaction_score\"]": {
      "number_style": "decimal",
      "decimals": 1,
      "suffix": "%"
    }
  }
}
```

### Sales Performance Gauge

```json
{
  "card.title": "Sales Target Achievement",
  "gauge.field": "achievement_percentage",
  "gauge.min": 0,
  "gauge.max": 150,
  "gauge.show_values": true,
  "gauge.segments": [
    {
      "min": 0,
      "max": 80,
      "color": "#ED6E6E",
      "label": "Below Target"
    },
    {
      "min": 80,
      "max": 100,
      "color": "#F9CF48",
      "label": "On Target"
    },
    {
      "min": 100,
      "max": 150,
      "color": "#84BB4C",
      "label": "Exceeds Target"
    }
  ],
  "column_settings": {
    "[\"name\",\"achievement_percentage\"]": {
      "number_style": "percent",
      "decimals": 0,
      "scale": 0.01
    }
  }
}
```

### Quality Score Gauge

```json
{
  "card.title": "Product Quality Score",
  "gauge.field": "quality_rating",
  "gauge.min": 1,
  "gauge.max": 5,
  "gauge.show_values": true,
  "gauge.segments": [
    {
      "min": 1,
      "max": 2,
      "color": "#DC3545",
      "label": "Critical"
    },
    {
      "min": 2,
      "max": 3,
      "color": "#FD7E14",
      "label": "Needs Improvement"
    },
    {
      "min": 3,
      "max": 4,
      "color": "#FFC107",
      "label": "Good"
    },
    {
      "min": 4,
      "max": 5,
      "color": "#28A745",
      "label": "Excellent"
    }
  ],
  "column_settings": {
    "[\"name\",\"quality_rating\"]": {
      "number_style": "decimal",
      "decimals": 2,
      "suffix": " / 5"
    }
  }
}
```

### Revenue Gauge with Auto Range

```json
{
  "card.title": "Monthly Revenue",
  "gauge.field": "monthly_revenue",
  "gauge.auto_range": true,
  "gauge.show_values": true,
  "gauge.segments": [
    {
      "min": 0,
      "max": 50000,
      "color": "#ED6E6E"
    },
    {
      "min": 50000,
      "max": 100000,
      "color": "#F9CF48"
    },
    {
      "min": 100000,
      "max": 200000,
      "color": "#84BB4C"
    }
  ],
  "column_settings": {
    "[\"name\",\"monthly_revenue\"]": {
      "number_style": "currency",
      "currency": "USD",
      "currency_style": "symbol",
      "decimals": 0
    }
  }
}
```

## Common Patterns

### Performance KPI
```json
{
  "gauge.field": "performance_score",
  "gauge.min": 0,
  "gauge.max": 100,
  "gauge.segments": [
    {"min": 0, "max": 60, "color": "#ED6E6E"},
    {"min": 60, "max": 80, "color": "#F9CF48"},
    {"min": 80, "max": 100, "color": "#84BB4C"}
  ]
}
```

### Progress Indicator
```json
{
  "gauge.field": "completion_percentage",
  "gauge.min": 0,
  "gauge.max": 100,
  "gauge.show_values": true
}
```

### Health Score
```json
{
  "gauge.field": "health_score",
  "gauge.min": 0,
  "gauge.max": 10,
  "gauge.segments": [
    {"min": 0, "max": 4, "color": "#DC3545", "label": "Critical"},
    {"min": 4, "max": 7, "color": "#FFC107", "label": "Warning"},
    {"min": 7, "max": 10, "color": "#28A745", "label": "Healthy"}
  ]
}
```

## Use Cases

Gauge charts are perfect for:

- **KPI Dashboards**: Display key performance indicators
- **Quality Metrics**: Show satisfaction, quality, or health scores
- **Progress Tracking**: Visualize completion percentages
- **Performance Monitoring**: Display achievement against targets
- **Status Indicators**: Show system health or operational status
- **Goal Achievement**: Track progress toward objectives

## Design Tips

- **Color Psychology**: Use red for poor/critical, yellow for warning, green for good
- **Segment Ranges**: Ensure segments cover the full gauge range without gaps
- **Label Clarity**: Use descriptive labels that clearly indicate performance levels
- **Value Display**: Always show values for precise readings
- **Range Setting**: Set appropriate min/max values that make sense for your metric