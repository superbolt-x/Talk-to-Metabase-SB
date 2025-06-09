# Detail Visualization Settings Documentation

## Overview

Detail visualizations (also called object detail views) display information for a single record or entity in a structured format. They're ideal for showing comprehensive details about customers, products, orders, or any individual database record.

## Core Settings

### Card-Level Settings

```json
{
  "card.title": "Customer Profile",
  "card.description": "Detailed view of customer information",
  "card.hide_empty": true
}
```

### Layout Options

```json
{
  "detail.show_compact": false
}
```

- `false` - Standard layout with full field names and values
- `true` - Compact layout for space-efficient display

## Field Configuration

### Field Selection and Order

```json
{
  "detail.fields": [
    {
      "name": "customer_id",
      "fieldRef": ["field", 1, null],
      "enabled": true
    },
    {
      "name": "full_name", 
      "fieldRef": ["field", 2, null],
      "enabled": true
    },
    {
      "name": "email",
      "fieldRef": ["field", 3, null],
      "enabled": true
    }
  ]
}
```

**Field Reference Types**:
- `["field", field_id, options]` - Database field
- `["expression", "expression_name"]` - Custom expression

## Field Formatting

### Column Settings Structure

```json
{
  "column_settings": {
    "[\"ref\",[\"field\",3,null]]": {
      "column_title": "Email Address",
      "view_as": "email"
    },
    "[\"ref\",[\"field\",4,null]]": {
      "column_title": "Orders",
      "number_style": "decimal",
      "decimals": 0,
      "show_mini_bar": true
    }
  }
}
```

### Display Options

```json
{
  "view_as": "auto|link|email|image",
  "link_text": "View Details",
  "link_url": "https://example.com/user/{{value}}",
  "markdown_template": "**{{value}}**"
}
```

**View As Options**:
- `"auto"` - Default display based on field type
- `"link"` - Display as clickable link
- `"email"` - Format as email address
- `"image"` - Display as image (for URLs)

### Number Formatting

```json
{
  "number_style": "decimal|currency|percent|scientific",
  "currency": "USD",
  "currency_style": "symbol",
  "decimals": 2,
  "prefix": "$",
  "suffix": " USD",
  "show_mini_bar": true
}
```

### Date/Time Formatting

```json
{
  "date_style": "YYYY-MM-DD|MM/DD/YYYY|MMMM D, YYYY",
  "time_style": "HH:mm|h:mm A"
}
```

## Click Behaviors

### Field-Specific Click Actions

```json
{
  "column_settings": {
    "[\"ref\",[\"field\",1,null]]": {
      "click_behavior": {
        "type": "link",
        "linkType": "dashboard",
        "targetId": 456,
        "parameterMapping": {
          "customer_filter": {
            "id": "customer_filter",
            "source": {
              "type": "column",
              "id": "customer_id",
              "name": "Customer ID"
            },
            "target": {
              "type": "parameter",
              "id": "customer_filter"
            }
          }
        }
      }
    }
  }
}
```

**Click Behavior Types**:
- `"crossfilter"` - Filter connected dashboard cards
- `"link"` - Navigate to another resource
- `"none"` - Disable click behavior

## Complete Examples

### Customer Profile Detail

```json
{
  "card.title": "Customer Profile",
  "card.description": "Comprehensive customer information",
  "detail.show_compact": false,
  "detail.fields": [
    {
      "name": "customer_id",
      "fieldRef": ["field", 1, null],
      "enabled": true
    },
    {
      "name": "full_name",
      "fieldRef": ["field", 2, null],
      "enabled": true
    },
    {
      "name": "email",
      "fieldRef": ["field", 3, null],
      "enabled": true
    },
    {
      "name": "phone",
      "fieldRef": ["field", 4, null],
      "enabled": true
    },
    {
      "name": "total_orders",
      "fieldRef": ["field", 5, null],
      "enabled": true
    },
    {
      "name": "lifetime_value",
      "fieldRef": ["field", 6, null],
      "enabled": true
    }
  ],
  "column_settings": {
    "[\"ref\",[\"field\",1,null]]": {
      "column_title": "Customer ID"
    },
    "[\"ref\",[\"field\",2,null]]": {
      "column_title": "Full Name"
    },
    "[\"ref\",[\"field\",3,null]]": {
      "column_title": "Email Address",
      "view_as": "email"
    },
    "[\"ref\",[\"field\",4,null]]": {
      "column_title": "Phone Number"
    },
    "[\"ref\",[\"field\",5,null]]": {
      "column_title": "Total Orders",
      "number_style": "decimal",
      "decimals": 0,
      "show_mini_bar": true
    },
    "[\"ref\",[\"field\",6,null]]": {
      "column_title": "Lifetime Value",
      "number_style": "currency",
      "currency": "USD",
      "currency_style": "symbol",
      "decimals": 2
    }
  }
}
```

### Product Information Detail

```json
{
  "card.title": "Product Details",
  "detail.show_compact": true,
  "detail.fields": [
    {
      "name": "product_id",
      "fieldRef": ["field", 10, null],
      "enabled": true
    },
    {
      "name": "product_name",
      "fieldRef": ["field", 11, null],
      "enabled": true
    },
    {
      "name": "category",
      "fieldRef": ["field", 12, null],
      "enabled": true
    },
    {
      "name": "price",
      "fieldRef": ["field", 13, null],
      "enabled": true
    },
    {
      "name": "stock_quantity",
      "fieldRef": ["field", 14, null],
      "enabled": true
    },
    {
      "name": "product_url",
      "fieldRef": ["field", 15, null],
      "enabled": true
    }
  ],
  "column_settings": {
    "[\"ref\",[\"field\",13,null]]": {
      "column_title": "Price",
      "number_style": "currency",
      "currency": "USD",
      "decimals": 2
    },
    "[\"ref\",[\"field\",14,null]]": {
      "column_title": "Stock",
      "number_style": "decimal",
      "decimals": 0,
      "suffix": " units"
    },
    "[\"ref\",[\"field\",15,null]]": {
      "column_title": "Product Page",
      "view_as": "link",
      "link_text": "View Product"
    }
  }
}
```

### Order Summary Detail

```json
{
  "card.title": "Order Details",
  "detail.fields": [
    {
      "name": "order_id",
      "fieldRef": ["field", 20, null],
      "enabled": true
    },
    {
      "name": "order_date",
      "fieldRef": ["field", 21, null],
      "enabled": true
    },
    {
      "name": "customer_name",
      "fieldRef": ["field", 22, null],
      "enabled": true
    },
    {
      "name": "total_amount",
      "fieldRef": ["field", 23, null],
      "enabled": true
    },
    {
      "name": "status",
      "fieldRef": ["field", 24, null],
      "enabled": true
    }
  ],
  "column_settings": {
    "[\"ref\",[\"field\",21,null]]": {
      "column_title": "Order Date",
      "date_style": "MMMM D, YYYY",
      "time_style": "h:mm A"
    },
    "[\"ref\",[\"field\",22,null]]": {
      "column_title": "Customer",
      "click_behavior": {
        "type": "link",
        "linkType": "dashboard",
        "targetId": 789
      }
    },
    "[\"ref\",[\"field\",23,null]]": {
      "column_title": "Total",
      "number_style": "currency",
      "currency": "USD",
      "decimals": 2
    }
  }
}
```

## Common Patterns

### User Profile View
```json
{
  "detail.fields": [
    {"name": "user_id", "fieldRef": ["field", 1, null], "enabled": true},
    {"name": "username", "fieldRef": ["field", 2, null], "enabled": true},
    {"name": "email", "fieldRef": ["field", 3, null], "enabled": true}
  ]
}
```

### Product Catalog Detail
```json
{
  "detail.show_compact": true,
  "detail.fields": [
    {"name": "sku", "fieldRef": ["field", 10, null], "enabled": true},
    {"name": "name", "fieldRef": ["field", 11, null], "enabled": true},
    {"name": "price", "fieldRef": ["field", 12, null], "enabled": true}
  ]
}
```

### Transaction Record
```json
{
  "detail.fields": [
    {"name": "transaction_id", "fieldRef": ["field", 20, null], "enabled": true},
    {"name": "amount", "fieldRef": ["field", 21, null], "enabled": true},
    {"name": "date", "fieldRef": ["field", 22, null], "enabled": true}
  ]
}
```

## Use Cases

Detail visualizations are perfect for:

- **Customer Support**: Display complete customer information
- **Product Management**: Show detailed product specifications
- **Order Processing**: View comprehensive order details
- **User Profiles**: Present user account information
- **Record Investigation**: Examine specific database records
- **Data Validation**: Review individual entries for accuracy