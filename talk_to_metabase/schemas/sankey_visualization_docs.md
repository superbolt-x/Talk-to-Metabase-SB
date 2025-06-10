# Sankey Diagram Visualization Settings Documentation

## Overview

Sankey diagrams visualize flows between different nodes, where the width of each flow is proportional to the quantity being transferred. They're perfect for showing data flows, customer journeys, budget allocations, and any process where items move between categories.

## Core Settings

### Card-Level Settings

```json
{
  "card.title": "Customer Journey Flow",
  "card.description": "Flow of customers through different touchpoints",
  "card.hide_empty": true
}
```

### Required Configuration

```json
{
  "sankey.source": "from_touchpoint",
  "sankey.target": "to_touchpoint",
  "sankey.value": "customer_count"
}
```

**Required Fields**:
- `sankey.source` - Source node column (where flow originates)
- `sankey.target` - Target node column (where flow ends)
- `sankey.value` - Value column (flow quantity/weight)

## Visual Options

### Value Display

```json
{
  "sankey.show_values": true,
  "sankey.show_percentages": false
}
```

- `show_values` - Display numeric values on flow links
- `show_percentages` - Show percentages instead of absolute values

### Node Configuration

```json
{
  "sankey.node_width": 25,
  "sankey.node_padding": 15,
  "sankey.node_alignment": "justify"
}
```

**Node Options**:
- `node_width` - Width of node rectangles (10-100 pixels, default: 20)
- `node_padding` - Vertical spacing between nodes (5-50 pixels, default: 10)  
- `node_alignment` - How to align nodes: `"left"`, `"right"`, `"center"`, `"justify"`

### Flow Appearance

```json
{
  "sankey.link_opacity": 0.7
}
```

**Flow Options**:
- `link_opacity` - Opacity of flow links (0.1-1.0, default: 0.6)

## Color Configuration

```json
{
  "sankey.color_palette": [
    "#509EE3",
    "#88BF4D", 
    "#F9CF48",
    "#ED6E6E",
    "#A989C5"
  ]
}
```

Colors are applied to nodes and their associated flows automatically.

## Value Formatting

```json
{
  "column_settings": {
    "[\"name\",\"customer_count\"]": {
      "number_style": "decimal",
      "decimals": 0,
      "suffix": " customers"
    },
    "[\"name\",\"amount\"]": {
      "number_style": "currency",
      "currency": "USD",
      "decimals": 0
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
      "touchpoint_filter": {
        "id": "touchpoint_filter",
        "source": {
          "type": "column",
          "id": "from_touchpoint",
          "name": "From Touchpoint"
        },
        "target": {
          "type": "parameter",
          "id": "touchpoint_filter"
        }
      }
    }
  }
}
```

## Complete Examples

### Customer Journey Analysis

```json
{
  "card.title": "Customer Journey Flow",
  "card.description": "Flow of customers through different touchpoints",
  "sankey.source": "from_touchpoint",
  "sankey.target": "to_touchpoint",
  "sankey.value": "customer_count",
  "sankey.show_values": true,
  "sankey.show_percentages": false,
  "sankey.node_width": 25,
  "sankey.node_padding": 15,
  "sankey.link_opacity": 0.7,
  "sankey.node_alignment": "justify",
  "sankey.color_palette": [
    "#509EE3",
    "#88BF4D",
    "#F9CF48",
    "#ED6E6E",
    "#A989C5"
  ],
  "column_settings": {
    "[\"name\",\"customer_count\"]": {
      "number_style": "decimal",
      "decimals": 0,
      "suffix": " customers"
    }
  },
  "click_behavior": {
    "type": "crossfilter",
    "parameterMapping": {
      "touchpoint_filter": {
        "id": "touchpoint_filter",
        "source": {
          "type": "column",
          "id": "from_touchpoint",
          "name": "From Touchpoint"
        },
        "target": {
          "type": "parameter",
          "id": "touchpoint_filter"
        }
      }
    }
  }
}
```

### Budget Allocation Flow

```json
{
  "card.title": "Budget Allocation Flow",
  "sankey.source": "department",
  "sankey.target": "expense_category",
  "sankey.value": "amount",
  "sankey.show_values": true,
  "sankey.show_percentages": true,
  "sankey.node_width": 20,
  "sankey.node_padding": 10,
  "sankey.link_opacity": 0.6,
  "column_settings": {
    "[\"name\",\"amount\"]": {
      "number_style": "currency",
      "currency": "USD",
      "decimals": 0
    }
  }
}
```

### Website Traffic Flow

```json
{
  "card.title": "User Path Analysis",
  "sankey.source": "entry_page",
  "sankey.target": "exit_page", 
  "sankey.value": "session_count",
  "sankey.show_values": false,
  "sankey.show_percentages": true,
  "sankey.node_alignment": "left",
  "sankey.color_palette": [
    "#4285F4",
    "#34A853",
    "#FBBC04",
    "#EA4335"
  ],
  "column_settings": {
    "[\"name\",\"session_count\"]": {
      "number_style": "decimal",
      "decimals": 0,
      "suffix": " sessions"
    }
  }
}
```

### Supply Chain Flow

```json
{
  "card.title": "Supply Chain Flow",
  "sankey.source": "supplier",
  "sankey.target": "distribution_center",
  "sankey.value": "volume",
  "sankey.show_values": true,
  "sankey.node_width": 30,
  "sankey.node_padding": 20,
  "sankey.link_opacity": 0.8,
  "column_settings": {
    "[\"name\",\"volume\"]": {
      "number_style": "decimal",
      "decimals": 0,
      "suffix": " units"
    }
  }
}
```

## Common Patterns

### Process Flow Analysis
```json
{
  "sankey.source": "process_step_from",
  "sankey.target": "process_step_to",
  "sankey.value": "item_count"
}
```

### Revenue Flow Tracking
```json
{
  "sankey.source": "revenue_source",
  "sankey.target": "business_unit",
  "sankey.value": "revenue_amount",
  "sankey.show_percentages": true
}
```

### User Conversion Funnel
```json
{
  "sankey.source": "current_stage",
  "sankey.target": "next_stage",
  "sankey.value": "user_count",
  "sankey.show_values": true
}
```

## Use Cases

Sankey diagrams are perfect for:

- **Customer Journey**: Track user paths through websites or apps
- **Budget Allocation**: Show how budgets flow from departments to expenses
- **Supply Chain**: Visualize material flow through manufacturing
- **Revenue Attribution**: Track revenue from sources to business units
- **Process Analysis**: Understand flow through business processes
- **Energy Flow**: Visualize energy consumption and distribution
- **Data Migration**: Show data movement between systems

## Design Tips

- **Flow Direction**: Organize flows from left to right for clarity
- **Node Naming**: Use clear, descriptive names for source and target nodes
- **Value Context**: Ensure flow values are meaningful and comparable
- **Color Consistency**: Use consistent colors for related node types
- **Complexity Management**: Avoid too many nodes to maintain readability