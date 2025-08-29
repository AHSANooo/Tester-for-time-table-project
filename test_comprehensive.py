#!/usr/bin/env python3

import sys
sys.path.append('.')
from extract_timetable import matches_selected_course

def test_comprehensive_matching():
    """Test both group courses and regular courses to ensure no regressions."""
    
    # Mock required parameters
    cell_color = (255, 255, 255)
    batch_colors = {'BS CS (2022)': (255, 255, 255)}
    
    print("COMPREHENSIVE MATCHING TEST")
    print("=" * 60)
    
    # Test 1: Group courses
    print("\n1. GROUP COURSES:")
    selected_group_course = {
        'name': 'Gen AI (CS,G-1)',
        'department': 'CS', 
        'section': 'C',
        'batch': 'BS CS (2022)'
    }
    
    group_test_entries = [
        ('Gen AI (CS-C,G-1)', True, 'Exact match'),
        ('Gen AI (CS-A,G-1)', False, 'Wrong section'),
        ('Gen AI (CS-C,G-2)', False, 'Wrong group'),
        ('Deep Learning (CS-C,G-1)', False, 'Different course'),
    ]
    
    print(f"Selected: {selected_group_course['name']} (Section {selected_group_course['section']})")
    for entry, expected, description in group_test_entries:
        result = matches_selected_course(entry, selected_group_course, cell_color, batch_colors)
        status = "✅" if result == expected else "❌"
        print(f"  {entry:<25} -> {result:<5} {status} ({description})")
    
    # Test 2: Regular courses  
    print("\n2. REGULAR COURSES:")
    selected_regular_course = {
        'name': 'COAL',
        'department': 'CS',
        'section': 'E', 
        'batch': 'BS CS (2022)'
    }
    
    regular_test_entries = [
        ('COAL (CS-E)', True, 'Exact match'),
        ('COAL (CS-A)', False, 'Wrong section'),
        ('PPIT (CS-E)', False, 'Different course'),
        ('COAL Lab (CS-E)', False, 'Lab (should be rejected)'),
    ]
    
    print(f"Selected: {selected_regular_course['name']} (Section {selected_regular_course['section']})")
    for entry, expected, description in regular_test_entries:
        result = matches_selected_course(entry, selected_regular_course, cell_color, batch_colors)
        status = "✅" if result == expected else "❌"
        print(f"  {entry:<25} -> {result:<5} {status} ({description})")
    
    print("\n" + "=" * 60)
    print("Test completed!")

if __name__ == "__main__":
    test_comprehensive_matching()
