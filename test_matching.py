#!/usr/bin/env python3

import sys
sys.path.append('.')
from extract_timetable import matches_selected_course

def test_matching():
    # Test problematic course
    selected_course = {
        'name': 'DIP',
        'department': 'CS',
        'section': 'A',
        'batch': 'BS CS (2022)'
    }
    
    # Test various cell entry formats that might appear in the timetable
    test_entries = [
        'DIP (CS, G-2)',
        'DIP (CS, G-2) A',
        'DIP (CS, G-2) (CS-A)',
        'DIP (CS, G-2) -A',
        'DIP (CS, G-2) (A)',
        'DIP A',
        'DIP (A)',
        'DIP (CS-A)',
        'DIP -A'
    ]
    
    print("Testing course matching:")
    print("=" * 50)
    print(f"Selected course: {selected_course}")
    print()
    
    for entry in test_entries:
        # Mock batch colors and cell color
        batch_colors = {'test_color': 'BS CS (2022)'}
        cell_color = 'test_color'
        
        match_result = matches_selected_course(entry, selected_course, cell_color, batch_colors)
        print(f"Entry: '{entry}' -> Match: {match_result}")

if __name__ == "__main__":
    test_matching()
