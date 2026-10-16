import re
from typing import List, Dict, Any

class PrescriptionAgent:
    def parse_prescription_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Parses extracted OCR text into a structured list of prescription items.
        
        Example Input:
            Rx
            Tab Crocin 650
            1-0-1
            5 Days
            
            Tab Amoxicillin 500
            1-1-1
            7 Days

        Example Output:
            [
                {
                    "medicine_name": "Tab Crocin 650",
                    "strength": "650",
                    "dosage_pattern": "1-0-1",
                    "frequency": 2,
                    "duration_days": 5,
                    "calculated_quantity": 10,
                    "confidence_score": 0.95
                },
                ...
            ]
        """
        items = []
        if not text:
            return items

        # Split text into sections by double newline (blocks representing each medicine)
        blocks = text.split("\n\n")
        
        for block in blocks:
            lines = [line.strip() for line in block.split("\n") if line.strip()]
            if not lines:
                continue

            # Remove "Rx" or standalone markers
            lines = [l for l in lines if l.upper() != "RX"]
            if not lines:
                continue

            medicine_name = None
            strength = None
            dosage_pattern = None
            frequency = None
            duration_days = None
            confidence_score = 0.95

            for line in lines:
                # 1. Look for dosage pattern: e.g. "1-0-1" or "0-0-1"
                dosage_match = re.search(r'\b([0-2])\s*-\s*([0-2])\s*-\s*([0-2])\b', line)
                
                # 2. Look for duration: e.g. "5 Days"
                duration_match = re.search(r'\b(\d+)\s*(?:Day|Days|Week|Weeks|Month|Months)\b', line, re.IGNORECASE)
                
                if dosage_match:
                    dosage_pattern = f"{dosage_match.group(1)}-{dosage_match.group(2)}-{dosage_match.group(3)}"
                    frequency = sum(int(x) for x in [dosage_match.group(1), dosage_match.group(2), dosage_match.group(3)])
                elif duration_match:
                    val = int(duration_match.group(1))
                    unit = duration_match.group(0).lower()
                    if "week" in unit:
                        duration_days = val * 7
                    elif "month" in unit:
                        duration_days = val * 30
                    else:
                        duration_days = val
                else:
                    # Treat this line as medicine name if we don't have one yet
                    # Or if it starts with Tab/Cap/Syp
                    is_med_start = any(line.lower().startswith(pfx) for pfx in ["tab", "cap", "syp", "tablet", "capsule", "syrup", "ointment"])
                    if not medicine_name or is_med_start:
                        # Extract strength if any (e.g. 650, 500mg, 10mg)
                        strength_match = re.search(r'\b(\d+\s*(?:mg|g|ml)?)\b', line, re.IGNORECASE)
                        if strength_match:
                            strength = strength_match.group(1)
                        medicine_name = line

            # Apply defaults if missing to ensure data integrity
            if not medicine_name:
                # Fallback to the first line if nothing else was classified
                medicine_name = lines[0]
            
            if not dosage_pattern:
                dosage_pattern = "1-0-1"
                frequency = 2
                confidence_score = min(confidence_score, 0.85)

            if not duration_days:
                duration_days = 5
                confidence_score = min(confidence_score, 0.85)

            # Calculate total quantity
            calculated_quantity = (frequency or 1) * duration_days

            items.append({
                "medicine_name": medicine_name,
                "strength": strength,
                "dosage_pattern": dosage_pattern,
                "frequency": frequency,
                "duration_days": duration_days,
                "calculated_quantity": calculated_quantity,
                "confidence_score": confidence_score
            })

        return items
