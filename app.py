import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import re

# Import core timetable functions
try:
    import extract_timetable
    extract_batch_colors = extract_timetable.extract_batch_colors
    get_timetable = extract_timetable.get_timetable
    
    # Try to get get_custom_timetable function
    if hasattr(extract_timetable, 'get_custom_timetable'):
        get_custom_timetable = extract_timetable.get_custom_timetable
    else:
        # Fallback function if not available
        def get_custom_timetable(spreadsheet, selected_courses):
            return "⚠️ Custom timetable function not available. Please check the implementation."
        st.warning("Custom timetable function not found. Using fallback function.")
        
except ImportError as e:
    st.error(f"Failed to import timetable functions: {e}")
    st.stop()

# Import course extraction functions
try:
    # Use the fuller extractor which reliably extracts departments and batches
    from course_extractor import extract_departments_and_batches, extract_all_courses, search_courses
except ImportError as e:
    st.error(f"Failed to import course extraction functions: {e}")
    st.stop()

# Import user preferences functions
try:
    from user_preferences import (
        initialize_session_state, add_course_to_selection, remove_course_from_selection,
        clear_all_selections, get_selected_courses, update_search_filters, 
        get_search_filters, save_search_results, get_last_search_results,
        is_course_selected, get_selection_summary
    )
except ImportError as e:
    st.error(f"Failed to import user preferences functions: {e}")
    st.stop()

SHEET_URL = "https://docs.google.com/spreadsheets/d/1cmDXt7UTIKBVXBHhtZ0E4qMnJrRoexl2GmDFfTBl0Z4/edit?usp=drivesdk"


def get_google_sheets_data(sheet_url):
    """Fetch Google Sheets data with formatting using Sheets API v4"""
    credentials_dict = st.secrets["google_service_account"]
    creds = Credentials.from_service_account_info(
        credentials_dict,
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )

    service = build('sheets', 'v4', credentials=creds)
    spreadsheet_id = sheet_url.split('/d/')[1].split('/')[0]

    # Get spreadsheet with cell formatting
    spreadsheet = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        includeGridData=True
    ).execute()

    return spreadsheet


def main():
    st.title("FAST-NUCES FCS Timetable System")

    # Initialize session state
    initialize_session_state()

    # Fetch full spreadsheet data
    st.info("Welcome Everyone!")
    try:
        spreadsheet = get_google_sheets_data(SHEET_URL)
    except Exception as e:
        st.error(f"❌ Connection failed: {str(e)}")
        return

    # Extract batch-color mappings
    batch_colors = extract_batch_colors(spreadsheet)

    if not batch_colors:
        st.error("⚠️ No batches found. Please check the sheet format.")
        return

    # Create tabs
    tab1, tab2 = st.tabs(["📚 Batch Timetable", "🔍 Custom Course Selection"])

    # Tab 1: Original Batch Timetable (existing functionality)
    with tab1:
        st.header("📚 Batch Timetable")
        st.write("Select your batch and section to view your timetable.")
        
        # Dropdown for batch selection
        batch_list = list(batch_colors.values())

        with st.expander("✅ **Select Your Batch and Department:**"):
            batch = st.radio("Select your batch:", batch_list, index=None)

        # User input for section
        section = st.text_input("🔠 Enter your section (e.g., 'A')").strip().upper()

        # Submit button
        if st.button("Show Timetable", key="batch_timetable_btn"):
            if not batch or not section:
                st.warning("⚠️ Please enter both batch and section.")
                return

            schedule = get_timetable(spreadsheet, batch, section)

            if schedule.startswith("⚠️"):
                st.error(schedule)
            else:
                st.markdown(f"## Timetable for **{batch}, Section {section}**")
                st.markdown(schedule)

    # Tab 2: Custom Course Selection (new functionality)
    with tab2:
        st.header("🔍 Custom Course Selection")
        st.write("Search and select individual courses to create your custom timetable.")
        
        # Reuse the batch info already extracted for the Batch Timetable tab
        # batch_colors is a dict color_hex -> batch_string extracted earlier
        unique_batches = sorted(set(batch_colors.values())) if batch_colors else []

        # Derive departments from batch strings (robust to formats like 'BS-CS-1' or 'BS CS (2025)')
        departments_set = set()
        for b in unique_batches:
            dept = ""
            if '-' in b:
                parts = b.split('-')
                if len(parts) >= 2:
                    dept = parts[1]
            else:
                # Find uppercase tokens like CS, EE, DS etc., ignore 'BS'
                tokens = re.findall(r"\b[A-Z]{2,4}\b", b)
                for t in tokens:
                    if t != 'BS':
                        dept = t
                        break

            if dept:
                departments_set.add(dept)

        department_list = sorted(list(departments_set))
        batch_list = unique_batches
        
        # Extract all courses for search
        all_courses = extract_all_courses(spreadsheet)
        
        # Search and filter section
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_query = st.text_input("🔍 Search courses", 
                                       value=st.session_state.search_query,
                                       placeholder="Enter course name...")
        
        with col2:
            selected_department = st.selectbox("🏢 Department", 
                                             [""] + department_list,
                                             index=0 if not st.session_state.selected_department else 
                                                   department_list.index(st.session_state.selected_department) + 1)
        
        with col3:
            selected_batch = st.selectbox("👥 Batch", 
                                        [""] + batch_list,
                                        index=0 if not st.session_state.selected_batch else 
                                              batch_list.index(st.session_state.selected_batch) + 1)
        
        # Update search filters
        update_search_filters(search_query, selected_department, selected_batch)
        
        # Search courses
        if search_query or selected_department or selected_batch:
            search_results = search_courses(all_courses, search_query, selected_department, selected_batch)
            save_search_results(search_results)
            
            if search_results:
                st.subheader(f"📋 Search Results ({len(search_results)} courses found)")
                
                # Display search results
                for course in search_results:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"**{course['name']}** - {course['department']} - Section {course['section']} - {course['batch']}")
                    
                    with col2:
                        if is_course_selected(course):
                            st.write("✅ Selected")
                        else:
                            if st.button("➕ Add", key=f"add_{course['name']}_{course['section']}_{course['batch']}"):
                                add_course_to_selection(course)
                                st.rerun()
                    
                    with col3:
                        if is_course_selected(course):
                            if st.button("❌ Remove", key=f"remove_{course['name']}_{course['section']}_{course['batch']}"):
                                remove_course_from_selection(course)
                                st.rerun()
            else:
                st.info("No courses found matching your criteria.")
        else:
            st.info("Enter search criteria to find courses.")
        
        # Selected courses section
        selected_courses = get_selected_courses()
        if selected_courses:
            st.subheader("📝 Selected Courses")
            
            # Show selection summary
            summary = get_selection_summary()
            st.write(f"**Total Courses:** {summary['total_courses']}")
            st.write(f"**Departments:** {', '.join(summary['departments']) if summary['departments'] else 'None'}")
            st.write(f"**Batches:** {', '.join(summary['batches']) if summary['batches'] else 'None'}")
            
            # Display selected courses with remove buttons
            for i, course in enumerate(selected_courses):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{course['name']}** - {course['department']} - Section {course['section']} - {course['batch']}")
                with col2:
                    if st.button("❌ Remove", key=f"selected_remove_{i}"):
                        remove_course_from_selection(course)
                        st.rerun()
            
            # Clear all and show timetable buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear All Selections"):
                    clear_all_selections()
                    st.rerun()
            
            with col2:
                if st.button("📅 Show Custom Timetable", key="custom_timetable_btn"):
                    schedule = get_custom_timetable(spreadsheet, selected_courses)
                    
                    if schedule.startswith("⚠️"):
                        st.error(schedule)
                    else:
                        st.markdown("## Custom Timetable")
                        st.markdown(schedule)
        else:
            st.info("No courses selected. Search and add courses to create your custom timetable.")


if __name__ == "__main__":
    main()

    # Footer with support contact and LinkedIn profile
    st.markdown("---")
    st.markdown("📧 **For any issues or support, please contact:** [i230553@isb.nu.edu.pk](mailto:i230553@isb.nu.edu.pk)")

    st.markdown("🔗 **Connect with me on LinkedIn:** [Muhammad Ahsan](https://www.linkedin.com/in/muhammad-ahsan-7612701a7)")

