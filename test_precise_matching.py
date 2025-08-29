#!/usr/bin/env python3

import sys
sys.path.append('.')
from extract_timetable import matches_selected_course

def test_precise_group_matching():
    # Test case: User selects "Gen AI (CS,G-1) CS C 2022"
    selected_course_c = {
        'name': 'Gen AI (CS,G-1)',
        'department': 'CS',
        'section': 'C',
        'batch': 'BS CS (2022)'
    }
    
    # Test various actual timetable cell entries
    test_entries = [
        'Gen AI (CS-A,G-1)',      # Should NOT match (section A, not C)
        'Gen AI (CS-B,G-1)',      # Should NOT match (section B, not C)  
        'Gen AI (CS-C,G-1)',      # Should match (section C)
        'Gen AI (CS-A,G-2)',      # Should NOT match (different group)
        'Gen AI (CS-C,G-2)',      # Should NOT match (different group)
        'COAL (CS-C)'             # Should NOT match (different course)
    ]
    
    print("Testing precise group course matching:")
    print("=" * 60)
    print(f"Selected course: {selected_course_c}")
    print()
    
    for entry in test_entries:
        # Mock batch colors and cell color
        batch_colors = {'test_color': 'BS CS (2022)'}
        cell_color = 'test_color'
        
        match_result = matches_selected_course(entry, selected_course_c, cell_color, batch_colors)
        expected = "✅ MATCH" if entry == 'Gen AI (CS-C,G-1)' else "❌ no match"
        print(f"Entry: '{entry}' -> {match_result} {expected}")

if __name__ == "__main__":
    test_precise_group_matching()
