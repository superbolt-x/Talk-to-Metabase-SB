# Pie Chart Visualization Settings Documentation

## Overview

Pie charts display data as slices of a circular chart, where each slice represents a proportion of the whole. This documentation covers the essential settings for customizing pie chart appearance and behavior.

## Core Settings

### Card-Level Settings

```json
{
  "card.title": "Sales by Category",
  "card.description": "Distribution of sales across product categories",
  "card.hide_empty": true
}
```

### Required Configuration

```json
{
  "pie.dimension": "category",
  "pie.metric": "total_sales"
}
```

**Required Fields**:
- `pie.dimension` - Field for pie slice categories (string or array for nested pies)
- `pie.metric` - Field for slice values/sizes

## Display Options

### Legend and Labels

```json
{
  "pie.show_legend": true,
  "pie.show_labels": true,
  "pie.show_total": false
}
```

### Percentage Display

```json
{
  "pie.percent_visibility": "off|legend|inside|both",
  "pie.decimal_places": 1
}
```

- `"off"` - No percentages shown
- `"legend"` - Percentages in legend only
- `"inside"` - Percentages inside slices
- `"both"` - Percentages in both locations

## Slice Management

### Slice Threshold and Sorting

```json
{
  "pie.slice_threshold": 2.5,
  "pie.sort_rows": "desc|asc"
}
```

**Slice Threshold**: Minimum percentage for a slice to be shown separately (smaller slices grouped as "Other")

### Custom Slice Configuration

```json
{
  "pie.rows": [
    {
      "key": "Electronics",
      "name": "Electronics & Gadgets",
      "color": "#509EE3",
      "enabled": true,
      "value": 45000,
      "percentage": 45.0
    },
    {
      "key": "Clothing",
      "name": "Apparel",
      "color": "#88BF4D",
      "enabled": true,
      "value": 32000,
      "percentage": 32.0
    }
  ]
}
```

## Series Settings

Individual slice customization:

```json
{
  "series_settings": {
    "Electronics": {
      "name": "Electronics & Gadgets",
      "color": "#509EE3",
      "enabled": true
    },
    "Clothing": {
      "name": "Apparel",
      "color": "#88BF4D",
      "enabled": false
    }
  }
}
```

## Color Mapping

```json
{
  "pie.colors": {
    "Electronics": "#509EE3",
    "Clothing": "#88BF4D",
    "Books": "#F9CF48",
    "Other": "#CCCCCC"
  }
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
    "[\"name\",\"category\"]": {
      "column_title": "Product Category"
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
      "category_filter": {
        "id": "category_filter",
        "source": {
          "type": "column",
          "id": "category",
          "name": "Category"
        },
        "target": {
          "type": "parameter",
          "id": "category_filter"
        }
      }
    }
  }
}
```

## Complete Examples

### Basic Pie Chart

```json
{
  "card.title": "Sales by Category",
  "pie.dimension": "category",
  "pie.metric": "total_sales",
  "pie.show_legend": true,
  "pie.show_total": true,
  "pie.percent_visibility": "legend",
  "pie.decimal_places": 1,
  "pie.slice_threshold": 5.0,
  "series_settings": {
    "Electronics": {
      "name": "Electronics & Gadgets",
      "color": "#509EE3"
    },
    "Clothing": {
      "name": "Apparel",
      "color": "#88BF4D"
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

### Market Share Analysis

```json
{
  "card.title": "Market Share Analysis",
  "pie.dimension": "company",
  "pie.metric": "market_share_percent",
  "pie.show_legend": true,
  "pie.show_labels": true,
  "pie.percent_visibility": "both",
  "pie.decimal_places": 2,
  "pie.slice_threshold": 1.0,
  "pie.rows": [
    {
      "key": "Company A",
      "name": "Company A",
      "color": "#509EE3",
      "enabled": true,
      "percentage": 45.5
    },
    {
      "key": "Company B",
      "name": "Company B", 
      "color": "#88BF4D",
      "enabled": true,
      "percentage": 32.1
    }
  ]
}
```

## Common Patterns

### Revenue Distribution
```json
{
  "pie.dimension": "department",
  "pie.metric": "revenue",
  "pie.show_total": true
}
```

### Customer Segmentation
```json
{
  "pie.dimension": "customer_type",
  "pie.metric": "count",
  "pie.percent_visibility": "inside"
}
```

### Product Performance
```json
{
  "pie.dimension": "product_category",
  "pie.metric": "sales_volume",
  "pie.slice_threshold": 3.0
}
```