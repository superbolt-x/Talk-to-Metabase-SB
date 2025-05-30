# Metabase Visualization Settings API Documentation

This comprehensive guide documents the `visualization_settings` parameter format for the Metabase `/api/card/{id}` endpoint. These settings control how charts and visualizations appear in the Metabase interface.

## Overview

The `visualization_settings` field in a Card object contains a JSON object that defines how the visualization should be displayed. The structure varies depending on the chart type specified in the `display` field.

## Common Chart Types and Their Display Values

- `table` - Data table
- `bar` - Bar chart
- `line` - Line chart
- `pie` - Pie chart
- `scalar` - Single number
- `row` - Horizontal bar chart  
- `area` - Area chart
- `combo` - Combination chart
- `pivot` - Pivot table
- `smartscalar` - Smart scalar (with comparison)
- `gauge` - Gauge chart
- `progress` - Progress bar
- `funnel` - Funnel chart
- `object` - Object detail
- `map` - Geographic map
- `scatter` - Scatter plot
- `waterfall` - Waterfall chart
- `sankey` - Sankey diagram

## Virtual Card Types

These are special display types for dashboard cards:
- `action` - Action button
- `heading` - Text heading
- `link` - Link card
- `placeholder` - Placeholder
- `text` - Text block
- `iframe` - Embedded iframe

## Common Settings Structure

All visualization types share some common settings:

```json
{
  "card.title": "Custom Title",
  "card.description": "Custom Description",
  "card.hide_empty": false,
  "click_behavior": {
    "type": "crossfilter|link|none",
    "linkType": "question|dashboard|url",
    "targetId": 123,
    "linkTemplate": "/dashboard/1?param={{column:Field}}"
  }
}
```

## Chart-Specific Settings

### Table Visualization (`"display": "table"`)

```json
{
  "table.columns": [
    {
      "name": "ID",
      "fieldRef": ["field", 1, null],
      "enabled": true
    },
    {
      "name": "Name", 
      "fieldRef": ["expression", "Custom Name"],
      "enabled": true
    }
  ],
  "column_settings": {
    "[\"ref\",[\"field\",1,null]]": {
      "column_title": "Custom Column Name",
      "show_mini_bar": true,
      "number_style": "currency",
      "currency": "USD",
      "currency_style": "symbol",
      "currency_in_header": false,
      "number_separators": ",.",
      "decimals": 2,
      "scale": 1,
      "prefix": "$",
      "suffix": " USD"
    },
    "[\"name\",\"Column Name\"]": {
      "column_title": "Display Name",
      "time_style": "HH:mm"
    }
  }
}
```

### Line Chart (`"display": "line"`)

```json
{
  "graph.dimensions": ["Field1"],
  "graph.metrics": ["Field2", "Field3"],
  "graph.x_axis.scale": "linear|log|pow|timeseries",
  "graph.y_axis.scale": "linear|log|pow",
  "graph.x_axis.axis_enabled": true,
  "graph.y_axis.axis_enabled": true,
  "graph.x_axis.labels_enabled": true,
  "graph.y_axis.labels_enabled": true,
  "graph.x_axis.title_text": "X Axis Label",
  "graph.y_axis.title_text": "Y Axis Label",
  "graph.y_axis.auto_range": true,
  "graph.y_axis.min": 0,
  "graph.y_axis.max": 100,
  "graph.y_axis.auto_split": false,
  "graph.y_axis.unpin_from_zero": false,
  "graph.show_values": false,
  "graph.label_value_frequency": "fit|all",
  "graph.label_value_formatting": "auto|compact|full",
  "graph.show_trendline": false,
  "graph.tooltip_type": "series_comparison|default",
  "graph.tooltip_columns": ["additional_field"],
  "series_settings": {
    "Field2": {
      "display": "line|bar|area",
      "line.interpolate": "linear|cardinal|step-before|step-after",
      "line.marker_enabled": true,
      "line.missing": "interpolate|zero|none",
      "color": "#509EE3"
    }
  }
}
```

### Bar Chart (`"display": "bar"`)

```json
{
  "graph.dimensions": ["Field1"],
  "graph.metrics": ["Field2"],
  "stackable.stack_type": null, // null, "stacked", "normalized"
  "graph.show_values": true,
  "graph.show_stack_values": "total|series|all",
  "graph.x_axis.scale": "ordinal|linear|timeseries",
  "graph.y_axis.scale": "linear|log|pow",
  "graph.series_order": [
    {"key": "Series1", "enabled": true, "color": "#509EE3", "name": "Custom Name"},
    {"key": "Series2", "enabled": false, "color": "#88BF4D"}
  ]
}
```

### Area Chart (`"display": "area"`)

Similar to line chart with additional stacking options:

```json
{
  "graph.dimensions": ["Date"],
  "graph.metrics": ["Revenue", "Profit"],
  "stackable.stack_type": "stacked",
  "series_settings": {
    "Revenue": {
      "display": "area",
      "color": "#509EE3"
    },
    "Profit": {
      "display": "area", 
      "color": "#88BF4D"
    }
  }
}
```

### Pie Chart (`"display": "pie"`)

```json
{
  "pie.dimension": "Category",
  "pie.metric": "Count",
  "pie.show_legend": true,
  "pie.show_total": false,
  "pie.show_labels": true,
  "pie.percent_visibility": "off|legend|inside|both",
  "pie.decimal_places": 1,
  "pie.slice_threshold": 2.5,
  "pie.sort_rows": "asc|desc",
  "pie.rows": [
    {
      "key": "Category A",
      "name": "Custom Name A",
      "color": "#509EE3",
      "enabled": true
    }
  ],
  "series_settings": {
    "Category A": {
      "name": "Custom Category Name",
      "color": "#509EE3"
    }
  }
}
```

### Scalar/Number (`"display": "scalar"`)

```json
{
  "scalar.field": "Field1",
  "scalar.locale": "en",
  "scalar.decimals": 2,
  "scalar.prefix": "$",
  "scalar.suffix": " USD",
  "scalar.scale": 1,
  "column_settings": {
    "[\"name\",\"Field1\"]": {
      "number_style": "currency|percent|scientific|decimal",
      "currency": "USD",
      "currency_style": "symbol|code|name",
      "number_separators": ",.",
      "decimals": 2,
      "scale": 1,
      "prefix": "$",
      "suffix": " USD"
    }
  }
}
```

### Smart Scalar (`"display": "smartscalar"`)

```json
{
  "scalar.field": "Revenue",
  "scalar.comparisons": [
    {
      "id": "comparison1",
      "type": "previousValue|previousPeriod|periodsAgo|staticNumber|anotherColumn",
      "column": "Previous Revenue", // for anotherColumn type
      "value": 1000, // for staticNumber or periodsAgo type
      "label": "vs Last Month"
    }
  ]
}
```

### Gauge Chart (`"display": "gauge"`)

```json
{
  "gauge.field": "Progress",
  "gauge.min": 0,
  "gauge.max": 100,
  "gauge.segments": [
    {"min": 0, "max": 30, "color": "#ED6E6E", "label": "Poor"},
    {"min": 30, "max": 70, "color": "#F9CF48", "label": "Average"},
    {"min": 70, "max": 100, "color": "#84BB4C", "label": "Good"}
  ],
  "gauge.show_values": true
}
```

### Progress Bar (`"display": "progress"`)

```json
{
  "progress.goal": 100,
  "progress.color": "#84BB4C"
}
```

### Scatter Plot (`"display": "scatter"`)

```json
{
  "graph.dimensions": ["X_Field"],
  "graph.metrics": ["Y_Field"],
  "scatter.bubble": "Size_Field", // Optional bubble size field
  "graph.x_axis.scale": "linear|log|pow",
  "graph.y_axis.scale": "linear|log|pow"
}
```

### Map Visualization (`"display": "map"`)

```json
{
  "map.type": "region|pin",
  "map.region": "us_states|world_countries|custom",
  "map.latitude_column": "latitude",
  "map.longitude_column": "longitude",
  "map.metric_column": "population",
  "map.heat_map": false,
  "map.marker_style": "marker|heat"
}
```

### Funnel Chart (`"display": "funnel"`)

```json
{
  "funnel.dimension": "Stage",
  "funnel.metric": "Count",
  "funnel.type": "funnel|bar"
}
```

### Combo Chart (`"display": "combo"`)

```json
{
  "graph.dimensions": ["Date"],
  "graph.metrics": ["Revenue", "Orders"],
  "series_settings": {
    "Revenue": {
      "display": "line",
      "axis": "left",
      "color": "#509EE3"
    },
    "Orders": {
      "display": "bar", 
      "axis": "right",
      "color": "#88BF4D"
    }
  },
  "graph.y_axis.auto_split": true
}
```

### Waterfall Chart (`"display": "waterfall"`)

```json
{
  "waterfall.dimension": "Category",
  "waterfall.metric": "Change",
  "waterfall.increase_color": "#84BB4C",
  "waterfall.decrease_color": "#ED6E6E",
  "waterfall.total_color": "#509EE3",
  "waterfall.show_total": true
}
```

### Pivot Table (`"display": "pivot"`)

```json
{
  "pivot_table.column_split": {"rows": ["Field1"], "columns": ["Field2"], "values": ["Field3"]},
  "pivot.show_row_totals": true,
  "pivot.show_column_totals": true,
  "column_settings": {
    "[\"name\",\"Field3\"]": {
      "number_style": "currency",
      "currency": "USD"
    }
  }
}
```

## Column Settings Format

Column settings use specific key formats to identify columns:

### Field References (for database fields)
```json
"[\"ref\",[\"field\",123,null]]": {
  "column_title": "Custom Name"
}
```

### Field References with Options
```json
"[\"ref\",[\"field\",123,{\"base-type\":\"type/Integer\"}]]": {
  "number_style": "currency"
}
```

### Column Names (for expressions, aggregations)
```json
"[\"name\",\"Column Name\"]": {
  "column_title": "Display Name"
}
```

### Expression References
```json
"[\"ref\",[\"expression\",\"Custom Calculation\"]]": {
  "number_style": "percent"
}
```

## Click Behavior Settings

### Crossfilter (Dashboard filtering)
```json
{
  "click_behavior": {
    "type": "crossfilter",
    "parameterMapping": {
      "parameter_id": {
        "source": {"type": "column", "id": "Field", "name": "Field"},
        "target": {"type": "parameter", "id": "parameter_id"},
        "id": "parameter_id"
      }
    }
  }
}
```

### Link to Question
```json
{
  "click_behavior": {
    "type": "link",
    "linkType": "question",
    "targetId": 123,
    "linkTextTemplate": "View Details",
    "parameterMapping": {}
  }
}
```

### Link to Dashboard
```json
{
  "click_behavior": {
    "type": "link", 
    "linkType": "dashboard",
    "targetId": 456,
    "parameterMapping": {
      "dashboard_param_id": {
        "source": {"type": "column", "id": "Field", "name": "Field"},
        "target": {"type": "parameter", "id": "dashboard_param_id"},
        "id": "dashboard_param_id"
      }
    }
  }
}
```

### Link to URL
```json
{
  "click_behavior": {
    "type": "link",
    "linkType": "url", 
    "linkTemplate": "https://example.com/details?id={{column:ID}}"
  }
}
```

## Series Settings Format

Series settings control individual data series in multi-series charts:

```json
{
  "series_settings": {
    "Series Name": {
      "display": "line|bar|area",
      "color": "#509EE3", 
      "name": "Custom Display Name",
      "axis": "left|right", // for combo charts
      "line.interpolate": "linear|cardinal|step-before|step-after",
      "line.marker_enabled": true,
      "line.missing": "interpolate|zero|none"
    }
  }
}
```

## Number Formatting Options

Common number formatting settings available in `column_settings`:

```json
{
  "number_style": "decimal|currency|percent|scientific", 
  "currency": "USD|EUR|GBP|JPY|...",
  "currency_style": "symbol|code|name",
  "currency_in_header": false,
  "number_separators": ".,|, |. |,.| .",
  "decimals": 2,
  "scale": 1,
  "prefix": "$",
  "suffix": " USD"
}
```

## Date/Time Formatting Options

```json
{
  "date_style": "YYYY-MM-DD|MM/DD/YYYY|DD/MM/YYYY|MMMM D, YYYY|...",
  "time_style": "HH:mm|HH:mm:ss|h:mm A|h:mm:ss A|...",
  "date_separator": "-|/|.",
  "date_abbreviate": true
}
```

## Color Settings

Colors can be specified as:
- Hex codes: `"#509EE3"`
- RGB: `"rgb(80, 158, 227)"`
- Metabase color names: `"brand"|"accent1"|"accent2"|...`

## Best Practices

1. **Always validate field references** - Ensure field IDs exist in your database
2. **Test with your data** - Visualization settings depend on your specific data structure
3. **Use meaningful names** - Custom titles improve dashboard readability
4. **Consider performance** - Complex visualizations may impact load times
5. **Mobile compatibility** - Test settings on mobile devices

## Example Complete Card API Call

```json
{
  "name": "Sales by Region",
  "display": "bar",
  "visualization_settings": {
    "graph.dimensions": ["region"],
    "graph.metrics": ["total_sales"],
    "graph.show_values": true,
    "graph.y_axis.title_text": "Total Sales ($)",
    "graph.x_axis.title_text": "Region",
    "column_settings": {
      "[\"name\",\"total_sales\"]": {
        "number_style": "currency",
        "currency": "USD",
        "decimals": 0
      }
    },
    "series_settings": {
      "total_sales": {
        "color": "#509EE3"
      }
    }
  },
  "dataset_query": {
    "type": "query",
    "query": {
      "source-table": 1,
      "aggregation": [["sum", ["field", 5, null]]],
      "breakout": [["field", 3, null]]
    },
    "database": 1
  }
}
```

This documentation covers the major visualization types and settings available in Metabase. The exact settings available may vary based on your Metabase version and the specific data being visualized.