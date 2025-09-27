import requests
import json
from typing import Dict, Any
from datetime import datetime, timedelta

# Simple in-memory storage for appointments and medical records
APPOINTMENTS_DB = {"appointments": {}, "next_id": 1}
PATIENTS_DB = {"patients": {}, "next_id": 1}

# Medical conditions database
MEDICAL_CONDITIONS = {
    "headache": {
        "name": "Headache",
        "symptoms": ["head pain", "sensitivity to light", "nausea"],
        "common_causes": ["tension", "dehydration", "stress", "lack of sleep"],
        "recommendations": ["rest", "hydration", "pain relief", "stress management"],
        "severity": "mild to moderate"
    },
    "fever": {
        "name": "Fever",
        "symptoms": ["elevated temperature", "chills", "sweating", "fatigue"],
        "common_causes": ["infection", "inflammation", "heat exhaustion"],
        "recommendations": ["rest", "fluids", "monitor temperature", "seek medical care if persistent"],
        "severity": "mild to serious"
    },
    "cough": {
        "name": "Cough",
        "symptoms": ["persistent coughing", "throat irritation", "mucus production"],
        "common_causes": ["cold", "flu", "allergies", "respiratory infection"],
        "recommendations": ["rest", "warm liquids", "honey", "avoid irritants"],
        "severity": "mild to moderate"
    },
    "chest_pain": {
        "name": "Chest Pain",
        "symptoms": ["chest discomfort", "pressure", "tightness"],
        "common_causes": ["muscle strain", "acid reflux", "anxiety", "heart conditions"],
        "recommendations": ["immediate medical attention if severe", "rest", "monitor symptoms"],
        "severity": "mild to emergency"
    },
    "stomach_pain": {
        "name": "Stomach Pain",
        "symptoms": ["abdominal discomfort", "cramping", "bloating"],
        "common_causes": ["indigestion", "gas", "food poisoning", "stress"],
        "recommendations": ["rest", "bland diet", "hydration", "monitor symptoms"],
        "severity": "mild to moderate"
    },
    "anxiety": {
        "name": "Anxiety",
        "symptoms": ["worry", "restlessness", "rapid heartbeat", "difficulty concentrating"],
        "common_causes": ["stress", "life changes", "medical conditions", "genetics"],
        "recommendations": ["relaxation techniques", "exercise", "counseling", "stress management"],
        "severity": "mild to severe"
    }
}

# Medications database
MEDICATIONS = {
    "acetaminophen": {
        "name": "Acetaminophen",
        "uses": ["pain relief", "fever reduction"],
        "dosage": "500-1000mg every 4-6 hours",
        "warnings": ["do not exceed 4000mg daily", "avoid alcohol"],
        "side_effects": ["rare when used as directed"]
    },
    "ibuprofen": {
        "name": "Ibuprofen", 
        "uses": ["pain relief", "inflammation", "fever reduction"],
        "dosage": "200-400mg every 4-6 hours",
        "warnings": ["take with food", "avoid if allergic to NSAIDs"],
        "side_effects": ["stomach upset", "drowsiness"]
    },
    "aspirin": {
        "name": "Aspirin",
        "uses": ["pain relief", "inflammation", "heart protection"],
        "dosage": "81-325mg daily for heart protection",
        "warnings": ["avoid in children", "bleeding risk"],
        "side_effects": ["stomach irritation", "bleeding"]
    }
}

def assess_symptoms(symptoms: str) -> Dict[str, Any]:
    """Assess symptoms and provide medical guidance"""
    symptoms_lower = symptoms.lower()
    possible_conditions = []
    
    # Check for matching conditions
    for condition_key, condition_data in MEDICAL_CONDITIONS.items():
        condition_symptoms = [s.lower() for s in condition_data["symptoms"]]
        condition_causes = [c.lower() for c in condition_data["common_causes"]]
        
        # Check if any symptoms match
        if any(symptom in symptoms_lower for symptom in condition_symptoms):
            possible_conditions.append({
                "condition": condition_data["name"],
                "symptoms": condition_data["symptoms"],
                "causes": condition_data["common_causes"],
                "recommendations": condition_data["recommendations"],
                "severity": condition_data["severity"]
            })
    
    if possible_conditions:
        return {
            "patient_symptoms": symptoms,
            "possible_conditions": possible_conditions,
            "general_advice": "This is general information only. Please consult a healthcare professional for proper diagnosis and treatment.",
            "emergency_note": "Seek immediate medical attention if symptoms are severe or worsening."
        }
    
    return {
        "patient_symptoms": symptoms,
        "message": "Unable to match symptoms to common conditions. Please consult a healthcare professional.",
        "advice": "It's always best to speak with a medical professional about any health concerns."
    }

def get_medication_info(medication_name: str) -> Dict[str, Any]:
    """Get information about medications"""
    medication = MEDICATIONS.get(medication_name.lower())
    
    if medication:
        return {
            "medication": medication["name"],
            "uses": medication["uses"],
            "dosage": medication["dosage"],
            "warnings": medication["warnings"],
            "side_effects": medication["side_effects"],
            "note": "This information is for educational purposes only. Always consult a healthcare provider before taking any medication."
        }
    
    return {
        "error": f"Medication '{medication_name}' not found in database",
        "advice": "Please consult a pharmacist or healthcare provider for medication information."
    }

def schedule_appointment(patient_name: str, reason: str, preferred_date: str = None) -> Dict[str, Any]:
    """Schedule a medical appointment"""
    appointment_id = APPOINTMENTS_DB["next_id"]
    APPOINTMENTS_DB["next_id"] += 1
    
    # Default to tomorrow if no date specified
    if not preferred_date:
        appointment_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d 10:00 AM")
    else:
        appointment_date = preferred_date
    
    appointment = {
        "id": appointment_id,
        "patient_name": patient_name,
        "reason": reason,
        "date": appointment_date,
        "status": "scheduled",
        "type": "consultation"
    }
    
    APPOINTMENTS_DB["appointments"][appointment_id] = appointment
    
    return {
        "appointment_id": appointment_id,
        "message": f"Appointment scheduled for {patient_name}",
        "date": appointment_date,
        "reason": reason,
        "status": "scheduled",
        "note": "Please arrive 15 minutes early for check-in."
    }

def check_appointment(appointment_id: str) -> Dict[str, Any]:
    """Check appointment status"""
    try:
        appt_id = int(appointment_id)
        appointment = APPOINTMENTS_DB["appointments"].get(appt_id)
        
        if appointment:
            return {
                "appointment_id": appt_id,
                "patient_name": appointment["patient_name"],
                "reason": appointment["reason"],
                "date": appointment["date"],
                "status": appointment["status"],
                "type": appointment["type"]
            }
    except ValueError:
        pass
    
    return {"error": f"Appointment {appointment_id} not found"}

def get_health_tips(category: str = "general") -> Dict[str, Any]:
    """Provide health tips and wellness advice"""
    tips_database = {
        "general": [
            "Stay hydrated by drinking 8 glasses of water daily",
            "Get 7-9 hours of sleep each night",
            "Exercise for at least 30 minutes, 5 days a week",
            "Eat a balanced diet with fruits and vegetables",
            "Practice stress management techniques"
        ],
        "nutrition": [
            "Include colorful fruits and vegetables in every meal",
            "Choose whole grains over refined grains",
            "Limit processed foods and added sugars",
            "Include lean proteins like fish, chicken, and legumes",
            "Practice portion control"
        ],
        "exercise": [
            "Start with 10-15 minutes of daily activity if you're new to exercise",
            "Include both cardio and strength training",
            "Take breaks from sitting every hour",
            "Try activities you enjoy to stay motivated",
            "Warm up before and cool down after exercise"
        ],
        "mental_health": [
            "Practice mindfulness or meditation daily",
            "Maintain social connections",
            "Set realistic goals and celebrate achievements",
            "Take breaks from technology and social media",
            "Seek professional help when needed"
        ]
    }
    
    category_tips = tips_database.get(category.lower(), tips_database["general"])
    
    return {
        "category": category,
        "tips": category_tips,
        "note": "These are general wellness suggestions. Consult healthcare providers for personalized advice."
    }

def emergency_guidance(emergency_type: str) -> Dict[str, Any]:
    """Provide emergency guidance and when to seek immediate care"""
    emergency_situations = {
        "chest_pain": {
            "immediate_actions": ["Call 911 immediately", "Sit down and rest", "Chew aspirin if not allergic"],
            "warning": "Chest pain can be a sign of heart attack - seek immediate medical attention"
        },
        "difficulty_breathing": {
            "immediate_actions": ["Call 911", "Sit upright", "Loosen tight clothing", "Use prescribed inhaler if available"],
            "warning": "Difficulty breathing requires immediate medical attention"
        },
        "severe_bleeding": {
            "immediate_actions": ["Apply direct pressure to wound", "Elevate injured area above heart", "Call 911"],
            "warning": "Severe bleeding can be life-threatening"
        },
        "poisoning": {
            "immediate_actions": ["Call Poison Control: 1-800-222-1222", "Do not induce vomiting unless instructed"],
            "warning": "Call poison control immediately for any suspected poisoning"
        },
        "allergic_reaction": {
            "immediate_actions": ["Use EpiPen if available", "Call 911", "Monitor breathing"],
            "warning": "Severe allergic reactions can be life-threatening"
        }
    }
    
    situation = emergency_situations.get(emergency_type.lower())
    
    if situation:
        return {
            "emergency_type": emergency_type,
            "immediate_actions": situation["immediate_actions"],
            "warning": situation["warning"],
            "emergency_number": "911",
            "poison_control": "1-800-222-1222"
        }
    
    return {
        "emergency_type": emergency_type,
        "general_guidance": "Call 911 for any life-threatening emergency",
        "message": "When in doubt, seek immediate medical attention"
    }

# Function mapping dictionary
FUNCTION_MAP = {
    'assess_symptoms': assess_symptoms,
    'get_medication_info': get_medication_info,
    'schedule_appointment': schedule_appointment,
    'check_appointment': check_appointment,
    'get_health_tips': get_health_tips,
    'emergency_guidance': emergency_guidance
}