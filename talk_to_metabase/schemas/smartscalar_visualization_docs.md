# Smart Scalar Visualization Settings Documentation

## Overview

Smart Scalar (trend) charts display a single primary number with comparison values and trend indicators. They're perfect for KPI dashboards where you need to show current performance against historical data, targets, or other benchmarks.

## Core Settings

### Card-Level Settings

```json
{
  "card.title": "Monthly Revenue Trend",
  "card.description": "Current month revenue vs previous periods",
  "card.hide_empty": true
}
```

### Required Configuration

```json
{
  "scalar.field": "current_revenue"
}
```

**Required Fields**:
- `scalar.field` - Field containing the primary value to display

## Comparison Configuration

### Comparison Types

Smart scalars can include multiple comparison values to provide context:

```json
{
  "scalar.comparisons": [
    {
      "id": "comp1",
      "type": "previousPeriod",
      "label": "vs Last Month"
    },
    {
      "id": "comp2",
      "type": "periodsAgo",
      "value": 12,
      "label": "vs Same Month Last Year"
    },
    {
      "id": "comp3",
      "type": "staticNumber",
      "value": 100000,
      "label": "vs Target"
    },
    {
      "id": "comp4",
      "type": "anotherColumn",
      "column": "previous_month_revenue",
      "label": "vs Previous Month"
    }
  ]
}
```

### Comparison Types Available

#### Previous Period
```json
{
  "type": "previousPeriod",
  "label": "vs Last Period"
}
```
Compares to the immediately previous time period.

#### Periods Ago
```json
{
  "type": "periodsAgo",
  "value": 12,
  "label": "vs Same Period Last Year"
}
```
Compares to a specific number of periods in the past.

#### Static Number
```json
{
  "type": "staticNumber",
  "value": 100000,
  "label": "vs Target"
}
```
Compares to a fixed target or benchmark value.

#### Another Column
```json
{
  "type": "anotherColumn",
  "column": "budget_amount",
  "label": "vs Budget"
}
```
Compares to a value from another column in the same dataset.

#### Previous Value
```json
{
  "type": "previousValue",
  "label": "vs Previous"
}
```
Compares to the previous value in the dataset.

## Value Formatting

```json
{
  "column_settings": {
    "[\"name\",\"current_revenue\"]": {
      "number_style": "currency",
      "currency": "USD",
      "currency_style": "symbol",
      "decimals": 0,
      "currency_in_header": false
    }
  }
}
```

### Number Formatting Options

```json
{
  "number_style": "decimal|currency|percent|scientific",
  "currency": "USD",
  "currency_style": "symbol|code|name",
  "decimals": 0,
  "prefix": "",
  "suffix": "%",
  "scale": 1,
  "currency_in_header": false
}
```

## Click Behaviors

```json
{
  "click_behavior": {
    "type": "link",
    "linkType": "dashboard",
    "targetId": 789,
    "parameterMapping": {
      "time_filter": {
        "id": "time_filter",
        "source": {
          "type": "column",
          "id": "month",
          "name": "Month"
        },
        "target": {
          "type": "parameter",
          "id": "time_filter"
        }
      }
    }
  }
}
```

## Complete Examples

### Revenue Trend with Multiple Comparisons

```json
{
  "card.title": "Monthly Revenue Trend",
  "card.description": "Current month revenue with trend indicators",
  "scalar.field": "current_revenue",
  "scalar.comparisons": [
    {
      "id": "comp1",
      "type": "previousPeriod",
      "label": "vs Last Month"
    },
    {
      "id": "comp2",
      "type": "periodsAgo",
      "value": 12,
      "label": "vs Same Month Last Year"
    },
    {
      "id": "comp3",
      "type": "staticNumber",
      "value": 100000,
      "label": "vs Target"
    }
  ],
  "column_settings": {
    "[\"name\",\"current_revenue\"]": {
      "number_style": "currency",
      "currency": "USD",
      "currency_style": "symbol",
      "decimals": 0
    }
  }
}
```

### Customer Satisfaction Score

```json
{
  "card.title": "Customer Satisfaction",
  "scalar.field": "satisfaction_score",
  "scalar.comparisons": [
    {
      "id": "target_comp",
      "type": "staticNumber",
      "value": 85,
      "label": "vs Target (85%)"
    },
    {
      "id": "previous_comp",
      "type": "previousPeriod",
      "label": "vs Last Quarter"
    }
  ],
  "column_settings": {
    "[\"name\",\"satisfaction_score\"]": {
      "number_style": "percent",
      "decimals": 1,
      "scale": 0.01
    }
  }
}
```

### Budget vs Actual Performance

```json
{
  "card.title": "Budget Performance",
  "scalar.field": "actual_spend",
  "scalar.comparisons": [
    {
      "id": "budget_comp",
      "type": "anotherColumn",
      "column": "budget_amount",
      "label": "vs Budget"
    },
    {
      "id": "last_year_comp",
      "type": "periodsAgo",
      "value": 12,
      "label": "vs Last Year"
    }
  ],
  "column_settings": {
    "[\"name\",\"actual_spend\"]": {
      "number_style": "currency",
      "currency": "USD",
      "decimals": 0
    }
  }
}
```

### Growth Rate Indicator

```json
{
  "card.title": "Monthly Growth Rate",
  "scalar.field": "growth_percentage",
  "scalar.comparisons": [
    {
      "id": "target_growth",
      "type": "staticNumber",
      "value": 5,
      "label": "vs Target Growth (5%)"
    }
  ],
  "column_settings": {
    "[\"name\",\"growth_percentage\"]": {
      "number_style": "percent",
      "decimals": 2,
      "suffix": "%"
    }
  }
}
```

## Common Patterns

### KPI with Target
```json
{
  "scalar.field": "current_kpi",
  "scalar.comparisons": [
    {
      "type": "staticNumber",
      "value": 100,
      "label": "vs Goal"
    }
  ]
}
```

### Period-over-Period Comparison
```json
{
  "scalar.field": "this_month",
  "scalar.comparisons": [
    {
      "type": "previousPeriod",
      "label": "vs Last Month"
    },
    {
      "type": "periodsAgo",
      "value": 12,
      "label": "vs Last Year"
    }
  ]
}
```

### Performance vs Budget
```json
{
  "scalar.field": "actual_value",
  "scalar.comparisons": [
    {
      "type": "anotherColumn",
      "column": "budget_value",
      "label": "vs Budget"
    }
  ]
}
```

## Use Cases

Smart scalars are perfect for:

- **Executive Dashboards**: High-level KPI monitoring with context
- **Performance Tracking**: Current vs historical performance
- **Goal Monitoring**: Progress against targets and benchmarks
- **Trend Analysis**: Quick visual indication of performance direction
- **Budget Management**: Actual vs planned spending
- **Sales Metrics**: Revenue, conversion rates, and growth indicators

## Design Tips

- **Limit Comparisons**: 2-3 comparisons maximum to avoid clutter
- **Meaningful Labels**: Use clear, descriptive comparison labels
- **Consistent Time Periods**: Ensure period comparisons make sense
- **Appropriate Formatting**: Match number format to the metric type
- **Color Coding**: Metabase automatically colors positive/negative trends