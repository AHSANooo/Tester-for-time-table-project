#!/usr/bin/env python3

import sys
sys.path.append('.')
from course_extractor import parse_course_entry

def test_actual_timetable_formats():
    # Test the actual timetable cell formats
    test_cases = [
        ('Gen AI (CS-A,G-1)', 'BS CS (2022)'),
        ('Gen AI (CS-B,G-1)', 'BS CS (2022)'),
        ('Gen AI (CS-C,G-1)', 'BS CS (2022)'),
        ('Gen AI (CS-A,G-2)', 'BS CS (2022)'),
        ('COAL (CS-E)', 'BS CS (2022)'),
        ('DIP (CS-A,G-2)', 'BS CS (2022)'),
        ('Deep Learning (CS-C,G-2)', 'BS CS (2022)')
    ]

    print("Testing actual timetable cell formats:")
    print("=" * 60)
    
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
    test_actual_timetable_formats()
