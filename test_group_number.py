#!/usr/bin/env python3

import re

def test_group_number_matching():
    # Test cases
    test_cases = [
        {
            'selected': 'Gen AI (CS,G-1)',
            'entries': [
                'Gen AI (CS-C,G-1)',  # Should match (same group)
                'Gen AI (CS-C,G-2)',  # Should NOT match (different group)
            ]
        }
    ]
    
    department = 'CS'
    section = 'C'
    
    for case in test_cases:
        print(f"Selected: {case['selected']}")
        
        # Extract group number from selected course
        selected_group_match = re.search(r'G-(\d+)', case['selected'])
        if selected_group_match:
            selected_group = selected_group_match.group(1)
            print(f"Selected group: G-{selected_group}")
        
        for entry in case['entries']:
            print(f"\nTesting entry: {entry}")
            
            # Current pattern - only checks section, not group number
            current_pattern = rf"\({department}-{section},\s*G-\d+\)"
            current_match = re.search(current_pattern, entry) is not None
            print(f"Current pattern '{current_pattern}': {current_match}")
            
            # Fixed pattern - checks both section AND group number
            if selected_group_match:
                fixed_pattern = rf"\({department}-{section},\s*G-{selected_group}\)"
                fixed_match = re.search(fixed_pattern, entry) is not None
                print(f"Fixed pattern '{fixed_pattern}': {fixed_match}")
        print("-" * 50)

if __name__ == "__main__":
    test_group_number_matching()
