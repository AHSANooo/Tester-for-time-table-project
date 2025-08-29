#!/usr/bin/env python3

import sys
sys.path.append('.')
from extract_timetable import parse_embedded_time_info
import re

def debug_matching_steps():
    class_entry = 'Gen AI (CS-C,G-1)'
    selected_course = {
        'name': 'Gen AI (CS,G-1)',
        'department': 'CS',
        'section': 'C',
        'batch': 'BS CS (2022)'
    }
    
    print("Debugging matching steps:")
    print("=" * 50)
    print(f"Class entry: '{class_entry}'")
    print(f"Selected course name: '{selected_course['name']}'")
    print(f"Selected section: '{selected_course['section']}'")
    print()
    
    # Step 1: Parse embedded time info
    cleaned_entry, _, has_embedded_time = parse_embedded_time_info(class_entry)
    entry_to_match = cleaned_entry if has_embedded_time else class_entry
    
    print(f"Step 1 - Entry to match: '{entry_to_match}'")
    print(f"Has embedded time: {has_embedded_time}")
    print()
    
    # Step 2: Check group patterns
    group_pattern = r'\([A-Z]{2,4},\s*G-\d+\)'
    entry_has_group = re.search(group_pattern, entry_to_match)
    selected_has_group = re.search(group_pattern, selected_course['name'])
    
    print(f"Step 2 - Entry has group: {entry_has_group is not None}")
    print(f"Selected has group: {selected_has_group is not None}")
    print()
    
    # Step 3: Name matching
    if entry_has_group and selected_has_group:
        print(f"Step 3 - Comparing names:")
        print(f"  Selected: '{selected_course['name'].lower()}'")
        print(f"  Entry: '{entry_to_match.lower()}'")
        print(f"  Match: {selected_course['name'].lower() == entry_to_match.lower()}")
    print()
    
    # Step 4: Section matching
    department = selected_course.get('department', '')
    section = selected_course.get('section', '')
    group_section_pattern = rf"\({department}-{section},\s*G-\d+\)"
    
    print(f"Step 4 - Section matching:")
    print(f"  Pattern: '{group_section_pattern}'")
    print(f"  Class entry: '{class_entry}'")
    section_match = re.search(group_section_pattern, class_entry) is not None
    print(f"  Section match: {section_match}")

if __name__ == "__main__":
    debug_matching_steps()
