"""
MediLoop Master Healthcare Dataset Seeder
Populates the PostgreSQL database with:
- 46 Real-world pharmaceuticals across 8 therapeutic classes
- 4 Registered dispensing pharmacies with opening/closing hours
- Real-time pharmacy inventory with varied stock, pricing, and batch expirations
- 4 Patient test personas with targeted allergies and chronic medical conditions
- 2 Licensed dispensing pharmacists
- Historical orders for testing adherence & refill calculation
"""
import sys
import os
from datetime import date, datetime, time, timedelta, timezone

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, Base, engine
from app.core.security import hash_password
from app.models.user import User, Gender
from app.models.address import Address, AddressType
from app.models.medical_info import MedicalInfo
from app.models.emergency_contact import EmergencyContact
from app.models.pharmacy import Pharmacy
from app.models.pharmacist import Pharmacist
from app.models.medicine import Medicine
from app.models.pharmacy_inventory import PharmacyInventory
from app.models.order import Order, OrderItem, OrderStatus


MEDICINES_DATA = [
    # 1. Antipyretics, Analgesics & NSAIDs
    {
        "brand_name": "Crocin 650",
        "generic_name": "Paracetamol",
        "manufacturer": "GSK plc",
        "strength": "650 mg",
        "dosage_form": "Tablet",
        "prescription_required": False,
        "description": "Fast relief from fever, body aches, headaches and mild to moderate pain."
    },
    {
        "brand_name": "Dolo 650",
        "generic_name": "Paracetamol",
        "manufacturer": "Micro Labs Ltd",
        "strength": "650 mg",
        "dosage_form": "Tablet",
        "prescription_required": False,
        "description": "Popular antipyretic and analgesic for viral fevers, feverish colds and headaches."
    },
    {
        "brand_name": "Calpol 500",
        "generic_name": "Paracetamol",
        "manufacturer": "GSK plc",
        "strength": "500 mg",
        "dosage_form": "Tablet",
        "prescription_required": False,
        "description": "Gentle pain relief and antipyretic for all age groups."
    },
    {
        "brand_name": "Brufen 400",
        "generic_name": "Ibuprofen",
        "manufacturer": "Abbott Healthcare",
        "strength": "400 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Non-steroidal anti-inflammatory drug (NSAID) for muscle inflammation, dental pain and arthritis."
    },
    {
        "brand_name": "Combiflam",
        "generic_name": "Ibuprofen + Paracetamol",
        "manufacturer": "Sanofi India",
        "strength": "400 mg + 325 mg",
        "dosage_form": "Tablet",
        "prescription_required": False,
        "description": "Combination analgesic and anti-inflammatory formulation for severe joint and muscular aches."
    },
    {
        "brand_name": "Voveran 50",
        "generic_name": "Diclofenac",
        "manufacturer": "Novartis",
        "strength": "50 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Potent anti-inflammatory for acute musculoskeletal injuries, gout, and postoperative pain."
    },
    {
        "brand_name": "Ecosprin 75",
        "generic_name": "Aspirin",
        "manufacturer": "USV Ltd",
        "strength": "75 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Low-dose antiplatelet cardioprotective medication to prevent blood clots and secondary heart attacks."
    },

    # 2. Antibiotics & Anti-Infectives
    {
        "brand_name": "Amoxil 500",
        "generic_name": "Amoxicillin",
        "manufacturer": "GSK plc",
        "strength": "500 mg",
        "dosage_form": "Capsule",
        "prescription_required": True,
        "description": "Broad-spectrum penicillin antibiotic for ear, throat, respiratory and urinary tract bacterial infections."
    },
    {
        "brand_name": "Mox 250",
        "generic_name": "Amoxicillin",
        "manufacturer": "Sun Pharma",
        "strength": "250 mg",
        "dosage_form": "Capsule",
        "prescription_required": True,
        "description": "Pediatric/moderate dose amoxicillin capsule for mild-to-moderate bacterial infections."
    },
    {
        "brand_name": "Augmentin 625",
        "generic_name": "Amoxicillin + Clavulanic Acid",
        "manufacturer": "GSK plc",
        "strength": "625 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Potent beta-lactamase inhibitor combination for resistant bacterial sinus, lung and skin infections."
    },
    {
        "brand_name": "Azee 500",
        "generic_name": "Azithromycin",
        "manufacturer": "Cipla Ltd",
        "strength": "500 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Macrolide antibiotic for atypical pneumonia, strep throat, and chronic bronchitis flare-ups."
    },
    {
        "brand_name": "Cifran 500",
        "generic_name": "Ciprofloxacin",
        "manufacturer": "Sun Pharma",
        "strength": "500 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Fluoroquinolone antibiotic for typhoid, gastrointestinal and complicated urinary infections."
    },
    {
        "brand_name": "Taxim-O 200",
        "generic_name": "Cefixime",
        "manufacturer": "Alkem Laboratories",
        "strength": "200 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Third-generation cephalosporin for severe respiratory, urinary tract and otitis media infections."
    },
    {
        "brand_name": "Flagyl 400",
        "generic_name": "Metronidazole",
        "manufacturer": "Abbott",
        "strength": "400 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Antiprotozoal and antimicrobial for amoebiasis, dental abscesses, and anaerobic bacterial infections."
    },

    # 3. Cardiovascular & Antihypertensives
    {
        "brand_name": "Lipitor 10",
        "generic_name": "Atorvastatin",
        "manufacturer": "Pfizer Inc",
        "strength": "10 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "HMG-CoA reductase inhibitor (statin) for lowering LDL cholesterol and cardiovascular risk reduction."
    },
    {
        "brand_name": "Atorva 20",
        "generic_name": "Atorvastatin",
        "manufacturer": "Zydus Lifesciences",
        "strength": "20 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "High-intensity lipid-lowering medication for hypercholesterolemia and coronary artery disease."
    },
    {
        "brand_name": "Telma 40",
        "generic_name": "Telmisartan",
        "manufacturer": "Glenmark Pharmaceuticals",
        "strength": "40 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Angiotensin II receptor antagonist (ARB) for essential hypertension and kidney protection in diabetics."
    },
    {
        "brand_name": "Amlopres 5",
        "generic_name": "Amlodipine",
        "manufacturer": "Cipla Ltd",
        "strength": "5 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Calcium channel blocker for systemic hypertension and chronic stable angina pectoris."
    },
    {
        "brand_name": "Metolar 25",
        "generic_name": "Metoprolol Succinate",
        "manufacturer": "Cipla Ltd",
        "strength": "25 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Cardioselective beta-1 blocker for tachycardia, angina, high blood pressure and heart failure."
    },
    {
        "brand_name": "Rosuvas 10",
        "generic_name": "Rosuvastatin",
        "manufacturer": "Sun Pharma",
        "strength": "10 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Synthetic statin offering powerful triglyceride and LDL reduction with cardioprotective effects."
    },
    {
        "brand_name": "Clopilet 75",
        "generic_name": "Clopidogrel",
        "manufacturer": "Sun Pharma",
        "strength": "75 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Antiplatelet agent preventing thrombotic events in post-angioplasty and myocardial infarction patients."
    },

    # 4. Antidiabetics & Endocrine
    {
        "brand_name": "Glucophage 500",
        "generic_name": "Metformin",
        "manufacturer": "Merck",
        "strength": "500 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "First-line biguanide oral antihyperglycemic for glycemic control in Type 2 Diabetes Mellitus."
    },
    {
        "brand_name": "Glycomet-SR 500",
        "generic_name": "Metformin (Sustained Release)",
        "manufacturer": "USV Ltd",
        "strength": "500 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Extended-release metformin minimizing gastrointestinal side effects for sustained glucose control."
    },
    {
        "brand_name": "Januvia 100",
        "generic_name": "Sitagliptin",
        "manufacturer": "MSD Pharma",
        "strength": "100 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "DPP-4 inhibitor stimulating glucose-dependent insulin secretion without causing hypoglycemia."
    },
    {
        "brand_name": "Amaryl 1",
        "generic_name": "Glimepiride",
        "manufacturer": "Sanofi",
        "strength": "1 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Second-generation sulfonylurea promoting endogenous insulin release from pancreatic beta cells."
    },
    {
        "brand_name": "Forxiga 10",
        "generic_name": "Dapagliflozin",
        "manufacturer": "AstraZeneca",
        "strength": "10 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "SGLT2 inhibitor expelling excess blood glucose via urine while offering heart & renal protection."
    },
    {
        "brand_name": "Thyronorm 50",
        "generic_name": "Levothyroxine Sodium",
        "manufacturer": "Abbott",
        "strength": "50 mcg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Synthetic thyroid hormone replacement therapy for primary and secondary hypothyroidism."
    },

    # 5. Respiratory & Antiallergic
    {
        "brand_name": "Zyrtec 10",
        "generic_name": "Cetirizine",
        "manufacturer": "Dr. Reddy's Laboratories",
        "strength": "10 mg",
        "dosage_form": "Tablet",
        "prescription_required": False,
        "description": "Second-generation antihistamine for seasonal allergic rhinitis, watery eyes, hives and itching."
    },
    {
        "brand_name": "Allegra 120",
        "generic_name": "Fexofenadine",
        "manufacturer": "Sanofi India",
        "strength": "120 mg",
        "dosage_form": "Tablet",
        "prescription_required": False,
        "description": "Non-sedating antihistamine for indoor/outdoor seasonal allergies and chronic idiopathic urticaria."
    },
    {
        "brand_name": "Montair-LC",
        "generic_name": "Montelukast + Levocetirizine",
        "manufacturer": "Cipla Ltd",
        "strength": "10 mg + 5 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Leukotriene receptor antagonist plus antihistamine for allergic asthma, sneezing and nasal congestion."
    },
    {
        "brand_name": "Asthalin Inhaler",
        "generic_name": "Salbutamol",
        "manufacturer": "Cipla Ltd",
        "strength": "100 mcg/puff",
        "dosage_form": "Inhaler",
        "prescription_required": True,
        "description": "Fast-acting rescue bronchodilator relieving acute asthma bronchospasm and wheezing within minutes."
    },
    {
        "brand_name": "Budecort 200",
        "generic_name": "Budesonide",
        "manufacturer": "Cipla Ltd",
        "strength": "200 mcg",
        "dosage_form": "Inhaler",
        "prescription_required": True,
        "description": "Inhaled corticosteroid for daily maintenance and prevention of chronic airway inflammation in asthma."
    },

    # 6. Gastrointestinal & Acid Reducers
    {
        "brand_name": "Pantocid 40",
        "generic_name": "Pantoprazole",
        "manufacturer": "Sun Pharma",
        "strength": "40 mg",
        "dosage_form": "Tablet",
        "prescription_required": False,
        "description": "Proton pump inhibitor (PPI) suppressing gastric acid secretion for GERD, gastritis and peptic ulcers."
    },
    {
        "brand_name": "Omez 20",
        "generic_name": "Omeprazole",
        "manufacturer": "Dr. Reddy's",
        "strength": "20 mg",
        "dosage_form": "Capsule",
        "prescription_required": False,
        "description": "Gastric proton pump inhibitor relieving acid indigestion, heartburn, and reflux esophagitis."
    },
    {
        "brand_name": "Rantac 150",
        "generic_name": "Ranitidine",
        "manufacturer": "J.B. Chemicals",
        "strength": "150 mg",
        "dosage_form": "Tablet",
        "prescription_required": False,
        "description": "H2-receptor antagonist reducing stomach acid for quick relief of indigestion and sour stomach."
    },
    {
        "brand_name": "Gelusil MPS",
        "generic_name": "Aluminium Hydroxide + Magnesium Hydroxide + Simethicone",
        "manufacturer": "Pfizer",
        "strength": "200 ml",
        "dosage_form": "Syrup",
        "prescription_required": False,
        "description": "Instant soothing antacid and antiflatulent liquid providing heartburn and acid gas relief."
    },
    {
        "brand_name": "Dulcolax 5",
        "generic_name": "Bisacodyl",
        "manufacturer": "Sanofi",
        "strength": "5 mg",
        "dosage_form": "Tablet",
        "prescription_required": False,
        "description": "Overnight stimulant laxative for gentle, predictable relief from acute constipation."
    },

    # 7. Central Nervous System & Psychiatric
    {
        "brand_name": "Nexito 10",
        "generic_name": "Escitalopram",
        "manufacturer": "Sun Pharma",
        "strength": "10 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Selective serotonin reuptake inhibitor (SSRI) for generalized anxiety disorder and major depression."
    },
    {
        "brand_name": "Gabapin 300",
        "generic_name": "Gabapentin",
        "manufacturer": "Intas Pharmaceuticals",
        "strength": "300 mg",
        "dosage_form": "Capsule",
        "prescription_required": True,
        "description": "GABA analogue for neuropathic nerve pain, post-herpetic neuralgia and adjunct seizure control."
    },
    {
        "brand_name": "Vertin 16",
        "generic_name": "Betahistine",
        "manufacturer": "Abbott",
        "strength": "16 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Histamine analogue for managing peripheral vertigo, dizziness, and Meniere's disease inner ear pressure."
    },

    # 8. Vitamins, Minerals & Supplements
    {
        "brand_name": "Shelcal 500",
        "generic_name": "Calcium + Vitamin D3",
        "manufacturer": "Torrent Pharmaceuticals",
        "strength": "500 mg + 250 IU",
        "dosage_form": "Tablet",
        "prescription_required": False,
        "description": "Essential bone calcium supplement with Vitamin D3 to combat osteoporosis, osteopenia and deficiency."
    },
    {
        "brand_name": "Limcee 500",
        "generic_name": "Vitamin C (Ascorbic Acid)",
        "manufacturer": "Abbott",
        "strength": "500 mg",
        "dosage_form": "Chewable Tablet",
        "prescription_required": False,
        "description": "Orange-flavored chewable antioxidant boosting immune defenses, collagen synthesis and wound healing."
    },
    {
        "brand_name": "Becosules Z",
        "generic_name": "B-Complex + Zinc + Vitamin C",
        "manufacturer": "Pfizer",
        "strength": "Standard",
        "dosage_form": "Capsule",
        "prescription_required": False,
        "description": "Therapeutic multivitamin formula for mouth ulcers, recovery fatigue, hair vitality and immunity."
    },
    {
        "brand_name": "Neurobion Forte",
        "generic_name": "Vitamin B1 + B6 + B12",
        "manufacturer": "Procter & Gamble",
        "strength": "Standard",
        "dosage_form": "Tablet",
        "prescription_required": False,
        "description": "Neurotropic B-vitamin formulation supporting nerve regeneration, tingling numbness and stamina."
    },
    {
        "brand_name": "Uprise-D3 60K",
        "generic_name": "Cholecalciferol (Vitamin D3)",
        "manufacturer": "Alkem",
        "strength": "60,000 IU",
        "dosage_form": "Capsule",
        "prescription_required": True,
        "description": "High-potency weekly Vitamin D3 therapy restoring severe skeletal and muscular deficiency levels."
    },
    {
        "brand_name": "Supradyn Daily",
        "generic_name": "Multivitamin + Multi-mineral",
        "manufacturer": "Bayer",
        "strength": "Standard",
        "dosage_form": "Tablet",
        "prescription_required": False,
        "description": "Daily vitality multivitamin with zinc, iron and essential trace elements for active lifestyles."
    },
]

PHARMACIES_DATA = [
    {
        "pharmacy_name": "MediLoop Central Super Pharmacy",
        "license_number": "DL-CENTRAL-2026-001",
        "address": "100 Healthcare Hub Boulevard, Suite 10",
        "city": "Bengaluru",
        "state": "Karnataka",
        "pincode": "560001",
        "phone_number": "+91 80 4455 6677",
        "email": "central@mediloop.com",
        "opening_time": time(8, 0),
        "closing_time": time(23, 0),
        "supports_home_delivery": True,
        "estimated_delivery_minutes": 25,
        "is_active": True
    },
    {
        "pharmacy_name": "Apollo Pharmacy - Express Hub",
        "license_number": "DL-APOLLO-2026-042",
        "address": "45 Mahatma Gandhi Road",
        "city": "Bengaluru",
        "state": "Karnataka",
        "pincode": "560025",
        "phone_number": "+91 80 2233 4455",
        "email": "apollo.mgroad@apollo.com",
        "opening_time": time(0, 0),
        "closing_time": time(23, 59),
        "supports_home_delivery": True,
        "estimated_delivery_minutes": 20,
        "is_active": True
    },
    {
        "pharmacy_name": "MedPlus 24x7 Care Pharmacy",
        "license_number": "DL-MEDPLUS-2026-088",
        "address": "78 Station Road, Indiranagar",
        "city": "Bengaluru",
        "state": "Karnataka",
        "pincode": "560038",
        "phone_number": "+91 80 8899 0011",
        "email": "medplus.indira@medplus.com",
        "opening_time": time(0, 0),
        "closing_time": time(23, 59),
        "supports_home_delivery": True,
        "estimated_delivery_minutes": 35,
        "is_active": True
    },
    {
        "pharmacy_name": "Wellness Forever Day & Night Pharmacy",
        "license_number": "DL-WELLNESS-2026-105",
        "address": "12 Ring Road, Koramangala 4th Block",
        "city": "Bengaluru",
        "state": "Karnataka",
        "pincode": "560034",
        "phone_number": "+91 80 7766 5544",
        "email": "wellness.koramangala@wellnessforever.com",
        "opening_time": time(7, 0),
        "closing_time": time(23, 30),
        "supports_home_delivery": True,
        "estimated_delivery_minutes": 30,
        "is_active": True
    }
]

PATIENTS_DATA = [
    {
        "user": {
            "full_name": "Aarav Sharma",
            "email": "aarav.sharma@example.com",
            "mobile_number": "+91 9876543210",
            "password": "Password123",
            "date_of_birth": date(1988, 5, 14),
            "gender": Gender.MALE,
        },
        "address": {
            "house_number": "Apt 4B",
            "street": "Green Glen Layout, Bellandur",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560103",
            "landmark": "Near Central Mall",
            "is_default_delivery": True,
            "address_type": AddressType.HOME
        },
        "medical_info": {
            "allergies": "Penicillin, Amoxicillin",  # Targeted for Penicillin allergy test
            "medical_conditions": "Mild Asthma"
        },
        "emergency_contact": {
            "contact_number": "+91 9876543211",
            "relationship": "Spouse"
        }
    },
    {
        "user": {
            "full_name": "Priya Patel",
            "email": "priya.patel@example.com",
            "mobile_number": "+91 9811223344",
            "password": "Password123",
            "date_of_birth": date(1975, 11, 22),
            "gender": Gender.FEMALE,
        },
        "address": {
            "house_number": "Villa 18",
            "street": "Palm Meadows, Whitefield",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560066",
            "landmark": "Opposite Tech Park",
            "is_default_delivery": True,
            "address_type": AddressType.HOME
        },
        "medical_info": {
            "allergies": "Sulfa drugs",
            "medical_conditions": "Type 2 Diabetes, Hypertension" # Targeted for chronic refill test
        },
        "emergency_contact": {
            "contact_number": "+91 9811223345",
            "relationship": "Spouse"
        }
    },
    {
        "user": {
            "full_name": "David Fernandes",
            "email": "david.fernandes@example.com",
            "mobile_number": "+91 9744556677",
            "password": "Password123",
            "date_of_birth": date(1992, 8, 3),
            "gender": Gender.MALE,
        },
        "address": {
            "house_number": "Flat 302",
            "street": "Richmond Towers, Richmond Road",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560025",
            "landmark": "Behind Hockey Stadium",
            "is_default_delivery": True,
            "address_type": AddressType.HOME
        },
        "medical_info": {
            "allergies": "Aspirin, Ibuprofen, NSAIDs", # Targeted for NSAID interaction test
            "medical_conditions": "Gastric Hyperacidity"
        },
        "emergency_contact": {
            "contact_number": "+91 9744556678",
            "relationship": "Mother"
        }
    },
    {
        "user": {
            "full_name": "Sneha Iyer",
            "email": "sneha.iyer@example.com",
            "mobile_number": "+91 9900112233",
            "password": "Password123",
            "date_of_birth": date(1996, 2, 19),
            "gender": Gender.FEMALE,
        },
        "address": {
            "house_number": "No 42",
            "street": "14th Cross, 2nd Stage, JP Nagar",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560078",
            "landmark": "Near Mini Forest Park",
            "is_default_delivery": True,
            "address_type": AddressType.HOME
        },
        "medical_info": {
            "allergies": "No known drug allergies",
            "medical_conditions": "None (Healthy adult)"
        },
        "emergency_contact": {
            "contact_number": "+91 9900112234",
            "relationship": "Sister"
        }
    }
]

PHARMACISTS_DATA = [
    {
        "user": {
            "full_name": "Dr. Ramesh Menon, R.Ph",
            "email": "pharmacist.ramesh@mediloop.com",
            "mobile_number": "+91 9123456780",
            "password": "Password123",
            "date_of_birth": date(1982, 4, 15),
            "gender": Gender.MALE,
        },
        "registration_number": "KA-PHARM-2010-8841",
        "designation": "Chief Supervising Pharmacist",
        "pharmacy_name": "MediLoop Central Super Pharmacy"
    },
    {
        "user": {
            "full_name": "Dr. Anjali Nair, R.Ph",
            "email": "pharmacist.anjali@apollo.com",
            "mobile_number": "+91 9123456781",
            "password": "Password123",
            "date_of_birth": date(1986, 9, 28),
            "gender": Gender.FEMALE,
        },
        "registration_number": "KA-PHARM-2014-9920",
        "designation": "Lead Dispensing Pharmacist",
        "pharmacy_name": "Apollo Pharmacy - Express Hub"
    }
]


def seed_database():
    print("=" * 70)
    print("[*] MediLoop Master Healthcare Dataset Seeder")
    print("=" * 70)
    
    db = SessionLocal()
    try:
        # 1. Seed Medicines
        print(f"\n[1/5] Seeding {len(MEDICINES_DATA)} Pharmaceuticals...")
        seeded_medicines = {}
        for med_dict in MEDICINES_DATA:
            med = db.query(Medicine).filter(Medicine.brand_name == med_dict["brand_name"]).first()
            if not med:
                med = Medicine(**med_dict)
                db.add(med)
                db.commit()
                db.refresh(med)
                print(f"  + Added Medicine: {med.brand_name} ({med.strength}) [{med.generic_name}]")
            else:
                for k, v in med_dict.items():
                    setattr(med, k, v)
                db.commit()
                db.refresh(med)
                print(f"  ~ Synced Medicine: {med.brand_name} ({med.strength})")
            seeded_medicines[med.brand_name] = med

        # 2. Seed Pharmacies
        print(f"\n[2/5] Seeding {len(PHARMACIES_DATA)} Dispensing Pharmacies...")
        seeded_pharmacies = {}
        for pharm_dict in PHARMACIES_DATA:
            pharm = db.query(Pharmacy).filter(Pharmacy.license_number == pharm_dict["license_number"]).first()
            if not pharm:
                pharm = Pharmacy(**pharm_dict)
                db.add(pharm)
                db.commit()
                db.refresh(pharm)
                print(f"  + Added Pharmacy: {pharm.pharmacy_name}")
            else:
                for k, v in pharm_dict.items():
                    setattr(pharm, k, v)
                db.commit()
                db.refresh(pharm)
                print(f"  ~ Synced Pharmacy: {pharm.pharmacy_name}")
            seeded_pharmacies[pharm.pharmacy_name] = pharm

        # 3. Seed Pharmacy Inventory (Pricing, Stock, Batch Expiration)
        print("\n[3/5] Generating Real-Time Stock & Batch Inventory across Pharmacies...")
        today = date.today()
        base_prices = {
            "Crocin 650": (32.50, 35.00),
            "Dolo 650": (30.00, 32.00),
            "Calpol 500": (24.00, 26.50),
            "Brufen 400": (42.00, 48.00),
            "Combiflam": (45.00, 52.00),
            "Voveran 50": (85.00, 98.00),
            "Ecosprin 75": (15.50, 18.00),
            "Amoxil 500": (88.00, 102.00),
            "Mox 250": (55.00, 64.00),
            "Augmentin 625": (210.00, 240.00),
            "Azee 500": (125.00, 145.00),
            "Cifran 500": (95.00, 110.00),
            "Taxim-O 200": (115.00, 130.00),
            "Flagyl 400": (28.00, 32.00),
            "Lipitor 10": (140.00, 160.00),
            "Atorva 20": (185.00, 215.00),
            "Telma 40": (110.00, 128.00),
            "Amlopres 5": (48.00, 56.00),
            "Metolar 25": (82.00, 95.00),
            "Rosuvas 10": (160.00, 185.00),
            "Clopilet 75": (98.00, 112.00),
            "Glucophage 500": (62.00, 70.00),
            "Glycomet-SR 500": (45.00, 52.00),
            "Januvia 100": (380.00, 420.00),
            "Amaryl 1": (75.00, 88.00),
            "Forxiga 10": (410.00, 460.00),
            "Thyronorm 50": (120.00, 138.00),
            "Zyrtec 10": (38.00, 44.00),
            "Allegra 120": (145.00, 165.00),
            "Montair-LC": (180.00, 210.00),
            "Asthalin Inhaler": (165.00, 185.00),
            "Budecort 200": (290.00, 325.00),
            "Pantocid 40": (118.00, 135.00),
            "Omez 20": (58.00, 68.00),
            "Rantac 150": (34.00, 40.00),
            "Gelusil MPS": (95.00, 110.00),
            "Dulcolax 5": (12.00, 15.00),
            "Nexito 10": (115.00, 132.00),
            "Gabapin 300": (215.00, 245.00),
            "Vertin 16": (195.00, 225.00),
            "Shelcal 500": (115.00, 130.00),
            "Limcee 500": (25.00, 30.00),
            "Becosules Z": (48.00, 55.00),
            "Neurobion Forte": (38.00, 45.00),
            "Uprise-D3 60K": (240.00, 280.00),
            "Supradyn Daily": (65.00, 75.00),
        }

        for p_idx, (pharm_name, pharm) in enumerate(seeded_pharmacies.items()):
            for m_idx, (med_name, med) in enumerate(seeded_medicines.items()):
                inv = db.query(PharmacyInventory).filter(
                    PharmacyInventory.pharmacy_id == pharm.id,
                    PharmacyInventory.medicine_id == med.id
                ).first()

                price_tuple = base_prices.get(med_name, (50.0, 60.0))
                # Alternate stocks to test Out-Of-Stock and Low-Stock agent scenarios
                if (p_idx + m_idx) % 17 == 0:
                    stock = 0 # Out of stock
                elif (p_idx + m_idx) % 7 == 0:
                    stock = 8 # Low stock
                else:
                    stock = 75 + (m_idx * 3)

                batch_num = f"BAT-{pharm.id:02d}-{med.id:03d}"
                expiry = today + timedelta(days=180 + (m_idx * 15))

                if not inv:
                    inv = PharmacyInventory(
                        pharmacy_id=pharm.id,
                        medicine_id=med.id,
                        stock_quantity=stock,
                        selling_price=price_tuple[0],
                        mrp=price_tuple[1],
                        batch_number=batch_num,
                        expiry_date=expiry,
                        is_available=(stock > 0)
                    )
                    db.add(inv)
                else:
                    inv.stock_quantity = stock
                    inv.selling_price = price_tuple[0]
                    inv.mrp = price_tuple[1]
                    inv.is_available = (stock > 0)
                    inv.expiry_date = expiry
            db.commit()
        print(f"  + Inventory synchronized: {len(seeded_pharmacies) * len(seeded_medicines)} SKU stock items configured.")

        # 4. Seed Patient Test Personas
        print(f"\n[4/5] Seeding {len(PATIENTS_DATA)} Patient Test Personas with Allergies & History...")
        seeded_patients = []
        for p_data in PATIENTS_DATA:
            u_info = p_data["user"]
            patient = db.query(User).filter(User.email == u_info["email"]).first()
            if not patient:
                patient = User(
                    full_name=u_info["full_name"],
                    email=u_info["email"],
                    mobile_number=u_info["mobile_number"],
                    hashed_password=hash_password(u_info["password"]),
                    date_of_birth=u_info["date_of_birth"],
                    gender=u_info["gender"],
                    is_active=True
                )
                db.add(patient)
                db.commit()
                db.refresh(patient)
                print(f"  + Added Patient: {patient.full_name} ({patient.email})")

                # Add Address
                addr = Address(user_id=patient.id, **p_data["address"])
                db.add(addr)

                # Add Medical Info
                med_info = MedicalInfo(user_id=patient.id, **p_data["medical_info"])
                db.add(med_info)

                # Add Emergency Contact
                em_contact = EmergencyContact(user_id=patient.id, **p_data["emergency_contact"])
                db.add(em_contact)
                db.commit()
            else:
                print(f"  ~ Exists Patient: {patient.full_name}")
            seeded_patients.append(patient)

        # 5. Seed Pharmacists
        print(f"\n[5/5] Seeding {len(PHARMACISTS_DATA)} Licensed Dispensing Pharmacists...")
        for ph_data in PHARMACISTS_DATA:
            u_info = ph_data["user"]
            pharmacy = seeded_pharmacies.get(ph_data["pharmacy_name"])
            pharmacist = db.query(Pharmacist).filter(Pharmacist.email == u_info["email"]).first()
            if not pharmacist:
                pharmacist = Pharmacist(
                    pharmacy_id=pharmacy.id if pharmacy else None,
                    registration_number=ph_data["registration_number"],
                    full_name=u_info["full_name"],
                    email=u_info["email"],
                    mobile_number=u_info["mobile_number"],
                    hashed_password=hash_password(u_info["password"]),
                    designation=ph_data["designation"],
                    is_active=True
                )
                db.add(pharmacist)
                db.commit()
                print(f"  + Added Pharmacist: {pharmacist.full_name} -> {ph_data['pharmacy_name']}")
            else:
                print(f"  ~ Exists Pharmacist: {pharmacist.full_name}")

        # 6. Seed Sample Past Order for Refill Reminder Agent Testing
        print("\n[Bonus] Seeding Historical Adherence Orders for Refill Testing...")
        priya = seeded_patients[1] # Priya Patel (Diabetes & Hypertension)
        central_pharm = list(seeded_pharmacies.values())[0]
        
        existing_order = db.query(Order).filter(Order.customer_id == priya.id).first()
        if not existing_order:
            placed_date = datetime.now(timezone.utc) - timedelta(days=25)
            test_order = Order(
                order_number="ORD-REFILL-TEST-001",
                customer_id=priya.id,
                pharmacy_id=central_pharm.id,
                payment_method="UPI",
                payment_status="PAID",
                order_status=OrderStatus.DELIVERED,
                total_amount=172.00,
                placed_at=placed_date
            )
            db.add(test_order)
            db.commit()
            db.refresh(test_order)

            glucophage = seeded_medicines["Glucophage 500"]
            telma = seeded_medicines["Telma 40"]

            item1 = OrderItem(
                order_id=test_order.id,
                medicine_id=glucophage.id,
                quantity=30,
                unit_price=62.00,
                total_price=62.00
            )
            item2 = OrderItem(
                order_id=test_order.id,
                medicine_id=telma.id,
                quantity=30,
                unit_price=110.00,
                total_price=110.00
            )
            db.add_all([item1, item2])
            db.commit()
            print(f"  + Created sample past order {test_order.order_number} (placed 25 days ago, 5 days remaining before refill!)")

        print("\n" + "=" * 70)
        print("[SUCCESS] MediLoop Master Dataset successfully seeded into PostgreSQL!")
        print("=" * 70)

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Seeding Error: {str(e)}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
