#!/usr/bin/env python3

import sys
sys.path.append('.')
from course_extractor import parse_course_entry

def debug_full_parsing():
    test_case = 'DIP (CS, G-2) (CS-A)'
    batch = 'BS CS (2022)'
    
    print(f"Testing full parsing of: '{test_case}'")
    print(f"Batch: '{batch}'")
    print()
    
    # Parse normally
    result = parse_course_entry(test_case, batch)
    
    if result:
        print("Result:")
        for key, value in result.items():
            print(f"  {key}: '{value}'")
    else:
        print("No result returned")

if __name__ == "__main__":
    debug_full_parsing()
