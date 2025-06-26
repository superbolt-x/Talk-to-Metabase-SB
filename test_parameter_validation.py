#!/usr/bin/env python3
"""
Test script for parameter validation functions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from talk_to_metabase.tools.card import extract_sql_parameters, validate_sql_parameter_consistency

def test_parameter_extraction():
    """Test the parameter extraction function."""
    
    # Test case 1: Mix of required and optional parameters
    query1 = """
    SELECT 
        channel,
        SUM(spend) as total_spend
    FROM reporting.bariendo_blended
    WHERE date_granularity = 'day'
        AND {{date_range_filter}}
        [[AND {{channel_filter}}]]
        [[AND {{spend_range}}]]
    GROUP BY channel
    ORDER BY total_spend DESC
    """
    
    result1 = extract_sql_parameters(query1)
    print("Test 1 - Mixed parameters:")
    print(f"Required: {result1['required']}")
    print(f"Optional: {result1['optional']}")
    print()
    
    # Test case 2: Only required parameters
    query2 = "SELECT * FROM orders WHERE date >= {{start_date}} AND status = {{order_status}}"
    
    result2 = extract_sql_parameters(query2)
    print("Test 2 - Only required parameters:")
    print(f"Required: {result2['required']}")
    print(f"Optional: {result2['optional']}")
    print()
    
    # Test case 3: Only optional parameters
    query3 = "SELECT * FROM products WHERE 1=1 [[AND category = {{category}}]] [[AND price > {{min_price}}]]"
    
    result3 = extract_sql_parameters(query3)
    print("Test 3 - Only optional parameters:")
    print(f"Required: {result3['required']}")
    print(f"Optional: {result3['optional']}")
    print()

def test_parameter_consistency():
    """Test the parameter consistency validation."""
    
    query = """
    SELECT channel, SUM(spend) as total_spend
    FROM reporting.bariendo_blended
    WHERE date_granularity = 'day'
        AND {{date_range_filter}}
        [[AND {{channel_filter}}]]
        [[AND {{spend_range}}]]
    ORDER BY total_spend DESC
    """
    
    # Test case 1: Matching parameters
    parameters1 = [
        {"name": "date_range_filter", "slug": "date_range_filter", "type": "date/range"},
        {"name": "channel_filter", "slug": "channel_filter", "type": "string/="},
        {"name": "spend_range", "slug": "spend_range", "type": "number/between"}
    ]
    
    issues1 = validate_sql_parameter_consistency(query, parameters1)
    print("Test 1 - Matching parameters:")
    print(f"Issues: {issues1}")
    print()
    
    # Test case 2: Missing parameter in config
    parameters2 = [
        {"name": "date_range_filter", "slug": "date_range_filter", "type": "date/range"},
        {"name": "channel_filter", "slug": "channel_filter", "type": "string/="}
        # Missing spend_range
    ]
    
    issues2 = validate_sql_parameter_consistency(query, parameters2)
    print("Test 2 - Missing parameter in config:")
    print(f"Issues: {issues2}")
    print()
    
    # Test case 3: Extra parameter in config
    parameters3 = [
        {"name": "date_range_filter", "slug": "date_range_filter", "type": "date/range"},
        {"name": "channel_filter", "slug": "channel_filter", "type": "string/="},
        {"name": "spend_range", "slug": "spend_range", "type": "number/between"},
        {"name": "extra_param", "slug": "extra_param", "type": "category"}  # Extra
    ]
    
    issues3 = validate_sql_parameter_consistency(query, parameters3)
    print("Test 3 - Extra parameter in config:")
    print(f"Issues: {issues3}")
    print()

if __name__ == "__main__":
    print("Testing parameter extraction...")
    test_parameter_extraction()
    
    print("\nTesting parameter consistency validation...")
    test_parameter_consistency()
