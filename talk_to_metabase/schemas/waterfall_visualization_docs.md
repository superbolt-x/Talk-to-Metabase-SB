# Waterfall Chart Visualization Settings Documentation

## Overview

Waterfall charts visualize how an initial value is affected by a series of positive or negative changes, showing the cumulative effect of sequential contributions. They're perfect for financial analysis, variance reporting, and showing step-by-step changes.

## Core Settings

### Card-Level Settings

```json
{
  "card.title": "Quarterly P&L Breakdown",
  "card.description": "Waterfall analysis of profit and loss components",
  "card.hide_empty": true
}
```

### Required Configuration

```json
{
  "waterfall.dimension": "category",
  "waterfall.metric": "amount"
}
```

**Required Fields**:
- `waterfall.dimension` - Field containing category/step names
- `waterfall.metric` - Field containing change values (positive/negative numbers)

## Color Configuration

### Bar Colors

```json
{
  "waterfall.increase_color": "#84BB4C",
  "waterfall.decrease_color": "#ED6E6E", 
  "waterfall.total_color": "#509EE3"
}
```

- `increase_color` - Color for positive value bars (default: green)
- `decrease_color` - Color for negative value bars (default: red)
- `total_color` - Color for running total bars (default: blue)

### Show Running Totals

```json
{
  "waterfall.show_total": true
}
```

Controls whether to display running total bars between changes.

## Axes Configuration

### X-Axis Settings

```json
{
  "graph.x_axis.axis_enabled": true|"compact"|"rotate-45"|"rotate-90",
  "graph.x_axis.labels_enabled": true,
  "graph.x_axis.title_text": "P&L Categories"
}
```

### Y-Axis Settings

```json
{
  "graph.y_axis.axis_enabled": true,
  "graph.y_axis.labels_enabled": true,
  "graph.y_axis.title_text": "Amount ($)",
  "graph.y_axis.auto_range": true,
  "graph.y_axis.min": -50000,
  "graph.y_axis.max": 200000
}
```

## Value Display

### Show Values on Bars

```json
{
  "graph.show_values": true
}
```

Controls whether to display numeric values on each waterfall bar.

## Column Formatting

```json
{
  "column_settings": {
    "[\"name\",\"amount\"]": {
      "number_style": "currency",
      "currency": "USD",
      "currency_style": "symbol",
      "decimals": 0
    },
    "[\"name\",\"category\"]": {
      "column_title": "P&L Category"
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
  "suffix": " change",
  "scale": 1
}
```

## Click Behaviors

```json
{
  "click_behavior": {
    "type": "link",
    "linkType": "dashboard",
    "targetId": 67,
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

### Financial P&L Waterfall

```json
{
  "card.title": "Quarterly P&L Breakdown",
  "card.description": "Waterfall analysis of profit and loss components",
  "waterfall.dimension": "category",
  "waterfall.metric": "amount",
  "waterfall.increase_color": "#84BB4C",
  "waterfall.decrease_color": "#ED6E6E",
  "waterfall.total_color": "#509EE3",
  "waterfall.show_total": true,
  "graph.show_values": true,
  "graph.x_axis.title_text": "P&L Categories",
  "graph.y_axis.title_text": "Amount ($)",
  "column_settings": {
    "[\"name\",\"amount\"]": {
      "number_style": "currency",
      "currency": "USD",
      "decimals": 0
    }
  },
  "click_behavior": {
    "type": "link",
    "linkType": "dashboard",
    "targetId": 67,
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

### Budget Variance Analysis

```json
{
  "card.title": "Budget vs Actual Variance",
  "waterfall.dimension": "budget_category",
  "waterfall.metric": "variance_amount",
  "waterfall.increase_color": "#28A745",
  "waterfall.decrease_color": "#DC3545",
  "waterfall.total_color": "#17A2B8",
  "waterfall.show_total": true,
  "graph.show_values": true,
  "graph.x_axis.axis_enabled": "rotate-45",
  "column_settings": {
    "[\"name\",\"variance_amount\"]": {
      "number_style": "currency",
      "currency": "USD",
      "decimals": 0,
      "prefix": "",
      "suffix": " variance"
    }
  }
}
```

### Sales Performance Breakdown

```json
{
  "card.title": "Sales Performance Components",
  "waterfall.dimension": "performance_factor",
  "waterfall.metric": "impact_value",
  "waterfall.increase_color": "#20C997",
  "waterfall.decrease_color": "#FD7E14",
  "waterfall.total_color": "#6F42C1",
  "waterfall.show_total": false,
  "graph.show_values": true,
  "graph.y_axis.auto_range": false,
  "graph.y_axis.min": -10000,
  "graph.y_axis.max": 25000,
  "column_settings": {
    "[\"name\",\"impact_value\"]": {
      "number_style": "decimal",
      "decimals": 0,
      "number_separators": ".,"
    }
  }
}
```

### Cash Flow Analysis

```json
{
  "card.title": "Monthly Cash Flow",
  "waterfall.dimension": "cash_flow_type",
  "waterfall.metric": "cash_amount",
  "waterfall.increase_color": "#84BB4C",
  "waterfall.decrease_color": "#ED6E6E",
  "waterfall.total_color": "#509EE3",
  "waterfall.show_total": true,
  "graph.show_values": true,
  "graph.x_axis.title_text": "Cash Flow Components",
  "graph.y_axis.title_text": "Cash Amount",
  "column_settings": {
    "[\"name\",\"cash_amount\"]": {
      "number_style": "currency",
      "currency": "USD",
      "currency_style": "symbol",
      "decimals": 0
    }
  }
}
```

## Common Patterns

### Financial Analysis
```json
{
  "waterfall.dimension": "line_item",
  "waterfall.metric": "amount_change",
  "waterfall.show_total": true
}
```

### Variance Reporting
```json
{
  "waterfall.dimension": "variance_category",
  "waterfall.metric": "variance_amount",
  "graph.show_values": true
}
```

### Performance Breakdown
```json
{
  "waterfall.dimension": "contributing_factor",
  "waterfall.metric": "performance_impact",
  "waterfall.show_total": false
}
```

## Use Cases

Waterfall charts are perfect for:

- **Financial Analysis**: P&L statements, budget variance, cash flow
- **Sales Analysis**: Revenue bridges, performance drivers
- **Cost Analysis**: Cost breakdowns, expense variances
- **Performance Analysis**: Factor contribution to overall performance
- **Project Analysis**: Resource allocation and budget tracking
- **Inventory Analysis**: Stock level changes over time

## Data Requirements

For effective waterfall charts:

- **Sequential Data**: Categories should represent sequential steps
- **Positive/Negative Values**: Metric should contain both increases and decreases
- **Meaningful Order**: Arrange categories in logical sequence
- **Clear Categories**: Use descriptive names for each component
- **Balanced Scale**: Ensure value ranges make visual sense

## Design Tips

- **Color Consistency**: Use green for positive, red for negative
- **Clear Labels**: Ensure category names are descriptive
- **Value Display**: Always show values for precise interpretation
- **Total Bars**: Use running totals to show cumulative effect
- **Axis Ranges**: Set appropriate Y-axis ranges for clarity