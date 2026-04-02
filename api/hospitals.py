from http.server import BaseHTTPRequestHandler
import json
import os
import math

GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")
GOOGLE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
GOOGLE_PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
HOSPITAL_SEARCH_RADIUS = 5000

EXCLUDED_KEYWORDS = [
    "diagnostic", "diagnostics", "lab", "laboratory", "laboratories",
    "scan", "scanning", "imaging", "pathology", "path lab",
    "x-ray", "xray", "mri", "ct scan", "ultrasound",
    "pharmacy", "medical store", "chemist",
    "dental", "dentist", "eye clinic", "optical",
    "physiotherapy", "physio", "rehab center",
    "nursing home", "old age", "hospice",
    "blood bank", "test", "testing"
]

VALID_HOSPITAL_KEYWORDS = [
    "hospital", "medical center", "medical centre",
    "emergency", "trauma center", "trauma centre",
    "multi-speciality", "multispeciality", "multi-specialty", "multispecialty",
    "general hospital", "govt hospital", "government hospital"
]

CONDITION_KEYWORDS = {
    "CARDIAC": ["chest pain", "heart", "cardiac", "breathing difficulty", "breathless", "shortness of breath", "palpitation", "heart attack", "angina"],
    "TRAUMA": ["injury", "injured", "accident", "bleeding", "fracture", "broken", "wound", "cut", "burn", "fall", "trauma", "hit", "crash"],
    "NEURO": ["unconscious", "seizure", "convulsion", "stroke", "paralysis", "numbness", "headache severe", "fainting", "blackout", "fits"],
    "GENERAL": ["fever", "infection", "cold", "cough", "flu", "vomiting", "diarrhea", "stomach", "pain", "weakness", "fatigue"]
}

CONDITION_HOSPITAL_PREFERENCES = {
    "CARDIAC": ["cardiac", "heart", "multi-speciality", "multispeciality", "general"],
    "TRAUMA": ["trauma", "emergency", "accident", "multi-speciality", "general"],
    "NEURO": ["neuro", "brain", "multi-speciality", "multispeciality", "general"],
    "GENERAL": ["general", "multi-speciality", "multispeciality", "hospital"],
    "OTHER": ["general", "multi-speciality", "hospital"]
}


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)


def classify_condition(symptoms):
    if not symptoms:
        return "OTHER"
    symptoms_lower = symptoms.lower()
    for condition, keywords in CONDITION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in symptoms_lower:
                return condition
    return "OTHER"


def is_valid_hospital(name):
    name_lower = name.lower()
    for excluded in EXCLUDED_KEYWORDS:
        if excluded in name_lower:
            if "hospital" not in name_lower:
                return False
    for valid in VALID_HOSPITAL_KEYWORDS:
        if valid in name_lower:
            return True
    return False


def calculate_hospital_score(hospital_name, condition):
    name_lower = hospital_name.lower()
    score = 0
    if "hospital" in name_lower:
        score += 10
    if any(kw in name_lower for kw in ["multi-speciality", "multispeciality", "multi-specialty", "multispecialty"]):
        score += 20
    preferred_keywords = CONDITION_HOSPITAL_PREFERENCES.get(condition, [])
    for keyword in preferred_keywords:
        if keyword in name_lower:
            score += 50
            break
    for excluded in EXCLUDED_KEYWORDS:
        if excluded in name_lower:
            score -= 30
            break
    return score


def get_hospital_match_tag(score, is_best):
    if is_best and score >= 50:
        return "Best Match"
    elif score >= 30:
        return "Good Match"
    else:
        return "Nearby Option"


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return

    def do_POST(self):
        try:
            import urllib.request
            import urllib.parse
            
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            lat = data.get('lat')
            lng = data.get('lng')
            symptoms = data.get('symptoms', '')
            
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                self.send_json_response({"success": False, "hospitals": [], "error": "Invalid coordinates"})
                return
            
            condition = classify_condition(symptoms)
            
            # Call Google Places API
            params = urllib.parse.urlencode({
                "location": f"{lat},{lng}",
                "radius": HOSPITAL_SEARCH_RADIUS,
                "type": "hospital",
                "key": GOOGLE_MAPS_API_KEY
            })
            
            url = f"{GOOGLE_PLACES_URL}?{params}"
            
            with urllib.request.urlopen(url, timeout=10) as resp:
                places_data = json.loads(resp.read().decode('utf-8'))
            
            if places_data.get("status") != "OK":
                error_msg = places_data.get("error_message", places_data.get("status", "Unknown error"))
                self.send_json_response({"success": False, "hospitals": [], "error": f"Google Places API: {error_msg}"})
                return
            
            results = places_data.get("results", [])
            if not results:
                self.send_json_response({"success": True, "hospitals": [], "error": "No hospitals found within 5km", "condition_category": condition})
                return
            
            # Filter hospitals
            valid_hospitals = [place for place in results if is_valid_hospital(place.get("name", ""))]
            
            safety_message = None
            if not valid_hospitals:
                valid_hospitals = results
                safety_message = "Showing nearest available hospitals. Please confirm with medical professionals."
            
            # Process hospitals
            hospitals = []
            for place in valid_hospitals[:15]:
                place_lat = place["geometry"]["location"]["lat"]
                place_lng = place["geometry"]["location"]["lng"]
                distance = haversine_distance(lat, lng, place_lat, place_lng)
                
                name = place.get("name", "Unknown Hospital")
                score = calculate_hospital_score(name, condition)
                is_open = place.get("opening_hours", {}).get("open_now")
                
                hospitals.append({
                    "name": name,
                    "address": place.get("vicinity", "Address not available"),
                    "distance": distance,
                    "distance_text": f"{distance} km",
                    "lat": place_lat,
                    "lng": place_lng,
                    "place_id": place.get("place_id"),
                    "score": score,
                    "match_tag": "Nearby Option",
                    "phone": None,
                    "is_open": is_open
                })
            
            # Sort by score (descending), then by distance (ascending)
            hospitals.sort(key=lambda h: (-h["score"], h["distance"]))
            
            # Assign match tags
            if hospitals:
                hospitals[0]["match_tag"] = get_hospital_match_tag(hospitals[0]["score"], is_best=True)
                for h in hospitals[1:]:
                    h["match_tag"] = get_hospital_match_tag(h["score"], is_best=False)
            
            # Get top 5 and fetch phone numbers
            top_hospitals = hospitals[:5]
            
            for hospital in top_hospitals:
                if hospital.get("place_id"):
                    try:
                        details_params = urllib.parse.urlencode({
                            "place_id": hospital["place_id"],
                            "fields": "formatted_phone_number",
                            "key": GOOGLE_MAPS_API_KEY
                        })
                        details_url = f"{GOOGLE_PLACE_DETAILS_URL}?{details_params}"
                        
                        with urllib.request.urlopen(details_url, timeout=5) as details_resp:
                            details_data = json.loads(details_resp.read().decode('utf-8'))
                        
                        if details_data.get("status") == "OK":
                            hospital["phone"] = details_data.get("result", {}).get("formatted_phone_number")
                    except:
                        pass
            
            self.send_json_response({
                "success": True,
                "hospitals": top_hospitals,
                "condition_category": condition,
                "safety_message": safety_message
            })
            
        except Exception as e:
            print(f"Error: {e}")
            self.send_json_response({"success": False, "hospitals": [], "error": "An error occurred while finding hospitals"})
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
