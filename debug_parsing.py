#!/usr/bin/env python3

import sys
sys.path.append('.')
from course_extractor import parse_course_entry

def test_course_parsing():
    # Test the problematic course formats
    test_cases = [
        ('DIP (CS, G-2)', 'BS CS (2022)'),
        ('Gen AI (CS, G-1)', 'BS CS (2022)'),
        ('Deep Learning (CS, G-2)', 'BS CS (2022)'),
        ('PPIT', 'BS CS (2022)'),
        ('Info Sec', 'BS CS (2022)')
    ]

    print("Testing course parsing:")
    print("=" * 50)
    
    for course_entry, batch in test_cases:
        result = parse_course_entry(course_entry, batch)
        if result:
            print(f'Input: "{course_entry}"')
            print(f'  Name: "{result["name"]}"')
            print(f'  Department: "{result["department"]}"')
            print(f'  Section: "{result["section"]}"')
            print(f'  Batch: "{result["batch"]}"')
            print()

if __name__ == "__main__":
    test_course_parsing()
