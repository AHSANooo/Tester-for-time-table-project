#!/usr/bin/env python3

import sys
sys.path.append('.')
from extract_timetable import parse_embedded_time_info
import re

def debug_matching_detailed():
    class_entry = 'Gen AI (CS-C,G-1)'
    selected_course = {
        'name': 'Gen AI (CS,G-1)',
        'department': 'CS',
        'section': 'C',
        'batch': 'BS CS (2022)'
    }
    
    # Mock cell_color and batch_colors since they're not used in our case
    cell_color = (255, 255, 255)  # White
    batch_colors = {'BS CS (2022)': (255, 255, 255)}
    
    print("DETAILED MATCHING DEBUG:")
    print("=" * 60)
    
    # Step 1: Parse embedded time info
    cleaned_entry, _, has_embedded_time = parse_embedded_time_info(class_entry)
    entry_to_match = cleaned_entry if has_embedded_time else class_entry
    print(f"1. Entry to match: '{entry_to_match}'")
    
    # Step 2: Check group patterns
    group_pattern = r'\([A-Z]{2,4}(?:-[A-Z])?,\s*G-\d+\)'
    entry_has_group = re.search(group_pattern, entry_to_match)
    selected_has_group = re.search(group_pattern, selected_course['name'])
    print(f"2. Entry has group: {entry_has_group is not None}")
    print(f"   Selected has group: {selected_has_group is not None}")
    
    # Step 3: If both have groups, check name matching
    if entry_has_group and selected_has_group:
        print(f"3. Name comparison:")
        print(f"   Selected: '{selected_course['name'].lower()}'")
        print(f"   Entry: '{entry_to_match.lower()}'")
        name_match = selected_course['name'].lower() == entry_to_match.lower()
        print(f"   Names match: {name_match}")
        
        if not name_match:
            print("   FAILED: Names don't match!")
            return False
    
    # Step 4: Check lab logic
    selected_name = selected_course['name']
    has_lab_check = 'lab' not in selected_name.lower() and 'lab' in entry_to_match.lower()
    print(f"4. Lab check (reject if true): {has_lab_check}")
    
    if has_lab_check:
        print("   FAILED: Lab rejection!")
        return False
    
    # Step 5: Section matching
    department = selected_course.get('department', '')
    section = selected_course.get('section', '')
    print(f"5. Section matching:")
    print(f"   Department: '{department}'")
    print(f"   Section: '{section}'")
    
    if entry_has_group or selected_has_group:
        if department and section:
            group_section_pattern = rf"\({department}-{section},\s*G-\d+\)"
            print(f"   Group pattern: '{group_section_pattern}'")
            print(f"   Testing against: '{class_entry}'")
            section_match = re.search(group_section_pattern, class_entry) is not None
            print(f"   Section match: {section_match}")
        else:
            section_match = False
            print(f"   No department/section - section_match: {section_match}")
    
    print(f"6. Final result: {section_match}")
    return section_match

if __name__ == "__main__":
    debug_matching_detailed()
