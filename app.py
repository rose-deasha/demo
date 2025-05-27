#!/usr/bin/env python3
"""
FHIR Agentic Scheduler - Client Production Version

An intelligent appointment scheduling system that connects to FHIR servers
to find, rank, and book optimal appointment options based on patient preferences.

Dependencies:
streamlit>=1.28.0
requests>=2.31.0
pandas>=2.0.0
python-dateutil>=2.8.0
"""

import streamlit as st
import requests
import json
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
import logging

# Graceful dependency handling
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    st.warning("Pandas not available. Some features may be limited.")

try:
    from dateutil.parser import parse as parse_date
except ImportError:
    def parse_date(date_string):
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FHIRSchedulerAgent:
    """
    FHIR Agentic Scheduler - Core AI Engine
    
    Provides intelligent appointment scheduling with real FHIR server connectivity,
    AI-powered ranking, and transparent scoring explanations.
    """
    
    def __init__(self, base_url: str = "https://hapi.fhir.org/baseR4"):
        """Initialize FHIR connection with proper headers."""
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/fhir+json',
            'Content-Type': 'application/fhir+json'
        })
        
    def test_connection(self) -> bool:
        """Test connection to the FHIR server."""
        try:
            response = self.session.get(f"{self.base_url}/metadata", timeout=10)
            return response.status_code == 200
        except requests.RequestException as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def search_schedules(self, active_only: bool = True) -> List[Dict]:
        """Search for available schedules in the FHIR server."""
        try:
            params = {'_count': 50}
            if active_only:
                params['active'] = 'true'
                
            response = self.session.get(f"{self.base_url}/Schedule", params=params, timeout=15)
            
            if response.status_code == 200:
                bundle = response.json()
                schedules = []
                
                if 'entry' in bundle:
                    for entry in bundle['entry']:
                        schedules.append(entry['resource'])
                        
                logger.info(f"Found {len(schedules)} schedules")
                return schedules
            else:
                logger.error(f"Failed to fetch schedules: {response.status_code}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"Error searching schedules: {e}")
            return []
    
    def create_sample_schedule(self, practitioner_name: str = "Dr. Sample Provider") -> Optional[str]:
        """Create a sample schedule for testing purposes."""
        try:
            start_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=7)
            
            schedule_resource = {
                "resourceType": "Schedule",
                "identifier": [{
                    "use": "usual",
                    "system": "http://scheduler-app.org/schedule-ids",
                    "value": f"SCH-{int(datetime.now().timestamp())}"
                }],
                "active": True,
                "serviceCategory": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/service-category",
                        "code": "17",
                        "display": "General Practice"
                    }]
                }],
                "serviceType": [{
                    "concept": {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/service-type",
                            "code": "124",
                            "display": "General Practice"
                        }]
                    }
                }],
                "specialty": [{
                    "coding": [{
                        "system": "http://snomed.info/sct",
                        "code": "419772000",
                        "display": "Family practice"
                    }]
                }],
                "name": f"{practitioner_name} - Schedule",
                "actor": [{
                    "display": practitioner_name
                }],
                "planningHorizon": {
                    "start": start_time.isoformat() + "Z",
                    "end": end_time.isoformat() + "Z"
                },
                "comment": "Schedule created by FHIR Agentic Scheduler"
            }
            
            response = self.session.post(
                f"{self.base_url}/Schedule",
                data=json.dumps(schedule_resource),
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                created_resource = response.json()
                schedule_id = created_resource.get('id')
                logger.info(f"Created schedule with ID: {schedule_id}")
                return schedule_id
            else:
                logger.error(f"Failed to create schedule: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating schedule: {e}")
            return None
    
    def rank_appointment_options(self, schedules: List[Dict], 
                               user_preferences: Dict) -> List[Dict]:
        """
        AI-powered appointment ranking using intelligent scoring algorithm.
        
        Evaluates appointments across multiple criteria:
        - Service type matching (30 points)
        - Medical specialty alignment (25 points)
        - Time preference optimization (15 points)
        - Availability scoring (20 points)
        - Active status verification (10 points)
        """
        ranked_options = []
        
        for schedule in schedules:
            score = 0
            details = {
                'schedule_id': schedule.get('id', 'Unknown'),
                'name': schedule.get('name', 'Unknown Schedule'),
                'comment': schedule.get('comment', ''),
                'actors': [],
                'service_types': [],
                'specialties': [],
                'planning_horizon': {},
                'score': 0,
                'score_details': {}
            }
            
            # Extract healthcare data from FHIR structure
            if 'actor' in schedule:
                details['actors'] = [actor.get('display', 'Unknown') for actor in schedule['actor']]
            
            if 'serviceType' in schedule:
                details['service_types'] = [
                    st.get('concept', {}).get('coding', [{}])[0].get('display', 'Unknown')
                    for st in schedule['serviceType']
                ]
            
            if 'specialty' in schedule:
                details['specialties'] = [
                    spec.get('coding', [{}])[0].get('display', 'Unknown')
                    for spec in schedule['specialty']
                ]
            
            if 'planningHorizon' in schedule:
                details['planning_horizon'] = schedule['planningHorizon']
            
            # AI Scoring Algorithm
            score_details = {}
            
            # Service type matching (30 points)
            preferred_service = user_preferences.get('service_type', '').lower()
            if preferred_service:
                for service_type in details['service_types']:
                    if preferred_service in service_type.lower():
                        score += 30
                        score_details['Service Match'] = 30
                        break
            
            # Specialty matching (25 points)
            preferred_specialty = user_preferences.get('specialty', '').lower()
            if preferred_specialty:
                for specialty in details['specialties']:
                    if preferred_specialty in specialty.lower():
                        score += 25
                        score_details['Specialty Match'] = 25
                        break
            
            # Time preference scoring (15 points)
            if 'planning_horizon' in details and details['planning_horizon']:
                try:
                    start_time = parse_date(details['planning_horizon'].get('start', ''))
                    preferred_time = user_preferences.get('preferred_time', 'morning')
                    
                    if preferred_time == 'morning' and start_time.hour < 12:
                        score += 15
                        score_details['Time Preference'] = 15
                    elif preferred_time == 'afternoon' and 12 <= start_time.hour < 17:
                        score += 15
                        score_details['Time Preference'] = 15
                    elif preferred_time == 'evening' and start_time.hour >= 17:
                        score += 15
                        score_details['Time Preference'] = 15
                except:
                    pass
            
            # Availability scoring (20 points)
            try:
                if 'planning_horizon' in details and details['planning_horizon']:
                    start_time = parse_date(details['planning_horizon'].get('start', ''))
                    days_from_now = (start_time.date() - date.today()).days
                    
                    if days_from_now <= 7:
                        score += 20
                        score_details['Availability'] = 20
                    elif days_from_now <= 14:
                        score += 15
                        score_details['Availability'] = 15
                    elif days_from_now <= 30:
                        score += 10
                        score_details['Availability'] = 10
            except:
                pass
            
            # Active status verification (10 points)
            if schedule.get('active', False):
                score += 10
                score_details['Active Schedule'] = 10
            
            details['score'] = score
            details['score_details'] = score_details
            ranked_options.append(details)
        
        # Sort by AI-calculated scores (highest first)
        ranked_options.sort(key=lambda x: x['score'], reverse=True)
        return ranked_options
    
    def create_appointment_booking(self, schedule_id: str, patient_name: str = "Patient") -> Optional[str]:
        """Create an actual appointment booking in the FHIR server."""
        try:
            appointment_time = datetime.now() + timedelta(days=1)
            appointment_time = appointment_time.replace(hour=10, minute=0, second=0, microsecond=0)
            end_time = appointment_time + timedelta(hours=1)
            
            appointment_resource = {
                "resourceType": "Appointment",
                "identifier": [{
                    "use": "usual", 
                    "system": "http://scheduler-app.org/appointment-ids",
                    "value": f"APT-{int(datetime.now().timestamp())}"
                }],
                "status": "booked",
                "serviceCategory": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/service-category",
                        "code": "17",
                        "display": "General Practice"
                    }]
                }],
                "serviceType": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/service-type",
                        "code": "124", 
                        "display": "General Practice"
                    }]
                }],
                "specialty": [{
                    "coding": [{
                        "system": "http://snomed.info/sct",
                        "code": "419772000",
                        "display": "Family practice"
                    }]
                }],
                "priority": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/appointmentstatus",
                        "code": "routine",
                        "display": "Routine"
                    }]
                },
                "description": f"Appointment for {patient_name}",
                "supportingInformation": [{
                    "reference": f"Schedule/{schedule_id}",
                    "display": "Selected Schedule"
                }],
                "start": appointment_time.isoformat() + "Z",
                "end": end_time.isoformat() + "Z",
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
                "reasonCode": [{
                    "coding": [{
                        "system": "http://snomed.info/sct",
                        "code": "185349003",
                        "display": "Encounter for check up"
                    }]
                }],
                "comment": f"Appointment booked via FHIR Scheduler on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            }
            
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

def create_streamlit_ui():
    """Create the main application interface."""
    
    st.set_page_config(
        page_title="FHIR Agentic Scheduler",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("FHIR Agentic Scheduler")
    st.markdown("""
    **Intelligent appointment scheduling powered by FHIR and AI**
    
    Find and book optimal appointment options based on your preferences using real-time 
    healthcare data and AI-powered ranking.
    """)
    
    # Initialize the scheduler
    if 'scheduler' not in st.session_state:
        st.session_state.scheduler = FHIRSchedulerAgent()
    
    scheduler = st.session_state.scheduler
    
    # Sidebar for preferences
    st.sidebar.header("Appointment Preferences")
    
    user_preferences = {}
    
    user_preferences['service_type'] = st.sidebar.selectbox(
        "Service Type",
        ["", "General Practice", "Genetic Counselling", "Mental Health", "Surgery", "Emergency"],
        help="Choose the type of medical service you need"
    )
    
    user_preferences['specialty'] = st.sidebar.selectbox(
        "Medical Specialty",
        ["", "Family practice", "Clinical genetics", "Psychotherapy", "Surgery-Neurosurgery"],
        help="Select your preferred medical specialty"
    )
    
    user_preferences['preferred_time'] = st.sidebar.selectbox(
        "Preferred Time",
        ["morning", "afternoon", "evening"],
        help="When do you prefer your appointments?"
    )
    
    user_preferences['max_results'] = st.sidebar.slider(
        "Maximum Results",
        min_value=5,
        max_value=50,
        value=10,
        help="How many appointment options to display"
    )
    
    # Main layout
    col1, col2 = st.columns([2, 1])
    
    # Control panel
    with col2:
        st.subheader("System Controls")
        
        # Connection test
        if st.button("Test FHIR Connection", help="Verify connection to FHIR server"):
            with st.spinner("Testing connection..."):
                is_connected = scheduler.test_connection()
                if is_connected:
                    st.success("Successfully connected to FHIR server!")
                    st.info("Server: https://hapi.fhir.org/baseR4")
                else:
                    st.error("Failed to connect to FHIR server")
                    st.warning("Please check your internet connection")
        
        # Create sample data
        if st.button("Add Sample Provider", help="Add sample provider data for testing"):
            with st.spinner("Creating provider schedule..."):
                provider_name = st.text_input("Provider Name", "Dr. Sample Provider", key="provider_name")
                schedule_id = scheduler.create_sample_schedule(provider_name)
                if schedule_id:
                    st.success("Successfully added provider!")
                    st.info(f"Schedule ID: {schedule_id}")
                    st.session_state.refresh_data = True
                else:
                    st.error("Failed to add provider")
        
        st.markdown("---")
      
    # Results panel
    with col1:
        st.subheader("Available Appointments")
        
        if st.button("Search Appointments", help="Search for available appointments") or st.session_state.get('refresh_data', False):
            
            with st.spinner("Searching for appointments..."):
                st.session_state.refresh_data = False
                
                schedules = scheduler.search_schedules(active_only=True)
                
                if schedules:
                    with st.spinner("Ranking appointments with AI..."):
                        ranked_options = scheduler.rank_appointment_options(schedules, user_preferences)
                    
                    st.success(f"Found {len(ranked_options)} appointment options")
                    
                    if user_preferences['service_type'] or user_preferences['specialty']:
                        st.info(f"Filtered for: {user_preferences['service_type']} {user_preferences['specialty']}".strip())
                    
                    max_results = user_preferences['max_results']
                    top_options = ranked_options[:max_results]
                    
                    for i, option in enumerate(top_options, 1):
                        # Score indicator
                        if option['score'] >= 60:
                            score_indicator = "⭐ HIGH"
                        elif option['score'] >= 30:
                            score_indicator = "⚡ MEDIUM"
                        else:
                            score_indicator = "📋 LOW"
                        
                        with st.expander(f"{score_indicator} | {option['name']} (Score: {option['score']}/100)", 
                                       expanded=(i <= 3)):
                            
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                st.write("**Schedule ID:**", option['schedule_id'])
                                st.write("**Providers:**", ", ".join(option['actors']) or "Not specified")
                                st.write("**Services:**", ", ".join(option['service_types']) or "General")
                                
                            with col_b:
                                st.write("**Specialties:**", ", ".join(option['specialties']) or "General")
                                if option['planning_horizon']:
                                    start = option['planning_horizon'].get('start', 'N/A')
                                    end = option['planning_horizon'].get('end', 'N/A')
                                    st.write("**Available Period:**")
                                    st.write(f"From: {start}")
                                    st.write(f"To: {end}")
                            
                            if option['comment']:
                                st.write("**Notes:**", option['comment'])
                            
                            # AI scoring breakdown
                            if option['score_details']:
                                st.write("**AI Score Breakdown:**")
                                
                                if PANDAS_AVAILABLE:
                                    score_df = pd.DataFrame([
                                        {"Criteria": k, "Points": v} 
                                        for k, v in option['score_details'].items()
                                    ])
                                    st.dataframe(score_df, use_container_width=True, hide_index=True)
                                else:
                                    for criteria, points in option['score_details'].items():
                                        st.write(f"• **{criteria}**: +{points} points")
                            
                            # Booking interface
                            col_book1, col_book2 = st.columns(2)
                            
                            with col_book1:
                                if st.button(f"Book Appointment", 
                                           key=f"book_{option['schedule_id']}", 
                                           help="Book this appointment"):
                                    
                                    patient_name = st.text_input(
                                        "Patient Name", 
                                        "Patient Name",
                                        key=f"patient_{option['schedule_id']}"
                                    )
                                    
                                    with st.spinner("Booking appointment..."):
                                        appointment_id = scheduler.create_appointment_booking(
                                            option['schedule_id'], 
                                            patient_name
                                        )
                                        
                                        if appointment_id:
                                            st.success("**Appointment Booked Successfully!**")
                                            st.info(f"**Appointment ID:** {appointment_id}")
                                            st.info(f"**Patient:** {patient_name}")
                                            st.info(f"**Provider:** {', '.join(option['actors'])}")
                                            st.info(f"**Scheduled:** Tomorrow at 10:00 AM")
                                            
                                            # Store booking
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
                            
                            with col_book2:
                                if st.button(f"View Details", 
                                           key=f"details_{option['schedule_id']}", 
                                           help="View technical details"):
                                    st.json(option)
                
                else:
                    st.warning("No appointments found.")
                    st.info("Try adding a sample provider first, then search again.")
    
        # Show booking history
        if 'booked_appointments' in st.session_state and st.session_state.booked_appointments:
            st.markdown("---")
            st.subheader("Recent Bookings")
            
            booking_data = []
            for booking in st.session_state.booked_appointments:
                booking_data.append({
                    "Appointment ID": booking['appointment_id'],
                    "Patient": booking['patient_name'], 
                    "Provider": booking['provider'],
                    "Booked": booking['booking_time']
                })
            
            if PANDAS_AVAILABLE:
                booking_df = pd.DataFrame(booking_data)
                st.dataframe(booking_df, use_container_width=True, hide_index=True)
            else:
                for i, booking in enumerate(booking_data, 1):
                    with st.expander(f"Booking #{i}: {booking['Patient']}"):
                        for key, value in booking.items():
                            st.write(f"**{key}:** {value}")

if __name__ == "__main__":
    create_streamlit_ui()
