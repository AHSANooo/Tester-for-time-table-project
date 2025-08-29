#!/usr/bin/env python3

import re

def debug_section_extraction():
    test_entry = "DIP (CS, G-2) (CS-A)"
    dept = "CS"
    
    print(f"Testing: '{test_entry}'")
    print(f"Department: '{dept}'")
    print()
    
    # Test each pattern individually
    section_patterns = [
        (rf'\({dept}-([A-Z])\)', rf'\({dept}-[A-Z]\)'),  # Pattern like "(CS-A)"
        (r'-([A-Z])\b', r'-[A-Z]\b'),                    # Pattern like "-A"
        (r'\(([A-Z])\)', r'\([A-Z]\)'),                  # Pattern like "(A)"
        (r'\s([A-Z])\s', r'\s[A-Z]\s'),                  # Pattern like " A "
        (r'\s([A-Z])$', r'\s[A-Z]$')                     # Pattern like " A" at end
    ]
    
    for i, (extract_pattern, remove_pattern) in enumerate(section_patterns):
        print(f"Pattern {i+1}: Extract='{extract_pattern}', Remove='{remove_pattern}'")
        match = re.search(extract_pattern, test_entry)
        if match:
            section = match.group(1)
            print(f"  Found section: '{section}'")
            
            # Test removal
            clean_name = re.sub(remove_pattern, '', test_entry)
            print(f"  After removal: '{clean_name}'")
        else:
            print(f"  No match")
        print()

if __name__ == "__main__":
    debug_section_extraction()
