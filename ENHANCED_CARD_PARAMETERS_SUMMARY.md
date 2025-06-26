## ⚠️ Critical SQL Parameter Usage Fixes

A major enhancement addresses common AI assistant mistakes with SQL parameter usage:

### Field Filter Behavior Clarification
Field filters are replaced with **boolean values (true/false)**, NOT with complete SQL conditions:
- ✅ **Correct**: `WHERE {{customer_filter}}` (becomes `WHERE true` or `WHERE false`)
- ❌ **Wrong**: `WHERE customer_name = {{customer_filter}}` (field filters are booleans!)

### SQL Parameter Mistake Detection
The system now detects and warns about common mistakes:
- **Quoted Parameters**: `'{{param}}'` (parameters include quotes automatically)
- **CASE WHEN Errors**: `CASE WHEN '{{metric}}' = 'value'` (remove quotes around parameters)
- **Parameter Consistency**: SQL references must match parameter configurations

### Parameter Preservation
The `update_card` tool now preserves existing parameters when updating queries:
- Prevents "template tag not found" errors
- Maintains parameter functionality during query-only updates
- Automatically preserves both parameters and template tags

### Enhanced Widget Compatibility
UI widget validation has been improved:
- Search widgets now work with all string field filter types
- Better validation for dropdown and search widget requirements
- Clearer error messages for incompatible configurations

# Enhanced Card Parameters Implementation Summary

## Overview

Talk to Metabase now provides comprehensive support for creating sophisticated interactive filters in Metabase cards through an enhanced card parameters system. This implementation supports both simple variable filters and advanced field filters that connect directly to database columns, providing users with powerful filtering capabilities while maintaining ease of use.

## 🎯 Key Achievements

### Complete Parameter Type Support

The implementation supports all Metabase parameter types:

#### Simple Filters (Variable Targets)
- **`category`**: Text input with autocomplete, dropdown, or search options
- **`number/=`**: Number input with optional dropdown values
- **`date/single`**: Date picker for single date selection

#### Field Filters (Database Column Targeting)
- **String Filters**: `string/=`, `string/!=`, `string/contains`, `string/does-not-contain`, `string/starts-with`, `string/ends-with`
- **Numeric Filters**: `number/=`, `number/!=`, `number/between`, `number/>=`, `number/<=`
- **Date Filters**: `date/range`, `date/relative`, `date/all-options`, `date/month-year`, `date/quarter-year`

### Critical SQL Usage Distinction

The system clearly distinguishes between two parameter usage patterns:

#### Simple Variable Filters
```sql
-- ✅ Correct usage
WHERE status = {{order_status}}
WHERE date >= {{start_date}}
WHERE price > {{min_price}}
```
- Parameter value gets substituted directly into SQL
- User provides the value, SQL provides column name and operator

#### Field Filters
```sql
-- ✅ Correct usage  
WHERE {{customer_filter}}
[[AND {{date_range_filter}}]]
[[AND {{spend_range}}]]
```
- Field filters are replaced with BOOLEAN VALUES (true/false) indicating if the condition is met
- User provides the filter values through UI, Metabase evaluates the condition
- Field filters connect directly to database columns and handle filtering logic

**Critical Rule**: Never mix syntax patterns (`WHERE column = {{field_filter}}` won't work - field filters are booleans!)

## 🏗️ Architecture

### Core Components

1. **Enhanced Parameters Module**: `/talk_to_metabase/tools/enhanced_parameters/`
   - `core.py`: Main implementation with validation, processing, and tools
   - `__init__.py`: Module exports for easy importing

2. **JSON Schema Validation**: `/talk_to_metabase/schemas/enhanced_card_parameters.json`
   - Comprehensive validation for all parameter types
   - Conditional validation for field filters requiring field configuration
   - UI widget compatibility validation with exceptions for connected field filters
   - Special handling for number dropdown formatting

3. **Complete Documentation**: `/talk_to_metabase/schemas/enhanced_card_parameters_docs.md`
   - Detailed examples for all parameter types
   - Clear SQL usage patterns and best practices
   - UI widget mapping guide
   - Value source configuration examples

### Processing Flow

```python
# Main processing pipeline
parameters (user input) 
→ JSON Schema validation 
→ Field reference validation (against database)
→ Business rule validation 
→ Parameter processing (UUID generation, etc.)
→ Template tag creation
→ Metabase API format output
```

## 🔧 Key Features

### 1. Automatic Processing
- **UUID Generation**: Unique IDs for parameter linking
- **Slug Generation**: URL-friendly slugs from parameter names  
- **Template Tag Creation**: Automatic generation from parameters
- **Target Mapping**: Correct variable vs dimension targeting

### 2. UI Widget Support
- **`input`**: Free text/number entry (`values_query_type: "none"`)
- **`dropdown`**: Select from list (`values_query_type: "list"`)
- **`search`**: Search with suggestions (`values_query_type: "search"`)

### 3. Value Source Management
- **`static`**: Predefined list of values
- **`card`**: Values from another card/model  
- **`connected`**: Values from connected database field (field filters only)

### 4. Comprehensive Validation
- **JSON Schema**: Structure and type validation
- **Field References**: Database validation for field filters
- **Widget Compatibility**: Enhanced UI widget compatibility checking (search widgets now work with all string field filters)
- **Required Parameters**: Must have default values
- **Business Rules**: Duplicate names, proper configuration
- **SQL Parameter Consistency**: Validates SQL references match parameter configurations
- **SQL Mistake Detection**: Detects quoted parameters and provides correction guidance
- **Parameter Preservation**: Automatically preserves existing parameters during query-only updates

## 🔢 Special Handling

### Number Dropdown Format
Number parameters with dropdowns require special API formatting:

```json
// Input format
{
  "type": "number/=",
  "default": 100,
  "values_source": {
    "type": "static", 
    "values": [50, 100, 200]
  }
}

// Generated API format
{
  "default": ["100"],
  "values_source_config": {
    "values": [["50"], ["100"], ["200"]]
  }
}
```

### Connected Field Filter Configuration
Connected field filters use special API configuration:

```json
// Input format
{
  "ui_widget": "dropdown",
  "values_source": {"type": "connected"}
}

// Generated API format  
{
  "values_source_type": null,
  "values_source_config": {}
}
```

## 🛠️ Tools Integration

### Enhanced Card Creation/Update Tools
Both `create_card` and `update_card` now support enhanced parameters:

```python
# Automatic parameter processing with validation
if ENHANCED_PARAMETERS_AVAILABLE and parsed_parameters:
    processed_parameters, template_tags, errors = await process_enhanced_parameters(
        client, parsed_parameters
    )
    if errors:
        return detailed_validation_error_response
```

### Documentation Tool
`GET_ENHANCED_CARD_PARAMETERS_DOCUMENTATION` provides:
- Complete schema and examples
- UI widget mappings  
- Value source configurations
- SQL usage patterns
- Parameter type reference

## 📝 Usage Examples

### Simple Category Filter with Dropdown
```json
{
  "name": "order_status",
  "type": "category",
  "default": "pending",
  "ui_widget": "dropdown",
  "values_source": {
    "type": "static",
    "values": ["pending", "shipped", "delivered", "cancelled"]
  }
}
```

### String Field Filter with Connected Values
```json
{
  "name": "customer_filter", 
  "type": "string/=",
  "display_name": "Customer Name",
  "field": {
    "database_id": 195,
    "table_id": 50112,
    "field_id": 50705149
  },
  "ui_widget": "dropdown",
  "values_source": {
    "type": "connected"
  }
}
```

### Number Range Field Filter
```json
{
  "name": "spend_range",
  "type": "number/between", 
  "display_name": "Spend Range",
  "field": {
    "database_id": 195,
    "table_id": 50112,
    "field_id": 50705151
  },
  "default": [100, 10000]
}
```

### Date Field Filter with All Options
```json
{
  "name": "date_filter",
  "type": "date/all-options",
  "display_name": "Date Range",
  "field": {
    "database_id": 195,
    "table_id": 50112, 
    "field_id": 50705150
  },
  "default": "past30days"
}
```

### Required Number Parameter with Dropdown
```json
{
  "name": "row_limit",
  "type": "number/=",
  "display_name": "Rows to Display",
  "default": 100,
  "required": true,
  "ui_widget": "dropdown",
  "values_source": {
    "type": "static",
    "values": [50, 100, 200, 500, 1000]
  }
}
```

## ✅ Validation & Error Handling

### Multi-Layer Validation
1. **JSON Schema**: Automatic validation of structure, types, conditional requirements
2. **Field Reference Validation**: Verifies database fields exist via API calls
3. **Business Rule Validation**: Duplicate names, required parameters with defaults, widget compatibility
4. **Special Format Validation**: Number dropdown arrays, connected field filter configuration

### Clear Error Messages
```json
{
  "success": false,
  "error": "Invalid enhanced parameters",
  "validation_errors": [
    "Parameter 2 (date_filter): required parameters must have a default value",
    "Parameter 3 (customer_filter): Field 99999 not found in table 50112"
  ],
  "parameters_count": 4,
  "help": "Call GET_ENHANCED_CARD_PARAMETERS_DOCUMENTATION for format details"
}
```

## 🚀 Benefits Achieved

### For AI Assistants
- **Simplified Input**: Only specify what matters - UUIDs, slugs, targets auto-generated
- **Comprehensive Filtering**: Support for all Metabase filter types
- **Clear Documentation**: UI terms mapped to API values with complete examples
- **Fewer Errors**: JSON Schema prevents most configuration mistakes
- **Field Validation**: Database fields validated automatically

### For End Users
- **Rich Filtering Options**: Both simple variables and database field filters
- **Appropriate UI Widgets**: Dropdowns for categories, date pickers for dates, search for text
- **Connected Data**: Field filters use actual database values automatically
- **Performance**: Optimized parameter substitution and query execution

### For Developers  
- **Maintainable**: Clear separation of concerns with modular architecture
- **Extensible**: Easy to add new parameter types following established patterns
- **Reliable**: Comprehensive validation prevents API errors
- **Clean**: Single enhanced system instead of legacy/enhanced dual approach

## 🔄 Migration & Legacy Support

### Complete Legacy Replacement
- **Legacy Files Removed**: Old `card_parameters.py` moved to `.deprecated`
- **No Dual Systems**: Single enhanced system for all parameter needs
- **Backward Compatibility**: Simple use cases work the same way
- **Enhanced Capabilities**: Field filters and advanced features now available

### Upgrade Path
Users can enhance existing simple parameters by adding field mappings:

```json
// Before (simple variable)
{
  "name": "status_filter",
  "type": "category", 
  "default": "active"
}

// After (field filter with same functionality)
{
  "name": "status_filter",
  "type": "string/=",
  "field": {
    "database_id": 195,
    "table_id": 50112,
    "field_id": 50705149
  },
  "default": "active",
  "ui_widget": "dropdown",
  "values_source": {"type": "connected"}
}
```

## 📋 Implementation Status

### ✅ Completed Features
- [x] Complete parameter type support (simple + field filters)
- [x] JSON Schema validation with conditional logic
- [x] Field reference validation against database
- [x] Enhanced UI widget compatibility validation (search widgets work with all string field filters)
- [x] Number dropdown special formatting
- [x] Connected field filter configuration
- [x] Required parameter validation
- [x] Template tag auto-generation
- [x] Integration with create_card and update_card tools
- [x] Comprehensive documentation and examples
- [x] Error handling with clear messages
- [x] Legacy system removal and cleanup
- [x] **SQL parameter consistency validation**
- [x] **SQL mistake detection and guidance**
- [x] **Parameter preservation during query updates**
- [x] **Field filter behavior clarification (boolean values)**

### 🎯 Production Ready
The enhanced card parameters system is **production-ready** and provides:

1. **Comprehensive validation** prevents configuration errors
2. **Field validation** ensures database references are valid  
3. **Clear error messages** guide users to correct issues
4. **Complete documentation** with examples for all scenarios
5. **Clean integration** with existing card creation/update tools
6. **Performance optimization** through efficient validation and processing

## 🏁 Conclusion

The enhanced card parameters implementation provides a robust, comprehensive solution for creating sophisticated interactive filters in Metabase. It successfully bridges the gap between simple parameter usage and advanced field filtering capabilities, while maintaining ease of use and providing clear guidance for AI assistants.

Key achievements include:
- **Complete Metabase parameter support** across all types
- **Corrected SQL usage patterns** preventing common AI mistakes
- **Field filter behavior clarification** (boolean values, not SQL conditions)
- **SQL parameter consistency validation** ensuring SQL matches configuration
- **Parameter preservation** during query updates preventing template tag errors
- **Enhanced widget compatibility** with improved validation
- **Automatic processing** of complex configurations
- **Comprehensive validation** preventing errors
- **Production-ready reliability** with thorough testing

Users can now create sophisticated interactive dashboards and queries with minimal effort, while the system handles all the complex internal configuration automatically.
