import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import re
import time

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

# Global flag to control offline mode
OFFLINE_MODE_ACTIVE = False

def fetch_google_sheets_data_once(sheet_url):
    """Fetch Google Sheets data ONLY ONCE during initial load"""
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


def initialize_offline_data():
    """Initialize and store all data in session state for true offline operation"""
    if 'offline_data_loaded' not in st.session_state:
        st.session_state.offline_data_loaded = False
        st.session_state.offline_spreadsheet = None
        st.session_state.offline_batch_colors = None
        st.session_state.offline_all_courses = None
        st.session_state.offline_departments = None
        st.session_state.offline_years = None
        st.session_state.offline_mode_enabled = False
    # When True, the app will never attempt network calls and will only use cached data
    st.session_state.force_offline = False
    st.session_state.offline_timestamp = None


def is_offline_data_expired():
    """Check if offline data is older than 1 hour"""
    if st.session_state.get('offline_timestamp') is None:
        return True
    
    # Check if data is older than 1 hour (3600 seconds)
    current_time = time.time()
    elapsed_time = current_time - st.session_state.offline_timestamp
    return elapsed_time > 3600  # 1 hour


def load_all_data_for_offline():
    """Load and store all necessary data in session state for offline use"""
    global OFFLINE_MODE_ACTIVE
    
    # Check if data is expired and needs refresh
    if st.session_state.get('offline_data_loaded') and not is_offline_data_expired():
        # Data is still fresh, no need to reload
        OFFLINE_MODE_ACTIVE = True
        st.session_state.offline_mode_enabled = True
        return True
    
    # If user explicitly requested 'force offline' mode, do not attempt any network calls
    if st.session_state.get('force_offline'):
        # If we already have cached data and it's not expired, enable offline mode
        if st.session_state.get('offline_data_loaded') and not is_offline_data_expired():
            OFFLINE_MODE_ACTIVE = True
            st.session_state.offline_mode_enabled = True
            return True
        # Otherwise, we cannot fetch data because network calls are disabled
        st.error("⚠️ Force-offline mode enabled but no cached data is available. Please disable Force Offline or reload the app while connected to the internet to populate cache.")
        return False

    try:
        # Clear old data if expired
        if is_offline_data_expired():
            st.session_state.offline_spreadsheet = None
            st.session_state.offline_batch_colors = None
            st.session_state.offline_all_courses = None
            
        # Fetch spreadsheet data ONLY if not already cached
        if st.session_state.offline_spreadsheet is None:
            st.session_state.offline_spreadsheet = fetch_google_sheets_data_once(SHEET_URL)
        
        # Extract and store batch colors
        if st.session_state.offline_batch_colors is None:
            st.session_state.offline_batch_colors = extract_batch_colors(st.session_state.offline_spreadsheet)
        
        # Extract and store all courses
        if st.session_state.offline_all_courses is None:
            st.session_state.offline_all_courses = extract_all_courses(st.session_state.offline_spreadsheet)
        
        # Extract and store departments and years
        if st.session_state.offline_departments is None or st.session_state.offline_years is None:
            all_courses = st.session_state.offline_all_courses
            
            # Extract departments
            department_list = sorted(set(c.get('department', '') for c in all_courses if c.get('department')))
            
            # Extract years
            year_list = []
            for course in all_courses:
                batch = str(course.get('batch', ''))
                m = re.search(r"(20\d{2})", batch)
                if m and m.group(1) not in year_list:
                    year_list.append(m.group(1))
            
            st.session_state.offline_departments = department_list
            st.session_state.offline_years = sorted(year_list)
        
        # Mark as loaded and activate offline mode with timestamp
        st.session_state.offline_data_loaded = True
        st.session_state.offline_mode_enabled = True
        st.session_state.offline_timestamp = time.time()  # Record load time
        OFFLINE_MODE_ACTIVE = True
        return True
        
    except Exception as e:
        st.error(f"Failed to load data for offline use: {str(e)}")
        return False


def get_offline_batch_colors():
    """Get batch colors from session state (works offline)"""
    return st.session_state.get('offline_batch_colors', {})


def get_offline_all_courses():
    """Get all courses from session state (works offline)"""
    return st.session_state.get('offline_all_courses', [])


def get_offline_departments_and_years():
    """Get departments and years from session state (works offline)"""
    departments = st.session_state.get('offline_departments', [])
    years = st.session_state.get('offline_years', [])
    return departments, years


def is_offline_ready():
    """Check if app is ready for offline operation"""
    return (st.session_state.get('offline_data_loaded', False) and
            st.session_state.get('offline_spreadsheet') is not None and
            st.session_state.get('offline_batch_colors') is not None and
            st.session_state.get('offline_all_courses') is not None and
            st.session_state.get('offline_mode_enabled', False) and
            not is_offline_data_expired())


def get_offline_timetable(batch, section):
    """Generate timetable using ONLY cached data (100% offline)"""
    try:
        # Use ONLY session state data - NO NETWORK CALLS
        spreadsheet = st.session_state.get('offline_spreadsheet')
        if spreadsheet is None:
            return "⚠️ Offline data not available. Please reload the page with internet connection."
        
        # Call timetable function with cached spreadsheet data
        return get_timetable(spreadsheet, batch, section)
    except Exception as e:
        return f"⚠️ Offline timetable generation failed: {str(e)}"


def get_offline_custom_timetable(selected_courses):
    """Generate custom timetable using ONLY cached data (100% offline)"""
    try:
        # Use ONLY session state data - NO NETWORK CALLS
        spreadsheet = st.session_state.get('offline_spreadsheet')
        if spreadsheet is None:
            return "⚠️ Offline data not available. Please reload the page with internet connection."
        
        # Call custom timetable function with cached spreadsheet data
        return get_custom_timetable(spreadsheet, selected_courses)
    except Exception as e:
        return f"⚠️ Offline custom timetable generation failed: {str(e)}"


def format_course_display(course: dict) -> str:
    """Return a compact display string for a course: 'name dept section year-or-batch'
    Example: 'Data St CS A 2024' (falls back to full batch string if year not found)
    """
    name = course.get('name', '').strip()
    dept = course.get('department', '').strip()
    section = course.get('section', '').strip()
    batch = str(course.get('batch', '')).strip()
    # Prefer year (e.g., 2024) when available inside the batch string
    m = re.search(r"(20\d{2})", batch)
    year = m.group(1) if m else batch
    parts = [p for p in [name, dept, section, year] if p]
    return " ".join(parts)


def main():
    st.title("FAST-NUCES FCS Timetable System")
    
    # Initialize session state and offline data
    initialize_session_state()
    initialize_offline_data()

    # Check if we're in offline mode
    # Provide user control to force offline-only operation (will prevent network calls)
    st.write("")
    force_offline = st.checkbox("🔒 Force Offline (do not attempt network calls)", value=st.session_state.get('force_offline', False))
    st.session_state.force_offline = force_offline

    offline_ready = is_offline_ready()
    
    if offline_ready:
        st.success("🌐 **OFFLINE MODE ACTIVE** - App works without internet for 1 hour!")
        # Use offline data - NO NETWORK CALLS
        batch_colors = get_offline_batch_colors()
        all_courses = get_offline_all_courses()
        department_list, year_list = get_offline_departments_and_years()
    else:
        st.info("🔄 Loading data for offline use... (requires internet connection)")
        with st.spinner("Downloading data for offline operation..."):
            try:
                # Load all data for offline use - ONLY NETWORK CALL
                if load_all_data_for_offline():
                    st.success("✅ **OFFLINE MODE ACTIVATED** - App now works without internet for 1 hour!")
                    # Use the newly loaded offline data
                    batch_colors = get_offline_batch_colors()
                    all_courses = get_offline_all_courses()
                    department_list, year_list = get_offline_departments_and_years()
                else:
                    st.error("❌ Failed to load data for offline use")
                    return
            except Exception as e:
                st.error(f"❌ Failed to load data: {str(e)}")
                st.warning("⚠️ Internet connection required for initial data loading.")
                return

    # Validate data
    if not batch_colors:
        st.error("⚠️ No batches found. Please check the sheet format.")
        return
    
    # Add offline test section for debugging
    if is_offline_ready():
        # Calculate remaining offline time
        current_time = time.time()
        elapsed_time = current_time - st.session_state.offline_timestamp
        remaining_time = 3600 - elapsed_time  # 1 hour - elapsed time
        remaining_minutes = max(0, int(remaining_time / 60))
        
        with st.expander("🧪 Offline Status & Test"):
            st.write("**Offline Mode Status:** ✅ ACTIVE")
            st.write(f"**Time Remaining:** {remaining_minutes} minutes")
            st.write(f"- Spreadsheet data: {'✅ Loaded' if st.session_state.get('offline_spreadsheet') else '❌ Missing'}")
            st.write(f"- Batch colors: {len(batch_colors)} batches")
            st.write(f"- Courses: {len(all_courses)} courses")
            st.write(f"- Departments: {len(department_list)} departments")
            st.write(f"- Years: {len(year_list)} years")
            st.success("🔌 **FULLY OFFLINE!** No internet needed for timetables.")
            
            if remaining_minutes < 10:
                st.warning(f"⏰ Data will expire in {remaining_minutes} minutes. Refresh page to reload.")

    # Create tabs
    tab1, tab2 = st.tabs(["📚 Batch Timetable", "🔍 Custom Course Selection"])

    # Tab 1: Original Batch Timetable (existing functionality)
    with tab1:
        st.header("📚 Batch Timetable")
        st.write("Select your batch and section to view your timetable.")
        
        # Prepare batch data for dropdown selection
        batch_list = list(batch_colors.values())
        
        # Extract departments from batch names (e.g., "BS CS (2024)" -> "CS")
        dept_pattern = r"BS\s+([A-Z]+)"
        departments_in_batches = set()
        for batch_name in batch_list:
            match = re.search(dept_pattern, str(batch_name))
            if match:
                departments_in_batches.add(match.group(1))
        department_list_tab1 = sorted(departments_in_batches)
        
        # Extract years from batch names
        year_to_batches_tab1 = {}
        year_list_tab1 = []
        for b in batch_list:
            m = re.search(r"(20\d{2})", str(b))
            if m:
                y = m.group(1)
                year_to_batches_tab1.setdefault(y, []).append(b)
                if y not in year_list_tab1:
                    year_list_tab1.append(y)
        year_list_tab1 = sorted(year_list_tab1)

        # Dropdown selection for department and batch (no auto-refresh)
        col1, col2 = st.columns(2)
        
        with col1:
            selected_department_tab1 = st.selectbox("🏢 Department",
                                                   [""] + department_list_tab1,
                                                   key="dept_tab1")
        
        with col2:
            selected_year_tab1 = st.selectbox("👥 Batch",
                                            [""] + year_list_tab1,
                                            key="year_tab1")
        
        # Filter batches based on selections
        filtered_batches = batch_list
        if selected_department_tab1:
            filtered_batches = [b for b in filtered_batches if selected_department_tab1 in str(b)]
        if selected_year_tab1:
            filtered_batches = [b for b in filtered_batches if selected_year_tab1 in str(b)]
        
        # Auto-select batch from filtered list (take first match)
        if filtered_batches:
            batch = filtered_batches[0]  # Auto-select first matching batch
            if selected_department_tab1 or selected_year_tab1:
                st.success(f"📋 Auto-selected batch: **{batch}**")
        else:
            batch = ""
            if selected_department_tab1 or selected_year_tab1:
                st.warning("No batches found for the selected filters.")

        # User input for section
        section = st.text_input("🔠 Enter your section (e.g., 'A')").strip().upper()

        # Submit button - works offline using cached data
        if st.button("Show Timetable", key="batch_timetable_btn"):
            if not batch or not section:
                st.warning("⚠️ Please enter both batch and section.")
            else:
                # Generate timetable using cached data (works offline)
                with st.spinner("Generating timetable..."):
                    try:
                        # Try offline generation first
                        schedule = get_offline_timetable(batch, section)
                        
                        if schedule.startswith("⚠️"):
                            st.error(schedule)
                        else:
                            st.markdown(f"## Timetable for **{batch}, Section {section}**")
                            st.markdown(schedule)
                            if is_offline_ready():
                                st.info("📱 Generated using offline data")
                                
                    except Exception as e:
                        st.error(f"❌ Failed to generate timetable: {str(e)}")
                        st.warning("🌐 Please check your internet connection and try again.")

    # Tab 2: Custom Course Selection (new functionality)
    with tab2:
        st.header("🔍 Custom Course Selection")
        st.write("Search and select individual courses to create your custom timetable.")

        # Use cached data instead of recomputing
        unique_batches = sorted(set(batch_colors.values())) if batch_colors else []
        batch_list = unique_batches

        # Filter section - moved above search for better mobile layout
        col1, col2 = st.columns(2)

        with col1:
            # Safely compute the initial index for department selectbox — avoid ValueError if session value not present
            dept_index = 0
            if st.session_state.selected_department:
                try:
                    dept_index = department_list.index(st.session_state.selected_department) + 1
                except ValueError:
                    dept_index = 0

            selected_department = st.selectbox("🏢 Department",
                                             [""] + department_list,
                                             index=dept_index)

        with col2:
            # Decide initial index based on previous selection which might be a full batch or a year
            initial_index = 0
            if st.session_state.selected_batch:
                m_prev = re.search(r"(20\d{2})", str(st.session_state.selected_batch))
                prev_year = m_prev.group(1) if m_prev else str(st.session_state.selected_batch)
                if prev_year in year_list:
                    initial_index = ([""] + year_list).index(prev_year)

            # Show only years in the dropdown; selected_year holds the year string (e.g., '2025')
            selected_year = st.selectbox("👥 Batch", [""] + year_list, index=initial_index)

            # For filtering we'll later map selected_year -> list of batches via year_to_batches
            selected_batch = selected_year or ""

        # Course search section - now appears below filters for better mobile experience
        # Get filtered courses based on current department and batch selections
        # This allows the course dropdown to update dynamically
        current_courses = all_courses  # Use cached data
        
        # Apply department filter if selected
        if selected_department:
            current_courses = [c for c in current_courses if c.get('department') == selected_department]
        
        # Apply batch/year filter if selected
        if selected_year:
            current_courses = [c for c in current_courses if selected_year in str(c.get('batch', ''))]
        
        # Show filter status
        if selected_department or selected_year:
            st.info(f"📚 Found {len(current_courses)} courses for {selected_department or 'All Departments'} - {selected_year or 'All Years'}")
        
        # Create course options for dropdown with the new format: "course_name department section batch"
        course_options = [""]  # Clear option message
        course_map = {}  # Map display text to course object
        
        for course in current_courses:
            display_text = format_course_display(course)
            course_options.append(display_text)
            course_map[display_text] = course
        
        selected_course_text = st.selectbox("🔍 Search courses",
                                           course_options,
                                           index=0)

        # Update search filters (store selected_year in session state's selected_batch for persistence)
        update_search_filters("", selected_department, selected_batch)

        # Handle course selection from dropdown - automatically add to selection
        # Only auto-add when course is actually selected (not empty) and different from current
        if (selected_course_text and 
            selected_course_text != "" and 
            selected_course_text in course_map):
            
            selected_course = course_map[selected_course_text]
            
            # Check if course is not already selected, then add it automatically
            if not is_course_selected(selected_course):
                add_course_to_selection(selected_course)
                st.success(f"✅ Added **{format_course_display(selected_course)}** to your selection!")
                st.rerun()
            else:
                # Show a brief message that it's already selected
                st.info(f"✅ **{format_course_display(selected_course)}** is already in your selection.")
        
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
                    # Use compact format for selected courses list
                    st.write(f"**{format_course_display(course)}**")
                with col2:
                    if st.button("❌ Remove", key=f"selected_remove_{i}"):
                        remove_course_from_selection(course)
                        st.rerun()
            
            # Small Clear All button on the left and a centered Show Custom Timetable button below it
            c1, c2 = st.columns([1, 3])
            with c1:
                # use a smaller button by adding a compact label and container
                if st.button("🗑️ Clear", key="clear_small"):
                    clear_all_selections()
                    st.rerun()

            # Centered Show Timetable button on its own row
            st.write("")
            center_col1, center_col2, center_col3 = st.columns([1, 2, 1])
            with center_col2:
                if st.button("📅 Show Custom Timetable", key="custom_timetable_btn"):
                    # Generate custom timetable using cached data (works offline)
                    with st.spinner("Generating custom timetable..."):
                        try:
                            # Try offline generation first
                            schedule = get_offline_custom_timetable(selected_courses)
                            
                            if schedule.startswith("⚠️"):
                                st.error(schedule)
                            else:
                                st.markdown("## Custom Timetable")
                                st.markdown(schedule)
                                if is_offline_ready():
                                    st.info("📱 Generated using offline data")
                                    
                        except Exception as e:
                            st.error(f"❌ Failed to generate custom timetable: {str(e)}")
                            st.warning("🌐 Please check your internet connection and try again.")
        else:
            st.info("No courses selected. Search and add courses to create your custom timetable.")


if __name__ == "__main__":
    main()

    # Footer with offline capability highlight and support contact
    st.markdown("---")
    
    # Highlight key offline feature
    st.markdown("""
    ### 🌟 **KEY FEATURE: OFFLINE CAPABILITY**
    
    ✅ **Works without internet** once initially loaded  
    ✅ **All data cached locally** for 1 hour  
    ✅ **Full functionality offline** - select courses, generate timetables  
    ✅ **Perfect for poor connectivity** areas  
    
    *The app automatically caches all timetable data on first load, enabling complete offline functionality.*
    """)
    
    st.markdown("📧 **For any issues or support, please contact:** [i230553@isb.nu.edu.pk](mailto:i230553@isb.nu.edu.pk)")

    st.markdown("🔗 **Connect with me on LinkedIn:** [Muhammad Ahsan](https://www.linkedin.com/in/muhammad-ahsan-7612701a7)")

