import re
from difflib import SequenceMatcher
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.models.medicine import Medicine

def clean_medicine_name(name: str) -> str:
    """
    Cleans a medicine name by removing common dosage form prefixes and strength suffixes.
    e.g. "Tab Crocin 650mg" -> "crocin"
    """
    if not name:
        return ""
    
    # Lowercase and replace punctuation/extra spaces
    cleaned = name.lower().strip()
    
    # Remove common prefixes
    prefixes = [r'^tab\b', r'^cap\b', r'^syp\b', r'^tablet\b', r'^capsule\b', r'^syrup\b', r'^ointment\b', r'^rx\b']
    for pfx in prefixes:
        cleaned = re.sub(pfx, "", cleaned).strip()
        
    # Remove strengths (e.g. 650mg, 500 mg, 10mg, 10 ml)
    cleaned = re.sub(r'\b\d+\s*(?:mg|g|ml|mcg)\b', "", cleaned).strip()
    # Remove plain numbers (e.g. 650, 500)
    cleaned = re.sub(r'\b\d+\b', "", cleaned).strip()
    
    # Remove extra whitespace
    cleaned = " ".join(cleaned.split())
    return cleaned

def match_extracted_medicine(db: Session, raw_name: str) -> Dict[str, Any]:
    """
    Fuzzy matches an extracted medicine name against the database catalog.
    Returns:
        Dict containing:
        - "medicine": Optional[Medicine] (best match above threshold)
        - "confidence": float (match confidence score between 0.0 and 1.0)
        - "alternatives": List[Medicine] (substitutes with same generic name or close spellings)
    """
    result = {
        "medicine": None,
        "confidence": 0.0,
        "alternatives": []
    }
    
    if not raw_name:
        return result
        
    # Fetch all active medicines from database
    all_medicines = db.query(Medicine).filter(Medicine.is_active == True).all()
    if not all_medicines:
        return result
        
    cleaned_query = clean_medicine_name(raw_name)
    if not cleaned_query:
        # Fallback to simple lowercasing if cleanup emptied it completely
        cleaned_query = raw_name.lower().strip()
        
    best_match = None
    best_score = 0.0
    
    # First pass: look for exact/case-insensitive matches
    for med in all_medicines:
        brand_clean = clean_medicine_name(med.brand_name)
        generic_clean = clean_medicine_name(med.generic_name)
        
        # Exact brand or generic matches
        if cleaned_query == brand_clean or cleaned_query == generic_clean:
            best_match = med
            best_score = 1.0
            break
            
    # Second pass: Fuzzy matching using difflib if no exact match found
    if best_score < 1.0:
        for med in all_medicines:
            brand_clean = clean_medicine_name(med.brand_name)
            generic_clean = clean_medicine_name(med.generic_name)
            
            # Compare query to brand name
            brand_ratio = SequenceMatcher(None, cleaned_query, brand_clean).ratio()
            # Compare query to generic name
            generic_ratio = SequenceMatcher(None, cleaned_query, generic_clean).ratio()
            
            max_ratio = max(brand_ratio, generic_ratio)
            if max_ratio > best_score:
                best_score = max_ratio
                best_match = med
                
    # Check threshold for declaring a match
    threshold = 0.70
    if best_score >= threshold and best_match:
        result["medicine"] = best_match
        result["confidence"] = round(best_score, 2)
        
        # Find alternatives (same generic name/substitutes or other close spellings)
        alternatives = []
        for med in all_medicines:
            if med.id == best_match.id:
                continue
                
            # Direct generic substitute
            if med.generic_name.lower() == best_match.generic_name.lower():
                alternatives.append(med)
            else:
                # Close spelling match
                brand_clean = clean_medicine_name(med.brand_name)
                ratio = SequenceMatcher(None, cleaned_query, brand_clean).ratio()
                if ratio > 0.50:
                    alternatives.append(med)
                    
        result["alternatives"] = alternatives[:5] # limit to 5
    else:
        # If no match above threshold, collect close spellings as alternatives
        result["confidence"] = round(best_score, 2)
        close_matches = []
        for med in all_medicines:
            brand_clean = clean_medicine_name(med.brand_name)
            ratio = SequenceMatcher(None, cleaned_query, brand_clean).ratio()
            if ratio > 0.40:
                close_matches.append((ratio, med))
                
        # Sort by ratio descending
        close_matches.sort(key=lambda x: x[0], reverse=True)
        result["alternatives"] = [med for _, med in close_matches[:5]]
        
    return result
