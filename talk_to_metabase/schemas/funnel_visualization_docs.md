# Funnel Chart Visualization Settings Documentation

## Overview

Funnel charts visualize conversion processes where data flows through sequential stages, with each stage typically having fewer items than the previous one. They're perfect for analyzing sales pipelines, user conversion flows, and multi-step processes.

## Core Settings

### Card-Level Settings

```json
{
  "card.title": "Sales Conversion Funnel",
  "card.description": "Lead to customer conversion stages",
  "card.hide_empty": true
}
```

### Required Configuration

```json
{
  "funnel.dimension": "stage",
  "funnel.metric": "count"
}
```

**Required Fields**:
- `funnel.dimension` - Field containing the stage/step names
- `funnel.metric` - Field containing the count/value for each stage

## Visual Options

### Funnel Type

```json
{
  "funnel.type": "funnel|bar"
}
```

- `"funnel"` - Traditional funnel shape (default)
- `"bar"` - Horizontal bar chart representation

### Value Display

```json
{
  "funnel.show_values": true,
  "funnel.show_percentages": true
}
```

- `show_values` - Display numeric values on each segment
- `show_percentages` - Show conversion percentages between stages

## Color Configuration

### Color Palette

```json
{
  "funnel.colors": [
    "#509EE3",
    "#88BF4D", 
    "#F9CF48",
    "#ED6E6E"
  ]
}
```

Colors are applied to funnel segments in order from top to bottom.

## Column Formatting

```json
{
  "column_settings": {
    "[\"name\",\"count\"]": {
      "number_style": "decimal",
      "decimals": 0,
      "number_separators": ".,"
    },
    "[\"name\",\"stage\"]": {
      "column_title": "Conversion Stage"
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
  "decimals": 0,
  "prefix": "",
  "suffix": " leads",
  "scale": 1
}
```

## Click Behaviors

```json
{
  "click_behavior": {
    "type": "crossfilter",
    "parameterMapping": {
      "stage_filter": {
        "id": "stage_filter",
        "source": {
          "type": "column",
          "id": "stage",
          "name": "Stage"
        },
        "target": {
          "type": "parameter",
          "id": "stage_filter"
        }
      }
    }
  }
}
```

**Click Behavior Types**:
- `"crossfilter"` - Filter dashboard by clicked stage
- `"link"` - Navigate to detailed analysis
- `"none"` - Disable click behavior

## Complete Examples

### Sales Pipeline Funnel

```json
{
  "card.title": "Sales Conversion Funnel",
  "card.description": "Lead to customer conversion stages",
  "funnel.dimension": "stage",
  "funnel.metric": "count",
  "funnel.type": "funnel",
  "funnel.show_values": true,
  "funnel.show_percentages": true,
  "funnel.colors": [
    "#509EE3",
    "#88BF4D",
    "#F9CF48", 
    "#ED6E6E"
  ],
  "column_settings": {
    "[\"name\",\"count\"]": {
      "number_style": "decimal",
      "decimals": 0,
      "suffix": " prospects"
    },
    "[\"name\",\"stage\"]": {
      "column_title": "Sales Stage"
    }
  },
  "click_behavior": {
    "type": "crossfilter",
    "parameterMapping": {
      "stage_filter": {
        "id": "stage_filter",
        "source": {
          "type": "column",
          "id": "stage",
          "name": "Stage"
        },
        "target": {
          "type": "parameter",
          "id": "stage_filter"
        }
      }
    }
  }
}
```

### E-commerce Conversion Funnel

```json
{
  "card.title": "Website Conversion Funnel",
  "funnel.dimension": "conversion_step",
  "funnel.metric": "users",
  "funnel.type": "funnel",
  "funnel.show_values": true,
  "funnel.show_percentages": true,
  "funnel.colors": [
    "#4285F4",
    "#34A853",
    "#FBBC04",
    "#EA4335"
  ],
  "column_settings": {
    "[\"name\",\"users\"]": {
      "number_style": "decimal",
      "decimals": 0,
      "suffix": " users"
    }
  }
}
```

### Marketing Campaign Funnel (Bar Style)

```json
{
  "card.title": "Campaign Performance",
  "funnel.dimension": "campaign_stage", 
  "funnel.metric": "total_value",
  "funnel.type": "bar",
  "funnel.show_values": true,
  "funnel.show_percentages": false,
  "column_settings": {
    "[\"name\",\"total_value\"]": {
      "number_style": "currency",
      "currency": "USD",
      "currency_style": "symbol",
      "decimals": 0
    }
  }
}
```

## Common Patterns

### Sales Pipeline Analysis
```json
{
  "funnel.dimension": "sales_stage",
  "funnel.metric": "opportunity_count",
  "funnel.show_percentages": true
}
```

### User Journey Tracking
```json
{
  "funnel.dimension": "user_step",
  "funnel.metric": "session_count",
  "funnel.type": "funnel"
}
```

### Lead Qualification Process
```json
{
  "funnel.dimension": "qualification_stage",
  "funnel.metric": "lead_count",
  "funnel.show_values": true
}
```

## Use Cases

Funnel charts are ideal for:

- **Sales Analysis**: Track leads through qualification to closure
- **User Experience**: Analyze user drop-off in multi-step processes
- **Marketing**: Measure campaign effectiveness across touchpoints
- **Product**: Understand feature adoption and user onboarding
- **E-commerce**: Track shopping cart to purchase conversion
- **Support**: Analyze ticket resolution workflows

## Tips for Effective Funnels

- **Order Matters**: Ensure stages are in logical sequence
- **Stage Naming**: Use clear, descriptive stage names
- **Color Coding**: Use colors that indicate progression (e.g., green for success)
- **Percentage Focus**: Conversion rates often more important than absolute numbers
- **Segment Analysis**: Consider creating separate funnels for different user types