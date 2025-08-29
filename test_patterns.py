#!/usr/bin/env python3

import re

def test_group_patterns():
    patterns = [
        r'\([A-Z]{2,4},\s*G-\d+\)',  # Current pattern
        r'\([A-Z]{2,4}-[A-Z],\s*G-\d+\)',  # Pattern with section
        r'\([A-Z]{2,4}(?:-[A-Z])?,\s*G-\d+\)',  # Pattern with optional section
    ]
    
    test_strings = [
        'Gen AI (CS,G-1)',      # Normalized
        'Gen AI (CS-C,G-1)',    # With section
        'DIP (CS,G-2)',         # Normalized
        'DIP (CS-A,G-2)',       # With section
    ]
    
    for i, pattern in enumerate(patterns):
        print(f"Pattern {i+1}: {pattern}")
        for test_str in test_strings:
            match = re.search(pattern, test_str)
            print(f"  '{test_str}': {match is not None}")
        print()

if __name__ == "__main__":
    test_group_patterns()
