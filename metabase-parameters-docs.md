# Complete Guide to Metabase Parameters and Parameter Mappings

## Overview

This documentation provides a comprehensive guide to using parameters and parameter mappings in Metabase's API endpoints `/api/card/{id}` and `/api/dashboard/{id}`. Parameters allow you to create dynamic filters for your questions and dashboards.

## Table of Contents

1. [Parameter Structure](#parameter-structure)
2. [Parameter Types](#parameter-types)
3. [Parameter Mapping Structure](#parameter-mapping-structure)
4. [Targets](#targets)
5. [Complete Examples](#complete-examples)
6. [Best Practices](#best-practices)

## Parameter Structure

A parameter is a JSON object with the following structure:

```json
{
  "id": "unique-parameter-id",
  "type": "parameter-type",
  "name": "Display Name",
  "slug": "url-slug",
  "sectionId": "section-identifier",
  "default": "default-value",
  "required": false,
  "values_source_type": null,
  "values_source_config": {},
  "temporal_units": ["week", "month"]
}
```

### Required Fields

- **`id`** (string): Unique identifier for the parameter. Used to link parameter mappings.
- **`type`** (string): The parameter type (see [Parameter Types](#parameter-types) below).
- **`name`** (string): Human-readable display name for the parameter.

### Optional Fields

- **`slug`** (string): URL-friendly version of the name.
- **`sectionId`** (string): Groups parameters in the UI.
- **`default`** (any): Default value for the parameter.
- **`required`** (boolean): Whether the parameter is required.
- **`values_source_type`** (string): Source for parameter values (`"static-list"`, `"card"`, or `null`).
- **`values_source_config`** (object): Configuration for values source.
- **`options`** (object): Parameter-specific options. Structure:
  ```json
  {
    "case-sensitive": true  // For string parameters, whether matching is case-sensitive
  }
  ```
- **`filteringParameters`** (array): List of parameter IDs that can filter this parameter's values
- **`isMultiSelect`** (boolean): Whether the parameter allows multiple value selection
- **`temporal_units`** (array): Available temporal units for temporal-unit parameters. Valid values:
  - **Date truncation units**: `"day"`, `"week"`, `"month"`, `"quarter"`, `"year"`
  - **Date extraction units**: `"day-of-week"`, `"day-of-month"`, `"day-of-year"`, `"week-of-year"`, `"month-of-year"`, `"quarter-of-year"`, `"year"`, `"year-of-era"`
  - **Time truncation units**: `"millisecond"`, `"second"`, `"minute"`, `"hour"`
  - **Time extraction units**: `"second-of-minute"`, `"minute-of-hour"`, `"hour-of-day"`
  - **Special**: `"default"`
  - **Date truncation units**: `"day"`, `"week"`, `"month"`, `"quarter"`, `"year"`
  - **Date extraction units**: `"day-of-week"`, `"day-of-month"`, `"day-of-year"`, `"week-of-year"`, `"month-of-year"`, `"quarter-of-year"`, `"year"`, `"year-of-era"`
  - **Time truncation units**: `"millisecond"`, `"second"`, `"minute"`, `"hour"`
  - **Time extraction units**: `"second-of-minute"`, `"minute-of-hour"`, `"hour-of-day"`
  - **Special**: `"default"`

## Parameter Types

### String Parameters

For text-based filtering:

- **`string/=`** - Exact match
- **`string/!=`** - Not equal
- **`string/contains`** - Contains text
- **`string/does-not-contain`** - Does not contain text
- **`string/starts-with`** - Starts with text
- **`string/ends-with`** - Ends with text
- **`text`** - Generic text parameter (legacy)

### Number Parameters

For numeric filtering:

- **`number/=`** - Exact match
- **`number/!=`** - Not equal
- **`number/>`** - Greater than
- **`number/>=`** - Greater than or equal
- **`number/<`** - Less than
- **`number/<=`** - Less than or equal
- **`number/between`** - Between two values
- **`number`** - Generic number parameter (legacy)

### Date Parameters

For date/time filtering:

- **`date/single`** - Single date (like January 31, 2016)
- **`date/range`** - Date range (like December 25, 2015 - February 14, 2016)
- **`date/relative`** - Relative date (like "the previous 7 days" or "this month")
- **`date/month-year`** - Month and year picker (like January 2016)
- **`date/quarter-year`** - Quarter and year picker (like Q1 2016)
- **`date/all-options`** - All date options available (contains all of the above)
- **`date`** - Generic date parameter (legacy)

#### Date Relative Values

When using `date/relative` parameters, you can use these predefined values:

**Predefined shortcuts:**
- **`thisday`** - Today
- **`past1days`** - Yesterday  
- **`past7days`** - Previous 7 Days
- **`past30days`** - Previous 30 Days
- **`past1weeks`** - Previous Week
- **`past1months`** - Previous Month
- **`past1years`** - Previous Year
- **`thisweek`** - This Week
- **`thismonth`** - This Month
- **`thisyear`** - This Year

**Custom relative date patterns:**

You can also use custom patterns for more specific date ranges:

- **`past{N}days`** - Last N days (e.g., `"past28days"` for last 28 days)
- **`past{N}weeks`** - Last N weeks (e.g., `"past4weeks"` for last 4 weeks)  
- **`past{N}months`** - Last N months (e.g., `"past6months"` for last 6 months)
- **`past{N}years`** - Last N years (e.g., `"past2years"` for last 2 years)
- **`next{N}days`** - Next N days (e.g., `"next14days"` for next 14 days)
- **`next{N}weeks`** - Next N weeks (e.g., `"next8weeks"` for next 8 weeks)
- **`next{N}months`** - Next N months (e.g., `"next3months"` for next 3 months)
- **`next{N}years`** - Next N years (e.g., `"next1years"` for next year)

**Advanced patterns:**

- **`past{N}{unit}s~`** - Include current period (e.g., `"past7days~"` includes today)
- **`past{N}{unit}s-from-{M}{unit2}s`** - Offset ranges (e.g., `"past30days-from-1years"` for 30 days starting 1 year ago)

### Location Parameters

For geographic/location-based filtering:

- **`location/city`** - City parameter
- **`location/state`** - State/province parameter
- **`location/zip_code`** - ZIP/postal code parameter
- **`location/country`** - Country parameter

### Special Parameters

- **`id`** - ID parameter (typically for primary keys)
- **`category`** - Category parameter (for dropdown lists)
- **`temporal-unit`** - Temporal unit parameter (for grouping by time periods)
- **`boolean`** - Boolean parameter (true/false values)

## Parameter Mapping Structure

Parameter mappings connect dashboard parameters to specific fields in cards. Each mapping has this structure:

```json
{
  "parameter_id": "parameter-id-from-dashboard",
  "card_id": 123,
  "target": ["dimension", ["field", 456, null]]
}
```

### Required Fields

- **`parameter_id`** (string): Must match a parameter ID from the dashboard's parameters array.
- **`target`** (array): Specifies what field/dimension this parameter maps to.

### Optional Fields

- **`card_id`** (number): ID of the card this mapping applies to. Required for card-specific mappings.

## Targets

Targets specify what the parameter maps to. They use MBQL (Metabase Query Language) syntax.

### Field Targets

Map to a specific database field:

```json
["dimension", ["field", 123, null]]
```

Where `123` is the field ID and `null` represents field options.

### Field with Options

```json
["dimension", ["field", 123, {"source-field": 456}]]
```

### Template Tag Targets (Native Queries)

For native SQL queries with template tags:

```json
["dimension", ["template-tag", "tag_name"]]
```

### Variable Targets

For template tag variables:

```json
["variable", ["template-tag", "variable_name"]]
```

### Text Tag Targets

For text substitution:

```json
["text-tag", "tag_name"]
```

## Complete Examples

### Example 1: Dashboard with Text Parameter

```json
{
  "name": "Sales Dashboard",
  "parameters": [
    {
      "id": "category_filter",
      "type": "string/contains",
      "name": "Product Category",
      "slug": "category",
      "sectionId": "filters",
      "default": null
    }
  ]
}
```

### Example 2: Card with Parameter Mappings

```json
{
  "name": "Sales by Category",
  "parameter_mappings": [
    {
      "parameter_id": "category_filter",
      "card_id": 42,
      "target": ["dimension", ["field", 789, null]]
    }
  ]
}
```

### Example 3: Advanced Dashboard with Multiple Parameter Types

```json
{
  "name": "Advanced Analytics Dashboard",
  "parameters": [
    {
      "id": "date_range",
      "type": "date/range",
      "name": "Date Range",
      "slug": "date-range",
      "sectionId": "time",
      "default": "past30days"
    },
    {
      "id": "status_filter",
      "type": "category",
      "name": "Order Status",
      "slug": "status",
      "sectionId": "filters",
      "values_source_type": "static-list",
      "values_source_config": {
        "values": ["pending", "shipped", "delivered", "cancelled"]
      }
    },
    {
      "id": "revenue_min",
      "type": "number/>=",
      "name": "Minimum Revenue",
      "slug": "min-revenue",
      "sectionId": "financial",
      "default": 1000
    },
    {
      "id": "time_unit",
      "type": "temporal-unit",
      "name": "Time Grouping",
      "slug": "time-unit",
      "sectionId": "time",
      "temporal_units": ["day", "week", "month", "quarter", "year"]
    }
  ]
}
```

### Example 4: Complex Parameter Mappings

```json
{
  "name": "Revenue Analysis Card",
  "parameter_mappings": [
    {
      "parameter_id": "date_range",
      "card_id": 100,
      "target": ["dimension", ["field", 15, null]]
    },
    {
      "parameter_id": "status_filter",
      "card_id": 100,
      "target": ["dimension", ["field", 23, null]]
    },
    {
      "parameter_id": "revenue_min",
      "card_id": 100,
      "target": ["dimension", ["field", 45, null]]
    }
  ]
}
```

### Example 5: Native Query with Template Tags

```json
{
  "name": "Custom SQL Dashboard",
  "parameters": [
    {
      "id": "user_id",
      "type": "id",
      "name": "User ID",
      "slug": "user-id",
      "sectionId": "user"
    },
    {
      "id": "search_term",
      "type": "text",
      "name": "Search Term",
      "slug": "search",
      "sectionId": "search"
    }
  ]
}
```

With corresponding card parameter mappings:

```json
{
  "name": "User Activity Report",
  "parameter_mappings": [
    {
      "parameter_id": "user_id",
      "card_id": 200,
      "target": ["dimension", ["template-tag", "user_id"]]
    },
    {
      "parameter_id": "search_term",
      "card_id": 200,
      "target": ["variable", ["template-tag", "search_term"]]
    }
  ]
}
```

### Example 6: Values from Another Card

```json
{
  "id": "dynamic_category",
  "type": "category",
  "name": "Product Category",
  "slug": "category",
  "values_source_type": "card",
  "values_source_config": {
    "card_id": 150,
    "value_field": ["field", 789, null],
    "label_field": ["field", 790, null]
  }
}
```

### Example 7: Temporal Unit Parameter

```json
{
  "id": "time_grouping",
  "type": "temporal-unit",
  "name": "Group By Time Unit",
  "slug": "time-grouping",
  "sectionId": "time",
  "temporal_units": ["day", "week", "month", "quarter", "year"],
  "default": "month"
}
```

### Example 8: Location Parameters

```json
{
  "name": "Store Locations Dashboard",
  "parameters": [
    {
      "id": "store_city",
      "type": "location/city",
      "name": "Store City",
      "slug": "city",
      "sectionId": "location"
    },
    {
      "id": "store_state",
      "type": "location/state", 
      "name": "Store State",
      "slug": "state",
      "sectionId": "location"
    },
    {
      "id": "zip_code",
      "type": "location/zip_code",
      "name": "ZIP Code",
      "slug": "zip",
      "sectionId": "location"
    }
  ]
}
```

### Example 9: Advanced Parameter with Options

```json
{
  "name": "Advanced Search Dashboard",
  "parameters": [
    {
      "id": "search_filter",
      "type": "string/contains",
      "name": "Product Search",
      "slug": "search",
      "sectionId": "filters",
      "options": {
        "case-sensitive": false
      },
      "isMultiSelect": false,
      "required": false
    },
    {
      "id": "category_filter",
      "type": "category", 
      "name": "Categories",
      "slug": "categories",
      "sectionId": "filters",
      "isMultiSelect": true,
      "filteringParameters": ["brand_filter"],
      "values_source_type": "static-list",
      "values_source_config": {
        "values": ["electronics", "clothing", "books", "home"]
      }
    },
    {
      "id": "is_featured",
      "type": "boolean",
      "name": "Featured Products Only",
      "slug": "featured",
      "sectionId": "filters",
      "default": false
    }
  ]
}
```

### Example 10: Complex Date Filtering

```json
{
  "name": "Time Analysis Dashboard",
  "parameters": [
    {
      "id": "date_exclusion",
      "type": "date/relative",
      "name": "Exclude Weekends",
      "slug": "no-weekends",
      "sectionId": "time",
      "default": "exclude-days-Sat-Sun"
    },
    {
      "id": "business_hours",
      "type": "date/relative", 
      "name": "Business Hours Only",
      "slug": "business-hours",
      "sectionId": "time",
      "default": "exclude-hours-0-1-2-3-4-5-6-7-18-19-20-21-22-23"
    },
    {
      "id": "quarter_select",
      "type": "date/quarter-year",
      "name": "Select Quarter",
      "slug": "quarter",
      "sectionId": "time"
    }
  ]
}
```

```json
{
  "name": "Store Locations Dashboard",
  "parameters": [
    {
      "id": "store_city",
      "type": "location/city",
      "name": "Store City",
      "slug": "city",
      "sectionId": "location"
    },
    {
      "id": "store_state",
      "type": "location/state", 
      "name": "Store State",
      "slug": "state",
      "sectionId": "location"
    },
    {
      "id": "zip_code",
      "type": "location/zip_code",
      "name": "ZIP Code",
      "slug": "zip",
      "sectionId": "location"
    }
  ]
}
```

```json
{
  "id": "dynamic_category",
  "type": "category",
  "name": "Product Category",
  "slug": "category",
  "values_source_type": "card",
  "values_source_config": {
    "card_id": 150,
    "value_field": ["field", 789, null],
    "label_field": ["field", 790, null]
  }
}
```

## Advanced Parameter Value Formats

### Date-Specific Formats

Beyond the relative date patterns, Metabase supports several other date value formats:

#### Month/Year Values (`date/month-year`)
```json
{
  "parameter_id": "month_filter",
  "value": "2024-03"  // March 2024
}
```

#### Quarter/Year Values (`date/quarter-year`)
```json
{
  "parameter_id": "quarter_filter", 
  "value": "Q2-2024"  // Q2 2024
}
```

#### Specific Date Values (`date/single`)
```json
{
  "parameter_id": "date_filter",
  "value": "2024-03-15"  // March 15, 2024
}
```

#### Date with Time (`date/single` with time)
```json
{
  "parameter_id": "datetime_filter",
  "value": "2024-03-15T14:30:00"  // March 15, 2024 at 2:30 PM
}
```

#### Date Range Operators
```json
// Before a date
{
  "parameter_id": "date_filter",
  "value": "~2024-03-15"  // Before March 15, 2024
}

// After a date  
{
  "parameter_id": "date_filter",
  "value": "2024-03-15~"  // After March 15, 2024
}
```

#### Advanced Date Exclusions

Exclude specific times/days/months from results:

```json
// Exclude specific hours (0-23)
{
  "parameter_id": "time_filter",
  "value": "exclude-hours-1-5-22-23"  // Exclude hours 1, 5, 22, 23
}

// Exclude specific days of week
{
  "parameter_id": "day_filter", 
  "value": "exclude-days-Mon-Fri"  // Exclude Monday and Friday
}

// Exclude specific months
{
  "parameter_id": "month_filter",
  "value": "exclude-months-Jan-Dec"  // Exclude January and December  
}

// Exclude specific quarters
{
  "parameter_id": "quarter_filter",
  "value": "exclude-quarters-1-4"  // Exclude Q1 and Q4
}
```

Valid day abbreviations: `Mon`, `Tue`, `Wed`, `Thu`, `Fri`, `Sat`, `Sun`
Valid month abbreviations: `Jan`, `Feb`, `Mar`, `Apr`, `May`, `Jun`, `Jul`, `Aug`, `Sep`, `Oct`, `Nov`, `Dec`

### Multi-Value Parameters

For parameters that support multiple selections (`isMultiSelect: true`):

```json
{
  "parameter_id": "category_filter",
  "value": ["electronics", "clothing", "books"]  // Array of values
}
```

### Number Parameter Formats

#### Between Values (`number/between`)
```json
{
  "parameter_id": "price_filter",
  "value": [100, 500]  // Between 100 and 500
}
```

#### Single Number Values
```json
{
  "parameter_id": "quantity_filter", 
  "value": 42
}
```

### Boolean Parameter Values

```json
{
  "parameter_id": "is_active",
  "value": true
}

{
  "parameter_id": "is_featured",
  "value": false
}
```

### String Parameter Options

String parameters can include case-sensitivity options:

```json
{
  "id": "search_term",
  "type": "string/contains",
  "name": "Search Term",
  "options": {
    "case-sensitive": false  // Case-insensitive search
  }
}
```

### Date Relative Parameter Values

When using `date/relative` parameters, the values should match the supported patterns:

**Examples:**
```json
{
  "parameter_id": "date_filter",
  "value": "past28days"  // Last 28 days
}
```

```json
{
  "parameter_id": "date_filter", 
  "value": "past6months"  // Last 6 months
}
```

```json
{
  "parameter_id": "date_filter",
  "value": "next14days"  // Next 14 days
}
```

**Valid value patterns:**
- Predefined: `"thisday"`, `"past1days"`, `"past7days"`, `"past30days"`, `"past1weeks"`, `"past1months"`, `"past1years"`, `"thisweek"`, `"thismonth"`, `"thisyear"`
- Custom past: `"past{N}days"`, `"past{N}weeks"`, `"past{N}months"`, `"past{N}years"`
- Custom future: `"next{N}days"`, `"next{N}weeks"`, `"next{N}months"`, `"next{N}years"`
- With current included: `"past{N}days~"`, `"next{N}days~"`
- Offset ranges: `"past{N}days-from-{M}years"`

### Date Range Parameter Values

For `date/range` parameters, use ISO date format:

```json
{
  "parameter_id": "date_range",
  "value": "2024-01-01~2024-12-31"
}
```

### Temporal Unit Parameter Values

For `temporal-unit` parameters, use the temporal unit strings:

```json
{
  "parameter_id": "time_unit",
  "value": "month"
}
```

Valid values include: `"day"`, `"week"`, `"month"`, `"quarter"`, `"year"`, `"day-of-week"`, etc.

## Field ID Discovery

To find field IDs for your targets, you can:

1. **Use the `/api/database/{id}/fields` endpoint** to list all fields in a database
2. **Use the `/api/table/{id}/fields` endpoint** to list fields for a specific table
3. **Inspect existing cards** that use the fields you want to target
4. **Use the Data Browser** in Metabase UI and inspect network requests

## Best Practices

### 1. Parameter ID Naming
- Use descriptive, unique IDs
- Follow a consistent naming convention (e.g., `field_name_filter`)
- Avoid special characters except underscores and hyphens

### 2. Parameter Organization
- Use `sectionId` to group related parameters
- Order parameters logically in the array
- Use clear, user-friendly names

### 3. Default Values
- Provide sensible defaults for better user experience
- Use `null` when no default is appropriate
- Test defaults with your data

### 4. Parameter Types
- Choose the most specific type possible
- Use operator types (`string/contains`, `number/>=`) for better UX
- Consider using `category` for fields with limited distinct values

### 5. Values Sources
- Use `static-list` for small, fixed sets of values
- Use `card` source for dynamic values from queries
- Keep static lists small for performance

### 6. Error Handling
- Validate field IDs exist before creating mappings
- Test parameter mappings with sample data
- Handle cases where parameters might be null

### 7. Performance Considerations
- Limit the number of parameters to essential filters
- Use indexed fields when possible for better query performance
- Consider the impact of complex parameter combinations

## Common Issues and Solutions

### 1. Parameter Not Filtering
- **Check field ID**: Ensure the field ID in the target exists
- **Verify parameter ID**: Confirm the parameter_id matches exactly
- **Check card ID**: Make sure card_id is correct if specified

### 2. Invalid Parameter Type
- Refer to the [Parameter Types](#parameter-types) section for valid types
- Ensure the type matches the field's data type

### 3. Template Tag Issues
- Verify template tag names match exactly (case-sensitive)
- Use `["dimension", ["template-tag", "name"]]` for field filters
- Use `["variable", ["template-tag", "name"]]` for value substitution

### 4. Values Source Problems
- Ensure the source card exists and is accessible
- Verify field references in values_source_config are correct
- Test the source card independently

## API Endpoints Reference

### Update Dashboard
```http
PUT /api/dashboard/{id}
Content-Type: application/json

{
  "parameters": [...],
  "dashcards": [
    {
      "parameter_mappings": [...]
    }
  ]
}
```

### Update Card
```http
PUT /api/card/{id}
Content-Type: application/json

{
  "parameters": [...],
  "parameter_mappings": [...]
}
```

### Get Parameter Values
```http
GET /api/dashboard/{id}/params/{param-key}/values
GET /api/card/{id}/params/{param-key}/values
```

This documentation provides a complete foundation for working with Metabase parameters and parameter mappings. For the most up-to-date information, always refer to your specific Metabase version's API documentation.