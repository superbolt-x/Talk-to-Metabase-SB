# Scatter Plot Visualization Settings Documentation

## Overview

Scatter plots display the relationship between two numeric variables using points plotted on X and Y axes. They're excellent for identifying correlations, patterns, and outliers in data relationships.

## Core Settings

### Card-Level Settings

```json
{
  "card.title": "Sales vs Marketing Spend",
  "card.description": "Correlation between marketing investment and sales results",
  "card.hide_empty": true
}
```

### Required Configuration

```json
{
  "graph.dimensions": ["marketing_spend"],
  "graph.metrics": ["sales_revenue"]
}
```

**Required Fields**:
- `graph.dimensions` - X-axis field (single numeric or categorical field)
- `graph.metrics` - Y-axis field (single numeric field)

## Bubble Chart Option

### Bubble Size Field

```json
{
  "scatter.bubble": "profit_margin"
}
```

When specified, creates a bubble chart where point size represents the bubble field value.

## Axes Configuration

### X-Axis Settings

```json
{
  "graph.x_axis.scale": "linear|log|pow",
  "graph.x_axis.title_text": "Marketing Spend ($)",
  "graph.x_axis.axis_enabled": true,
  "graph.x_axis.labels_enabled": true,
  "graph.x_axis.auto_range": true,
  "graph.x_axis.min": 0,
  "graph.x_axis.max": 10000
}
```

### Y-Axis Settings

```json
{
  "graph.y_axis.scale": "linear|log|pow",
  "graph.y_axis.title_text": "Sales Revenue ($)",
  "graph.y_axis.axis_enabled": true,
  "graph.y_axis.labels_enabled": true,
  "graph.y_axis.auto_range": true,
  "graph.y_axis.min": 0,
  "graph.y_axis.max": 100000
}
```

## Visual Options

### Trend Lines

```json
{
  "graph.show_trendline": true
}
```

Displays a trend line showing the correlation between X and Y variables.

### Tooltips

```json
{
  "graph.tooltip_type": "default",
  "graph.tooltip_columns": ["region", "campaign_type"]
}
```

## Point Styling

### Series Settings

```json
{
  "series_settings": {
    "sales_revenue": {
      "color": "#509EE3",
      "name": "Sales Performance"
    }
  }
}
```

## Column Formatting

```json
{
  "column_settings": {
    "[\"name\",\"marketing_spend\"]": {
      "number_style": "currency",
      "currency": "USD",
      "currency_style": "symbol",
      "decimals": 0
    },
    "[\"name\",\"sales_revenue\"]": {
      "number_style": "currency",
      "currency": "USD",
      "decimals": 0
    },
    "[\"name\",\"profit_margin\"]": {
      "number_style": "percent",
      "decimals": 1,
      "scale": 0.01
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
      "region_filter": {
        "id": "region_filter",
        "source": {
          "type": "column",
          "id": "region",
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

### Sales vs Marketing Spend Analysis

```json
{
  "card.title": "Sales vs Marketing Spend",
  "card.description": "Correlation analysis with profit margin as bubble size",
  "graph.dimensions": ["marketing_spend"],
  "graph.metrics": ["sales_revenue"],
  "scatter.bubble": "profit_margin",
  "graph.x_axis.title_text": "Marketing Spend ($)",
  "graph.y_axis.title_text": "Sales Revenue ($)",
  "graph.show_trendline": true,
  "series_settings": {
    "sales_revenue": {
      "color": "#509EE3",
      "name": "Sales Performance"
    }
  },
  "column_settings": {
    "[\"name\",\"marketing_spend\"]": {
      "number_style": "currency",
      "currency": "USD",
      "decimals": 0
    },
    "[\"name\",\"sales_revenue\"]": {
      "number_style": "currency",
      "currency": "USD",
      "decimals": 0
    },
    "[\"name\",\"profit_margin\"]": {
      "number_style": "percent",
      "decimals": 1
    }
  }
}
```

### Simple Correlation Analysis

```json
{
  "card.title": "Temperature vs Ice Cream Sales",
  "graph.dimensions": ["temperature"],
  "graph.metrics": ["ice_cream_sales"],
  "graph.x_axis.title_text": "Temperature (°F)",
  "graph.y_axis.title_text": "Ice Cream Sales ($)",
  "graph.show_trendline": true,
  "series_settings": {
    "ice_cream_sales": {
      "color": "#F9CF48"
    }
  }
}
```

### Customer Analysis Bubble Chart

```json
{
  "card.title": "Customer Value Analysis",
  "graph.dimensions": ["acquisition_cost"],
  "graph.metrics": ["lifetime_value"],
  "scatter.bubble": "retention_rate",
  "graph.x_axis.title_text": "Customer Acquisition Cost",
  "graph.y_axis.title_text": "Customer Lifetime Value",
  "graph.tooltip_columns": ["customer_segment"],
  "column_settings": {
    "[\"name\",\"acquisition_cost\"]": {
      "number_style": "currency",
      "currency": "USD",
      "decimals": 0
    },
    "[\"name\",\"lifetime_value\"]": {
      "number_style": "currency",
      "currency": "USD",
      "decimals": 0
    },
    "[\"name\",\"retention_rate\"]": {
      "number_style": "percent",
      "decimals": 1
    }
  }
}
```

## Common Patterns

### Price vs Quality Analysis
```json
{
  "graph.dimensions": ["price"],
  "graph.metrics": ["quality_score"],
  "graph.show_trendline": true
}
```

### Performance Correlation
```json
{
  "graph.dimensions": ["experience_years"],
  "graph.metrics": ["performance_rating"],
  "scatter.bubble": "salary"
}
```

### Market Analysis
```json
{
  "graph.dimensions": ["market_share"],
  "graph.metrics": ["profit_margin"],
  "graph.tooltip_columns": ["company_name"]
}
```

## Use Cases

Scatter plots are ideal for:

- **Correlation Analysis**: Identify relationships between variables
- **Trend Analysis**: Visualize patterns and outliers
- **Performance Analysis**: Compare metrics across dimensions
- **Market Research**: Analyze competitive positioning
- **Quality Control**: Identify anomalies in data
- **Predictive Analysis**: Understand variable relationships for forecasting

## Tips for Effective Scatter Plots

- **Choose Related Variables**: Use variables that may have a logical relationship
- **Use Bubble Size Wisely**: Third dimension should add meaningful context
- **Include Trend Lines**: Help viewers see correlations more clearly
- **Label Axes Clearly**: Ensure units and scales are obvious
- **Consider Outliers**: Investigate points that don't fit the pattern