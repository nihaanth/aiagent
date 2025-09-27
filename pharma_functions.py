import requests
import json
from typing import Dict, Any

# Simple in-memory storage
ORDERS_DB = {"orders": {}, "next_id": 1}
DRUG_DB = { 
    "aspirin": {"name": "Acetylsalicylic Acid", "price": 5.99,
                "description": "Non-steroidal anti-inflammatory drug for pain relief and fever reduction",
                "quantity": 30},
    "ibuprofen": {"name": "Ibuprofen", "price": 7.99,
                  "description": "Anti-inflammatory medication for pain and inflammation management", "quantity": 20},
    "acetaminophen": {"name": "Acetaminophen", "price": 6.99,
                      "description": "Analgesic and antipyretic medication for pain and fever control", "quantity": 25},
    "metformin": {"name": "Metformin Hydrochloride", "price": 12.50,
                  "description": "Biguanide antidiabetic medication for type 2 diabetes management", "quantity": 60},
    "lisinopril": {"name": "Lisinopril", "price": 8.75,
                   "description": "ACE inhibitor for hypertension and heart failure treatment", "quantity": 30},
    "atorvastatin": {"name": "Atorvastatin Calcium", "price": 15.25,
                     "description": "HMG-CoA reductase inhibitor for cholesterol management", "quantity": 30},
    "omeprazole": {"name": "Omeprazole", "price": 11.99,
                   "description": "Proton pump inhibitor for acid reflux and ulcer treatment", "quantity": 28},
    "amlodipine": {"name": "Amlodipine Besylate", "price": 9.50,
                   "description": "Calcium channel blocker for hypertension and angina", "quantity": 30},
    "metoprolol": {"name": "Metoprolol Tartrate", "price": 7.25,
                   "description": "Beta-blocker for hypertension and heart rhythm disorders", "quantity": 30},
    "sertraline": {"name": "Sertraline Hydrochloride", "price": 13.75,
                   "description": "Selective serotonin reuptake inhibitor for depression and anxiety", "quantity": 30}
}


def get_drug_info_from_fda(drug_name: str) -> Dict[str, Any]:
    """Get real drug information from OpenFDA API."""
    try:
        # OpenFDA API for drug labels
        url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:\"{drug_name}\"&limit=1"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                result = data['results'][0]
                return {
                    "brand_name": result.get('openfda', {}).get('brand_name', ['Unknown'])[0] if result.get('openfda', {}).get('brand_name') else 'Unknown',
                    "generic_name": result.get('openfda', {}).get('generic_name', ['Unknown'])[0] if result.get('openfda', {}).get('generic_name') else 'Unknown',
                    "manufacturer": result.get('openfda', {}).get('manufacturer_name', ['Unknown'])[0] if result.get('openfda', {}).get('manufacturer_name') else 'Unknown',
                    "indications": result.get('indications_and_usage', ['Not available'])[0] if result.get('indications_and_usage') else 'Not available',
                    "warnings": result.get('warnings', ['None listed'])[0][:200] + "..." if result.get('warnings') and len(result.get('warnings', [''])[0]) > 200 else result.get('warnings', ['None listed'])[0] if result.get('warnings') else 'None listed',
                    "dosage": result.get('dosage_and_administration', ['Not specified'])[0][:200] + "..." if result.get('dosage_and_administration') and len(result.get('dosage_and_administration', [''])[0]) > 200 else result.get('dosage_and_administration', ['Not specified'])[0] if result.get('dosage_and_administration') else 'Not specified'
                }
        return {"error": f"No FDA data found for '{drug_name}'"}
    except Exception as e:
        return {"error": f"FDA API error: {str(e)}"}

def get_drug_info(drug_name: str) -> Dict[str, Any]:
    """Get drug information from local DB first, then FDA API."""
    # Check local database first
    drug = DRUG_DB.get(drug_name.lower())
    if drug:
        local_info = {
            "name": drug["name"],
            "description": drug["description"],
            "price": drug["price"],
            "quantity": drug["quantity"],
            "source": "local"
        }
        
        # Try to enhance with FDA data
        fda_info = get_drug_info_from_fda(drug_name)
        if "error" not in fda_info:
            local_info.update({
                "fda_data": fda_info,
                "enhanced": True
            })
        
        return local_info
    
    # If not in local DB, try FDA API
    fda_info = get_drug_info_from_fda(drug_name)
    if "error" not in fda_info:
        return {
            "source": "fda",
            "fda_data": fda_info,
            "note": "This drug is not in our local inventory. Showing FDA information only."
        }
    
    return {"error": f"Drug '{drug_name}' not found in local inventory or FDA database"}


def place_order(customer_name, drug_name):
    """Place a simple order with predefined quantity."""
    drug = DRUG_DB.get(drug_name.lower())
    if not drug:
        return {"error": f"Drug '{drug_name}' not found"}

    order_id = ORDERS_DB["next_id"]
    ORDERS_DB["next_id"] += 1

    order = {
        "id": order_id,
        "customer": customer_name,
        "drug": drug["name"],
        "quantity": drug["quantity"],
        "total": drug["price"],
        "status": "pending"
    }
    ORDERS_DB["orders"][order_id] = order

    return {
        "order_id": order_id,
        "message": f"Order {order_id} placed: {drug['quantity']} {drug['name']} for ${order['total']:.2f}",
        "total": order['total'],
        "quantity": drug['quantity']
    }


def lookup_order(order_id):
    """Look up an order."""
    order = ORDERS_DB["orders"].get(int(order_id))
    if order:
        return {
            "order_id": order_id,
            "customer": order["customer"],
            "drug": order["drug"],
            "quantity": order["quantity"],
            "total": order["total"],
            "status": order["status"]
        }
    return {"error": f"Order {order_id} not found"}


def check_drug_interactions(drug1: str, drug2: str) -> Dict[str, Any]:
    """Check for potential drug interactions using a simple rule-based system."""
    # Common interaction pairs (simplified for demo)
    interactions = {
        ("warfarin", "aspirin"): "Increased bleeding risk",
        ("metformin", "alcohol"): "Risk of lactic acidosis",
        ("lisinopril", "potassium"): "Risk of hyperkalemia",
        ("atorvastatin", "grapefruit"): "Increased statin levels",
        ("sertraline", "tramadol"): "Risk of serotonin syndrome"
    }
    
    drug1_lower = drug1.lower()
    drug2_lower = drug2.lower()
    
    # Check both combinations
    interaction = interactions.get((drug1_lower, drug2_lower)) or interactions.get((drug2_lower, drug1_lower))
    
    if interaction:
        return {
            "interaction_found": True,
            "drugs": [drug1, drug2],
            "warning": interaction,
            "severity": "moderate",
            "recommendation": "Consult with healthcare provider before combining these medications"
        }
    
    return {
        "interaction_found": False,
        "drugs": [drug1, drug2],
        "message": "No known interactions found in our database",
        "note": "This is not a comprehensive check. Always consult healthcare providers."
    }

def get_drug_alternatives(drug_name: str) -> Dict[str, Any]:
    """Find alternative medications for a given drug."""
    alternatives = {
        "aspirin": ["ibuprofen", "acetaminophen", "naproxen"],
        "ibuprofen": ["aspirin", "acetaminophen", "naproxen"],
        "metformin": ["glipizide", "pioglitazone", "insulin"],
        "lisinopril": ["losartan", "amlodipine", "metoprolol"],
        "atorvastatin": ["simvastatin", "rosuvastatin", "pravastatin"],
        "sertraline": ["fluoxetine", "paroxetine", "citalopram"]
    }
    
    drug_alternatives = alternatives.get(drug_name.lower(), [])
    
    if drug_alternatives:
        # Get info for alternatives
        alternative_info = []
        for alt in drug_alternatives:
            alt_info = DRUG_DB.get(alt, {"name": alt.title(), "description": "Alternative medication"})
            alternative_info.append({
                "name": alt_info["name"],
                "description": alt_info.get("description", "No description available"),
                "price": alt_info.get("price", "N/A")
            })
        
        return {
            "original_drug": drug_name,
            "alternatives_found": len(drug_alternatives),
            "alternatives": alternative_info,
            "note": "Always consult with healthcare provider before switching medications"
        }
    
    return {
        "original_drug": drug_name,
        "alternatives_found": 0,
        "message": f"No alternatives found for {drug_name} in our database"
    }

def check_prescription_status(prescription_id: str) -> Dict[str, Any]:
    """Check prescription status (mock implementation)."""
    # Mock prescription database
    prescriptions = {
        "RX001": {"status": "ready", "patient": "John Doe", "drug": "Metformin", "pickup_time": "2024-01-15 14:30"},
        "RX002": {"status": "processing", "patient": "Jane Smith", "drug": "Lisinopril", "estimated_ready": "2024-01-15 16:00"},
        "RX003": {"status": "expired", "patient": "Bob Johnson", "drug": "Atorvastatin", "expiry_date": "2024-01-10"}
    }
    
    prescription = prescriptions.get(prescription_id.upper())
    if prescription:
        return {
            "prescription_id": prescription_id,
            "status": prescription["status"],
            "patient": prescription["patient"],
            "drug": prescription["drug"],
            **{k: v for k, v in prescription.items() if k not in ["status", "patient", "drug"]}
        }
    
    return {"error": f"Prescription {prescription_id} not found"}

# Function mapping dictionary
FUNCTION_MAP = {
    'get_drug_info': get_drug_info,
    'place_order': place_order,
    'lookup_order': lookup_order,
    'check_drug_interactions': check_drug_interactions,
    'get_drug_alternatives': get_drug_alternatives,
    'check_prescription_status': check_prescription_status
}