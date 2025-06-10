# Map Visualization Settings Documentation

## Overview

Map visualizations display geographic data using either region-based choropleth maps or pin-based scatter maps. They're perfect for analyzing location-based data, regional performance, and geographic distributions.

## Core Settings

### Card-Level Settings

```json
{
  "card.title": "Sales by State",
  "card.description": "Geographic distribution of sales",
  "card.hide_empty": true
}
```

### Map Type Configuration

```json
{
  "map.type": "region|pin"
}
```

- `"region"` - Choropleth map coloring geographic regions
- `"pin"` - Scatter map with pins/markers at specific locations

## Region Maps

### Required Configuration

```json
{
  "map.type": "region",
  "map.region": "us_states|world_countries|custom",
  "map.dimension_column": "state",
  "map.metric_column": "total_sales"
}
```

### Region Options

```json
{
  "map.region": "us_states|world_countries|custom"
}
```

- `"us_states"` - United States state map
- `"world_countries"` - World countries map
- `"custom"` - Custom geographic regions

### Heat Map Styling

```json
{
  "map.heat_map": true,
  "map.color_range": [
    "#FEF0D9",
    "#FDD49E", 
    "#FDBB84",
    "#FC8D59",
    "#EF6548",
    "#D7301F",
    "#990000"
  ]
}
```

## Pin Maps

### Required Configuration

```json
{
  "map.type": "pin",
  "map.latitude_column": "latitude",
  "map.longitude_column": "longitude",
  "map.metric_column": "monthly_revenue"
}
```

### Pin Styling

```json
{
  "map.marker_style": "marker|heat",
  "map.pin_size": "small|medium|large"
}
```

- `marker` - Individual pin markers
- `heat` - Heat map style visualization

## Map View Configuration

### Zoom and Center

```json
{
  "map.zoom": 7,
  "map.center_latitude": 39.8283,
  "map.center_longitude": -98.5795,
  "map.auto_zoom": false
}
```

### Auto Zoom

```json
{
  "map.auto_zoom": true
}
```

When enabled, automatically fits the map to show all data points.

## Column Formatting

```json
{
  "column_settings": {
    "[\"name\",\"total_sales\"]": {
      "number_style": "currency",
      "currency": "USD",
      "decimals": 0
    },
    "[\"name\",\"state\"]": {
      "column_title": "State"
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
      "state_filter": {
        "id": "state_filter",
        "source": {
          "type": "column",
          "id": "state",
          "name": "State"
        },
        "target": {
          "type": "parameter",
          "id": "state_filter"
        }
      }
    }
  }
}
```

## Complete Examples

### US States Sales Map

```json
{
  "card.title": "Sales by State",
  "card.description": "Geographic distribution of sales across US states",
  "map.type": "region",
  "map.region": "us_states",
  "map.dimension_column": "state",
  "map.metric_column": "total_sales",
  "map.heat_map": true,
  "map.color_range": [
    "#FEF0D9",
    "#FDD49E",
    "#FDBB84", 
    "#FC8D59",
    "#EF6548",
    "#D7301F",
    "#990000"
  ],
  "column_settings": {
    "[\"name\",\"total_sales\"]": {
      "number_style": "currency",
      "currency": "USD",
      "decimals": 0
    }
  },
  "click_behavior": {
    "type": "crossfilter",
    "parameterMapping": {
      "state_filter": {
        "id": "state_filter",
        "source": {
          "type": "column",
          "id": "state",
          "name": "State"
        },
        "target": {
          "type": "parameter",
          "id": "state_filter"
        }
      }
    }
  }
}
```

### Store Locations Pin Map

```json
{
  "card.title": "Store Locations",
  "card.description": "Pin map showing store locations and performance",
  "map.type": "pin",
  "map.latitude_column": "latitude",
  "map.longitude_column": "longitude", 
  "map.metric_column": "monthly_revenue",
  "map.marker_style": "marker",
  "map.pin_size": "medium",
  "map.auto_zoom": true,
  "column_settings": {
    "[\"name\",\"monthly_revenue\"]": {
      "number_style": "currency",
      "currency": "USD",
      "decimals": 0
    }
  }
}
```

### Global Customer Distribution

```json
{
  "card.title": "Global Customer Distribution",
  "map.type": "region",
  "map.region": "world_countries",
  "map.dimension_column": "country",
  "map.metric_column": "customer_count",
  "map.heat_map": true,
  "map.color_range": [
    "#F7FBFF",
    "#DEEBF7",
    "#C6DBEF",
    "#9ECAE1",
    "#6BAED6",
    "#4292C6",
    "#2171B5",
    "#084594"
  ]
}
```

### Custom Region Map

```json
{
  "map.type": "region",
  "map.region": "custom",
  "map.dimension_column": "sales_territory",
  "map.metric_column": "quota_achievement",
  "map.heat_map": true,
  "column_settings": {
    "[\"name\",\"quota_achievement\"]": {
      "number_style": "percent",
      "decimals": 1,
      "scale": 0.01
    }
  }
}
```

## Common Patterns

### Regional Performance
```json
{
  "map.type": "region",
  "map.region": "us_states",
  "map.dimension_column": "state",
  "map.metric_column": "performance_score"
}
```

### Location Analysis
```json
{
  "map.type": "pin",
  "map.latitude_column": "lat",
  "map.longitude_column": "lng",
  "map.metric_column": "value"
}
```

### Heat Map Visualization
```json
{
  "map.heat_map": true,
  "map.marker_style": "heat",
  "map.auto_zoom": true
}
```

## Use Cases

Map visualizations are ideal for:

- **Regional Sales Analysis**: Compare performance across states/countries
- **Store Performance**: Visualize location-based business metrics
- **Customer Distribution**: Show geographic spread of customer base
- **Market Penetration**: Analyze presence in different regions
- **Logistics Optimization**: Identify service areas and coverage gaps
- **Risk Assessment**: Geographic risk and opportunity analysis

## Tips for Effective Maps

- **Data Quality**: Ensure location data is accurate and consistent
- **Color Schemes**: Use intuitive color gradients (light to dark for intensity)
- **Region Names**: Match geographic identifiers exactly with map regions
- **Zoom Levels**: Set appropriate zoom for your data's geographic scope
- **Pin Density**: Consider data density when choosing marker styles