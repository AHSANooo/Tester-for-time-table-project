#!/usr/bin/env python3

import sys
sys.path.append('.')
from course_extractor import parse_course_entry

def test_advanced_parsing():
    # Test various cell content formats that might appear in the timetable
    test_cases = [
        ('DIP (CS, G-2)', 'BS CS (2022)'),
        ('DIP (CS, G-2) A', 'BS CS (2022)'),
        ('DIP (CS, G-2) (CS-A)', 'BS CS (2022)'),
        ('DIP (CS, G-2) -A', 'BS CS (2022)'),
        ('DIP (CS, G-2) (A)', 'BS CS (2022)'),
        ('Gen AI (CS, G-1) B', 'BS CS (2022)'),
        ('Deep Learning (CS, G-2) C', 'BS CS (2022)'),
        ('PPIT A', 'BS CS (2022)'),
        ('Info Sec (CS-A)', 'BS CS (2022)')
    ]

    print("Testing advanced course parsing:")
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
    test_advanced_parsing()
