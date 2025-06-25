#!/usr/bin/env python3
"""
Comprehensive test suite for enhanced card parameters implementation.
This script validates schemas, validation logic, and parameter processing.
"""

import json
import sys
import os
import asyncio
from unittest.mock import AsyncMock, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from talk_to_metabase.resources import load_enhanced_card_parameters_schema, load_enhanced_card_parameters_docs
from talk_to_metabase.tools.enhanced_parameters.core import (
    validate_enhanced_parameters,
    generate_parameter_id,
    generate_slug,
    is_field_filter_parameter,
    process_single_parameter,
    resolve_field_reference,
    get_parameter_target,
    convert_ui_widget_to_values_query_type,
    build_values_source_config,
    create_template_tag,
    validate_parameter_widget_compatibility,
    process_enhanced_parameters
)

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def pass_test(self, test_name):
        print(f"✅ {test_name}")
        self.passed += 1
    
    def fail_test(self, test_name, error):
        print(f"❌ {test_name}: {error}")
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n🎯 Test Results: {self.passed}/{total} passed")
        if self.failed > 0:
            print(f"❌ {self.failed} failed tests:")
            for error in self.errors:
                print(f"   • {error}")
        return self.failed == 0

def test_schema_loading(results):
    """Test that schemas and docs load correctly."""
    print("📋 Testing schema and documentation loading...")
    
    try:
        schema = load_enhanced_card_parameters_schema()
        if schema is None:
            results.fail_test("Schema loading", "Failed to load enhanced parameters schema")
            return
        
        # Validate schema structure
        required_schema_fields = ["$schema", "title", "type", "items"]
        for field in required_schema_fields:
            if field not in schema:
                results.fail_test("Schema structure", f"Missing required field: {field}")
                return
        
        results.pass_test("Enhanced parameters schema loaded successfully")
        
        docs = load_enhanced_card_parameters_docs()
        if docs is None:
            results.fail_test("Documentation loading", "Failed to load enhanced parameters documentation")
            return
        
        # Check docs contain key sections
        required_sections = ["Overview", "Parameter Types", "Simple Filters", "Field Filter Parameters", "UI Widget Options"]
        for section in required_sections:
            if section not in docs:
                results.fail_test("Documentation content", f"Missing required section: {section}")
                return
        
        results.pass_test("Enhanced parameters documentation loaded successfully")
        
    except Exception as e:
        results.fail_test("Schema/docs loading", str(e))

def test_utility_functions(results):
    """Test utility functions for parameter processing."""
    print("\n🔧 Testing utility functions...")
    
    try:
        # Test parameter ID generation
        id1 = generate_parameter_id()
        id2 = generate_parameter_id()
        if not id1 or not id2 or id1 == id2:
            results.fail_test("Parameter ID generation", "IDs should be unique and non-empty")
            return
        results.pass_test("Parameter ID generation")
        
        # Test slug generation
        test_cases = [
            ("Order Status", "order_status"),
            ("price-limit", "price_limit"),
            ("Customer Name!", "customer_name"),
            ("  test  ", "test"),
            ("123abc", "123abc"),
            ("", "parameter")  # fallback case
        ]
        
        for input_name, expected_slug in test_cases:
            actual_slug = generate_slug(input_name)
            if actual_slug != expected_slug:
                results.fail_test("Slug generation", f"Input '{input_name}' should generate '{expected_slug}', got '{actual_slug}'")
                return
        results.pass_test("Slug generation")
        
        # Test field filter detection
        simple_types = ["category", "number/=", "date/single"]
        field_filter_types = ["string/=", "string/contains", "number/between", "date/range"]
        
        for param_type in simple_types:
            if is_field_filter_parameter(param_type):
                results.fail_test("Field filter detection", f"'{param_type}' incorrectly identified as field filter")
                return
        
        for param_type in field_filter_types:
            if not is_field_filter_parameter(param_type):
                results.fail_test("Field filter detection", f"'{param_type}' should be identified as field filter")
                return
        results.pass_test("Field filter detection")
        
        # Test field reference resolution
        field_config = {"database_id": 195, "table_id": 50112, "field_id": 50705149}
        field_ref = resolve_field_reference(field_config)
        expected_ref = ["field", 50705149, None]
        if field_ref != expected_ref:
            results.fail_test("Field reference resolution", f"Expected {expected_ref}, got {field_ref}")
            return
        results.pass_test("Field reference resolution")
        
        # Test parameter target generation
        variable_target = get_parameter_target("test_param", False)
        expected_variable = ["variable", ["template-tag", "test_param"]]
        if variable_target != expected_variable:
            results.fail_test("Variable target generation", f"Expected {expected_variable}, got {variable_target}")
            return
        
        dimension_target = get_parameter_target("test_param", True)
        expected_dimension = ["dimension", ["template-tag", "test_param"]]
        if dimension_target != expected_dimension:
            results.fail_test("Dimension target generation", f"Expected {expected_dimension}, got {dimension_target}")
            return
        results.pass_test("Parameter target generation")
        
        # Test UI widget conversion
        widget_mappings = [
            ("input", "none"),
            ("dropdown", "list"),
            ("search", "search"),
            (None, "none")
        ]
        
        for ui_widget, expected_query_type in widget_mappings:
            actual_query_type = convert_ui_widget_to_values_query_type(ui_widget)
            if actual_query_type != expected_query_type:
                results.fail_test("UI widget conversion", f"Widget '{ui_widget}' should map to '{expected_query_type}', got '{actual_query_type}'")
                return
        results.pass_test("UI widget conversion")
        
    except Exception as e:
        results.fail_test("Utility functions", str(e))

def test_simple_parameter_validation(results):
    """Test validation of simple parameters."""
    print("\n📝 Testing simple parameter validation...")
    
    try:
        # Valid simple parameters
        valid_simple_params = [
            {
                "name": "order_status",
                "type": "category",
                "default": "pending",
                "ui_widget": "dropdown",
                "values_source": {
                    "type": "static",
                    "values": ["pending", "shipped", "delivered"]
                }
            },
            {
                "name": "price_limit",
                "type": "number/=", 
                "default": 100
            },
            {
                "name": "start_date",
                "type": "date/single",
                "default": "2024-01-01"
            }
        ]
        
        is_valid, errors = validate_enhanced_parameters(valid_simple_params)
        if not is_valid:
            results.fail_test("Valid simple parameters", f"Validation failed: {errors}")
            return
        results.pass_test("Valid simple parameters validation")
        
        # Test parameter processing
        param_id = generate_parameter_id()
        processed_param, template_tag = process_single_parameter(valid_simple_params[0], param_id)
        
        # Validate processed parameter structure
        required_param_fields = ["id", "type", "target", "name", "slug", "values_query_type"]
        for field in required_param_fields:
            if field not in processed_param:
                results.fail_test("Parameter processing", f"Processed parameter missing field: {field}")
                return
        
        # Validate template tag structure
        required_tag_fields = ["type", "name", "id", "display-name"]
        for field in required_tag_fields:
            if field not in template_tag:
                results.fail_test("Template tag processing", f"Template tag missing field: {field}")
                return
        
        # Check that IDs match
        if processed_param["id"] != template_tag["id"]:
            results.fail_test("Parameter-template tag linking", "Parameter and template tag IDs should match")
            return
        
        # Test required parameter with default value
        required_param = {
            "name": "required_test",
            "type": "category",
            "required": True,
            "default": "test_value"
        }
        param_id_2 = generate_parameter_id()
        processed_param_2, template_tag_2 = process_single_parameter(required_param, param_id_2)
        
        # Check that required flag is in both parameter and template tag
        if not processed_param_2.get("required"):
            results.fail_test("Required parameter processing", "Required flag missing from processed parameter")
            return
        
        if not template_tag_2.get("required"):
            results.fail_test("Required template tag processing", "Required flag missing from template tag")
            return
        
        results.pass_test("Simple parameter processing")
        
    except Exception as e:
        results.fail_test("Simple parameter validation", str(e))

def test_field_filter_validation(results):
    """Test validation of field filter parameters."""
    print("\n🔗 Testing field filter parameter validation...")
    
    try:
        # Valid field filter parameters
        valid_field_filters = [
            {
                "name": "customer_filter",
                "type": "string/=",
                "field": {
                    "database_id": 195,
                    "table_id": 50112,
                    "field_id": 50705149
                },
                "ui_widget": "dropdown",
                "values_source": {
                    "type": "connected"
                }
            },
            {
                "name": "spend_range",
                "type": "number/between",
                "field": {
                    "database_id": 195,
                    "table_id": 50112,
                    "field_id": 50705151
                },
                "default": [100, 5000]
            },
            {
                "name": "date_filter",
                "type": "date/all-options",
                "field": {
                    "database_id": 195,
                    "table_id": 50112,
                    "field_id": 50705150
                },
                "default": "past30days"
            }
        ]
        
        is_valid, errors = validate_enhanced_parameters(valid_field_filters)
        if not is_valid:
            results.fail_test("Valid field filter parameters", f"Validation failed: {errors}")
            return
        results.pass_test("Valid field filter parameters validation")
        
        # Test field filter processing
        param_id = generate_parameter_id()
        processed_param, template_tag = process_single_parameter(valid_field_filters[0], param_id)
        
        # Check that field filter has dimension target
        if processed_param["target"][0] != "dimension":
            results.fail_test("Field filter target", "Field filter should have dimension target")
            return
        
        # Check template tag has dimension type and field reference
        if template_tag["type"] != "dimension":
            results.fail_test("Field filter template tag type", "Field filter template tag should have dimension type")
            return
        
        if "dimension" not in template_tag:
            results.fail_test("Field filter dimension reference", "Field filter template tag should have dimension reference")
            return
        
        expected_dimension = ["field", 50705149, None]
        if template_tag["dimension"] != expected_dimension:
            results.fail_test("Field filter dimension format", f"Expected {expected_dimension}, got {template_tag['dimension']}")
            return
        
        results.pass_test("Field filter parameter processing")
        
    except Exception as e:
        results.fail_test("Field filter validation", str(e))

def test_invalid_parameter_rejection(results):
    """Test that invalid parameters are properly rejected."""
    print("\n❌ Testing invalid parameter rejection...")
    
    try:
        # Test cases for invalid parameters
        invalid_test_cases = [
            {
                "name": "Missing required name",
                "params": [{"type": "category"}],
                "should_fail": True
            },
            {
                "name": "Invalid parameter type",
                "params": [{"name": "test", "type": "invalid_type"}],
                "should_fail": True
            },
            {
                "name": "Field filter without field config",
                "params": [{"name": "test", "type": "string/="}],
                "should_fail": True
            },
            {
                "name": "Dropdown without values source",
                "params": [{"name": "test", "type": "category", "ui_widget": "dropdown"}],
                "should_fail": True
            },
            {
                "name": "Duplicate parameter names",
                "params": [
                    {"name": "test", "type": "category"},
                    {"name": "test", "type": "number/="}
                ],
                "should_fail": True
            },
            {
                "name": "Invalid parameter name format",
                "params": [{"name": "123invalid", "type": "category"}],
                "should_fail": True
            }
        ]
        
        for test_case in invalid_test_cases:
            is_valid, errors = validate_enhanced_parameters(test_case["params"])
            
            if test_case["should_fail"]:
                if is_valid:
                    results.fail_test("Invalid parameter rejection", f"'{test_case['name']}' should have been rejected but passed validation")
                    return
            else:
                if not is_valid:
                    results.fail_test("Valid parameter acceptance", f"'{test_case['name']}' should have passed but failed: {errors}")
                    return
        
        results.pass_test("Invalid parameter rejection")
        
    except Exception as e:
        results.fail_test("Invalid parameter rejection", str(e))

def test_values_source_configuration(results):
    """Test value source configuration building."""
    print("\n📊 Testing value source configuration...")
    
    try:
        # Test static values source
        static_source = {"type": "static", "values": ["a", "b", "c"]}
        source_type, source_config = build_values_source_config(static_source)
        
        if source_type != "static-list":
            results.fail_test("Static values source type", f"Expected 'static-list', got '{source_type}'")
            return
        
        if source_config["values"] != ["a", "b", "c"]:
            results.fail_test("Static values source config", f"Values don't match: {source_config}")
            return
        
        # Test card values source
        card_source = {
            "type": "card",
            "card_id": 12345,
            "value_field": "category",
            "label_field": "label"
        }
        source_type, source_config = build_values_source_config(card_source)
        
        if source_type != "card":
            results.fail_test("Card values source type", f"Expected 'card', got '{source_type}'")
            return
        
        expected_value_field = ["field", "category", {"base-type": "type/Text"}]
        if source_config["value_field"] != expected_value_field:
            results.fail_test("Card values source value_field", f"Expected {expected_value_field}, got {source_config['value_field']}")
            return
        
        # Test connected values source
        connected_source = {"type": "connected"}
        field_config = {"field_id": 50705149}
        source_type, source_config = build_values_source_config(connected_source, field_config)
        
        if source_type is not None:
            results.fail_test("Connected values source type", f"Expected None, got '{source_type}'")
            return
        
        if source_config != {}:
            results.fail_test("Connected values source config", f"Expected empty dict, got: {source_config}")
            return
        
        results.pass_test("Values source configuration")
        
    except Exception as e:
        results.fail_test("Values source configuration", str(e))

def test_widget_compatibility_validation(results):
    """Test UI widget compatibility validation."""
    print("\n🎛️ Testing widget compatibility validation...")
    
    try:
        # Valid widget combinations
        valid_combinations = [
            {"name": "test1", "type": "category", "ui_widget": "input"},
            {"name": "test2", "type": "category", "ui_widget": "dropdown", "values_source": {"type": "static", "values": ["a"]}},
            {"name": "test3", "type": "string/contains", "ui_widget": "search", "field": {"database_id": 1, "table_id": 1, "field_id": 1}, "values_source": {"type": "connected"}},
            {"name": "test4", "type": "number/=", "ui_widget": "input"},
            {"name": "test5", "type": "date/single"}  # No widget specified, should work
        ]
        
        errors = validate_parameter_widget_compatibility(valid_combinations)
        if errors:
            results.fail_test("Valid widget combinations", f"Should be valid but got errors: {errors}")
            return
        results.pass_test("Valid widget combinations")
        
        # Invalid widget combinations
        invalid_combinations = [
            {"name": "test1", "type": "number/between", "ui_widget": "search"},  # Search not compatible with number/between
            {"name": "test2", "type": "date/range", "ui_widget": "dropdown"}     # Dropdown not compatible with date field filters
        ]
        
        errors = validate_parameter_widget_compatibility(invalid_combinations)
        if not errors:
            results.fail_test("Invalid widget combinations", "Should have validation errors but passed")
            return
        results.pass_test("Invalid widget combinations rejection")
        
    except Exception as e:
        results.fail_test("Widget compatibility validation", str(e))

async def test_field_validation_with_mock_client(results):
    """Test field validation with mocked Metabase client."""
    print("\n🗄️ Testing field validation...")
    
    try:
        # Create mock client
        mock_client = MagicMock()
        mock_client.auth = MagicMock()
        
        # Mock successful field validation
        mock_response = {
            "fields": [
                {"id": 50705149, "name": "customer_name"},
                {"id": 50705150, "name": "order_date"},
                {"id": 50705151, "name": "amount"}
            ]
        }
        mock_client.auth.make_request = AsyncMock(return_value=(mock_response, 200, None))
        
        # Parameters with valid field references
        valid_field_params = [
            {
                "name": "customer_filter",
                "type": "string/=",
                "field": {
                    "database_id": 195,
                    "table_id": 50112,
                    "field_id": 50705149
                }
            }
        ]
        
        # Test full parameter processing with field validation
        processed_params, template_tags, errors = await process_enhanced_parameters(mock_client, valid_field_params)
        
        if errors:
            results.fail_test("Field validation with valid fields", f"Should pass but got errors: {errors}")
            return
        
        if not processed_params or not template_tags:
            results.fail_test("Field validation processing", "Should return processed parameters and template tags")
            return
        
        results.pass_test("Field validation with valid fields")
        
        # Test with invalid field reference
        mock_client.auth.make_request = AsyncMock(return_value=(mock_response, 200, None))
        
        invalid_field_params = [
            {
                "name": "invalid_filter",
                "type": "string/=", 
                "field": {
                    "database_id": 195,
                    "table_id": 50112,
                    "field_id": 99999  # Field that doesn't exist
                }
            }
        ]
        
        processed_params, template_tags, errors = await process_enhanced_parameters(mock_client, invalid_field_params)
        
        if not errors:
            results.fail_test("Field validation with invalid fields", "Should fail with invalid field ID but passed")
            return
        
        results.pass_test("Field validation with invalid fields")
        
    except Exception as e:
        results.fail_test("Field validation", str(e))

def test_complete_examples(results):
    """Test complete real-world parameter examples."""
    print("\n🌍 Testing complete real-world examples...")
    
    try:
        # E-commerce filtering example
        ecommerce_params = [
            {
                "name": "order_status",
                "type": "category",
                "display_name": "Order Status",
                "default": "pending",
                "ui_widget": "dropdown", 
                "values_source": {
                    "type": "static",
                    "values": ["pending", "processing", "shipped", "delivered", "cancelled"]
                }
            },
            {
                "name": "customer_filter",
                "type": "string/contains",
                "display_name": "Customer Name Contains",
                "field": {
                    "database_id": 195,
                    "table_id": 50112,
                    "field_id": 50705149
                },
                "ui_widget": "search",
                "values_source": {
                    "type": "connected"
                }
            },
            {
                "name": "order_total_range", 
                "type": "number/between",
                "display_name": "Order Total",
                "field": {
                    "database_id": 195,
                    "table_id": 50112,
                    "field_id": 50705151
                },
                "default": [50, 1000]
            },
            {
                "name": "order_date",
                "type": "date/all-options",
                "display_name": "Order Date", 
                "field": {
                    "database_id": 195,
                    "table_id": 50112,
                    "field_id": 50705150
                },
                "default": "past30days"
            }
        ]
        
        is_valid, errors = validate_enhanced_parameters(ecommerce_params)
        if not is_valid:
            results.fail_test("E-commerce example validation", f"Failed: {errors}")
            return
        results.pass_test("E-commerce example validation")
        
        # Marketing campaign analysis example
        marketing_params = [
            {
                "name": "date_granularity",
                "type": "category",
                "display_name": "Date Granularity",
                "default": "day",
                "ui_widget": "dropdown",
                "values_source": {
                    "type": "static", 
                    "values": ["day", "week", "month", "quarter"]
                }
            },
            {
                "name": "campaign_channel",
                "type": "string/=",
                "display_name": "Marketing Channel",
                "field": {
                    "database_id": 195,
                    "table_id": 50112,
                    "field_id": 50705149
                },
                "ui_widget": "dropdown",
                "values_source": {
                    "type": "connected"
                }
            },
            {
                "name": "min_spend",
                "type": "number/>=", 
                "display_name": "Minimum Spend",
                "field": {
                    "database_id": 195,
                    "table_id": 50112,
                    "field_id": 50705151
                },
                "default": [1000]
            }
        ]
        
        is_valid, errors = validate_enhanced_parameters(marketing_params)
        if not is_valid:
            results.fail_test("Marketing example validation", f"Failed: {errors}")
            return
        results.pass_test("Marketing example validation")
        
    except Exception as e:
        results.fail_test("Complete examples", str(e))

async def main():
    """Run all tests."""
    print("🧪 Enhanced Card Parameters Test Suite")
    print("=" * 50)
    
    results = TestResults()
    
    # Run all test categories
    test_schema_loading(results)
    test_utility_functions(results)
    test_simple_parameter_validation(results)
    test_field_filter_validation(results)
    test_invalid_parameter_rejection(results)
    test_values_source_configuration(results)
    test_widget_compatibility_validation(results)
    await test_field_validation_with_mock_client(results)
    test_complete_examples(results)
    
    # Print final results
    print("\n" + "=" * 50)
    success = results.summary()
    
    if success:
        print("🎉 All tests passed! Enhanced parameters implementation is ready.")
    else:
        print("⚠️ Some tests failed. Please review and fix issues before deployment.")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
