# Scalar Visualization Settings Documentation

## Overview

Scalar visualizations (called "Number" in the Metabase UI) display a single numeric value prominently, often used for KPIs, totals, and key metrics on dashboards. They provide clean, focused display of important numbers with extensive formatting options.

## Core Settings

### Card-Level Settings

```json
{
  "card.title": "Total Revenue",
  "card.description": "Revenue for current period",
  "card.hide_empty": true
}
```

### Required Configuration

```json
{
  "scalar.field": "revenue_sum"
}
```

**Required Fields**:
- `scalar.field` - Field containing the numeric value to display

## Legacy Settings (Deprecated)

These settings are supported but deprecated in favor of `column_settings`:

```json
{
  "scalar.locale": "en",
  "scalar.decimals": 2,
  "scalar.prefix": "$",
  "scalar.suffix": " USD",
  "scalar.scale": 1
}
```

## Modern Value Formatting

Use `column_settings` for all formatting (recommended approach):

```json
{
  "column_settings": {
    "[\"name\",\"revenue_sum\"]": {
      "number_style": "currency",
      "currency": "USD",
      "currency_style": "symbol",
      "decimals": 0,
      "scale": 0.001,
      "suffix": "K"
    }
  }
}
```

### Number Style Options

```json
{
  "number_style": "decimal|currency|percent|scientific"
}
```

- `"decimal"` - Standard number formatting
- `"currency"` - Currency formatting with symbol
- `"percent"` - Percentage formatting
- `"scientific"` - Scientific notation

### Currency Formatting

```json
{
  "currency": "USD",
  "currency_style": "symbol|code|name",
  "currency_in_header": false
}
```

- `currency_style`: `"symbol"` ($), `"code"` (USD), `"name"` (US dollars)
- `currency_in_header`: Show currency in title instead of with value

### Number Separators

```json
{
  "number_separators": ".,|, |. |,."
}
```

- `".,"` - 1,234.56 (US format)
- `", "` - 1 234,56 (French format)
- `". "` - 1 234.56 (Alternative)
- `",."` - 1.234,56 (German format)

### Additional Formatting

```json
{
  "decimals": 2,
  "scale": 0.001,
  "prefix": "$",
  "suffix": "K"
}
```

- `decimals` - Number of decimal places (0-10)
- `scale` - Multiply by this factor before display
- `prefix` - Text before the number
- `suffix` - Text after the number

## Click Behaviors

```json
{
  "click_behavior": {
    "type": "link",
    "linkType": "dashboard",
    "targetId": 15,
    "parameterMapping": {
      "value_filter": {
        "id": "value_filter",
        "source": {
          "type": "column",
          "id": "revenue_sum",
          "name": "Revenue Sum"
        },
        "target": {
          "type": "parameter",
          "id": "value_filter"
        }
      }
    }
  }
}
```

## Complete Examples

### Revenue Display with Scaling

```json
{
  "card.title": "Total Revenue",
  "scalar.field": "revenue_sum",
  "column_settings": {
    "[\"name\",\"revenue_sum\"]": {
      "number_style": "currency",
      "currency": "USD",
      "currency_style": "symbol",
      "decimals": 0,
      "scale": 0.001,
      "suffix": "K"
    }
  },
  "click_behavior": {
    "type": "link",
    "linkType": "dashboard",
    "targetId": 15
  }
}
```

### Customer Count

```json
{
  "card.title": "Total Customers",
  "scalar.field": "customer_count",
  "column_settings": {
    "[\"name\",\"customer_count\"]": {
      "number_style": "decimal",
      "decimals": 0,
      "number_separators": ".,",
      "suffix": " customers"
    }
  }
}
```

### Conversion Rate Percentage

```json
{
  "card.title": "Conversion Rate",
  "scalar.field": "conversion_rate",
  "column_settings": {
    "[\"name\",\"conversion_rate\"]": {
      "number_style": "percent",
      "decimals": 2,
      "scale": 0.01
    }
  }
}
```

### Growth Rate with Custom Formatting

```json
{
  "card.title": "YoY Growth",
  "scalar.field": "growth_rate",
  "column_settings": {
    "[\"name\",\"growth_rate\"]": {
      "number_style": "decimal",
      "decimals": 1,
      "prefix": "+",
      "suffix": "%",
      "scale": 100
    }
  }
}
```

### Average Order Value

```json
{
  "card.title": "Average Order Value",
  "scalar.field": "avg_order_value",
  "column_settings": {
    "[\"name\",\"avg_order_value\"]": {
      "number_style": "currency",
      "currency": "USD",
      "currency_style": "symbol",
      "decimals": 2,
      "currency_in_header": true
    }
  }
}
```

### Scientific Notation Example

```json
{
  "card.title": "Data Points Processed",
  "scalar.field": "data_points",
  "column_settings": {
    "[\"name\",\"data_points\"]": {
      "number_style": "scientific",
      "decimals": 2
    }
  }
}
```

## Common Patterns

### Financial KPI
```json
{
  "scalar.field": "revenue",
  "column_settings": {
    "[\"name\",\"revenue\"]": {
      "number_style": "currency",
      "currency": "USD",
      "decimals": 0
    }
  }
}
```

### Count Metric
```json
{
  "scalar.field": "total_count",
  "column_settings": {
    "[\"name\",\"total_count\"]": {
      "number_style": "decimal",
      "decimals": 0,
      "number_separators": ".,"
    }
  }
}
```

### Percentage Metric
```json
{
  "scalar.field": "success_rate",
  "column_settings": {
    "[\"name\",\"success_rate\"]": {
      "number_style": "percent",
      "decimals": 1,
      "scale": 0.01
    }
  }
}
```

## Use Cases

Scalar visualizations are ideal for:

- **KPI Dashboards**: Display key performance indicators prominently
- **Financial Metrics**: Revenue, profit, costs, and financial ratios
- **Operational Metrics**: Customer counts, order volumes, processing times
- **Performance Indicators**: Conversion rates, success rates, efficiency metrics
- **Summary Statistics**: Totals, averages, maximums, minimums
- **Goal Tracking**: Current values for comparison with targets

## Design Tips

- **Clear Titles**: Use descriptive titles that explain what the number represents
- **Appropriate Precision**: Choose decimal places that match the metric's precision needs
- **Scaling**: Use scaling and suffixes (K, M, B) for large numbers
- **Context**: Consider adding comparison information in the description
- **Currency Display**: Decide whether currency belongs in the title or with the number
- **Click Actions**: Add click behaviors to allow drill-down into details

## Migration from Legacy Settings

If you have old scalar configurations using deprecated settings, migrate them:

**Old (Deprecated)**:
```json
{
  "scalar.decimals": 2,
  "scalar.prefix": "$",
  "scalar.suffix": " USD"
}
```

**New (Recommended)**:
```json
{
  "column_settings": {
    "[\"name\",\"field_name\"]": {
      "decimals": 2,
      "prefix": "$",
      "suffix": " USD"
    }
  }
}
```