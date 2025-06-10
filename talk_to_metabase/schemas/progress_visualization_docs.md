# Progress Bar Visualization Settings Documentation

## Overview

Progress bars display a single value as progress toward a goal, shown as a horizontal bar that fills based on the percentage of completion. They're perfect for showing KPI achievement, task completion, and goal tracking.

## Core Settings

### Card-Level Settings

```json
{
  "card.title": "Sales Goal Progress",
  "card.description": "Progress towards quarterly sales target",
  "card.hide_empty": true
}
```

### Required Configuration

```json
{
  "progress.goal": 1000000
}
```

**Required Fields**:
- `progress.goal` - Target value that represents 100% progress (must be > 0)

## Visual Options

### Progress Bar Appearance

```json
{
  "progress.color": "#84BB4C",
  "progress.show_total": true
}
```

- `progress.color` - Hex color code for the progress bar (default: green)
- `progress.show_total` - Show actual value alongside percentage

## Value Formatting

```json
{
  "column_settings": {
    "[\"name\",\"current_sales\"]": {
      "number_style": "currency",
      "currency": "USD",
      "currency_style": "symbol",
      "decimals": 0
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
  "prefix": "$",
  "suffix": "K",
  "scale": 0.001
}
```

## Click Behaviors

```json
{
  "click_behavior": {
    "type": "link",
    "linkType": "dashboard",
    "targetId": 25,
    "parameterMapping": {
      "goal_filter": {
        "id": "goal_filter",
        "source": {
          "type": "column",
          "id": "current_value",
          "name": "Current Value"
        },
        "target": {
          "type": "parameter",
          "id": "goal_filter"
        }
      }
    }
  }
}
```

## Complete Examples

### Sales Goal Progress

```json
{
  "card.title": "Sales Goal Progress",
  "card.description": "Progress towards quarterly sales target",
  "progress.goal": 1000000,
  "progress.color": "#509EE3",
  "progress.show_total": true,
  "column_settings": {
    "[\"name\",\"current_sales\"]": {
      "number_style": "currency",
      "currency": "USD",
      "currency_style": "symbol",
      "decimals": 0
    }
  },
  "click_behavior": {
    "type": "link",
    "linkType": "dashboard",
    "targetId": 25
  }
}
```

### Task Completion Progress

```json
{
  "card.title": "Project Completion",
  "progress.goal": 100,
  "progress.color": "#84BB4C",
  "progress.show_total": false,
  "column_settings": {
    "[\"name\",\"completed_tasks\"]": {
      "number_style": "decimal",
      "decimals": 0,
      "suffix": " tasks"
    }
  }
}
```

### Revenue Target with Scaling

```json
{
  "card.title": "Monthly Revenue Target",
  "progress.goal": 500,
  "progress.color": "#F9CF48",
  "progress.show_total": true,
  "column_settings": {
    "[\"name\",\"monthly_revenue\"]": {
      "number_style": "currency",
      "currency": "USD",
      "scale": 0.001,
      "suffix": "K",
      "decimals": 0
    }
  }
}
```

## Common Patterns

### KPI Achievement
```json
{
  "progress.goal": 100,
  "progress.color": "#509EE3",
  "progress.show_total": true
}
```

### Financial Target
```json
{
  "progress.goal": 1000000,
  "progress.color": "#84BB4C",
  "column_settings": {
    "[\"name\",\"current_value\"]": {
      "number_style": "currency",
      "currency": "USD"
    }
  }
}
```

### Percentage Goal
```json
{
  "progress.goal": 100,
  "progress.color": "#88BF4D",
  "column_settings": {
    "[\"name\",\"completion_rate\"]": {
      "number_style": "percent",
      "scale": 0.01
    }
  }
}
```

## Use Cases

Progress bars are ideal for:

- **Goal Tracking**: Sales targets, revenue goals, performance objectives
- **Project Management**: Task completion, milestone achievement
- **KPI Dashboards**: Performance against targets
- **Campaign Monitoring**: Progress toward campaign goals
- **Completion Tracking**: Training completion, survey responses
- **Budget Monitoring**: Spending against budget allocations

## Design Tips

- **Color Choice**: Use green for positive progress, red for overdue/critical
- **Goal Setting**: Ensure goals are realistic and meaningful
- **Value Display**: Show totals when absolute numbers matter
- **Progress Context**: Use clear titles that explain what's being measured