#!/usr/bin/env python3
"""
FHIR Agentic Scheduler - Professional Demo Version

Dependencies (add to requirements.txt or platform settings):
streamlit>=1.28.0
requests>=2.31.0
pandas>=2.0.0
python-dateutil>=2.8.0
"""

# =============================================================================
# IMPORTS AND CONFIGURATION
# =============================================================================

import streamlit as st        # Web UI framework - creates the interactive interface
import requests              # HTTP library - handles all FHIR server communication
import json                  # JSON handling - for FHIR resource formatting
from datetime import datetime, timedelta, date  # Date/time operations
from typing import List, Dict, Optional          # Type hints for better code quality
import logging              # Logging for debugging and demo monitoring

# DEMO FEATURE: Graceful dependency handling
# This ensures the demo works even with missing packages
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
    # Pandas provides enhanced data display in tables
except ImportError:
    PANDAS_AVAILABLE = False
    st.warning("Pandas not available. Some features may be limited.")

# DEMO FEATURE: Flexible date parsing
# Works with or without python-dateutil library
try:
    from dateutil.parser import parse as parse_date
except ImportError:
    # Fallback date parser for demo resilience
    def parse_date(date_string):
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))

# Configure logging for demo monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# FHIR SCHEDULER AGENT - THE CORE AI ENGINE
# =============================================================================

class FHIRSchedulerAgent:
    """
    FHIR Agentic Scheduler - The Core AI Engine
    
    DEMO SHOWCASE: This class demonstrates enterprise-grade healthcare interoperability
    
    Key Demo Features:
    - Real FHIR R4 server connectivity (HAPI test server)
    - RESTful API integration with proper headers and error handling
    - AI-powered appointment ranking with transparent scoring
    - Production-ready error handling and timeout management
    - Healthcare data standards compliance (HL7 FHIR)
    
    Perfect for showing:
    - Healthcare interoperability in action
    - Real-time API integration
    - AI/ML application in healthcare
    - Professional software architecture
    """
    
    def __init__(self, base_url: str = "https://hapi.fhir.org/baseR4"):
        """
        Initialize the FHIR connection
        
        DEMO HIGHLIGHT: We're connecting to a real, live FHIR server!
        - HAPI FHIR is a popular open-source FHIR implementation
        - This is the same technology used in major healthcare systems
        - Demonstrates real interoperability, not just mock data
        """
        self.base_url = base_url
        self.session = requests.Session()  # Reusable HTTP session for efficiency
        
        # DEMO FEATURE: Professional FHIR headers
        # These headers ensure proper FHIR communication
        self.session.headers.update({
            'Accept': 'application/fhir+json',      # Request FHIR JSON format
            'Content-Type': 'application/fhir+json' # Send FHIR JSON format
        })
        
    def test_connection(self) -> bool:
        """
        Test connection to the FHIR server
        
        DEMO HIGHLIGHT: Live connectivity test
        - Shows real-time server communication
        - Demonstrates proper error handling
        - Validates FHIR server availability for audience
        """
        try:
            # FHIR standard: /metadata endpoint provides server capabilities
            response = self.session.get(f"{self.base_url}/metadata", timeout=10)
            return response.status_code == 200
        except requests.RequestException as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def search_schedules(self, active_only: bool = True) -> List[Dict]:
        """
        Search for available schedules in the FHIR server
        
        DEMO SHOWCASE: Real FHIR resource querying
        - Uses standard FHIR search parameters
        - Demonstrates live data retrieval from healthcare systems
        - Shows how AI can work with real medical scheduling data
        
        Returns actual Schedule resources from the HAPI FHIR server
        """
        try:
            # DEMO FEATURE: FHIR search parameters
            params = {'_count': 50}  # Limit results for demo performance
            if active_only:
                params['active'] = 'true'  # Only get active schedules
                
            # DEMO HIGHLIGHT: Live FHIR API call
            response = self.session.get(f"{self.base_url}/Schedule", params=params, timeout=15)
            
            if response.status_code == 200:
                bundle = response.json()  # FHIR Bundle resource
                schedules = []
                
                # DEMO FEATURE: Parse FHIR Bundle structure
                if 'entry' in bundle:
                    for entry in bundle['entry']:
                        schedules.append(entry['resource'])  # Extract Schedule resources
                        
                logger.info(f"Found {len(schedules)} schedules")
                return schedules
            else:
                logger.error(f"Failed to fetch schedules: {response.status_code}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"Error searching schedules: {e}")
            return []
    
    def create_sample_schedule(self, practitioner_name: str = "Dr. Cloud Demo") -> Optional[str]:
        """
        Create a sample schedule for demonstration purposes
        
        DEMO SHOWCASE: Live FHIR resource creation
        - Creates a real Schedule resource on the HAPI server
        - Shows proper FHIR resource structure
        - Demonstrates write operations to healthcare systems
        - Perfect for live demo - creates data the audience can see immediately
        """
        try:
            # DEMO FEATURE: Dynamic scheduling (next 7 days)
            start_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=7)
            
            # DEMO HIGHLIGHT: Proper FHIR Schedule resource structure
            schedule_resource = {
                "resourceType": "Schedule",  # FHIR resource type
                
                # Business identifier for tracking
                "identifier": [{
                    "use": "usual",
                    "system": "http://cloud-demo.org/schedule-ids",
                    "value": f"CLOUD-SCH-{int(datetime.now().timestamp())}"  # Unique ID
                }],
                
                "active": True,  # Schedule is currently active
                
                # DEMO FEATURE: Healthcare service categorization
                "serviceCategory": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/service-category",
                        "code": "17",
                        "display": "General Practice"
                    }]
                }],
                
                # Specific service type
                "serviceType": [{
                    "concept": {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/service-type",
                            "code": "124",
                            "display": "General Practice"
                        }]
                    }
                }],
                
                # Medical specialty (using SNOMED CT codes)
                "specialty": [{
                    "coding": [{
                        "system": "http://snomed.info/sct",
                        "code": "419772000",
                        "display": "Family practice"
                    }]
                }],
                
                "name": f"{practitioner_name} - Cloud Demo Schedule",
                
                # DEMO FEATURE: Healthcare provider reference
                "actor": [{
                    "display": practitioner_name  # The healthcare provider
                }],
                
                # DEMO HIGHLIGHT: Time-based scheduling
                "planningHorizon": {
                    "start": start_time.isoformat() + "Z",  # ISO 8601 format
                    "end": end_time.isoformat() + "Z"
                },
                
                "comment": "Demo schedule created by FHIR Cloud Scheduler"
            }
            
            # DEMO SHOWCASE: Live FHIR resource creation
            response = self.session.post(
                f"{self.base_url}/Schedule",
                data=json.dumps(schedule_resource),
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                created_resource = response.json()
                schedule_id = created_resource.get('id')
                logger.info(f"Created demo schedule with ID: {schedule_id}")
                return schedule_id
            else:
                logger.error(f"Failed to create schedule: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating sample schedule: {e}")
            return None
    
    def rank_appointment_options(self, schedules: List[Dict], 
                               user_preferences: Dict) -> List[Dict]:
        """
        AI-POWERED APPOINTMENT RANKING ENGINE
        
        DEMO SHOWCASE: This is the "AI brain" of the system!
        
        KEY DEMO HIGHLIGHTS:
        - 100-point intelligent scoring system
        - Multi-criteria decision making
        - Transparent, explainable AI
        - Real-time preference matching
        - Healthcare-specific optimization
        
        BUSINESS VALUE:
        - Reduces appointment search time
        - Improves patient satisfaction
        - Optimizes provider schedules
        - Demonstrates AI in healthcare
        
        TECHNICAL SOPHISTICATION:
        - Weighted scoring algorithm
        - Multiple evaluation criteria
        - Graceful error handling
        - Scalable architecture
        """
        ranked_options = []
        
        for schedule in schedules:
            # Initialize scoring data structure
            score = 0
            details = {
                'schedule_id': schedule.get('id', 'Unknown'),
                'name': schedule.get('name', 'Unknown Schedule'),
                'comment': schedule.get('comment', ''),
                'actors': [],           # Healthcare providers
                'service_types': [],    # Types of medical services
                'specialties': [],      # Medical specialties
                'planning_horizon': {}, # Available time periods
                'score': 0,            # AI-calculated score (0-100)
                'score_details': {}    # Transparent scoring breakdown
            }
            
            # =================================================================
            # DEMO FEATURE: Healthcare Data Extraction
            # Parse complex FHIR data structures into usable information
            # =================================================================
            
            # Extract healthcare providers (doctors, nurses, etc.)
            if 'actor' in schedule:
                details['actors'] = [actor.get('display', 'Unknown') for actor in schedule['actor']]
            
            # Extract service types (what medical services are offered)
            if 'serviceType' in schedule:
                details['service_types'] = [
                    st.get('concept', {}).get('coding', [{}])[0].get('display', 'Unknown')
                    for st in schedule['serviceType']
                ]
            
            # Extract medical specialties (cardiology, dermatology, etc.)
            if 'specialty' in schedule:
                details['specialties'] = [
                    spec.get('coding', [{}])[0].get('display', 'Unknown')
                    for spec in schedule['specialty']
                ]
            
            # Extract scheduling timeframes
            if 'planningHorizon' in schedule:
                details['planning_horizon'] = schedule['planningHorizon']
            
            # =================================================================
            # AI SCORING ALGORITHM - THE DEMO CENTERPIECE
            # =================================================================
            
            score_details = {}  # Track why each score was given (explainable AI)
            
            # CRITERIA 1: Service Type Matching (30 points maximum)
            # DEMO HIGHLIGHT: Smart semantic matching
            preferred_service = user_preferences.get('service_type', '').lower()
            if preferred_service:
                for service_type in details['service_types']:
                    if preferred_service in service_type.lower():
                        score += 30
                        score_details['Service Match'] = 30
                        # DEMO NOTE: Show audience how exact matches get highest scores
                        break
            
            # CRITERIA 2: Medical Specialty Matching (25 points maximum)
            # DEMO HIGHLIGHT: Healthcare-specific intelligence
            preferred_specialty = user_preferences.get('specialty', '').lower()
            if preferred_specialty:
                for specialty in details['specialties']:
                    if preferred_specialty in specialty.lower():
                        score += 25
                        score_details['Specialty Match'] = 25
                        # DEMO NOTE: Shows understanding of medical domains
                        break
            
            # CRITERIA 3: Time Preference Optimization (15 points maximum)
            # DEMO HIGHLIGHT: Patient-centric scheduling
            if 'planning_horizon' in details and details['planning_horizon']:
                try:
                    start_time = parse_date(details['planning_horizon'].get('start', ''))
                    preferred_time = user_preferences.get('preferred_time', 'morning')
                    
                    # Smart time-of-day matching
                    if preferred_time == 'morning' and start_time.hour < 12:
                        score += 15
                        score_details['Time Preference'] = 15
                    elif preferred_time == 'afternoon' and 12 <= start_time.hour < 17:
                        score += 15
                        score_details['Time Preference'] = 15
                    elif preferred_time == 'evening' and start_time.hour >= 17:
                        score += 15
                        score_details['Time Preference'] = 15
                    # DEMO NOTE: Shows consideration of patient lifestyle preferences
                except:
                    pass  # Graceful handling of date parsing issues
            
            # CRITERIA 4: Availability Optimization (20 points maximum)
            # DEMO HIGHLIGHT: Urgency-aware scheduling
            try:
                if 'planning_horizon' in details and details['planning_horizon']:
                    start_time = parse_date(details['planning_horizon'].get('start', ''))
                    days_from_now = (start_time.date() - date.today()).days
                    
                    # Prioritize sooner appointments (urgent care consideration)
                    if days_from_now <= 7:
                        score += 20  # High priority for this week
                        score_details['Availability'] = 20
                    elif days_from_now <= 14:
                        score += 15  # Medium priority for next week
                        score_details['Availability'] = 15
                    elif days_from_now <= 30:
                        score += 10  # Lower priority for next month
                        score_details['Availability'] = 10
                    # DEMO NOTE: Demonstrates healthcare urgency considerations
            except:
                pass
            
            # CRITERIA 5: Active Schedule Verification (10 points maximum)
            # DEMO HIGHLIGHT: Quality assurance in healthcare
            if schedule.get('active', False):
                score += 10
                score_details['Active Schedule'] = 10
                # DEMO NOTE: Only recommends currently available providers
            
            # Store final scoring results
            details['score'] = score
            details['score_details'] = score_details
            ranked_options.append(details)
        
        # =================================================================
        # FINAL RANKING: Sort by AI-calculated scores
        # DEMO HIGHLIGHT: Best options appear first
        # =================================================================
        ranked_options.sort(key=lambda x: x['score'], reverse=True)
        
        return ranked_options
    
    def create_appointment_booking(self, schedule_id: str, patient_name: str = "Demo Patient") -> Optional[str]:
        """
        BOOK AN ACTUAL APPOINTMENT - Create FHIR Appointment Resource
        
        DEMO SHOWCASE: Real appointment booking functionality
        - Creates an Appointment resource linking Patient to Schedule
        - Shows complete booking workflow
        - Demonstrates FHIR Appointment resource structure
        
        This is what happens when a patient actually books an appointment!
        """
        try:
            # Generate appointment time (next available slot)
            appointment_time = datetime.now() + timedelta(days=1)
            appointment_time = appointment_time.replace(hour=10, minute=0, second=0, microsecond=0)
            end_time = appointment_time + timedelta(hours=1)  # 1-hour appointment
            
            # DEMO HIGHLIGHT: Proper FHIR Appointment resource structure
            appointment_resource = {
                "resourceType": "Appointment",
                
                # Business identifier
                "identifier": [{
                    "use": "usual", 
                    "system": "http://demo-clinic.org/appointment-ids",
                    "value": f"APT-{int(datetime.now().timestamp())}"
                }],
                
                # Appointment status
                "status": "booked",  # Patient has booked this appointment
                
                # Service category
                "serviceCategory": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/service-category",
                        "code": "17",
                        "display": "General Practice"
                    }]
                }],
                
                # Service type  
                "serviceType": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/service-type",
                        "code": "124", 
                        "display": "General Practice"
                    }]
                }],
                
                # Medical specialty
                "specialty": [{
                    "coding": [{
                        "system": "http://snomed.info/sct",
                        "code": "419772000",
                        "display": "Family practice"
                    }]
                }],
                
                # Priority (routine appointment)
                "priority": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/appointmentstatus",
                        "code": "routine",
                        "display": "Routine"
                    }]
                },
                
                # Description
                "description": f"Appointment booked via FHIR Agentic Scheduler for {patient_name}",
                
                # DEMO FEATURE: Link to the Schedule that was selected
                "supportingInformation": [{
                    "reference": f"Schedule/{schedule_id}",
                    "display": "Selected Schedule"
                }],
                
                # Appointment timing
                "start": appointment_time.isoformat() + "Z",
                "end": end_time.isoformat() + "Z",
                
                # DEMO HIGHLIGHT: Participants in the appointment
                "participant": [
                    {
                        "actor": {
                            "display": patient_name,
                            "type": "Patient"
                        },
                        "required": "required",
                        "status": "accepted"
                    },
                    {
                        "actor": {
                            "reference": f"Schedule/{schedule_id}",
                            "display": "Healthcare Provider"
                        },
                        "required": "required", 
                        "status": "accepted"
                    }
                ],
                
                # Appointment reason
                "reasonCode": [{
                    "coding": [{
                        "system": "http://snomed.info/sct",
                        "code": "185349003",
                        "display": "Encounter for check up"
                    }]
                }],
                
                # Comments
                "comment": f"Appointment booked via AI-powered FHIR scheduler demo on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            }
            
            # DEMO SHOWCASE: Create the Appointment resource on FHIR server
            response = self.session.post(
                f"{self.base_url}/Appointment",
                data=json.dumps(appointment_resource),
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                created_appointment = response.json()
                appointment_id = created_appointment.get('id')
                logger.info(f"Successfully booked appointment with ID: {appointment_id}")
                return appointment_id
            else:
                logger.error(f"Failed to book appointment: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            return None
    
    def get_appointment_details(self, appointment_id: str) -> Optional[Dict]:
        """
        GET APPOINTMENT DETAILS - Retrieve booked appointment info
        
        DEMO FEATURE: Shows the completed booking
        """
        try:
            response = self.session.get(f"{self.base_url}/Appointment/{appointment_id}", timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to retrieve appointment: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving appointment: {e}")
            return None

# =============================================================================
# USER INTERFACE - STREAMLIT WEB APPLICATION
# =============================================================================

def create_streamlit_ui():
    """
    DEMO PRESENTATION INTERFACE
    
    DEMO SHOWCASE: Professional healthcare application UI
    
    DEMO HIGHLIGHTS FOR AUDIENCE:
    1. Clean, professional healthcare interface
    2. Real-time FHIR server connectivity testing
    3. Interactive preference settings
    4. Live appointment search and ranking
    5. Transparent AI scoring explanations
    6. Responsive design for any device
    
    DEMO FLOW:
    1. Show FHIR connection test
    2. Create demo data live
    3. Set patient preferences
    4. Search appointments
    5. Explain AI ranking results
    
    BUSINESS VALUE:
    - Reduces appointment booking time
    - Improves patient experience
    - Optimizes healthcare provider schedules
    - Demonstrates AI/ML in healthcare
    """
    
    # =================================================================
    # PAGE CONFIGURATION - Professional Healthcare App Setup
    # =================================================================
    st.set_page_config(
        page_title="FHIR Agentic Scheduler",
        page_icon="🏥",
        layout="wide",                    # Use full screen width
        initial_sidebar_state="expanded"  # Show preferences panel immediately
    )
    
    # =================================================================
    # DEMO HEADER - Main Application Title and Description
    # =================================================================
    st.title("FHIR Agentic Scheduler")
    st.markdown("""
    **DEMO: Intelligent appointment scheduling powered by FHIR and AI**
    
    This application demonstrates enterprise-grade healthcare interoperability by connecting to 
    real FHIR servers and using AI to find and rank optimal appointment options based on patient preferences.
    
    **LIVE DEMO:** Real HAPI FHIR server • AI-powered ranking • Interactive user interface
    """)
    
    # =================================================================
    # DEMO FEATURE: Initialize the AI Scheduler Engine
    # =================================================================
    if 'scheduler' not in st.session_state:
        st.session_state.scheduler = FHIRSchedulerAgent()
        # DEMO NOTE: This creates our FHIR connection and AI engine
    
    scheduler = st.session_state.scheduler
    
    # =================================================================
    # PATIENT PREFERENCES PANEL - Left Sidebar
    # DEMO HIGHLIGHT: User-centric design
    # =================================================================
    st.sidebar.header("Patient Appointment Preferences")
    st.sidebar.markdown("*Set your preferences to get personalized recommendations*")
    
    user_preferences = {}
    
    # DEMO FEATURE: Healthcare service type selection
    user_preferences['service_type'] = st.sidebar.selectbox(
        "Preferred Service Type",
        ["", "General Practice", "Genetic Counselling", "Mental Health", "Surgery", "Emergency"],
        help="Choose the type of medical service you need"
    )
    
    # DEMO FEATURE: Medical specialty selection
    user_preferences['specialty'] = st.sidebar.selectbox(
        "Preferred Medical Specialty",
        ["", "Family practice", "Clinical genetics", "Psychotherapy", "Surgery-Neurosurgery"],
        help="Select the medical specialty you prefer"
    )
    
    # DEMO FEATURE: Time preference optimization
    user_preferences['preferred_time'] = st.sidebar.selectbox(
        "Preferred Time of Day",
        ["morning", "afternoon", "evening"],
        help="When do you prefer your appointments?"
    )
    
    # DEMO FEATURE: Results customization
    user_preferences['max_results'] = st.sidebar.slider(
        "Maximum Results to Show",
        min_value=5,
        max_value=50,
        value=10,
        help="How many appointment options should we display?"
    )
    
    # =================================================================
    # MAIN INTERFACE LAYOUT - Two-Column Design
    # =================================================================
    col1, col2 = st.columns([2, 1])  # 2/3 for results, 1/3 for controls
    
    # =================================================================
    # DEMO CONTROL PANEL - Right Column
    # DEMO HIGHLIGHT: Live FHIR server interaction
    # =================================================================
    with col2:
        st.subheader("Live FHIR Server Demo")
        st.markdown("*Interact with real healthcare systems*")
        
        # DEMO CENTERPIECE: Live FHIR connectivity test
        if st.button("Test FHIR Connection", 
                    help="DEMO: Verify live connection to HAPI FHIR server"):
            with st.spinner("Testing connection to HAPI FHIR server..."):
                # DEMO HIGHLIGHT: Real-time server communication
                is_connected = scheduler.test_connection()
                if is_connected:
                    st.success("Successfully connected to HAPI FHIR server!")
                    st.info("Server: https://hapi.fhir.org/baseR4")
                    st.balloons()  # Celebration for successful demo
                else:
                    st.error("Failed to connect to FHIR server")
                    st.warning("Please check internet connection")
        
        # DEMO FEATURE: Live data creation
        if st.button("Create Demo Schedule", 
                    help="DEMO: Create live appointment data on FHIR server"):
            with st.spinner("Creating demo schedule on FHIR server..."):
                # DEMO HIGHLIGHT: Real FHIR resource creation
                demo_practitioner = st.text_input("Demo Practitioner Name", 
                                                "Dr. Demo Presenter", 
                                                key="demo_name")
                schedule_id = scheduler.create_sample_schedule(demo_practitioner)
                if schedule_id:
                    st.success(f"Created live demo schedule!")
                    st.info(f"FHIR Schedule ID: {schedule_id}")
                    st.session_state.refresh_data = True
                    st.balloons()  # Celebrate successful data creation
                else:
                    st.error("Failed to create demo schedule")
        
        # DEMO INFORMATION PANEL
        st.markdown("---")
        st.markdown("### Demo Operations Explained")
        st.markdown("""
        **Create Demo Schedule:**
        - Creates **provider availability** 
        - Adds new Schedule resource to FHIR server
        - Like: "Dr. Smith is available Mon-Fri 9-5"
        
        **Find Appointments:**
        - Searches **existing schedules**
        - Reads Schedule resources from FHIR server  
        - Like: "Show me all available doctors"
        
        **Book Appointment:**
        - Creates **patient booking**
        - Adds Appointment resource to FHIR server
        - Like: "John Doe books with Dr. Smith at 2pm"
        """)
        
        st.markdown("---")
        st.markdown("### AI Scoring System")
        st.markdown("""
        **How our AI ranks appointments:**
        - Service Match: 30 pts
        - Specialty Match: 25 pts  
        - Availability: 20 pts
        - Time Preference: 15 pts
        - Active Status: 10 pts
        
        **Total: 100 points maximum**
        """)
    
    # =================================================================
    # APPOINTMENT RESULTS PANEL - Left Column
    # DEMO SHOWCASE: AI-powered appointment discovery
    # =================================================================
    with col1:
        st.subheader("AI-Powered Appointment Discovery")
        st.markdown("*Live search results from HAPI FHIR server with intelligent ranking*")
        
        # DEMO CENTERPIECE: Live appointment search
        if st.button("Find Appointment Options", 
                    help="DEMO: Search FHIR server and rank with AI") or st.session_state.get('refresh_data', False):
            
            with st.spinner("Searching HAPI FHIR server for appointments..."):
                # Reset refresh flag
                st.session_state.refresh_data = False
                
                # DEMO HIGHLIGHT: Real FHIR server query
                # Note: Set active_only=False to see all schedules (including inactive)
                schedules = scheduler.search_schedules(active_only=True)  # Change to False to see all
                
                if schedules:
                    # DEMO CENTERPIECE: AI ranking in action
                    with st.spinner("AI is ranking appointment options..."):
                        ranked_options = scheduler.rank_appointment_options(schedules, user_preferences)
                    
                    # DEMO RESULTS: Show successful discovery
                    st.success(f"Found {len(ranked_options)} appointment options!")
                    
                    # Show filtering information
                    if user_preferences['service_type'] or user_preferences['specialty']:
                        st.info(f"Personalized for: {user_preferences['service_type']} {user_preferences['specialty']}".strip())
                    
                    # DEMO SHOWCASE: Display ranked results
                    max_results = user_preferences['max_results']
                    top_options = ranked_options[:max_results]
                    
                    # DEMO HIGHLIGHT: Show each ranked option
                    for i, option in enumerate(top_options, 1):
                        # DEMO FEATURE: Visual score indication
                        if option['score'] >= 60:
                            score_color = "HIGH"  # High score indicator
                        elif option['score'] >= 30:
                            score_color = "MED"   # Medium score indicator
                        else:
                            score_color = "LOW"   # Low score indicator
                        
                        # DEMO PRESENTATION: Expandable result cards
                        with st.expander(f"[{score_color}] #{i} {option['name']} (AI Score: {option['score']}/100)", 
                                       expanded=(i <= 3)):  # Auto-expand top 3 for demo
                            
                            # DEMO LAYOUT: Professional information display
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                st.write("**Schedule ID:**", option['schedule_id'])
                                st.write("**Healthcare Providers:**", ", ".join(option['actors']) or "Not specified")
                                st.write("**Service Types:**", ", ".join(option['service_types']) or "General")
                                
                            with col_b:
                                st.write("**Medical Specialties:**", ", ".join(option['specialties']) or "General")
                                if option['planning_horizon']:
                                    start = option['planning_horizon'].get('start', 'N/A')
                                    end = option['planning_horizon'].get('end', 'N/A')
                                    st.write("**Available Period:**")
                                    st.write(f"From: {start}")
                                    st.write(f"To: {end}")
                            
                            # Show additional notes
                            if option['comment']:
                                st.write("**Schedule Notes:**", option['comment'])
                            
                            # DEMO CENTERPIECE: Explainable AI scoring
                            if option['score_details']:
                                st.write("**AI Scoring Breakdown (Explainable AI):**")
                                
                                if PANDAS_AVAILABLE:
                                    # DEMO FEATURE: Professional data table
                                    score_df = pd.DataFrame([
                                        {"Scoring Criteria": k, "Points Awarded": v} 
                                        for k, v in option['score_details'].items()
                                    ])
                                    st.dataframe(score_df, use_container_width=True, hide_index=True)
                                else:
                                    # Fallback display without pandas
                                    for criteria, points in option['score_details'].items():
                                        st.write(f"  • **{criteria}**: +{points} points")
                            
                            # DEMO CENTERPIECE: ACTUAL APPOINTMENT BOOKING
                            col_book1, col_book2 = st.columns(2)
                            
                            with col_book1:
                                if st.button(f"Book This Appointment", 
                                           key=f"book_{option['schedule_id']}", 
                                           help="DEMO: Actually book this appointment in FHIR"):
                                    
                                    # Get patient name for booking
                                    patient_name = st.text_input(
                                        "Patient Name for Booking", 
                                        "Demo Patient",
                                        key=f"patient_{option['schedule_id']}"
                                    )
                                    
                                    # DEMO HIGHLIGHT: Real appointment booking
                                    with st.spinner("Booking appointment in FHIR server..."):
                                        appointment_id = scheduler.create_appointment_booking(
                                            option['schedule_id'], 
                                            patient_name
                                        )
                                        
                                        if appointment_id:
                                            st.success(f"**APPOINTMENT BOOKED SUCCESSFULLY!**")
                                            st.info(f"**FHIR Appointment ID:** {appointment_id}")
                                            st.info(f"**Patient:** {patient_name}")
                                            st.info(f"**Provider:** {', '.join(option['actors'])}")
                                            st.info(f"**Scheduled:** Tomorrow at 10:00 AM")
                                            
                                            # Show booking confirmation
                                            st.markdown("""
                                            **DEMO SUCCESS!** 
                                            
                                            This created a real **Appointment resource** in the FHIR server that:
                                            - Links the patient to the selected schedule
                                            - Sets appointment status to 'booked'
                                            - Includes all required FHIR appointment fields
                                            - Can be retrieved by other FHIR systems
                                            """)
                                            
                                            st.balloons()  # Celebrate successful booking!
                                            
                                            # Store booking in session state for demo
                                            if 'booked_appointments' not in st.session_state:
                                                st.session_state.booked_appointments = []
                                            st.session_state.booked_appointments.append({
                                                'appointment_id': appointment_id,
                                                'patient_name': patient_name,
                                                'provider': ', '.join(option['actors']),
                                                'schedule_id': option['schedule_id'],
                                                'booking_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                            })
                                            
                                        else:
                                            st.error("Failed to book appointment")
                                            st.warning("This might be due to server limitations or network issues")
                            
                            with col_book2:
                                # DEMO FEATURE: View appointment details
                                if st.button(f"View Details", 
                                           key=f"details_{option['schedule_id']}", 
                                           help="View full schedule details"):
                                    st.json(option)  # Show raw data for technical demo
                
                else:
                    # DEMO GUIDANCE: Help with empty results
                    st.warning("No schedules found in the FHIR server.")
                    st.info("**Demo Tip:** Try creating a demo schedule first using the button in the control panel!")
                    
                    # Show helpful demo workflow
                    st.markdown("""
                    **Demo Workflow:**
                    1. **Create Demo Schedule** → Adds provider availability to FHIR server
                    2. **Find Appointment Options** → Searches and ranks available appointments  
                    3. **Book Appointment** → Creates actual patient booking
                    
                    This demonstrates the complete healthcare appointment lifecycle!
                    """)
    
        # DEMO FEATURE: Show booking history if any appointments have been booked
        if 'booked_appointments' in st.session_state and st.session_state.booked_appointments:
            st.markdown("---")
            st.subheader("Recent Appointment Bookings (Demo Session)")
            
            booking_data = []
            for booking in st.session_state.booked_appointments:
                booking_data.append({
                    "Appointment ID": booking['appointment_id'],
                    "Patient": booking['patient_name'], 
                    "Provider": booking['provider'],
                    "Booked At": booking['booking_time']
                })
            
            if PANDAS_AVAILABLE:
                booking_df = pd.DataFrame(booking_data)
                st.dataframe(booking_df, use_container_width=True, hide_index=True)
            else:
                for i, booking in enumerate(booking_data, 1):
                    with st.expander(f"Booking #{i}: {booking['Patient']}"):
                        for key, value in booking.items():
                            st.write(f"**{key}:** {value}")
            
            st.info("**Demo Note:** These are real Appointment resources created in the HAPI FHIR server during this demo session!")
        
        st.markdown("---")
    
# =============================================================================
# DEMO APPLICATION ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Launch the FHIR Agentic Scheduler Demo
    create_streamlit_ui()
