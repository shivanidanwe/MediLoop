"""
MediLoop 500+ Indian Pharmaceuticals Seeder
Covers authentic Indian pharmaceuticals across all major chronic diseases:
1. Cardiovascular & Hypertension (Hypertension, Angina, Heart Failure, Arrhythmia, Stroke prevention)
2. Dyslipidemia, Hypercholesterolemia & Anticoagulants
3. Type 1 & Type 2 Diabetes Mellitus (Oral Hypoglycemics, SGLT2, DPP4, Insulins)
4. Chronic Respiratory Diseases (Asthma, COPD, Allergic Rhinitis)
5. Neurology, Epilepsy, Parkinson's, Dementia & Neuropathic Pain
6. Psychiatry & Mental Health (Depression, Anxiety, Bipolar, Schizophrenia)
7. Gastroenterology & Hepatology (GERD, Peptic Ulcers, IBS, IBD, Liver Disease)
8. Rheumatology & Chronic Joint Disease (Rheumatoid Arthritis, Osteoarthritis, Gout)
9. Nephrology & Urology (CKD, BPH, Kidney Stones, Acidosis)
10. Thyroid & Endocrine Disorders (Hypothyroidism, Hyperthyroidism)
11. Dermatology & Chronic Skin Conditions (Scabies, Eczema, Psoriasis, Fungal)
12. Ophthalmology & ENT (Glaucoma, Dry Eyes, Conjunctivitis)
13. Infectious Diseases & Antimicrobial Therapy (Antibiotics, Antivirals, Antifungals)
14. Analgesics, Antipyretics, Spasmolytics & Musculoskeletal Care
15. Hematinics, Vitamins, Minerals & Chronic Nutritional Deficiency
"""
import sys
import os
from datetime import date, timedelta
import random

# Ensure backend root on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.medicine import Medicine
from app.models.pharmacy import Pharmacy
from app.models.pharmacy_inventory import PharmacyInventory

# Tuple structure:
# (brand_name, generic_name, manufacturer, strength, dosage_form, prescription_required, description, mrp, selling_price)
REAL_INDIAN_MEDICINES = [
    # =========================================================================
    # 1. CARDIOVASCULAR, HYPERTENSION & NEUROVASCULAR (60 items)
    # =========================================================================
    ("Nemode 20", "Nimodipine", "Sun Pharma", "20 mg", "Capsule", True, "Cerebral calcium channel blocker used in neurological vascular conditions and stroke care.", 165.0, 142.0),
    ("Nimodip 30", "Nimodipine", "Torrent Pharmaceuticals", "30 mg", "Tablet", True, "Neurovascular protective calcium channel antagonist for subarachnoid hemorrhage.", 195.0, 170.0),
    ("Telma 20", "Telmisartan", "Glenmark Pharmaceuticals", "20 mg", "Tablet", True, "Angiotensin II receptor blocker for essential hypertension management.", 95.0, 82.0),
    ("Telma 40", "Telmisartan", "Glenmark Pharmaceuticals", "40 mg", "Tablet", True, "Primary first-line antihypertensive therapy for cardiovascular protection.", 148.0, 126.0),
    ("Telma 80", "Telmisartan", "Glenmark Pharmaceuticals", "80 mg", "Tablet", True, "High-strength ARB for severe hypertension and heart failure risk reduction.", 235.0, 205.0),
    ("Telma-AM 40/5", "Telmisartan + Amlodipine", "Glenmark Pharmaceuticals", "40 mg + 5 mg", "Tablet", True, "Synergistic ARB and calcium channel blocker combination for resistant hypertension.", 195.0, 168.0),
    ("Telma-AM 80/5", "Telmisartan + Amlodipine", "Glenmark Pharmaceuticals", "80 mg + 5 mg", "Tablet", True, "Dual mechanism combination for difficult-to-treat arterial hypertension.", 285.0, 245.0),
    ("Telma-H 40/12.5", "Telmisartan + Hydrochlorothiazide", "Glenmark Pharmaceuticals", "40 mg + 12.5 mg", "Tablet", True, "Antihypertensive combination with diuretic for high volume blood pressure control.", 185.0, 160.0),
    ("Telpres 40", "Telmisartan", "Abbott Healthcare", "40 mg", "Tablet", True, "Effective 24-hour blood pressure control with organ protection.", 135.0, 118.0),
    ("Cilacar 5", "Cilnidipine", "J.B. Chemicals", "5 mg", "Tablet", True, "L/N-type dual calcium channel blocker reducing proteinuria in hypertension.", 98.0, 84.0),
    ("Cilacar 10", "Cilnidipine", "J.B. Chemicals", "10 mg", "Tablet", True, "Renal-protective calcium channel blocker with minimal pedal edema side effects.", 165.0, 142.0),
    ("Cilacar 20", "Cilnidipine", "J.B. Chemicals", "20 mg", "Tablet", True, "Higher dose dual-acting calcium antagonist for resistant chronic hypertension.", 245.0, 212.0),
    ("Cilacar-T 10/40", "Cilnidipine + Telmisartan", "J.B. Chemicals", "10 mg + 40 mg", "Tablet", True, "Dual vascular relaxing agents for hypertensive patients with kidney disease.", 220.0, 190.0),
    ("Amlopres 2.5", "Amlodipine", "Cipla Ltd", "2.5 mg", "Tablet", True, "Low-dose dihydropyridine calcium channel blocker for mild hypertension.", 35.0, 29.0),
    ("Amlopres 5", "Amlodipine", "Cipla Ltd", "5 mg", "Tablet", True, "Gold-standard peripheral vasodilator for high blood pressure and chronic angina.", 58.0, 49.0),
    ("Amlopres 10", "Amlodipine", "Cipla Ltd", "10 mg", "Tablet", True, "High-potency calcium antagonist for sustained arterial pressure reduction.", 98.0, 84.0),
    ("Amlong 5", "Amlodipine", "Micro Labs Ltd", "5 mg", "Tablet", True, "Long-acting peripheral arterial calcium channel blocker.", 52.0, 44.0),
    ("Amlopres-AT 5/50", "Amlodipine + Atenolol", "Cipla Ltd", "5 mg + 50 mg", "Tablet", True, "Effective dual blocker reducing both peripheral resistance and cardiac workload.", 115.0, 98.0),
    ("Metolar 25", "Metoprolol Succinate", "Cipla Ltd", "25 mg", "Tablet", True, "Cardioselective beta-1 blocker for angina, hypertension and heart rate control.", 95.0, 81.0),
    ("Metolar 50", "Metoprolol Succinate", "Cipla Ltd", "50 mg", "Tablet", True, "Long-acting beta blocker reducing myocardial oxygen demand.", 155.0, 132.0),
    ("Metolar-XR 25", "Metoprolol Succinate Extended Release", "Cipla Ltd", "25 mg", "Tablet", True, "24-hour sustained release beta blocker for post-myocardial infarction care.", 110.0, 94.0),
    ("Metolar-XR 50", "Metoprolol Succinate Extended Release", "Cipla Ltd", "50 mg", "Tablet", True, "Extended release beta-1 receptor antagonist for congestive heart failure.", 175.0, 150.0),
    ("Betaloc 25", "Metoprolol Tartrate", "AstraZeneca", "25 mg", "Tablet", True, "Cardioprotective beta blocker for tachycardia and secondary prevention.", 88.0, 76.0),
    ("Betaloc 50", "Metoprolol Tartrate", "AstraZeneca", "50 mg", "Tablet", True, "Rapid-acting beta blocker for rate control and hypertension.", 145.0, 124.0),
    ("Seloken XL 25", "Metoprolol Succinate", "AstraZeneca", "25 mg", "Tablet", True, "Premium sustained release beta-1 blocker for cardiac longevity.", 125.0, 108.0),
    ("Nebicard 2.5", "Nebivolol", "Torrent Pharmaceuticals", "2.5 mg", "Tablet", True, "Third-generation beta blocker with nitric oxide-mediated vasodilation.", 115.0, 98.0),
    ("Nebicard 5", "Nebivolol", "Torrent Pharmaceuticals", "5 mg", "Tablet", True, "Cardiovascular vasodilator beta blocker without erectile adverse effects.", 195.0, 168.0),
    ("Cardivas 3.125", "Carvedilol", "Sun Pharma", "3.125 mg", "Tablet", True, "Non-selective beta and alpha-1 blocker for initiating heart failure therapy.", 55.0, 46.0),
    ("Cardivas 6.25", "Carvedilol", "Sun Pharma", "6.25 mg", "Tablet", True, "Mortality-reducing vasodilating beta blocker for dilated cardiomyopathy.", 85.0, 72.0),
    ("Cardivas 12.5", "Carvedilol", "Sun Pharma", "12.5 mg", "Tablet", True, "Optimal maintenance therapy for chronic heart failure and ischemic heart disease.", 140.0, 120.0),
    ("Cardivas 25", "Carvedilol", "Sun Pharma", "25 mg", "Tablet", True, "Target dosage for maximum left ventricular remodeling protection.", 225.0, 192.0),
    ("Carca 6.25", "Carvedilol", "Intas Pharmaceuticals", "6.25 mg", "Tablet", True, "Dual alpha/beta adrenergic antagonist for congestive cardiac failure.", 78.0, 66.0),
    ("Concor 2.5", "Bisoprolol Fumarate", "Merck", "2.5 mg", "Tablet", True, "Highly selective beta-1 adrenoceptor blocker for chronic heart failure.", 85.0, 72.0),
    ("Concor 5", "Bisoprolol Fumarate", "Merck", "5 mg", "Tablet", True, "Target dose for stable symptomatic chronic systolic heart failure.", 145.0, 125.0),
    ("Aten 25", "Atenolol", "Zydus Lifesciences", "25 mg", "Tablet", True, "Hydrophilic cardioselective beta blocker for stress-induced tachycardia.", 38.0, 31.0),
    ("Aten 50", "Atenolol", "Zydus Lifesciences", "50 mg", "Tablet", True, "Standard dose beta blocker for high blood pressure and angina prophylaxis.", 65.0, 54.0),
    ("Olmat 20", "Olmesartan Medoxomil", "Micro Labs Ltd", "20 mg", "Tablet", True, "Potent long-lasting angiotensin receptor blocker for metabolic hypertension.", 160.0, 138.0),
    ("Olmat 40", "Olmesartan Medoxomil", "Micro Labs Ltd", "40 mg", "Tablet", True, "High efficacy ARB for rigorous 24-hour blood pressure targets.", 265.0, 228.0),
    ("Olmezest 20", "Olmesartan Medoxomil", "Sun Pharma", "20 mg", "Tablet", True, "Vascular smooth muscle relaxant blocking AT1 receptors.", 155.0, 132.0),
    ("Losar 25", "Losartan Potassium", "Unichem Laboratories", "25 mg", "Tablet", True, "First ARB reducing hyperuricemia and protecting renal perfusion.", 65.0, 55.0),
    ("Losar 50", "Losartan Potassium", "Unichem Laboratories", "50 mg", "Tablet", True, "Standard nephroprotective antihypertensive for diabetic nephropathy.", 115.0, 98.0),
    ("Losar-H 50/12.5", "Losartan + Hydrochlorothiazide", "Unichem Laboratories", "50 mg + 12.5 mg", "Tablet", True, "Synergistic ARB and thiazide diuretic for fluid-dependent hypertension.", 145.0, 124.0),
    ("Cardace 2.5", "Ramipril", "Sanofi India", "2.5 mg", "Tablet", True, "ACE inhibitor providing tissue-level cardiac remodeling protection.", 75.0, 64.0),
    ("Cardace 5", "Ramipril", "Sanofi India", "5 mg", "Tablet", True, "Cardiovascular mortality-reducing ACE inhibitor proven in HOPE trial.", 135.0, 116.0),
    ("Cardace 10", "Ramipril", "Sanofi India", "10 mg", "Tablet", True, "Target maintenance dose for post-MI and diabetic vascular complications.", 225.0, 194.0),
    ("Envas 5", "Enalapril Maleate", "Cadila Pharmaceuticals", "5 mg", "Tablet", True, "Classic ACE inhibitor for essential and renovascular hypertension.", 48.0, 40.0),
    ("Envas 10", "Enalapril Maleate", "Cadila Pharmaceuticals", "10 mg", "Tablet", True, "Effective afterload reducer in congestive cardiac failure.", 85.0, 72.0),
    ("Aquazide 12.5", "Hydrochlorothiazide", "Sun Pharma", "12.5 mg", "Tablet", True, "Thiazide diuretic reducing plasma volume in isolated systolic hypertension.", 45.0, 38.0),
    ("Lasix 40", "Furosemide", "Sanofi India", "40 mg", "Tablet", True, "Potent loop diuretic relieving acute and chronic pulmonary edema and fluid overload.", 18.0, 15.0),
    ("Dytor 10", "Torsemide", "Cipla Ltd", "10 mg", "Tablet", True, "High bioavailability loop diuretic with anti-aldosteronergic properties.", 78.0, 66.0),
    ("Dytor 20", "Torsemide", "Cipla Ltd", "20 mg", "Tablet", True, "Reliable diuresis for advanced heart failure and renal insufficiency.", 125.0, 106.0),
    ("Dytor Plus 10/50", "Torsemide + Spironolactone", "Cipla Ltd", "10 mg + 50 mg", "Tablet", True, "Balanced potassium-sparing and loop diuretic combination for ascites & CHF.", 165.0, 142.0),
    ("Aldactone 25", "Spironolactone", "RPG Life Sciences", "25 mg", "Tablet", True, "Mineralocorticoid receptor antagonist preventing cardiac fibrosis.", 48.0, 41.0),
    ("Aldactone 50", "Spironolactone", "RPG Life Sciences", "50 mg", "Tablet", True, "Potassium-sparing diuretic for primary hyperaldosteronism and edema.", 85.0, 72.0),
    ("Lanoxin 0.25", "Digoxin", "GSK India", "0.25 mg", "Tablet", True, "Cardiac glycoside strengthening myocardial contractility in atrial fibrillation.", 22.0, 18.0),
    ("Sorbitrate 5", "Isosorbide Dinitrate", "Abbott Healthcare", "5 mg", "Tablet", True, "Sublingual fast-acting nitrate for acute relief of angina pectoris attacks.", 35.0, 29.0),
    ("Sorbitrate 10", "Isosorbide Dinitrate", "Abbott Healthcare", "10 mg", "Tablet", True, "Coronary vasodilator reducing cardiac pre-load in coronary artery disease.", 48.0, 40.0),
    ("Monotrate 20", "Isosorbide Mononitrate", "Sun Pharma", "20 mg", "Tablet", True, "Active metabolite nitrate for long-term prophylaxis of angina pectoris.", 72.0, 61.0),
    ("Monotrate OD 50", "Isosorbide Mononitrate Extended Release", "Sun Pharma", "50 mg", "Tablet", True, "Once-daily extended release coronary nitrate preventing nitrate tolerance.", 165.0, 142.0),
    ("Angispan-TR 2.5", "Nitroglycerin", "USV Ltd", "2.5 mg", "Capsule", True, "Sustained release venodilator for round-the-clock prevention of angina spasms.", 185.0, 158.0),

    # =========================================================================
    # 2. DYSLIPIDEMIA, HYPERCHOLESTEROLEMIA & ANTICOAGULANTS (35 items)
    # =========================================================================
    ("Atorva 10", "Atorvastatin", "Zydus Lifesciences", "10 mg", "Tablet", True, "HMG-CoA reductase inhibitor lowering bad LDL cholesterol and triglycerides.", 110.0, 94.0),
    ("Atorva 20", "Atorvastatin", "Zydus Lifesciences", "20 mg", "Tablet", True, "Moderate-intensity statin therapy for atherosclerotic risk prevention.", 195.0, 168.0),
    ("Atorva 40", "Atorvastatin", "Zydus Lifesciences", "40 mg", "Tablet", True, "High-intensity statin for post-angioplasty and high-risk cardiac patients.", 310.0, 268.0),
    ("Storvas 10", "Atorvastatin", "Sun Pharma", "10 mg", "Tablet", True, "Plaque-stabilizing lipid regulator preventing cardiovascular events.", 115.0, 98.0),
    ("Storvas 20", "Atorvastatin", "Sun Pharma", "20 mg", "Tablet", True, "Proven LDL reduction for primary and secondary cardiovascular prophylaxis.", 205.0, 175.0),
    ("Rosuvas 5", "Rosuvastatin", "Sun Pharma", "5 mg", "Tablet", True, "Potent hydrophilic statin for dyslipidemia with high tolerability.", 125.0, 108.0),
    ("Rosuvas 10", "Rosuvastatin", "Sun Pharma", "10 mg", "Tablet", True, "High-efficacy statin delivering dramatic LDL reduction and HDL boost.", 215.0, 185.0),
    ("Rosuvas 20", "Rosuvastatin", "Sun Pharma", "20 mg", "Tablet", True, "Intensive lipid lowering for familial hypercholesterolemia and vascular disease.", 365.0, 315.0),
    ("Rosave 10", "Rosuvastatin", "Alembic Pharmaceuticals", "10 mg", "Tablet", True, "Premium statin formulation optimizing lipid panels and arterial health.", 198.0, 170.0),
    ("Rosuvas-F 10/160", "Rosuvastatin + Fenofibrate", "Sun Pharma", "10 mg + 160 mg", "Tablet", True, "Dual mechanism lipid regulator for mixed dyslipidemia and high triglycerides.", 295.0, 255.0),
    ("Lipicard 160", "Fenofibrate", "USV Ltd", "160 mg", "Tablet", True, "PPAR-alpha agonist specifically targeting dangerous elevated triglyceride levels.", 185.0, 158.0),
    ("Stanlip 145", "Fenofibrate Micronized", "Sun Pharma", "145 mg", "Tablet", True, "Nanoparticle micronized fenofibrate for optimal gastrointestinal absorption.", 210.0, 180.0),
    ("Lipaglyn 4", "Saroglitazar", "Zydus Lifesciences", "4 mg", "Tablet", True, "World's first dual PPAR agonist for diabetic dyslipidemia and NASH/fatty liver.", 385.0, 335.0),
    ("Ecosprin 75", "Aspirin", "USV Ltd", "75 mg", "Tablet", True, "Enteric-coated low-dose antiplatelet protecting against clot formation.", 18.5, 15.5),
    ("Ecosprin 150", "Aspirin", "USV Ltd", "150 mg", "Tablet", True, "Cardioprotective antiplatelet for secondary prevention after ischemic stroke.", 26.0, 22.0),
    ("Ecosprin-AV 75/10", "Aspirin + Atorvastatin", "USV Ltd", "75 mg + 10 mg", "Capsule", True, "Single pill combination for comprehensive vascular and plaque thrombosis protection.", 85.0, 72.0),
    ("Ecosprin-AV 75/20", "Aspirin + Atorvastatin", "USV Ltd", "75 mg + 20 mg", "Capsule", True, "Intensive secondary prevention combination for post-coronary stenting.", 135.0, 116.0),
    ("Clopilet 75", "Clopidogrel", "Sun Pharma", "75 mg", "Tablet", True, "P2Y12 platelet inhibitor preventing thrombosis in acute coronary syndrome.", 115.0, 98.0),
    ("Deplatt 75", "Clopidogrel", "Torrent Pharmaceuticals", "75 mg", "Tablet", True, "Potent antiplatelet therapy for peripheral vascular and coronary diseases.", 108.0, 92.0),
    ("Clopilet-A 75/75", "Clopidogrel + Aspirin", "Sun Pharma", "75 mg + 75 mg", "Capsule", True, "Dual antiplatelet therapy (DAPT) protocol post-percutaneous coronary intervention.", 155.0, 132.0),
    ("Brilinta 60", "Ticagrelor", "AstraZeneca", "60 mg", "Tablet", True, "Direct-acting reversible P2Y12 inhibitor for extended post-MI protection.", 680.0, 595.0),
    ("Brilinta 90", "Ticagrelor", "AstraZeneca", "90 mg", "Tablet", True, "Standard acute coronary syndrome antiplatelet with superior mortality benefits.", 950.0, 835.0),
    ("Eliquis 2.5", "Apixaban", "Pfizer", "2.5 mg", "Tablet", True, "Novel oral anticoagulant (NOAC) preventing stroke in non-valvular atrial fibrillation.", 850.0, 745.0),
    ("Eliquis 5", "Apixaban", "Pfizer", "5 mg", "Tablet", True, "Direct factor Xa inhibitor for deep vein thrombosis and pulmonary embolism treatment.", 1450.0, 1275.0),
    ("Xarelto 10", "Rivaroxaban", "Bayer", "10 mg", "Tablet", True, "Once-daily direct factor Xa inhibitor for DVT prophylaxis in major surgery.", 1250.0, 1090.0),
    ("Xarelto 15", "Rivaroxaban", "Bayer", "15 mg", "Tablet", True, "Target anticoagulation therapy during initial acute venous thromboembolism.", 1680.0, 1475.0),
    ("Xarelto 20", "Rivaroxaban", "Bayer", "20 mg", "Tablet", True, "Once-daily long-term stroke prevention in chronic atrial fibrillation.", 1950.0, 1720.0),
    ("Pradaxa 110", "Dabigatran Etexilate", "Boehringer Ingelheim", "110 mg", "Capsule", True, "Direct thrombin inhibitor with lower major bleeding rates than warfarin.", 1550.0, 1360.0),
    ("Pradaxa 150", "Dabigatran Etexilate", "Boehringer Ingelheim", "150 mg", "Capsule", True, "Full-dose direct oral anticoagulant for high-risk cardioembolic stroke.", 1850.0, 1625.0),
    ("Warf 1", "Warfarin Sodium", "Cipla Ltd", "1 mg", "Tablet", True, "Vitamin K antagonist for mechanical prosthetic heart valves.", 35.0, 29.0),
    ("Warf 2", "Warfarin Sodium", "Cipla Ltd", "2 mg", "Tablet", True, "Anticoagulant requiring INR monitoring for venous thrombosis prophylaxis.", 52.0, 44.0),
    ("Warf 5", "Warfarin Sodium", "Cipla Ltd", "5 mg", "Tablet", True, "Standard dose vitamin K antagonist for severe thromboembolic disorders.", 85.0, 72.0),
    ("Acitrom 1", "Nicoumalone / Acenocoumarol", "Abbott Healthcare", "1 mg", "Tablet", True, "Preferred oral coumarin anticoagulant with reliable hepatic clearance.", 125.0, 108.0),
    ("Acitrom 2", "Nicoumalone / Acenocoumarol", "Abbott Healthcare", "2 mg", "Tablet", True, "Precise INR control anticoagulant for rheumatic heart disease and valves.", 195.0, 168.0),
    ("Acitrom 3", "Nicoumalone / Acenocoumarol", "Abbott Healthcare", "3 mg", "Tablet", True, "Target dose oral anticoagulant for systemic thromboembolism prevention.", 265.0, 230.0),

    # =========================================================================
    # 3. TYPE 1 & TYPE 2 DIABETES MELLITUS & ENDOCRINE (55 items)
    # =========================================================================
    ("Glycomet 500", "Metformin Hydrochloride", "USV Ltd", "500 mg", "Tablet", True, "Foundational first-line biguanide improving insulin sensitivity.", 38.0, 32.0),
    ("Glycomet 850", "Metformin Hydrochloride", "USV Ltd", "850 mg", "Tablet", True, "Optimized dose biguanide reducing hepatic glucose production.", 55.0, 46.0),
    ("Glycomet 1000", "Metformin Hydrochloride", "USV Ltd", "1000 mg", "Tablet", True, "Maximum strength metformin for monotherapy glycemic target attainment.", 72.0, 61.0),
    ("Glycomet-SR 500", "Metformin Sustained Release", "USV Ltd", "500 mg", "Tablet", True, "Extended release matrix minimizing GI distress and diarrhea.", 48.0, 41.0),
    ("Glycomet-SR 850", "Metformin Sustained Release", "USV Ltd", "850 mg", "Tablet", True, "Sustained night-time and morning glucose control formulation.", 68.0, 58.0),
    ("Glycomet-SR 1000", "Metformin Sustained Release", "USV Ltd", "1000 mg", "Tablet", True, "High-dose sustained release biguanide for twice-daily or once-daily regimens.", 88.0, 75.0),
    ("Glyciphage 500", "Metformin", "Franco-Indian Pharmaceuticals", "500 mg", "Tablet", True, "Proven biguanide for newly diagnosed Type 2 diabetes and PCOS.", 35.0, 29.0),
    ("Amaryl 1", "Glimepiride", "Sanofi India", "1 mg", "Tablet", True, "Second-generation sulfonylurea stimulating physiologic insulin secretion.", 85.0, 72.0),
    ("Amaryl 2", "Glimepiride", "Sanofi India", "2 mg", "Tablet", True, "Standard potency beta-cell insulin secretagogue for glycemic control.", 145.0, 124.0),
    ("Amaryl 3", "Glimepiride", "Sanofi India", "3 mg", "Tablet", True, "Higher dose sulfonylurea for uncontrolled hyperglycemia.", 195.0, 168.0),
    ("Amaryl 4", "Glimepiride", "Sanofi India", "4 mg", "Tablet", True, "Maximum strength glimepiride for resistant diabetic hyperglycemia.", 245.0, 212.0),
    ("Glimisave 1", "Glimepiride", "Eris Lifesciences", "1 mg", "Tablet", True, "Pancreatic insulin secretagogue with lower risk of hypoglycemia.", 65.0, 55.0),
    ("Glimisave 2", "Glimepiride", "Eris Lifesciences", "2 mg", "Tablet", True, "Effective oral hypoglycemic agent for adult-onset diabetes.", 115.0, 98.0),
    ("Glycomet-GP 1", "Metformin + Glimepiride", "USV Ltd", "500 mg + 1 mg", "Tablet", True, "Classic synergistic dual combination targeting both insulin secretion and resistance.", 115.0, 98.0),
    ("Glycomet-GP 2", "Metformin + Glimepiride", "USV Ltd", "500 mg + 2 mg", "Tablet", True, "Most widely prescribed dual antidiabetic oral therapy across India.", 155.0, 132.0),
    ("Glycomet-GP 1 Forte", "Metformin + Glimepiride", "USV Ltd", "1000 mg + 1 mg", "Tablet", True, "Enhanced metformin dose combination for insulin-resistant individuals.", 145.0, 124.0),
    ("Glycomet-GP 2 Forte", "Metformin + Glimepiride", "USV Ltd", "1000 mg + 2 mg", "Tablet", True, "Intensive dual oral combination for advanced Type 2 diabetes.", 185.0, 158.0),
    ("Diamicron 30 MR", "Gliclazide Modified Release", "Serdia Pharmaceuticals", "30 mg", "Tablet", True, "Cardioprotective sulfonylurea with superior endothelial restoration properties.", 145.0, 124.0),
    ("Diamicron 60 MR", "Gliclazide Modified Release", "Serdia Pharmaceuticals", "60 mg", "Tablet", True, "Once-daily modified release gliclazide offering steady 24-hr insulin release.", 265.0, 230.0),
    ("Reclimet", "Gliclazide + Metformin", "Cadila Pharmaceuticals", "80 mg + 500 mg", "Tablet", True, "Dual oral agent for patients requiring beta-cell stimulation and glucose uptake.", 120.0, 102.0),
    ("Januvia 50", "Sitagliptin", "MSD India", "50 mg", "Tablet", True, "DPP-4 inhibitor enhancing incretin hormones without inducing hypoglycemia.", 245.0, 212.0),
    ("Januvia 100", "Sitagliptin", "MSD India", "100 mg", "Tablet", True, "Once-daily weight-neutral DPP-4 inhibitor providing safe HbA1c reductions.", 420.0, 365.0),
    ("Janumet 50/500", "Sitagliptin + Metformin", "MSD India", "50 mg + 500 mg", "Tablet", True, "Incretin enhancer plus insulin sensitizer for superior postprandial control.", 325.0, 280.0),
    ("Janumet 50/1000", "Sitagliptin + Metformin", "MSD India", "50 mg + 1000 mg", "Tablet", True, "High-strength combination improving fasting and mealtime glycemic excursions.", 395.0, 345.0),
    ("Galvus 50", "Vildagliptin", "Novartis", "50 mg", "Tablet", True, "Potent selective DPP-4 inhibitor preserving pancreatic islet architecture.", 215.0, 185.0),
    ("Galvus Met 50/500", "Vildagliptin + Metformin", "Novartis", "50 mg + 500 mg", "Tablet", True, "Twice-daily incretin combination for robust glycemic control.", 285.0, 245.0),
    ("Galvus Met 50/1000", "Vildagliptin + Metformin", "Novartis", "50 mg + 1000 mg", "Tablet", True, "Full-strength DPP-4 plus biguanide combination tablet.", 365.0, 315.0),
    ("Zita 20", "Teneligliptin", "Glenmark Pharmaceuticals", "20 mg", "Tablet", True, "Affordable third-generation DPP-4 inhibitor safe in mild-to-severe renal impairment.", 135.0, 116.0),
    ("Tenlimac 20", "Teneligliptin", "Macleods Pharmaceuticals", "20 mg", "Tablet", True, "Once-daily incretin agent suitable for diabetic CKD patients.", 115.0, 98.0),
    ("Tenali-M 20/500", "Teneligliptin + Metformin", "Torrent Pharmaceuticals", "20 mg + 500 mg", "Tablet", True, "Cost-effective fixed-dose combination improving overall glycemic variability.", 165.0, 142.0),
    ("Trajenta 5", "Linagliptin", "Boehringer Ingelheim", "5 mg", "Tablet", True, "Biliary-excreted DPP-4 inhibitor requiring zero dose adjustments in renal failure.", 540.0, 475.0),
    ("Trajenta Duo 2.5/500", "Linagliptin + Metformin", "Boehringer Ingelheim", "2.5 mg + 500 mg", "Tablet", True, "Fixed combination offering renal safety with comprehensive glucose lowering.", 410.0, 360.0),
    ("Forxiga 5", "Dapagliflozin", "AstraZeneca", "5 mg", "Tablet", True, "SGLT2 inhibitor inducing urinary glucose excretion and promoting weight loss.", 315.0, 275.0),
    ("Forxiga 10", "Dapagliflozin", "AstraZeneca", "10 mg", "Tablet", True, "Cardio-renal protective SGLT2 inhibitor reducing heart failure hospitalizations.", 495.0, 435.0),
    ("Oxra 10", "Dapagliflozin", "Sun Pharma", "10 mg", "Tablet", True, "Proven SGLT2 antagonist lowering blood pressure, glucose and renal decline.", 385.0, 335.0),
    ("Oxra-M 10/500", "Dapagliflozin + Metformin", "Sun Pharma", "10 mg + 500 mg", "Tablet", True, "Glycosuric agent combined with insulin sensitizer for obese diabetic patients.", 345.0, 300.0),
    ("Jardiance 10", "Empagliflozin", "Boehringer Ingelheim", "10 mg", "Tablet", True, "Cardiovascular death reducing SGLT2 inhibitor proven in EMPA-REG outcome trial.", 525.0, 460.0),
    ("Jardiance 25", "Empagliflozin", "Boehringer Ingelheim", "25 mg", "Tablet", True, "High-dose empagliflozin for intensive glycemic and systolic pressure control.", 680.0, 595.0),
    ("Jardiance Met 12.5/500", "Empagliflozin + Metformin", "Boehringer Ingelheim", "12.5 mg + 500 mg", "Tablet", True, "Synergistic renal glucose filtration and hepatic glucose suppression.", 485.0, 425.0),
    ("Pioz 15", "Pioglitazone", "USV Ltd", "15 mg", "Tablet", True, "Thiazolidinedione PPAR-gamma agonist addressing severe peripheral insulin resistance.", 85.0, 72.0),
    ("Pioz 30", "Pioglitazone", "USV Ltd", "30 mg", "Tablet", True, "Potent insulin sensitizer lowering free fatty acids and fasting glycemia.", 145.0, 124.0),
    ("Volibo 0.2", "Voglibose", "Sun Pharma", "0.2 mg", "Tablet", True, "Alpha-glucosidase inhibitor delaying carbohydrate digestion for postprandial spikes.", 98.0, 84.0),
    ("Volibo 0.3", "Voglibose", "Sun Pharma", "0.3 mg", "Tablet", True, "Higher strength enzyme blocker for carbohydrate-heavy South Asian diets.", 145.0, 124.0),
    ("Glucobay 50", "Acarbose", "Bayer", "50 mg", "Tablet", True, "Intestinal alpha-glucosidase inhibitor preventing postprandial hyperglycemia.", 195.0, 168.0),
    ("Rybelsus 3", "Semaglutide", "Novo Nordisk", "3 mg", "Tablet", True, "World's first oral GLP-1 receptor agonist initiation dose for diabetes and weight loss.", 3150.0, 2800.0),
    ("Rybelsus 7", "Semaglutide", "Novo Nordisk", "7 mg", "Tablet", True, "Maintenance GLP-1 therapy delivering exceptional HbA1c and weight reduction.", 3450.0, 3050.0),
    ("Rybelsus 14", "Semaglutide", "Novo Nordisk", "14 mg", "Tablet", True, "Maximum strength oral semaglutide for intensive glycemic transformation.", 3850.0, 3400.0),
    ("Human Mixtard 30/70", "Biphasic Isophane Insulin", "Novo Nordisk", "100 IU/ml", "Injection", True, "Pre-mixed human insulin supplying both basal and mealtime bolus control.", 185.0, 162.0),
    ("Human Mixtard 40 IU", "Biphasic Isophane Insulin", "Novo Nordisk", "40 IU/ml", "Injection", True, "Traditional 40 IU vial for insulin syringe administration.", 155.0, 136.0),
    ("Lantus 100 IU", "Insulin Glargine", "Sanofi India", "100 IU/ml", "Injection", True, "Peakless 24-hour long-acting basal insulin analogue mimicking physiologic basal state.", 685.0, 605.0),
    ("Basalog 100 IU", "Insulin Glargine", "Biocon", "100 IU/ml", "Injection", True, "Affordable biosimilar basal insulin glargine providing smooth continuous control.", 495.0, 435.0),
    ("Novorapid 100 IU", "Insulin Aspart", "Novo Nordisk", "100 IU/ml", "Injection", True, "Ultra-fast acting mealtime insulin analogue curbing immediate postprandial glucose.", 745.0, 655.0),
    ("Humalog 100 IU", "Insulin Lispro", "Eli Lilly", "100 IU/ml", "Injection", True, "Rapid-acting prandial insulin analogue taken immediately before meals.", 715.0, 630.0),
    ("Tresiba 100 IU", "Insulin Degludec", "Novo Nordisk", "100 IU/ml", "Injection", True, "Ultra-long acting basal insulin with beyond 42-hour duration and minimal nocturnal lows.", 1250.0, 1100.0),
    ("Eglucent 100 IU", "Insulin Lispro", "Sanofi India", "100 IU/ml", "Injection", True, "Biosimilar rapid mealtime insulin for Type 1 and advanced Type 2 diabetes.", 540.0, 475.0),

    # =========================================================================
    # 4. CHRONIC RESPIRATORY DISEASES: ASTHMA & COPD (45 items)
    # =========================================================================
    ("Asthalin Inhaler", "Salbutamol", "Cipla Ltd", "100 mcg/puff", "Inhaler", True, "Emergency fast-acting rescue bronchodilator for acute wheezing and asthma attacks.", 165.0, 142.0),
    ("Asthalin Respules 2.5", "Salbutamol Respirator Solution", "Cipla Ltd", "2.5 mg / 2.5 ml", "Respules", True, "Nebulization solution for acute exacerbations of asthma and severe COPD.", 72.0, 61.0),
    ("Asthalin Syrup", "Salbutamol", "Cipla Ltd", "2 mg / 5 ml", "Syrup", True, "Oral bronchodilator syrup for pediatric bronchospasm and wheezy bronchitis.", 35.0, 29.0),
    ("Asthalin 4", "Salbutamol", "Cipla Ltd", "4 mg", "Tablet", True, "Oral beta-2 agonist tablet for maintenance airway dilation.", 28.0, 23.0),
    ("Budecort 100", "Budesonide", "Cipla Ltd", "100 mcg", "Inhaler", True, "Low-dose inhaled corticosteroid for mild persistent childhood and adult asthma.", 245.0, 212.0),
    ("Budecort 200", "Budesonide", "Cipla Ltd", "200 mcg", "Inhaler", True, "Maintenance anti-inflammatory steroid inhaler suppressing chronic airway swelling.", 335.0, 290.0),
    ("Budecort 400", "Budesonide", "Cipla Ltd", "400 mcg", "Inhaler", True, "High-strength inhaled corticosteroid for severe persistent chronic asthma.", 465.0, 405.0),
    ("Budecort Respules 0.5", "Budesonide", "Cipla Ltd", "0.5 mg / 2 ml", "Respules", True, "Nebulized steroid suspension for acute croup, pediatric asthma and flare-ups.", 145.0, 125.0),
    ("Budecort Respules 1.0", "Budesonide", "Cipla Ltd", "1.0 mg / 2 ml", "Respules", True, "High-potency nebulized corticosteroid relieving severe bronchial mucosal edema.", 195.0, 168.0),
    ("Foracort 100", "Formoterol + Budesonide", "Cipla Ltd", "6 mcg + 100 mcg", "Inhaler", True, "Combination LABA and ICS for maintenance and reliever therapy (SMART).", 345.0, 300.0),
    ("Foracort 200", "Formoterol + Budesonide", "Cipla Ltd", "6 mcg + 200 mcg", "Inhaler", True, "India's leading dual asthma inhaler preventing exacerbations.", 465.0, 405.0),
    ("Foracort 400", "Formoterol + Budesonide", "Cipla Ltd", "6 mcg + 400 mcg", "Inhaler", True, "High-dose combination therapy for severe persistent asthma and advanced COPD.", 585.0, 510.0),
    ("Foracort 200 Rotacaps", "Formoterol + Budesonide", "Cipla Ltd", "6 mcg + 200 mcg", "Capsule", True, "Dry powder inhaler capsules for breath-actuated pulmonary delivery.", 225.0, 195.0),
    ("Foracort 400 Rotacaps", "Formoterol + Budesonide", "Cipla Ltd", "6 mcg + 400 mcg", "Capsule", True, "High-strength dry powder capsules for Rotahaler administration.", 295.0, 258.0),
    ("Seroflo 125", "Salmeterol + Fluticasone Propionate", "Cipla Ltd", "25 mcg + 125 mcg", "Inhaler", True, "Long-acting beta-2 agonist plus potent corticosteroid for stable airway control.", 445.0, 388.0),
    ("Seroflo 250", "Salmeterol + Fluticasone Propionate", "Cipla Ltd", "25 mcg + 250 mcg", "Inhaler", True, "Maintenance inhaler reducing frequency of nocturnal asthma symptoms.", 565.0, 495.0),
    ("Seroflo 250 Rotacaps", "Salmeterol + Fluticasone", "Cipla Ltd", "50 mcg + 250 mcg", "Capsule", True, "Dry powder capsules preventing exercise-induced and chronic bronchospasm.", 285.0, 248.0),
    ("Duolin Inhaler", "Levosalbutamol + Ipratropium", "Cipla Ltd", "50 mcg + 20 mcg", "Inhaler", True, "Dual bronchodilator relaxing smooth muscle via adrenergic and anticholinergic paths.", 365.0, 318.0),
    ("Duolin Respules", "Levosalbutamol + Ipratropium", "Cipla Ltd", "1.25 mg + 500 mcg", "Respules", True, "First-choice nebulization liquid for acute respiratory distress and COPD attacks.", 125.0, 108.0),
    ("Duolin Rotacaps", "Levosalbutamol + Ipratropium", "Cipla Ltd", "100 mcg + 40 mcg", "Capsule", True, "Dry powder combo capsules relieving chronic breathlessness in COPD.", 165.0, 142.0),
    ("Tiova Inhaler", "Tiotropium Bromide", "Cipla Ltd", "9 mcg", "Inhaler", True, "Long-acting muscarinic antagonist (LAMA) delivering 24-hr bronchodilation in COPD.", 485.0, 425.0),
    ("Tiova Rotacaps", "Tiotropium Bromide", "Cipla Ltd", "18 mcg", "Capsule", True, "Once-daily dry powder inhalation capsules improving lung capacity in emphysema.", 265.0, 230.0),
    ("Spiriva 18 mcg", "Tiotropium", "Boehringer Ingelheim", "18 mcg", "Capsule", True, "Gold-standard LAMA reducing hospital admissions in chronic bronchitis.", 650.0, 570.0),
    ("Montair 10", "Montelukast", "Cipla Ltd", "10 mg", "Tablet", True, "Leukotriene receptor antagonist blocking inflammatory mediators in allergic asthma.", 195.0, 168.0),
    ("Montair-LC", "Montelukast + Levocetirizine", "Cipla Ltd", "10 mg + 5 mg", "Tablet", True, "Best-selling anti-allergic combination for allergic rhinitis, sneezing and asthma.", 235.0, 204.0),
    ("Telekast-L", "Montelukast + Levocetirizine", "Lupin Ltd", "10 mg + 5 mg", "Tablet", True, "Comprehensive relief from perennial allergic rhinitis and nocturnal cough.", 215.0, 185.0),
    ("Montek-LC", "Montelukast + Levocetirizine", "Sun Pharma", "10 mg + 5 mg", "Tablet", True, "Dual anti-leukotriene and antihistamine formulation for seasonal allergies.", 220.0, 190.0),
    ("Bilashine 20", "Bilastine", "Sun Pharma", "20 mg", "Tablet", True, "Next-generation non-sedating antihistamine for urticaria and allergic rhinitis.", 185.0, 160.0),
    ("Bilaxten 20", "Bilastine", "Menarini India", "20 mg", "Tablet", True, "Rapid-acting non-drowsy anti-allergic agent with zero cardiac toxicity.", 220.0, 192.0),
    ("Allegra 120", "Fexofenadine", "Sanofi India", "120 mg", "Tablet", True, "Pure non-sedating second-generation antihistamine for seasonal hay fever.", 180.0, 155.0),
    ("Allegra 180", "Fexofenadine", "Sanofi India", "180 mg", "Tablet", True, "Maximum strength antihistamine for chronic idiopathic urticaria and skin hives.", 255.0, 222.0),
    ("Zyrtec 10", "Cetirizine Hydrochloride", "Dr. Reddy's", "10 mg", "Tablet", False, "Fast relief from allergic runny nose, itchy throat and watery eyes.", 45.0, 38.0),
    ("Cetzine 10", "Cetirizine", "GSK India", "10 mg", "Tablet", False, "Classic trusted antihistamine for widespread allergic reactions and dermatitis.", 42.0, 35.0),
    ("Levocet 5", "Levocetirizine", "Hetero Healthcare", "5 mg", "Tablet", False, "Active enantiomer of cetirizine providing double potency with less drowsiness.", 58.0, 49.0),
    ("Teczine 5", "Levocetirizine", "Sun Pharma", "5 mg", "Tablet", False, "Pure R-enantiomer antihistamine for day and night allergy control.", 65.0, 55.0),
    ("Deriphyllin Retard 150", "Theophylline + Etofylline", "Zydus Lifesciences", "150 mg", "Tablet", True, "Sustained release methylxanthine bronchodilator for chronic asthma maintenance.", 32.0, 26.0),
    ("Deriphyllin Retard 300", "Theophylline + Etofylline", "Zydus Lifesciences", "300 mg", "Tablet", True, "High-strength xanthine bronchodilator reducing nocturnal airway tightness.", 55.0, 46.0),
    ("Doxovent 400", "Doxofylline", "Glenmark Pharmaceuticals", "400 mg", "Tablet", True, "Novel xanthine bronchodilator without the cardiac and gastric toxicity of theophylline.", 145.0, 124.0),
    ("Doxiflo 650", "Doxofylline Extended Release", "Lupin Ltd", "650 mg", "Tablet", True, "Once-daily extended release bronchodilator for chronic obstructive airway disease.", 215.0, 185.0),
    ("AB Phylline 100", "Acebrophylline", "Sun Pharma", "100 mg", "Capsule", True, "Dual mucoregulatory and anti-inflammatory airway agent liquefying tenacious phlegm.", 175.0, 152.0),
    ("Ascoril LS Syrup", "Levosalbutamol + Ambroxol + Guaifenesin", "Glenmark Pharmaceuticals", "100 ml", "Syrup", True, "Doctor-preferred expectorant syrup for chesty cough with bronchial congestion.", 125.0, 108.0),
    ("Grilinctus Syrup", "Dextromethorphan + Chlorpheniramine", "Indian Immunologicals", "100 ml", "Syrup", False, "Trusted soothing formula for dry hacking cough and throat irritation.", 118.0, 102.0),
    ("Benadryl DR Syrup", "Dextromethorphan", "Johnson & Johnson", "100 ml", "Syrup", False, "Fast-acting cough suppressant silencing irritating dry allergic coughs.", 130.0, 112.0),
    ("Flomist Nasal Spray", "Fluticasone Propionate", "Cipla Ltd", "50 mcg/dose", "Spray", True, "Targeted anti-inflammatory steroid spray for chronic allergic sinus and rhinitis.", 385.0, 335.0),
    ("Otrivin 0.1%", "Xylometazoline", "GSK India", "10 ml", "Drops", False, "Direct nasal decongestant relieving acute blocked nose within 2 minutes.", 85.0, 74.0),

    # =========================================================================
    # 5. NEUROLOGY, EPILEPSY, PARKINSON'S & CHRONIC PAIN (45 items)
    # =========================================================================
    ("Levipil 250", "Levetiracetam", "Sun Pharma", "250 mg", "Tablet", True, "Broad-spectrum modern antiepileptic drug for focal and generalized seizures.", 115.0, 98.0),
    ("Levipil 500", "Levetiracetam", "Sun Pharma", "500 mg", "Tablet", True, "First-choice anticonvulsant with excellent cognitive tolerability and zero drug interactions.", 215.0, 185.0),
    ("Levipil 750", "Levetiracetam", "Sun Pharma", "750 mg", "Tablet", True, "Higher dose antiepileptic therapy for refractory seizure syndromes.", 315.0, 275.0),
    ("Levipil 1000", "Levetiracetam", "Sun Pharma", "1000 mg", "Tablet", True, "Maximum strength anticonvulsant for severe epilepsy control.", 425.0, 370.0),
    ("Epilive 500", "Levetiracetam", "Lupin Ltd", "500 mg", "Tablet", True, "Reliable antiepileptic formulation controlling tonic-clonic convulsions.", 195.0, 168.0),
    ("Encorate Chrono 200", "Sodium Valproate + Valproic Acid", "Sun Pharma", "200 mg", "Tablet", True, "Controlled release broad-spectrum antiepileptic and mood stabilizer.", 85.0, 72.0),
    ("Encorate Chrono 300", "Sodium Valproate + Valproic Acid", "Sun Pharma", "300 mg", "Tablet", True, "Steady plasma concentration valproate preventing absence and myoclonic seizures.", 135.0, 116.0),
    ("Encorate Chrono 500", "Sodium Valproate + Valproic Acid", "Sun Pharma", "500 mg", "Tablet", True, "Gold-standard controlled release formulation for idiopathic generalized epilepsy.", 215.0, 185.0),
    ("Valparin Chrono 500", "Sodium Valproate + Valproic Acid", "Sanofi India", "500 mg", "Tablet", True, "Chrono delivery system minimizing peak-related tremors and sedation.", 235.0, 204.0),
    ("Tegrital 100", "Carbamazepine", "Novartis", "100 mg", "Tablet", True, "Pediatric and initial titration dose for trigeminal neuralgia and focal epilepsy.", 32.0, 27.0),
    ("Tegrital 200", "Carbamazepine", "Novartis", "200 mg", "Tablet", True, "First-line therapy for stabbing trigeminal neuralgia facial pain and seizures.", 55.0, 46.0),
    ("Tegrital CR 200", "Carbamazepine Controlled Release", "Novartis", "200 mg", "Tablet", True, "Smooth release carbamazepine reducing peak dizziness and diplopia.", 78.0, 66.0),
    ("Tegrital CR 400", "Carbamazepine Controlled Release", "Novartis", "400 mg", "Tablet", True, "High-strength controlled release formulation for severe neuralgic pain.", 145.0, 124.0),
    ("Oxitol 150", "Oxcarbazepine", "Sun Pharma", "150 mg", "Tablet", True, "Keto-analogue of carbamazepine with reduced hepatic enzyme induction.", 95.0, 81.0),
    ("Oxitol 300", "Oxcarbazepine", "Sun Pharma", "300 mg", "Tablet", True, "Well-tolerated sodium channel blocker for partial-onset epileptic seizures.", 185.0, 158.0),
    ("Oxitol 600", "Oxcarbazepine", "Sun Pharma", "600 mg", "Tablet", True, "Target maintenance therapy for refractory focal seizures in adults.", 345.0, 298.0),
    ("Eptoin 100", "Phenytoin Sodium", "Abbott Healthcare", "100 mg", "Tablet", True, "Classic foundational hydantoin anticonvulsant for grand mal seizures.", 65.0, 55.0),
    ("Frisium 5", "Clobazam", "Sanofi India", "5 mg", "Tablet", True, "1,5-benzodiazepine for refractory epilepsy adjunctive control with low sedation.", 75.0, 64.0),
    ("Frisium 10", "Clobazam", "Sanofi India", "10 mg", "Tablet", True, "Effective add-on anticonvulsant for Lennox-Gastaut syndrome and focal seizures.", 135.0, 116.0),
    ("Frisium 20", "Clobazam", "Sanofi India", "20 mg", "Tablet", True, "High-dose clobazam for severe intractable drug-resistant epileptic clusters.", 245.0, 212.0),
    ("Lacosam 50", "Lacosamide", "Sun Pharma", "50 mg", "Tablet", True, "Slow sodium channel inactivation enhancer for modern seizure management.", 145.0, 124.0),
    ("Lacosam 100", "Lacosamide", "Sun Pharma", "100 mg", "Tablet", True, "Advanced add-on anticonvulsant with favorable pharmacokinetic profile.", 265.0, 230.0),
    ("Gabapin 100", "Gabapentin", "Intas Pharmaceuticals", "100 mg", "Capsule", True, "Initial titration dose for painful diabetic neuropathy and post-shingles nerve pain.", 95.0, 81.0),
    ("Gabapin 300", "Gabapentin", "Intas Pharmaceuticals", "300 mg", "Capsule", True, "Voltage-gated calcium channel modulator relieving burning neuropathic pain.", 215.0, 185.0),
    ("Gabaneuron 300/500", "Gabapentin + Methylcobalamin", "Aristo Pharmaceuticals", "300 mg + 500 mcg", "Tablet", True, "Dual analgesic and nerve regenerating combination for chronic peripheral neuropathy.", 245.0, 212.0),
    ("Pregabalin 75", "Pregabalin", "Cipla Ltd", "75 mg", "Capsule", True, "Alpha-2-delta ligand delivering fast relief from fibromyalgia and nerve pain.", 145.0, 125.0),
    ("Pregeb 75", "Pregabalin", "Torrent Pharmaceuticals", "75 mg", "Capsule", True, "Clinically proven relief from spinal radiculopathy, sciatica and neuropathy.", 165.0, 142.0),
    ("Pregeb 150", "Pregabalin", "Torrent Pharmaceuticals", "150 mg", "Capsule", True, "High-strength neural analgesic for severe diabetic peripheral neuropathy.", 285.0, 245.0),
    ("Pregalin-M 75/750", "Pregabalin + Methylcobalamin", "Torrent Pharmaceuticals", "75 mg + 750 mcg", "Capsule", True, "Synergistic nerve pain soother and active B12 myelin sheath regenerator.", 225.0, 194.0),
    ("Lioresal 10", "Baclofen", "Novartis", "10 mg", "Tablet", True, "Centrally acting GABA-B agonist muscle relaxant for spinal spasticity and MS.", 125.0, 108.0),
    ("Lioresal 25", "Baclofen", "Novartis", "25 mg", "Tablet", True, "High-strength antispasmodic for severe muscular rigidity and cerebral palsy.", 265.0, 230.0),
    ("Syndopa 110", "Levodopa + Carbidopa", "Sun Pharma", "100 mg + 10 mg", "Tablet", True, "Fundamental dopamine replacement therapy for Parkinson's disease tremor and rigidity.", 85.0, 72.0),
    ("Syndopa 275", "Levodopa + Carbidopa", "Sun Pharma", "250 mg + 25 mg", "Tablet", True, "Standard 10:1 ratio carbidopa-levodopa for motor symptom control in Parkinson's.", 165.0, 142.0),
    ("Syndopa Plus", "Levodopa + Carbidopa", "Sun Pharma", "100 mg + 25 mg", "Tablet", True, "Optimal 4:1 peripheral decarboxylase inhibition minimizing nausea and dyskinesia.", 125.0, 108.0),
    ("Syndopa CR", "Levodopa + Carbidopa Controlled Release", "Sun Pharma", "200 mg + 50 mg", "Tablet", True, "Continuous release levodopa mitigating nocturnal off-periods and morning akinesia.", 220.0, 192.0),
    ("Ropark 0.5", "Ropinirole", "Sun Pharma", "0.5 mg", "Tablet", True, "Non-ergot dopamine D2/D3 agonist for restless legs syndrome and early Parkinson's.", 78.0, 66.0),
    ("Ropark 1", "Ropinirole", "Sun Pharma", "1 mg", "Tablet", True, "Dopamine receptor stimulant delaying the need for levodopa therapy.", 135.0, 116.0),
    ("Ropark 2", "Ropinirole", "Sun Pharma", "2 mg", "Tablet", True, "Target dose dopamine agonist reducing Parkinsonian motor fluctuations.", 235.0, 204.0),
    ("Pacitane 2", "Trihexyphenidyl Hydrochloride", "Pfizer", "2 mg", "Tablet", True, "Anticholinergic agent specifically counteracting drug-induced extrapyramidal tremors.", 42.0, 35.0),
    ("Donecept 5", "Donepezil Hydrochloride", "Cipla Ltd", "5 mg", "Tablet", True, "Acetylcholinesterase inhibitor improving memory and cognition in mild Alzheimer's.", 145.0, 125.0),
    ("Donecept 10", "Donepezil Hydrochloride", "Cipla Ltd", "10 mg", "Tablet", True, "Target maintenance dose preserving cognitive function in Alzheimer's dementia.", 265.0, 230.0),
    ("Aricep 5", "Donepezil", "Eisai Pharma", "5 mg", "Tablet", True, "Original developer reversible cholinesterase inhibitor for cognitive decline.", 185.0, 160.0),
    ("Admenta 5", "Memantine Hydrochloride", "Sun Pharma", "5 mg", "Tablet", True, "NMDA receptor antagonist protecting neurons from excitotoxicity in Alzheimer's.", 125.0, 108.0),
    ("Admenta 10", "Memantine Hydrochloride", "Sun Pharma", "10 mg", "Tablet", True, "Target neuroprotective therapy for moderate to severe Alzheimer's disease.", 225.0, 194.0),
    ("Vertin 16", "Betahistine", "Abbott Healthcare", "16 mg", "Tablet", True, "Microvascular inner ear histamine analogue relieving true vertigo and Meniere's.", 215.0, 185.0),

    # =========================================================================
    # 6. PSYCHIATRY & BEHAVIORAL HEALTH (35 items)
    # =========================================================================
    ("Nexito 5", "Escitalopram", "Sun Pharma", "5 mg", "Tablet", True, "Titration starting dose for generalized anxiety disorder and panic attacks.", 68.0, 58.0),
    ("Nexito 10", "Escitalopram", "Sun Pharma", "10 mg", "Tablet", True, "Pure S-enantiomer SSRI delivering clean antidepressant and anxiolytic efficacy.", 125.0, 108.0),
    ("Nexito 20", "Escitalopram", "Sun Pharma", "20 mg", "Tablet", True, "Maximum strength SSRI for severe major depressive episodes and OCD.", 215.0, 185.0),
    ("Nexito Plus", "Escitalopram + Clonazepam", "Sun Pharma", "10 mg + 0.5 mg", "Tablet", True, "Dual SSRI and anxiolytic benzodiazepine for comorbid anxiety with depression.", 165.0, 142.0),
    ("Nexito Forte", "Escitalopram + Clonazepam", "Sun Pharma", "20 mg + 0.5 mg", "Tablet", True, "High antidepressant dose with rapid anxiolytic calming action.", 245.0, 212.0),
    ("Daxid 50", "Sertraline Hydrochloride", "Pfizer", "50 mg", "Tablet", True, "Cardiovascularly safe SSRI for major depression, PTSD and social phobia.", 135.0, 116.0),
    ("Daxid 100", "Sertraline Hydrochloride", "Pfizer", "100 mg", "Tablet", True, "Target dosage for obsessive compulsive disorder and recurrent panic disorder.", 245.0, 212.0),
    ("Flunil 20", "Fluoxetine Hydrochloride", "Intas Pharmaceuticals", "20 mg", "Capsule", True, "Long half-life activating SSRI ideal for depression with fatigue and bulimia.", 65.0, 55.0),
    ("Pari 12.5 CR", "Paroxetine Controlled Release", "Ipca Laboratories", "12.5 mg", "Tablet", True, "Controlled release SSRI for panic disorder without sudden peak nausea.", 145.0, 125.0),
    ("Pari 25 CR", "Paroxetine Controlled Release", "Ipca Laboratories", "25 mg", "Tablet", True, "Target maintenance therapy for severe social anxiety disorder and PTSD.", 265.0, 230.0),
    ("Venlor XR 37.5", "Venlafaxine Extended Release", "Cipla Ltd", "37.5 mg", "Capsule", True, "Dual serotonin-norepinephrine reuptake inhibitor (SNRI) for treatment-resistant mood.", 125.0, 108.0),
    ("Venlor XR 75", "Venlafaxine Extended Release", "Cipla Ltd", "75 mg", "Capsule", True, "SNRI for chronic depression with somatic pain and generalized anxiety.", 215.0, 185.0),
    ("Desven 50", "Desvenlafaxine", "Sun Pharma", "50 mg", "Tablet", True, "Active metabolite SNRI with minimal CYP2D6 hepatic drug interaction risk.", 195.0, 168.0),
    ("Desven 100", "Desvenlafaxine", "Sun Pharma", "100 mg", "Tablet", True, "Full-strength dual reuptake inhibitor for severe clinical depression.", 345.0, 298.0),
    ("Duzela 20", "Duloxetine", "Sun Pharma", "20 mg", "Capsule", True, "SNRI addressing both emotional depressive symptoms and diabetic neuropathic pain.", 115.0, 98.0),
    ("Duzela 30", "Duloxetine", "Sun Pharma", "30 mg", "Capsule", True, "Balanced SNRI relieving chronic musculoskeletal lower back pain and depression.", 165.0, 142.0),
    ("Duzela 40", "Duloxetine", "Sun Pharma", "40 mg", "Capsule", True, "High-dose dual reuptake inhibitor for generalized anxiety and fibromyalgia.", 225.0, 194.0),
    ("Tryptomer 10", "Amitriptyline Hydrochloride", "Wockhardt", "10 mg", "Tablet", True, "Tricyclic agent widely used off-label for tension headache and migraine prophylaxis.", 38.0, 31.0),
    ("Tryptomer 25", "Amitriptyline Hydrochloride", "Wockhardt", "25 mg", "Tablet", True, "Sedative antidepressant restoring sleep architecture and mitigating chronic pain.", 65.0, 55.0),
    ("Mirnite 7.5", "Mirtazapine", "Intas Pharmaceuticals", "7.5 mg", "Tablet", True, "Noradrenergic and specific serotonergic antidepressant (NaSSA) stimulating appetite and sleep.", 85.0, 72.0),
    ("Mirnite 15", "Mirtazapine", "Intas Pharmaceuticals", "15 mg", "Tablet", True, "Antidepressant promoting deep sleep without sexual dysfunction side effects.", 155.0, 132.0),
    ("Lonazep 0.25", "Clonazepam", "Sun Pharma", "0.25 mg", "Tablet", True, "Low-dose long-acting benzodiazepine for acute panic disorder and insomnia.", 35.0, 29.0),
    ("Lonazep 0.5", "Clonazepam", "Sun Pharma", "0.5 mg", "Tablet", True, "High-affinity GABA-A receptor positive allosteric modulator for anxiety.", 62.0, 52.0),
    ("Lonazep 1", "Clonazepam", "Sun Pharma", "1 mg", "Tablet", True, "Intermediate strength benzodiazepine for acute psychiatric crisis and agoraphobia.", 95.0, 81.0),
    ("Alprax 0.25", "Alprazolam", "Torrent Pharmaceuticals", "0.25 mg", "Tablet", True, "Short-acting triazolobenzodiazepine for situational panic and acute anxiety.", 28.0, 23.0),
    ("Alprax 0.5", "Alprazolam", "Torrent Pharmaceuticals", "0.5 mg", "Tablet", True, "Rapid anxiolytic for intense acute panic attacks under strict medical supervision.", 48.0, 40.0),
    ("Ativan 1", "Lorazepam", "Pfizer", "1 mg", "Tablet", True, "Safe glucuronidated benzodiazepine ideal for elderly patients with anxiety.", 45.0, 38.0),
    ("Ativan 2", "Lorazepam", "Pfizer", "2 mg", "Tablet", True, "Potent intermediate-acting anxiolytic and sedative for acute catatonia and agitation.", 78.0, 66.0),
    ("Oleanz 5", "Olanzapine", "Sun Pharma", "5 mg", "Tablet", True, "Second-generation atypical antipsychotic for schizophrenia and acute bipolar mania.", 95.0, 81.0),
    ("Oleanz 10", "Olanzapine", "Sun Pharma", "10 mg", "Tablet", True, "Target maintenance therapy for long-term bipolar disorder relapse prevention.", 165.0, 142.0),
    ("Qutan 50", "Quetiapine Fumarate", "Intas Pharmaceuticals", "50 mg", "Tablet", True, "Atypical antipsychotic with low extrapyramidal symptoms for bipolar depression.", 115.0, 98.0),
    ("Qutan 100", "Quetiapine Fumarate", "Intas Pharmaceuticals", "100 mg", "Tablet", True, "Dopamine D2 and 5-HT2 receptor antagonist for major psychosis and mood stabilization.", 195.0, 168.0),
    ("Sizodon 2", "Risperidone", "Sun Pharma", "2 mg", "Tablet", True, "Standard atypical antipsychotic for behavioral disturbances in autism and schizophrenia.", 75.0, 64.0),
    ("Arip MT 10", "Aripiprazole", "Torrent Pharmaceuticals", "10 mg", "Tablet", True, "Dopamine D2 partial agonist stabilizing neurotransmission without weight gain.", 185.0, 158.0),
    ("Licab 300", "Lithium Carbonate", "Torrent Pharmaceuticals", "300 mg", "Tablet", True, "Gold-standard mood stabilizer preventing suicide and manic relapse in bipolar disease.", 52.0, 44.0),

    # =========================================================================
    # 7. GASTROENTEROLOGY & HEPATOLOGY (40 items)
    # =========================================================================
    ("Pan 20", "Pantoprazole", "Alkem Laboratories", "20 mg", "Tablet", False, "Proton pump inhibitor maintaining healing in erosive reflux esophagitis.", 75.0, 64.0),
    ("Pan 40", "Pantoprazole", "Alkem Laboratories", "40 mg", "Tablet", False, "First-line irreversible PPI for severe GERD, heartburn and peptic ulcer disease.", 145.0, 124.0),
    ("Pan-D", "Pantoprazole + Domperidone", "Alkem Laboratories", "40 mg + 10 mg", "Capsule", True, "Dual acid suppressor and prokinetic agent preventing reflux regurgitation and nausea.", 185.0, 158.0),
    ("Pantocid-DSR", "Pantoprazole + Domperidone Sustained Release", "Sun Pharma", "40 mg + 30 mg", "Capsule", True, "Once-daily sustained prokinetic and PPI for severe diabetic gastroparesis & GERD.", 235.0, 204.0),
    ("Pan-L", "Pantoprazole + Levosulpiride", "Alkem Laboratories", "40 mg + 75 mg", "Capsule", True, "PPI with central prokinetic for severe non-ulcer dyspepsia and refractory heartburn.", 245.0, 212.0),
    ("Omez 20", "Omeprazole", "Dr. Reddy's", "20 mg", "Capsule", False, "Classic time-tested gastric proton pump inhibitor relieving acid indigestion.", 62.0, 52.0),
    ("Ocid 20", "Omeprazole", "Zydus Lifesciences", "20 mg", "Capsule", False, "Rapid-relief gastric acid inhibitor for hyperacidity and sour stomach.", 58.0, 49.0),
    ("Omez-D", "Omeprazole + Domperidone", "Dr. Reddy's", "20 mg + 10 mg", "Capsule", True, "Combined acid reduction and motility stimulant for nausea associated with acid reflux.", 125.0, 108.0),
    ("Razo 20", "Rabeprazole Sodium", "Dr. Reddy's", "20 mg", "Tablet", True, "Fastest-acting proton pump inhibitor providing rapid day and night relief.", 165.0, 142.0),
    ("Happi 20", "Rabeprazole", "Zydus Lifesciences", "20 mg", "Tablet", True, "High-affinity gastric H+/K+ ATPase inhibitor with non-enzymatic clearance.", 155.0, 132.0),
    ("Razo-D", "Rabeprazole + Domperidone", "Dr. Reddy's", "20 mg + 30 mg", "Capsule", True, "Fast-acting rabeprazole combined with sustained domperidone for vomiting and reflux.", 225.0, 194.0),
    ("Razo-L", "Rabeprazole + Levosulpiride", "Dr. Reddy's", "20 mg + 75 mg", "Capsule", True, "Effective combination for refractory gastroesophageal reflux and irritable bowel.", 285.0, 245.0),
    ("Nexpro 20", "Esomeprazole", "Torrent Pharmaceuticals", "20 mg", "Tablet", True, "Optically pure S-isomer of omeprazole delivering greater bioavailable acid suppression.", 115.0, 98.0),
    ("Nexpro 40", "Esomeprazole", "Torrent Pharmaceuticals", "40 mg", "Tablet", True, "Maximum acid suppression for healing severe grade C and D erosive esophagitis.", 195.0, 168.0),
    ("Nexpro-RD 20", "Esomeprazole + Domperidone", "Torrent Pharmaceuticals", "20 mg + 30 mg", "Capsule", True, "Optimized S-isomer PPI with sustained prokinetic for all-day reflux protection.", 215.0, 185.0),
    ("Sompraz 40", "Esomeprazole", "Sun Pharma", "40 mg", "Tablet", True, "Potent acid pump blocker for rapid symptom resolution in peptic ulcer bleeding.", 190.0, 165.0),
    ("Lanzol 30", "Lansoprazole", "Cipla Ltd", "30 mg", "Capsule", True, "Proton pump inhibitor with superior eradication rate in Helicobacter pylori regimens.", 125.0, 108.0),
    ("Rantac 150", "Ranitidine", "J.B. Chemicals", "150 mg", "Tablet", False, "H2-receptor antagonist reducing basal stomach acid secretion for quick relief.", 38.0, 32.0),
    ("Rantac 300", "Ranitidine", "J.B. Chemicals", "300 mg", "Tablet", False, "Night-time acid suppression tablet for active duodenal and benign gastric ulcers.", 68.0, 58.0),
    ("Aciloc 150", "Ranitidine", "Cadila Pharmaceuticals", "150 mg", "Tablet", False, "Affordable H2 blocker for mild acid indigestion and gas bloating.", 35.0, 29.0),
    ("Famocid 40", "Famotidine", "Sun Pharma", "40 mg", "Tablet", False, "Potent selective H2 receptor antagonist for Zollinger-Ellison syndrome and heartburn.", 45.0, 38.0),
    ("Sucrafil Suspension", "Sucralfate", "Fourrts Laboratories", "1000 mg / 10 ml", "Syrup", True, "Cytoprotective mucosal coating agent forming a barrier over ulcerated crater sites.", 195.0, 168.0),
    ("Sucrafil-O Gel", "Sucralfate + Oxetacaine", "Fourrts Laboratories", "1000 mg + 20 mg", "Syrup", True, "Dual ulcer protectant and local anesthetic offering instant relief from burning pain.", 245.0, 212.0),
    ("Udiliv 150", "Ursodeoxycholic Acid", "Abbott Healthcare", "150 mg", "Tablet", True, "Naturally occurring bile acid dissolving radiolucent cholesterol gallstones.", 295.0, 258.0),
    ("Udiliv 300", "Ursodeoxycholic Acid", "Abbott Healthcare", "300 mg", "Tablet", True, "First-line hepatoprotective therapy for primary biliary cholangitis & cholestasis.", 540.0, 475.0),
    ("Ursocol 300", "Ursodeoxycholic Acid", "Sun Pharma", "300 mg", "Tablet", True, "Hepatoprotective agent protecting liver sinusoidal cells in non-alcoholic steatohepatitis.", 510.0, 445.0),
    ("Ganaton 50", "Itopride Hydrochloride", "Abbott Healthcare", "50 mg", "Tablet", True, "D2 receptor and acetylcholinesterase inhibitor boosting gastric emptying without QT prolongation.", 195.0, 168.0),
    ("Emeset 4", "Ondansetron", "Cipla Ltd", "4 mg", "Tablet", True, "5-HT3 receptor antagonist suppressing nausea and vomiting from gastroenteritis.", 45.0, 38.0),
    ("Emeset 8", "Ondansetron", "Cipla Ltd", "8 mg", "Tablet", True, "High-strength antiemetic for chemotherapy and postoperative emesis prophylaxis.", 78.0, 66.0),
    ("Domstal 10", "Domperidone", "Torrent Pharmaceuticals", "10 mg", "Tablet", True, "Peripheral dopamine antagonist treating postprandial fullness and bloating.", 38.0, 32.0),
    ("Cyclopam", "Dicyclomine + Paracetamol", "Indoco Remedies", "20 mg + 500 mg", "Tablet", True, "Smooth muscle antispasmodic for acute intestinal cramps and colicky abdominal pain.", 65.0, 55.0),
    ("Meftal-Spas", "Mefenamic Acid + Dicyclomine", "Blue Cross Laboratories", "250 mg + 10 mg", "Tablet", True, "Number one anti-spasmodic formulation for primary dysmenorrhea and bowel spasms.", 58.0, 49.0),
    ("Colospa 135", "Mebeverine Hydrochloride", "Abbott Healthcare", "135 mg", "Tablet", True, "Direct musculotropic spasmolytic specifically normalizing irritable bowel syndrome (IBS).", 285.0, 248.0),
    ("Colospa Retard 200", "Mebeverine Extended Release", "Abbott Healthcare", "200 mg", "Capsule", True, "Extended release capsule for 24-hr relief from IBS abdominal pain and cramps.", 395.0, 345.0),
    ("Mesacol 400", "Mesalamine / 5-ASA", "Sun Pharma", "400 mg", "Tablet", True, "Delayed release anti-inflammatory for inducing remission in mild ulcerative colitis.", 245.0, 212.0),
    ("Mesacol 800", "Mesalamine / 5-ASA", "Sun Pharma", "800 mg", "Tablet", True, "High-dose targeted colonic release 5-ASA for maintenance of ulcerative colitis.", 465.0, 405.0),
    ("Creon 10000", "Pancreatin", "Abbott Healthcare", "10000 IU", "Capsule", True, "Enteric-coated minimicrospheres replacing digestive enzymes in pancreatic insufficiency.", 620.0, 545.0),
    ("Creon 25000", "Pancreatin", "Abbott Healthcare", "25000 IU", "Capsule", True, "High-potency pancreatic enzyme replacement therapy for chronic pancreatitis & cystic fibrosis.", 1150.0, 1010.0),
    ("Rifagut 400", "Rifaximin", "Sun Pharma", "400 mg", "Tablet", True, "Non-absorbed gut antibiotic reducing ammonia levels in hepatic encephalopathy.", 345.0, 300.0),
    ("Rifagut 550", "Rifaximin", "Sun Pharma", "550 mg", "Tablet", True, "Proven gut-selective therapy for travelers' diarrhea and irritable bowel with diarrhea.", 465.0, 405.0),

    # =========================================================================
    # 8. RHEUMATOLOGY, ORTHOPEDICS & CHRONIC JOINT DISEASE (35 items)
    # =========================================================================
    ("Folitrax 7.5", "Methotrexate", "Ipca Laboratories", "7.5 mg", "Tablet", True, "First-line disease-modifying antirheumatic drug (DMARD) for rheumatoid arthritis.", 145.0, 125.0),
    ("Folitrax 10", "Methotrexate", "Ipca Laboratories", "10 mg", "Tablet", True, "Weekly oral anchor drug halting structural joint erosions in RA.", 185.0, 158.0),
    ("Folitrax 15", "Methotrexate", "Ipca Laboratories", "15 mg", "Tablet", True, "Target weekly DMARD dose suppressing autoimmune synovitis.", 265.0, 230.0),
    ("HCQS 200", "Hydroxychloroquine Sulfate", "Ipca Laboratories", "200 mg", "Tablet", True, "Antimalarial immunomodulator reducing joint swelling in RA and systemic lupus.", 125.0, 108.0),
    ("HCQS 300", "Hydroxychloroquine Sulfate", "Ipca Laboratories", "300 mg", "Tablet", True, "Intermediate maintenance dose for chronic autoimmune connective tissue disorders.", 185.0, 158.0),
    ("HCQS 400", "Hydroxychloroquine Sulfate", "Ipca Laboratories", "400 mg", "Tablet", True, "High-strength DMARD suppressing autoimmune autoantibodies in active SLE.", 245.0, 212.0),
    ("Saaz 500", "Sulfasalazine", "Ipca Laboratories", "500 mg", "Tablet", True, "Enteric-coated anti-inflammatory DMARD for peripheral spondyloarthritis & RA.", 165.0, 142.0),
    ("Saaz-DS 1000", "Sulfasalazine", "Ipca Laboratories", "1000 mg", "Tablet", True, "Double strength formulation for ankylosing spondylitis spinal inflammation.", 310.0, 268.0),
    ("Lefra 10", "Leflunomide", "Torrent Pharmaceuticals", "10 mg", "Tablet", True, "Pyrimidine synthesis inhibitor suppressing activated rheumatoid lymphocytes.", 195.0, 168.0),
    ("Lefra 20", "Leflunomide", "Torrent Pharmaceuticals", "20 mg", "Tablet", True, "Target maintenance therapy for active severe rheumatoid arthritis.", 345.0, 298.0),
    ("Wysolone 5", "Prednisolone", "Pfizer", "5 mg", "Tablet", True, "Low-dose synthetic glucocorticoid bridging therapy for acute rheumatic flares.", 18.0, 15.0),
    ("Wysolone 10", "Prednisolone", "Pfizer", "10 mg", "Tablet", True, "Anti-inflammatory steroid suppressing acute joint effusion and morning stiffness.", 32.0, 27.0),
    ("Wysolone 20", "Prednisolone", "Pfizer", "20 mg", "Tablet", True, "Intermediate corticosteroid for polymyalgia rheumatica and systemic vasculitis.", 58.0, 49.0),
    ("Medrol 4", "Methylprednisolone", "Pfizer", "4 mg", "Tablet", True, "Potent corticosteroid with minimal sodium retention for joint inflammation.", 55.0, 46.0),
    ("Medrol 8", "Methylprednisolone", "Pfizer", "8 mg", "Tablet", True, "High-potency anti-inflammatory steroid for severe autoimmune connective tissue disease.", 95.0, 81.0),
    ("Medrol 16", "Methylprednisolone", "Pfizer", "16 mg", "Tablet", True, "Intensive immune suppression for acute flares of lupus nephritis and arthritis.", 175.0, 152.0),
    ("Defcort 6", "Deflazacort", "Macleods Pharmaceuticals", "6 mg", "Tablet", True, "Bone-sparing glucocorticoid with reduced osteoporosis and weight-gain risk.", 85.0, 72.0),
    ("Defcort 12", "Deflazacort", "Macleods Pharmaceuticals", "12 mg", "Tablet", True, "Higher dose modern oxazoline corticosteroid for severe musculoskeletal inflammation.", 155.0, 132.0),
    ("Nucoxia 60", "Etoricoxib", "Zydus Lifesciences", "60 mg", "Tablet", True, "Selective COX-2 inhibitor relieving osteoarthritis joint pain with lower ulcer risk.", 145.0, 124.0),
    ("Nucoxia 90", "Etoricoxib", "Zydus Lifesciences", "90 mg", "Tablet", True, "Once-daily COX-2 blocker for acute rheumatoid arthritis and ankylosing spondylitis.", 215.0, 185.0),
    ("Nucoxia 120", "Etoricoxib", "Zydus Lifesciences", "120 mg", "Tablet", True, "Fast-acting maximum dose for excruciating acute gouty arthritis attacks.", 275.0, 238.0),
    ("Nucoxia-MR", "Etoricoxib + Thiocolchicoside", "Zydus Lifesciences", "60 mg + 4 mg", "Tablet", True, "Dual anti-inflammatory and muscle relaxant for acute torticollis and sciatica.", 245.0, 212.0),
    ("Voveran 50", "Diclofenac Sodium", "Novartis", "50 mg", "Tablet", True, "Classic NSAID for traumatic swelling, dental pain and degenerative joint diseases.", 85.0, 72.0),
    ("Voveran SR 100", "Diclofenac Sodium Sustained Release", "Novartis", "100 mg", "Tablet", True, "24-hour sustained release tablet for nocturnal osteoarthritic joint stiffness.", 165.0, 142.0),
    ("Voveran Emulgel 30g", "Diclofenac Diethylamine", "Novartis", "1.16% w/w", "Gel", False, "Topical non-greasy pain relief gel penetrating deep into aching tendons and knees.", 135.0, 116.0),
    ("Zerodol 100", "Aceclofenac", "Ipca Laboratories", "100 mg", "Tablet", True, "Cartilage-sparing NSAID with superior gastric tolerability over diclofenac.", 75.0, 64.0),
    ("Zerodol-P", "Aceclofenac + Paracetamol", "Ipca Laboratories", "100 mg + 325 mg", "Tablet", True, "Synergistic analgesic for acute dental, post-surgical and muscular aches.", 85.0, 72.0),
    ("Zerodol-SP", "Aceclofenac + Paracetamol + Serratiopeptidase", "Ipca Laboratories", "100 mg + 325 mg + 15 mg", "Tablet", True, "Triple combination relieving pain, reducing fever and resolving inflamed tissue edema.", 135.0, 116.0),
    ("Zerodol-TH 4", "Aceclofenac + Thiocolchicoside", "Ipca Laboratories", "100 mg + 4 mg", "Tablet", True, "Muscle relaxant combo treating excruciating lower back spasms and neck stiffness.", 185.0, 158.0),
    ("Myoril 4", "Thiocolchicoside", "Sanofi India", "4 mg", "Capsule", True, "Semi-synthetic colchicine derivative muscle relaxant without central sedation.", 165.0, 142.0),
    ("Myoril 8", "Thiocolchicoside", "Sanofi India", "8 mg", "Capsule", True, "High-strength antispasmodic relieving acute skeletal muscle contractions.", 285.0, 245.0),
    ("Zyloric 100", "Allopurinol", "GSK India", "100 mg", "Tablet", True, "Xanthine oxidase inhibitor reducing serum uric acid to prevent chronic gout stones.", 35.0, 29.0),
    ("Zyloric 300", "Allopurinol", "GSK India", "300 mg", "Tablet", True, "Target dose for dissolving tophi and preventing recurrent hyperuricemic attacks.", 85.0, 72.0),
    ("Feburic 40", "Febuxostat", "Sun Pharma", "40 mg", "Tablet", True, "Non-purine selective xanthine oxidase inhibitor ideal for patients allergic to allopurinol.", 145.0, 124.0),
    ("Feburic 80", "Febuxostat", "Sun Pharma", "80 mg", "Tablet", True, "Potent hypouricemic agent achieving target uric acid levels below 6 mg/dL.", 245.0, 212.0),

    # =========================================================================
    # 9. NEPHROLOGY, UROLOGY & BLADDER HEALTH (30 items)
    # =========================================================================
    ("Urimax 0.4", "Tamsulosin Hydrochloride", "Cipla Ltd", "0.4 mg", "Capsule", True, "Uroselective alpha-1A blocker relaxing prostatic smooth muscle in benign prostatic hyperplasia.", 195.0, 168.0),
    ("Flodart 0.4", "Tamsulosin Hydrochloride", "Torrent Pharmaceuticals", "0.4 mg", "Capsule", True, "Rapidly relieves urinary hesitancy, straining and nocturnal urination in enlarged prostate.", 185.0, 158.0),
    ("Urimax-D", "Tamsulosin + Dutasteride", "Cipla Ltd", "0.4 mg + 0.5 mg", "Capsule", True, "Gold-standard dual therapy: relaxes prostatic muscle and shrinks prostate volume.", 385.0, 335.0),
    ("Tamflo 0.4", "Tamsulosin", "Sun Pharma", "0.4 mg", "Capsule", True, "Targeted bladder neck relaxant easing urine flow without altering blood pressure.", 190.0, 165.0),
    ("Tamflo-D", "Tamsulosin + Dutasteride", "Sun Pharma", "0.4 mg + 0.5 mg", "Capsule", True, "Long-term dual agent reducing risk of acute urinary retention and BPH surgery.", 375.0, 325.0),
    ("Silodal 4", "Silodosin", "Sun Pharma", "4 mg", "Capsule", True, "Super-selective alpha-1A antagonist delivering immediate relief from urinary retention.", 245.0, 212.0),
    ("Silodal 8", "Silodosin", "Sun Pharma", "8 mg", "Capsule", True, "Full-strength prostate relaxant with minimal orthostatic dizziness side effects.", 425.0, 370.0),
    ("Rapilif 8", "Silodosin", "Ipca Laboratories", "8 mg", "Capsule", True, "High uroselectivity medication improving peak urinary flow rate in BPH.", 395.0, 345.0),
    ("Fincar 5", "Finasteride", "Cipla Ltd", "5 mg", "Tablet", True, "5-alpha reductase inhibitor shrinking enlarged prostate gland over 6 months.", 265.0, 230.0),
    ("Duprost 0.5", "Dutasteride", "Cipla Ltd", "0.5 mg", "Capsule", True, "Dual type 1 and type 2 5-alpha reductase inhibitor halting prostate growth.", 215.0, 185.0),
    ("Dutas 0.5", "Dutasteride", "Dr. Reddy's", "0.5 mg", "Capsule", True, "Suppresses circulating DHT levels by over 90% for sustained prostate reduction.", 210.0, 180.0),
    ("Alfusin 10 ER", "Alfuzosin Hydrochloride Extended Release", "Cipla Ltd", "10 mg", "Tablet", True, "Once-daily bladder neck relaxant with proven low incidence of ejaculatory dysfunction.", 285.0, 245.0),
    ("Roliten 2", "Tolterodine Tartrate", "Sun Pharma", "2 mg", "Tablet", True, "Antimuscarinic agent reducing bladder detrusor muscle contractions in overactive bladder.", 145.0, 124.0),
    ("Roliten 4 ER", "Tolterodine Extended Release", "Sun Pharma", "4 mg", "Capsule", True, "24-hr control of urinary urge incontinence and daytime frequency.", 265.0, 230.0),
    ("Solicept 5", "Solifenacin Succinate", "Lupin Ltd", "5 mg", "Tablet", True, "Uroselective M3 receptor antagonist reducing urgency and frequency in OAB.", 245.0, 212.0),
    ("Solicept 10", "Solifenacin Succinate", "Lupin Ltd", "10 mg", "Tablet", True, "High-strength detrusor relaxant preventing sudden embarrassing urinary leaks.", 425.0, 370.0),
    ("Alkarate Liquid", "Disodium Hydrogen Citrate", "Wallace Pharmaceuticals", "1.4 g / 5 ml", "Syrup", False, "Systemic and urinary alkalizer for burning micturition, UTI symptoms, and gout.", 125.0, 108.0),
    ("Cital Syrup", "Disodium Hydrogen Citrate", "Indoco Remedies", "1.37 g / 5 ml", "Syrup", False, "Relieves severe burning during urination and dissolves acidic uric acid stones.", 118.0, 102.0),
    ("Potklor Syrup", "Potassium Chloride", "Walter Bushnell", "200 ml", "Syrup", True, "Therapeutic potassium supplement preventing hypokalemia caused by loop diuretics.", 135.0, 116.0),
    ("K-Cit Solution", "Potassium Citrate + Citric Acid", "RPG Life Sciences", "200 ml", "Syrup", True, "Urinary alkalizer preventing recurrent calcium oxalate and uric acid kidney stones.", 195.0, 168.0),
    ("Renvela 800", "Sevelamer Carbonate", "Sanofi India", "800 mg", "Tablet", True, "Non-calcium phosphate binder preventing vascular calcification in end-stage CKD.", 950.0, 835.0),
    ("Sevcar 800", "Sevelamer Carbonate", "Emcure Pharmaceuticals", "800 mg", "Tablet", True, "Affordable phosphate binder managing hyperphosphatemia in hemodialysis patients.", 680.0, 595.0),
    ("Phoscut 667", "Calcium Acetate", "Macleods Pharmaceuticals", "667 mg", "Tablet", True, "Binds dietary phosphate in gut lumen to control serum phosphorus in renal failure.", 165.0, 142.0),
    ("Sodamint 500", "Sodium Bicarbonate", "Sun Pharma", "500 mg", "Tablet", False, "Corrects metabolic acidosis and retards chronic kidney disease progression.", 35.0, 29.0),
    ("Sodamint 1000", "Sodium Bicarbonate", "Sun Pharma", "1000 mg", "Tablet", False, "High-dose oral systemic alkalizer for advanced chronic renal failure patients.", 62.0, 52.0),
    ("Ketosteril", "Alpha-Ketoanalogues to Essential Amino Acids", "Fresenius Kabi", "600 mg", "Tablet", True, "Preserves renal function and delays dialysis in conjunction with very low-protein diet.", 2850.0, 2490.0),
    ("Dytor Plus 20/50", "Torsemide + Spironolactone", "Cipla Ltd", "20 mg + 50 mg", "Tablet", True, "High-potency diuretic combo relieving refractory edema in nephrotic syndrome.", 215.0, 185.0),
    ("Cystone", "Didymocarpus pedicellata + Saxifraga ligulata", "Himalaya Wellness", "60 Tablets", "Tablet", False, "Herbal antilithiatic promoting expulsion of kidney stones and soothing UTI burning.", 160.0, 140.0),
    ("Urofos 3g", "Fosfomycin Tromethamine", "Torrent Pharmaceuticals", "3 g", "Sachet", True, "Single-dose oral megatherapy for acute uncomplicated urinary tract infections.", 425.0, 370.0),
    ("Cran-Max Sachet", "Cranberry Extract + D-Mannose", "Fourrts Laboratories", "5 g", "Sachet", False, "Anti-adherence natural formula preventing recurrent E. coli bladder infections.", 85.0, 72.0),

    # =========================================================================
    # 10. THYROID & ENDOCRINE DISORDERS (20 items)
    # =========================================================================
    ("Thyronorm 25", "Levothyroxine Sodium", "Abbott Healthcare", "25 mcg", "Tablet", True, "Lowest starting hormone replacement dose for mild subclinical hypothyroidism.", 145.0, 126.0),
    ("Thyronorm 37.5", "Levothyroxine Sodium", "Abbott Healthcare", "37.5 mcg", "Tablet", True, "Precision titration dose for fine-tuning serum TSH in elderly thyroid patients.", 155.0, 134.0),
    ("Thyronorm 50", "Levothyroxine Sodium", "Abbott Healthcare", "50 mcg", "Tablet", True, "India's most prescribed synthetic thyroid hormone restoring basal metabolic rate.", 165.0, 144.0),
    ("Thyronorm 62.5", "Levothyroxine Sodium", "Abbott Healthcare", "62.5 mcg", "Tablet", True, "Fine calibration strength for optimal thyroid hormone equilibrium.", 175.0, 152.0),
    ("Thyronorm 75", "Levothyroxine Sodium", "Abbott Healthcare", "75 mcg", "Tablet", True, "Standard daily maintenance dose for primary overt hypothyroidism.", 185.0, 160.0),
    ("Thyronorm 88", "Levothyroxine Sodium", "Abbott Healthcare", "88 mcg", "Tablet", True, "Precise microgram strength for target TSH normalization in Hashimoto's.", 195.0, 168.0),
    ("Thyronorm 100", "Levothyroxine Sodium", "Abbott Healthcare", "100 mcg", "Tablet", True, "High-strength levothyroxine for post-thyroidectomy and severe myxedema.", 205.0, 178.0),
    ("Thyronorm 112", "Levothyroxine Sodium", "Abbott Healthcare", "112 mcg", "Tablet", True, "Specialized dose balancing metabolic rate without inducing iatrogenic thyrotoxicosis.", 215.0, 185.0),
    ("Thyronorm 125", "Levothyroxine Sodium", "Abbott Healthcare", "125 mcg", "Tablet", True, "Complete thyroid hormone replacement following total thyroid cancer resection.", 225.0, 194.0),
    ("Thyronorm 150", "Levothyroxine Sodium", "Abbott Healthcare", "150 mcg", "Tablet", True, "Maximum strength synthetic levothyroxine for profound congenital hypothyroidism.", 245.0, 212.0),
    ("Eltroxin 50", "Levothyroxine Sodium", "GSK India", "50 mcg", "Tablet", True, "Classic trusted British Pharmacopoeia formulation for thyroid hormone deficiency.", 155.0, 134.0),
    ("Eltroxin 100", "Levothyroxine Sodium", "GSK India", "100 mcg", "Tablet", True, "Full replacement therapy overcoming chronic fatigue, hair loss and weight gain.", 195.0, 168.0),
    ("Neo-Mercazole 5", "Carbimazole", "Abbott Healthcare", "5 mg", "Tablet", True, "Thionamide antithyroid drug inhibiting thyroid peroxidase in Graves' disease.", 145.0, 125.0),
    ("Neo-Mercazole 10", "Carbimazole", "Abbott Healthcare", "10 mg", "Tablet", True, "Controls excessive thyroid hormone synthesis in toxic nodular goiter.", 265.0, 230.0),
    ("Neo-Mercazole 20", "Carbimazole", "Abbott Healthcare", "20 mg", "Tablet", True, "High-strength antithyroid therapy for severe hyperthyroidism crisis.", 485.0, 420.0),
    ("Thyrocab 5", "Methimazole", "Sun Pharma", "5 mg", "Tablet", True, "Direct active metabolite antithyroid medication rapidly calming palpitations.", 125.0, 108.0),
    ("Cabgolin 0.25", "Cabergoline", "Sun Pharma", "0.25 mg", "Tablet", True, "Dopamine D2 agonist suppressing excess pituitary prolactin secretion.", 345.0, 300.0),
    ("Cabgolin 0.5", "Cabergoline", "Sun Pharma", "0.5 mg", "Tablet", True, "Long-acting dopamine agonist treating prolactinomas, amenorrhea and galactorrhea.", 585.0, 510.0),
    ("Susten 100", "Progesterone Natural Micronized", "Sun Pharma", "100 mg", "Capsule", True, "Bioidentical natural progesterone for luteal phase support and recurrent miscarriage.", 245.0, 212.0),
    ("Susten 200", "Progesterone Natural Micronized", "Sun Pharma", "200 mg", "Capsule", True, "Target maintenance therapy for high-risk pregnancy and hormone replacement.", 425.0, 370.0),

    # =========================================================================
    # 11. DERMATOLOGY, SCABIES, PSORIASIS & SKIN DISEASES (30 items)
    # =========================================================================
    ("Scabex Cream 5%", "Permethrin", "Torque Pharmaceuticals", "5% w/w", "Cream", False, "Topical anti-parasitic cream for the treatment of scabies and pubic lice infestations.", 89.0, 75.0),
    ("Scaboma Lotion", "Lindane / Permethrin", "Glenmark Pharmaceuticals", "5% w/v", "Lotion", False, "Standard scabicidal lotion eradicating Sarcoptes scabiei mites and their eggs.", 95.0, 81.0),
    ("Permite 5% Cream", "Permethrin", "Curatio Healthcare", "5% w/w", "Cream", False, "Doctor-recommended overnight scabicide providing cure in a single application.", 115.0, 98.0),
    ("Iverfast 6", "Ivermectin", "Sun Pharma", "6 mg", "Tablet", True, "Oral anti-parasitic agent for resistant crusted scabies and strongyloidiasis.", 85.0, 72.0),
    ("Iverfast 12", "Ivermectin", "Sun Pharma", "12 mg", "Tablet", True, "Single oral dose treating widespread cutaneous scabies and filariasis.", 145.0, 124.0),
    ("Bandy-Plus", "Albendazole + Ivermectin", "Mankind Pharma", "400 mg + 6 mg", "Tablet", True, "Broad-spectrum oral deworming and anti-parasitic chewable tablet.", 38.0, 32.0),
    ("Tenovate 0.05% Cream", "Clobetasol Propionate", "GSK India", "0.05% w/w", "Cream", True, "Super-potent topical corticosteroid for resistant plaque psoriasis and severe eczema.", 135.0, 116.0),
    ("Tenovate-GN", "Clobetasol + Neomycin", "GSK India", "15 g", "Cream", True, "High-strength steroid with topical antibiotic for infected inflammatory dermatoses.", 155.0, 132.0),
    ("Betnovate-C Cream", "Betamethasone + Clioquinol", "GSK India", "20 g", "Cream", False, "Popular dual anti-inflammatory and antimicrobial cream for weeping eczema.", 62.0, 52.0),
    ("Betnovate-N Cream", "Betamethasone + Neomycin", "GSK India", "20 g", "Cream", False, "Trusted topical steroid with neomycin antibiotic for infected allergic rashes.", 60.0, 50.0),
    ("Momate 0.1% Cream", "Mometasone Furoate", "Glenmark Pharmaceuticals", "15 g", "Cream", True, "Once-daily medium-potency topical corticosteroid for dermatitis and skin allergies.", 195.0, 168.0),
    ("Elocon 0.1% Cream", "Mometasone Furoate", "Organon India", "10 g", "Cream", True, "High therapeutic index anti-inflammatory steroid with minimal systemic absorption.", 215.0, 185.0),
    ("Tacroz 0.03% Ointment", "Tacrolimus", "Sun Pharma", "10 g", "Ointment", True, "Steroid-free calcineurin inhibitor for sensitive facial and pediatric atopic dermatitis.", 285.0, 248.0),
    ("Tacroz 0.1% Ointment", "Tacrolimus", "Sun Pharma", "10 g", "Ointment", True, "Potent non-steroidal immunosuppressant ointment for moderate to severe eczema.", 395.0, 345.0),
    ("Candid 1% Cream", "Clotrimazole", "Glenmark Pharmaceuticals", "30 g", "Cream", False, "Broad-spectrum topical antifungal curing ringworm (tinea), athlete's foot and jock itch.", 115.0, 98.0),
    ("Candid Dusting Powder", "Clotrimazole", "Glenmark Pharmaceuticals", "100 g", "Dusting Powder", False, "Absorbs sweat and prevents recurrent fungal infections in body skin folds.", 145.0, 125.0),
    ("Canesten 1% Cream", "Clotrimazole", "Bayer", "30 g", "Cream", False, "Gentle, effective antifungal cream clearing candidiasis and fungal rash.", 110.0, 94.0),
    ("Nizral 2% Cream", "Ketoconazole", "Johnson & Johnson", "15 g", "Cream", False, "Imidazole antifungal clearing persistent skin tinea infections and pityriasis.", 165.0, 142.0),
    ("Nizral 2% Shampoo", "Ketoconazole", "Johnson & Johnson", "50 ml", "Shampoo", False, "Medicated shampoo eradicating Malassezia fungus causing severe dandruff & seborrhea.", 245.0, 212.0),
    ("Terbinaforce 250", "Terbinafine Hydrochloride", "Mankind Pharma", "250 mg", "Tablet", True, "Oral allylamine antifungal eradicating difficult nail and deep fungal infections.", 175.0, 150.0),
    ("Terbinaforce Cream 1%", "Terbinafine", "Mankind Pharma", "15 g", "Cream", False, "Fast-acting fungicidal cream relieving itching and clearing tinea pedis.", 95.0, 81.0),
    ("Candiforce 100", "Itraconazole", "Mankind Pharma", "100 mg", "Capsule", True, "Broad-spectrum oral triazole antifungal for stubborn dermatophyte infections.", 145.0, 125.0),
    ("Candiforce 200", "Itraconazole", "Mankind Pharma", "200 mg", "Capsule", True, "Gold-standard oral therapy for recalcitrant onychomycosis and extensive tinea cruris.", 265.0, 230.0),
    ("Itaspor 200", "Itraconazole", "Intas Pharmaceuticals", "200 mg", "Capsule", True, "High-bioavailability pellet technology itraconazole for systemic mycoses.", 285.0, 248.0),
    ("Forcan 150", "Fluconazole", "Cipla Ltd", "150 mg", "Tablet", True, "Single-dose oral triazole curing vaginal candidiasis and systemic thrush.", 35.0, 29.0),
    ("Forcan 200", "Fluconazole", "Cipla Ltd", "200 mg", "Tablet", True, "Weekly oral antifungal therapy for mucosal and cutaneous candidiasis.", 48.0, 40.0),
    ("Tretin 0.025% Gel", "Tretinoin", "Curatio Healthcare", "20 g", "Gel", True, "Topical retinoid accelerating cellular turnover for clearing acne and comedones.", 185.0, 158.0),
    ("Tretin 0.05% Cream", "Tretinoin", "Curatio Healthcare", "20 g", "Cream", True, "Prescription strength retinoid for cystic acne and photoaging skin repair.", 245.0, 212.0),
    ("Sotret 20", "Isotretinoin", "Ranbaxy / Sun Pharma", "20 mg", "Capsule", True, "Systemic oral retinoid permanently curing severe recalcitrant nodulocystic acne.", 395.0, 345.0),
    ("Calasoft Lotion", "Calamine + Light Liquid Paraffin", "Ipca Laboratories", "100 ml", "Lotion", False, "Soothing antipruritic lotion cooling sunburn, insect bites, prickly heat and chickenpox.", 145.0, 125.0),

    # =========================================================================
    # 12. OPHTHALMOLOGY & ENT (20 items)
    # =========================================================================
    ("Ciplox Eye/Ear Drops", "Ciprofloxacin", "Cipla Ltd", "0.3% w/v", "Eye Drops", False, "Broad-spectrum antibiotic drops for bacterial conjunctivitis, corneal ulcers and ear discharge.", 22.0, 18.0),
    ("Vigamox 0.5% Drops", "Moxifloxacin", "Alcon / Novartis", "5 ml", "Eye Drops", True, "Fourth-generation fluoroquinolone eye drops for severe bacterial eye infections.", 345.0, 300.0),
    ("Mahaflox 0.5% Drops", "Moxifloxacin", "Mankind Pharma", "5 ml", "Eye Drops", True, "Preservative-safe eye drops for postoperative ophthalmic infection prophylaxis.", 115.0, 98.0),
    ("Tobastar Eye Drops", "Tobramycin", "Mankind Pharma", "5 ml", "Eye Drops", True, "Aminoglycoside ophthalmic solution for acute external ocular bacterial infections.", 65.0, 55.0),
    ("Tobrex Eye Drops", "Tobramycin", "Novartis", "5 ml", "Eye Drops", True, "Gentle, effective antibiotic drops safe for pediatric conjunctivitis and blepharitis.", 185.0, 160.0),
    ("Glucomol 0.5% Drops", "Timolol Maleate", "Allergan India", "5 ml", "Eye Drops", True, "First-line beta-blocker eye drops reducing intraocular pressure in open-angle glaucoma.", 85.0, 72.0),
    ("Timolol 0.25% Drops", "Timolol Maleate", "Sun Pharma", "5 ml", "Eye Drops", True, "Low-dose beta blocker drop for ocular hypertension with minimal cardiac absorption.", 55.0, 46.0),
    ("Xalatan Drops", "Latanoprost", "Pfizer", "2.5 ml", "Eye Drops", True, "Prostaglandin F2-alpha analogue increasing uveoscleral outflow in glaucoma.", 680.0, 595.0),
    ("Latoprost Drops", "Latanoprost", "Sun Pharma", "2.5 ml", "Eye Drops", True, "Once-nightly eye drops significantly reducing intraocular pressure.", 385.0, 335.0),
    ("Lumigan 0.03% Drops", "Bimatoprost", "Allergan India", "3 ml", "Eye Drops", True, "Prostamide analogue offering powerful reduction in stubborn intraocular pressure.", 720.0, 630.0),
    ("Careprost Drops", "Bimatoprost", "Sun Pharma", "3 ml", "Eye Drops", True, "Effective prostaglandin analogue drops for open angle glaucoma management.", 410.0, 360.0),
    ("Alphagan 0.2% Drops", "Brimonidine Tartrate", "Allergan India", "5 ml", "Eye Drops", True, "Alpha-2 agonist providing dual action: reduces aqueous production and increases outflow.", 525.0, 460.0),
    ("Brimodin Drops", "Brimonidine Tartrate", "Sun Pharma", "5 ml", "Eye Drops", True, "Neuroprotective glaucoma drops lowering elevated eye fluid pressure.", 285.0, 248.0),
    ("Refresh Tears 0.5%", "Carboxymethylcellulose", "Allergan India", "10 ml", "Eye Drops", False, "Preservative-vanishing lubricant eye drops soothing digital eye strain & dry eyes.", 165.0, 142.0),
    ("Optive Eye Drops", "Carboxymethylcellulose + Glycerin", "Allergan India", "10 ml", "Eye Drops", False, "Advanced dual-action osmoprotective lubricating drops for long-lasting dry eye relief.", 245.0, 212.0),
    ("Add Tears Drops", "Carboxymethylcellulose", "Sun Pharma", "10 ml", "Eye Drops", False, "Affordable soothing artificial tears protecting corneal epithelium from burning dryness.", 115.0, 98.0),
    ("Systane Ultra Drops", "Polyethylene Glycol + Propylene Glycol", "Alcon", "10 ml", "Eye Drops", False, "High-performance dry eye therapy forming a protective intelligent shield over cornea.", 445.0, 388.0),
    ("Clearwax Ear Drops", "Paradichlorobenzene + Benzocaine", "Cipla Ltd", "10 ml", "Ear Drops", False, "Cerumenolytic ear drops gently dissolving and softening stubborn impacted earwax.", 95.0, 81.0),
    ("Soliwax Ear Drops", "Paradichlorobenzene + Chlorbutol", "Solvate Labs", "10 ml", "Ear Drops", False, "Fast-acting earwax dissolver with local pain-relieving action.", 88.0, 75.0),
    ("Waxolve Ear Drops", "Paradichlorobenzene + Turpentine Oil", "Torrent Pharmaceuticals", "10 ml", "Ear Drops", False, "Antiseptic and wax-softening formula preventing ear canal blockage.", 92.0, 78.0),

    # =========================================================================
    # 13. INFECTIOUS DISEASES & ANTIMICROBIALS (40 items)
    # =========================================================================
    ("Augmentin 625 Duo", "Amoxicillin + Clavulanic Acid", "GSK India", "500 mg + 125 mg", "Tablet", True, "Gold-standard beta-lactamase inhibitor combo for ENT, chest and skin infections.", 235.0, 204.0),
    ("Augmentin 375", "Amoxicillin + Clavulanic Acid", "GSK India", "250 mg + 125 mg", "Tablet", True, "Pediatric and mild infection antibiotic tablet.", 145.0, 125.0),
    ("Augmentin 1000", "Amoxicillin + Clavulanic Acid", "GSK India", "875 mg + 125 mg", "Tablet", True, "High-potency formulation for severe community-acquired pneumonia and dental abscesses.", 325.0, 280.0),
    ("Clavam 625", "Amoxicillin + Clavulanic Acid", "Alkem Laboratories", "500 mg + 125 mg", "Tablet", True, "Leading hospital and clinic antibiotic overcoming penicillin-resistant pathogens.", 225.0, 195.0),
    ("Moxikind-CV 625", "Amoxicillin + Clavulanic Acid", "Mankind Pharma", "500 mg + 125 mg", "Tablet", True, "Affordable co-amoxiclav antibiotic for respiratory and soft tissue infections.", 195.0, 168.0),
    ("Azee 250", "Azithromycin", "Cipla Ltd", "250 mg", "Tablet", True, "Macrolide antibiotic for mild pharyngitis, tonsillitis and respiratory infections.", 75.0, 64.0),
    ("Azee 500", "Azithromycin", "Cipla Ltd", "500 mg", "Tablet", True, "Once-daily 3-day macrolide antibiotic for chest infections, typhoid and sinusitis.", 135.0, 116.0),
    ("Azithral 500", "Azithromycin", "Alembic Pharmaceuticals", "500 mg", "Tablet", True, "High tissue penetration antibiotic effective against atypical intracellular organisms.", 138.0, 118.0),
    ("Taxim-O 100", "Cefixime", "Alkem Laboratories", "100 mg", "Tablet", True, "Third-generation cephalosporin for pediatric bronchitis and urinary tract infections.", 85.0, 72.0),
    ("Taxim-O 200", "Cefixime", "Alkem Laboratories", "200 mg", "Tablet", True, "Widely prescribed oral cephalosporin for enteric fever (typhoid) and UTI.", 135.0, 116.0),
    ("Ceftas 200", "Cefixime", "Intas Pharmaceuticals", "200 mg", "Tablet", True, "Potent broad-spectrum cephalosporin targeting gram-negative bacterial infections.", 125.0, 108.0),
    ("Mahacef 200", "Cefixime", "Mankind Pharma", "200 mg", "Tablet", True, "Cost-effective third-generation cephalosporin for respiratory and renal infections.", 115.0, 98.0),
    ("Ceftas-O 200", "Cefixime + Ofloxacin", "Intas Pharmaceuticals", "200 mg + 200 mg", "Tablet", True, "Potent dual antibiotic for complicated urinary tract and respiratory infections.", 168.0, 145.0),
    ("Taxim-O OF", "Cefixime + Ofloxacin", "Alkem Laboratories", "200 mg + 200 mg", "Tablet", True, "Synergistic cephalosporin and quinolone combo for multi-drug resistant typhoid.", 175.0, 150.0),
    ("Cefakind 250", "Cefuroxime Axetil", "Mankind Pharma", "250 mg", "Tablet", True, "Second-generation oral cephalosporin for acute bacterial sinusitis and otitis media.", 145.0, 125.0),
    ("Cefakind 500", "Cefuroxime Axetil", "Mankind Pharma", "500 mg", "Tablet", True, "High-strength cephalosporin for severe lower respiratory tract and bone infections.", 285.0, 245.0),
    ("Cetil 500", "Cefuroxime Axetil", "Lupin Ltd", "500 mg", "Tablet", True, "Premium quality beta-lactamase stable antibiotic for post-surgical wound care.", 315.0, 275.0),
    ("Gudcef 100", "Cefpodoxime Proxetil", "Mankind Pharma", "100 mg", "Tablet", True, "Oral extended-spectrum cephalosporin for pediatric and adolescent bacterial infections.", 115.0, 98.0),
    ("Gudcef 200", "Cefpodoxime Proxetil", "Mankind Pharma", "200 mg", "Tablet", True, "Superior oral antibiotic for acute community-acquired pneumonia and gonococcal urethritis.", 195.0, 168.0),
    ("Monocef-O 200", "Cefpodoxime Proxetil", "Aristo Pharmaceuticals", "200 mg", "Tablet", True, "High bioavailability cephalosporin delivering reliable tissue concentrations.", 190.0, 165.0),
    ("Monocef 1g", "Ceftriaxone Sodium", "Aristo Pharmaceuticals", "1 g", "Injection", True, "Hospital standard IV/IM broad-spectrum cephalosporin for meningitis, sepsis and typhoid.", 65.0, 55.0),
    ("Monocef 2g", "Ceftriaxone Sodium", "Aristo Pharmaceuticals", "2 g", "Injection", True, "High-dose intravenous cephalosporin for severe hospital-acquired intra-abdominal sepsis.", 125.0, 108.0),
    ("Cifran 500", "Ciprofloxacin", "Sun Pharma", "500 mg", "Tablet", True, "Classic broad-spectrum fluoroquinolone for severe bacterial gastroenteritis and prostatitis.", 115.0, 98.0),
    ("Ciplox 500", "Ciprofloxacin", "Cipla Ltd", "500 mg", "Tablet", True, "Reliable bactericidal quinolone for bone and joint, skin and urinary tract infections.", 108.0, 92.0),
    ("Levomac 500", "Levofloxacin", "Macleods Pharmaceuticals", "500 mg", "Tablet", True, "Respiratory fluoroquinolone with outstanding coverage against Streptococcus pneumoniae.", 115.0, 98.0),
    ("Levomac 750", "Levofloxacin", "Macleods Pharmaceuticals", "750 mg", "Tablet", True, "High-dose once-daily quinolone for acute pyelonephritis and nosocomial pneumonia.", 165.0, 142.0),
    ("Zanocin 200", "Ofloxacin", "Sun Pharma", "200 mg", "Tablet", True, "Broad-spectrum fluoroquinolone for pelvic inflammatory disease and dysentery.", 85.0, 72.0),
    ("O2 Tablet", "Ofloxacin + Ornidazole", "Medley Pharmaceuticals", "200 mg + 500 mg", "Tablet", True, "India's top dual antibiotic and antiprotozoal for acute diarrhea and mixed bowel infections.", 145.0, 125.0),
    ("Doxy-1 100", "Doxycycline", "USV Ltd", "100 mg", "Capsule", True, "Broad-spectrum tetracycline antibiotic for acne vulgaris, rickettsial typhus and malaria.", 45.0, 38.0),
    ("Doxt-SL", "Doxycycline + Lactic Acid Bacillus", "Dr. Reddy's", "100 mg", "Capsule", True, "Tetracycline formulated with gut-friendly probiotics preventing antibiotic-associated diarrhea.", 75.0, 64.0),
    ("Flagyl 400", "Metronidazole", "Abbott Healthcare", "400 mg", "Tablet", False, "Nitroimidazole antiprotozoal and anaerobic antibacterial for amoebiasis and giardiasis.", 32.0, 26.0),
    ("Metrogyl 400", "Metronidazole", "J.B. Chemicals", "400 mg", "Tablet", False, "Affordable anaerobic antibiotic clearing dental abscesses and amoebic dysentery.", 28.0, 23.0),
    ("Lizomac 600", "Linezolid", "Macleods Pharmaceuticals", "600 mg", "Tablet", True, "Oxazolidinone antibiotic reserved for multi-drug resistant MRSA and VRE infections.", 385.0, 335.0),
    ("Linid 600", "Linezolid", "Cadila Pharmaceuticals", "600 mg", "Tablet", True, "Bacteriostatic protein synthesis inhibitor targeting resistant Gram-positive pathogens.", 365.0, 318.0),
    ("Uribid 100 SR", "Nitrofurantoin", "Intas Pharmaceuticals", "100 mg", "Tablet", True, "Sustained release urinary antiseptic achieving high concentration in urine for cystitis.", 125.0, 108.0),
    ("Bactrim DS", "Trimethoprim + Sulfamethoxazole", "Abbott Healthcare", "160 mg + 800 mg", "Tablet", True, "Double-strength co-trimoxazole for PCP pneumonia, chronic bronchitis and shigellosis.", 35.0, 29.0),
    ("Zovirax 400", "Acyclovir", "GSK India", "400 mg", "Tablet", True, "Antiviral nucleoside analogue stopping herpes simplex, cold sores and genital herpes.", 95.0, 81.0),
    ("Herperax 800", "Acyclovir", "Micro Labs Ltd", "800 mg", "Tablet", True, "High-strength antiviral suppressing painful shingles (herpes zoster) outbreaks.", 195.0, 168.0),
    ("Fluvir 75", "Oseltamivir Phosphate", "Hetero Healthcare", "75 mg", "Capsule", True, "Neuraminidase inhibitor shortening duration and severity of influenza A (H1N1) and B.", 585.0, 510.0),
    ("Zentel 400", "Albendazole", "GSK India", "400 mg", "Tablet", False, "Single-dose chewable anthelmintic eliminating roundworm, pinworm and tapeworm.", 18.0, 15.0),

    # =========================================================================
    # 14. GENERAL ANALGESICS, ANTIPYRETICS & OTC ESSENTIALS (25 items)
    # =========================================================================
    ("Dolo 650", "Paracetamol", "Micro Labs Ltd", "650 mg", "Tablet", False, "India's household antipyretic for viral fevers, body aches and headache relief.", 32.0, 30.0),
    ("Crocin 650", "Paracetamol", "GSK India", "650 mg", "Tablet", False, "Fast-acting Optizorb technology paracetamol for quick fever and pain reduction.", 35.0, 32.5),
    ("Calpol 500", "Paracetamol", "GSK India", "500 mg", "Tablet", False, "Gentle, gastric-friendly antipyretic safe across all ages.", 26.5, 24.0),
    ("Calpol 650", "Paracetamol", "GSK India", "650 mg", "Tablet", False, "Standard strength paracetamol providing 6-hour fever suppression.", 34.0, 31.0),
    ("Calpol 250 Pead", "Paracetamol Paediatric Suspension", "GSK India", "250 mg / 5 ml", "Syrup", False, "Pleasant strawberry syrup relieving childhood fever after vaccination.", 45.0, 39.0),
    ("Brufen 400", "Ibuprofen", "Abbott Healthcare", "400 mg", "Tablet", True, "Anti-inflammatory painkiller for sports injuries, toothache and muscular back pain.", 48.0, 42.0),
    ("Brufen 600", "Ibuprofen", "Abbott Healthcare", "600 mg", "Tablet", True, "High-strength NSAID for severe post-traumatic and orthopedic joint pain.", 72.0, 62.0),
    ("Combiflam", "Ibuprofen + Paracetamol", "Sanofi India", "400 mg + 325 mg", "Tablet", False, "Trusted combination tablet providing rapid relief from severe headaches & body aches.", 52.0, 45.0),
    ("Ibugesic Plus", "Ibuprofen + Paracetamol", "Cipla Ltd", "400 mg + 325 mg", "Tablet", False, "Dual analgesic synergy for acute musculoskeletal pain and fever.", 46.0, 40.0),
    ("Meftal 500", "Mefenamic Acid", "Blue Cross Laboratories", "500 mg", "Tablet", True, "NSAID inhibiting prostaglandin synthesis for dental pain and heavy menstrual bleeding.", 45.0, 38.0),
    ("Meftal-P Suspension", "Mefenamic Acid", "Blue Cross Laboratories", "100 mg / 5 ml", "Syrup", True, "Pediatric antipyretic suspension for resistant high childhood fevers.", 48.0, 41.0),
    ("Drotin-DS", "Drotaverine Hydrochloride", "Walter Bushnell", "80 mg", "Tablet", True, "Antispasmodic medication for smooth muscle spasms, kidney stone pain and severe cramps.", 155.0, 135.0),
    ("Drotin 40", "Drotaverine Hydrochloride", "Walter Bushnell", "40 mg", "Tablet", True, "Pure antispasmodic relieving gallbladder, intestinal and uterine muscle spasms.", 85.0, 72.0),
    ("Buscopan 10", "Hyoscine Butylbromide", "Sanofi India", "10 mg", "Tablet", True, "Targeted antispasmodic relaxing abdominal viscera without systemic atropine side effects.", 45.0, 38.0),
    ("Ultracet", "Tramadol + Paracetamol", "Janssen / J&J", "37.5 mg + 325 mg", "Tablet", True, "Centrally acting dual analgesic for moderate-to-severe post-surgical acute pain.", 195.0, 168.0),
    ("Tramazac 50", "Tramadol Hydrochloride", "Zydus Lifesciences", "50 mg", "Capsule", True, "Opioid agonist for acute orthopedic trauma and severe cancer breakthrough pain.", 75.0, 64.0),
    ("Eldoper 2", "Loperamide Hydrochloride", "Micro Labs Ltd", "2 mg", "Capsule", False, "Antidiarrheal slowing intestinal peristalsis for rapid control of watery acute diarrhea.", 22.0, 18.0),
    ("Electral Sachet", "Oral Rehydration Salts IP", "FDC Ltd", "21.8 g", "Sachet", False, "WHO-recommended oral rehydration salts preventing dehydration in cholera and diarrhea.", 22.0, 19.5),
    ("Prolyte ORS", "Oral Rehydration Salts", "Cipla Ltd", "200 ml", "Drink", False, "Ready-to-drink apple flavored electrolyte drink for instant hydration in heat exhaustion.", 32.0, 28.0),
    ("Gelusil MPS Liquid", "Aluminium + Magnesium + Dimethicone", "Pfizer", "200 ml", "Syrup", False, "Instant soothing antacid and antiflatulent liquid providing heartburn relief.", 110.0, 95.0),
    ("Digene Liquid", "Magnesium Hydroxide + Aluminium Hydroxide", "Abbott Healthcare", "200 ml", "Syrup", False, "Cooling mint antacid neutralizing stomach acid and relieving gastric bloating.", 125.0, 108.0),
    ("Dulcolax 5", "Bisacodyl", "Sanofi India", "5 mg", "Tablet", False, "Overnight stimulant laxative providing gentle relief from constipation in 6 to 8 hours.", 15.0, 12.0),
    ("Cremaffin Liquid", "Liquid Paraffin + Milk of Magnesia", "Abbott Healthcare", "225 ml", "Syrup", False, "Gentle lubricating laxative softening hard stools without habit-forming cramps.", 165.0, 142.0),
    ("Softovac Bowel Regulator", "Isabgol / Psyllium Husk + Herbs", "Lupin Ltd", "100 g", "Powder", False, "Natural dietary fiber powder regulating bowel habits and curing chronic constipation.", 145.0, 128.0),
    ("Disprin", "Aspirin Soluble", "Reckitt Benckiser", "350 mg", "Tablet", False, "Effervescent soluble analgesic tablet for fast relief from migraine and toothache.", 14.0, 12.0),

    # =========================================================================
    # 15. HEMATINICS, VITAMINS, MINERALS & NUTRITIONAL DEFICIENCIES (35 items)
    # =========================================================================
    ("Shelcal 500", "Calcium + Vitamin D3", "Torrent Pharmaceuticals", "500 mg + 250 IU", "Tablet", False, "Essential bone calcium supplement with Vitamin D3 to combat osteoporosis.", 130.0, 115.0),
    ("Shelcal HD", "Calcium + Vitamin D3", "Torrent Pharmaceuticals", "500 mg + 500 IU", "Tablet", False, "High-dose Vitamin D3 formulation optimizing intestinal calcium absorption in osteopenia.", 165.0, 142.0),
    ("Shelcal XT", "Calcium + Vitamin D3 + B12", "Torrent Pharmaceuticals", "Standard", "Tablet", False, "Comprehensive bone and nerve supplement for postmenopausal and elderly bone health.", 225.0, 194.0),
    ("Gemcal", "Calcitriol + Calcium Carbonate + Zinc", "Alkem Laboratories", "Standard", "Capsule", False, "Active calcitriol softgel for renal osteodystrophy and severe bone demineralization.", 245.0, 212.0),
    ("Cipcal 500", "Calcium + Vitamin D3", "Cipla Ltd", "500 mg + 250 IU", "Tablet", False, "High-purity elemental calcium for pregnancy, lactation and fracture healing.", 115.0, 98.0),
    ("Uprise-D3 60K", "Cholecalciferol (Vitamin D3)", "Alkem Laboratories", "60,000 IU", "Capsule", True, "High-potency weekly Vitamin D3 therapy restoring severe skeletal deficiency levels.", 280.0, 240.0),
    ("Calcirol 60K Sachet", "Cholecalciferol", "Cadila Pharmaceuticals", "60,000 IU", "Sachet", True, "Granular Vitamin D3 sachet dissolved in milk for rapid bone mineralization.", 65.0, 56.0),
    ("D3-Must 60K", "Cholecalciferol", "Mankind Pharma", "60,000 IU", "Capsule", True, "Weekly high-strength Vitamin D3 softgel curing bone pain and hypocalcemia.", 195.0, 168.0),
    ("Depura 60K Drops", "Cholecalciferol Solution", "Sanofi India", "5 ml", "Drops", True, "Oral drops technology ensuring high bioavailability of Vitamin D in pediatrics & elderly.", 95.0, 82.0),
    ("Neurobion Forte", "Vitamin B1 + B6 + B12", "Procter & Gamble", "Standard", "Tablet", False, "Neurotropic B-vitamin formulation supporting nerve regeneration and tingling numbness.", 45.0, 38.0),
    ("Cobadex CZS", "B-Complex + Zinc + Selenium", "GSK India", "Standard", "Tablet", False, "Antioxidant multivitamin improving nerve conduction and wound healing in diabetics.", 85.0, 72.0),
    ("Becosules Z", "B-Complex + Zinc + Vitamin C", "Pfizer", "Standard", "Capsule", False, "Therapeutic multivitamin formula for mouth ulcers, recovery fatigue, hair vitality and immunity.", 55.0, 48.0),
    ("Becosules", "Vitamin B-Complex + Vitamin C", "Pfizer", "Standard", "Capsule", False, "Classic multivitamin capsule relieving stomatitis and nutritional exhaustion.", 48.0, 41.0),
    ("Nurokind-Plus RF", "Mecobalamin + Alpha Lipoic Acid", "Mankind Pharma", "Standard", "Capsule", False, "Powerful nerve protective antioxidant and methylcobalamin formula for sciatica.", 135.0, 116.0),
    ("Nurokind-LC", "Levocarnitine + Mecobalamin + Folic Acid", "Mankind Pharma", "Standard", "Tablet", False, "Treats painful nocturnal leg cramps, muscular fatigue and diabetic neuropathy.", 195.0, 168.0),
    ("Methycobal 500", "Methylcobalamin (Active B12)", "Wockhardt", "500 mcg", "Tablet", False, "Neurologically active Vitamin B12 repairing damaged peripheral nerve myelin sheaths.", 165.0, 142.0),
    ("Limcee 500", "Vitamin C (Ascorbic Acid)", "Abbott Healthcare", "500 mg", "Chewable Tablet", False, "Orange-flavored chewable antioxidant boosting immune defenses and collagen synthesis.", 30.0, 25.0),
    ("Celin 500", "Vitamin C", "Koye Pharmaceuticals", "500 mg", "Chewable Tablet", False, "Immune-fortifying ascorbic acid tablet for capillary strength and skin healing.", 28.0, 23.0),
    ("Orofer-XT", "Ferrous Ascorbate + Folic Acid", "Emcure Pharmaceuticals", "100 mg + 1.5 mg", "Tablet", False, "High absorption elemental iron restoring hemoglobin without causing gastric upset.", 185.0, 158.0),
    ("Autrin", "Ferrous Fumarate + B12 + Folic Acid", "Pfizer", "Standard", "Capsule", False, "Complete hematinic capsule replenishing red blood cell stores in chronic anemia.", 145.0, 124.0),
    ("Dexorange Syrup", "Ferric Ammonium Citrate + B12 + Folic Acid", "Franco-Indian Pharmaceuticals", "200 ml", "Syrup", False, "India's beloved cherry-flavored hematinic syrup curing nutritional weakness and anemia.", 165.0, 142.0),
    ("Dexorange Capsules", "Ferric Ammonium Citrate + B12", "Franco-Indian Pharmaceuticals", "30 Capsules", "Capsule", False, "Convenient oral iron capsules overcoming post-surgical and pregnancy blood loss.", 175.0, 150.0),
    ("Folvite 5", "Folic Acid", "Pfizer", "5 mg", "Tablet", False, "Essential Vitamin B9 preventing neural tube defects in pregnancy and macrocytic anemia.", 75.0, 64.0),
    ("Supradyn Daily", "Multivitamin + Multi-mineral", "Bayer", "Standard", "Tablet", False, "Daily vitality multivitamin with zinc, iron and essential trace elements for active lifestyles.", 75.0, 65.0),
    ("Zincovit", "Multivitamin + Zinc", "Apex Laboratories", "Standard", "Tablet", False, "Number one doctor-recommended zinc-enriched multivitamin boosting immune recovery.", 115.0, 98.0),
    ("Zincovit Syrup", "Multivitamin + Zinc Paediatric", "Apex Laboratories", "200 ml", "Syrup", False, "Growth-promoting multivitamin syrup stimulating appetite and stamina in children.", 135.0, 116.0),
    ("A to Z NS", "Multivitamin + Lycopene + Zinc", "Alkem Laboratories", "Standard", "Tablet", False, "Antioxidant multivitamin formulation defending against vascular oxidative damage.", 145.0, 125.0),
    ("Revital H Men", "Ginseng + Multivitamins + Minerals", "Sun Pharma", "Standard", "Capsule", False, "Energy booster softgel fighting daily physical exhaustion and mental lethargy.", 125.0, 108.0),
    ("Revital H Woman", "Ginseng + Iron + Calcium", "Sun Pharma", "Standard", "Capsule", False, "Targeted female nutritional vitality formula supporting bone strength and stamina.", 145.0, 124.0),
    ("Evion 400", "Vitamin E (Tocopheryl Acetate)", "Procter & Gamble", "400 mg", "Capsule", False, "Potent lipid antioxidant protecting cell membranes, muscle recovery and hair health.", 38.0, 32.0),
    ("Evion 600", "Vitamin E", "Procter & Gamble", "600 mg", "Capsule", False, "High-strength Vitamin E softgel for severe nocturnal leg cramps and non-alcoholic fatty liver.", 58.0, 49.0),
    ("CoQ10 100", "Coenzyme Q10 (Ubiquinone)", "Alkem Laboratories", "100 mg", "Capsule", False, "Mitochondrial bioenergetic nutrient preventing statin-induced muscle myopathy.", 485.0, 420.0),
    ("Ubicar 100", "Ubidecarenone (CoQ10) + L-Carnitine", "Fourrts Laboratories", "100 mg + 500 mg", "Tablet", False, "Cardioprotective and sperm vitality supplement enhancing cellular ATP production.", 565.0, 495.0),
    ("Benalgis 100", "Benfotiamine", "Sun Pharma", "100 mg", "Tablet", True, "Lipid-soluble active thiamine derivative blocking damaging advanced glycation end-products.", 245.0, 212.0),
    ("Maxirich", "Multivitamins + Minerals + Ginseng", "Cipla Ltd", "Standard", "Capsule", False, "Comprehensive wellness supplement boosting immunity and daily performance.", 110.0, 95.0),
]

def seed_medicines():
    db = SessionLocal()
    try:
        from sqlalchemy import text
        try:
            db.execute(text("SELECT setval('medicines_id_seq', (SELECT COALESCE(MAX(id), 1) FROM medicines));"))
            db.execute(text("SELECT setval('pharmacy_inventory_id_seq', (SELECT COALESCE(MAX(id), 1) FROM pharmacy_inventory));"))
            db.commit()
        except Exception:
            db.rollback()

        print("=" * 80)
        print(f"[*] MediLoop Master Pharmaceutical Seeder: Loading {len(REAL_INDIAN_MEDICINES)} Records")
        print("=" * 80)

        # 1. Fetch all existing pharmacies
        pharmacies = db.query(Pharmacy).all()
        if not pharmacies:
            print("[-] No pharmacies found in database! Creating default pharmacy...")
            default_pharm = Pharmacy(
                pharmacy_name="MediLoop Central Super Pharmacy",
                license_number="DL-CENTRAL-2026-001",
                address="100 Healthcare Hub Boulevard, Suite 10",
                city="Bengaluru",
                state="Karnataka",
                pincode="560001",
                phone_number="+91 80 4455 6677",
                email="central@mediloop.com",
                supports_home_delivery=True,
                estimated_delivery_minutes=25,
                is_active=True
            )
            db.add(default_pharm)
            db.commit()
            db.refresh(default_pharm)
            pharmacies = [default_pharm]

        print(f"[+] Found {len(pharmacies)} dispensing pharmacies in system.")

        today = date.today()
        added_count = 0
        updated_count = 0
        inventory_count = 0

        for idx, item in enumerate(REAL_INDIAN_MEDICINES, 1):
            brand_name, generic_name, manufacturer, strength, dosage_form, rx_req, description, mrp, selling_price = item

            # Check if medicine already exists
            med = db.query(Medicine).filter(Medicine.brand_name == brand_name).first()
            if not med:
                med = Medicine(
                    brand_name=brand_name,
                    generic_name=generic_name,
                    manufacturer=manufacturer,
                    strength=strength,
                    dosage_form=dosage_form,
                    prescription_required=rx_req,
                    description=description,
                    is_active=True
                )
                db.add(med)
                db.commit()
                db.refresh(med)
                added_count += 1
            else:
                med.generic_name = generic_name
                med.manufacturer = manufacturer
                med.strength = strength
                med.dosage_form = dosage_form
                med.prescription_required = rx_req
                med.description = description
                med.is_active = True
                db.commit()
                db.refresh(med)
                updated_count += 1

            # Seed inventory for this medicine in every pharmacy
            for p_idx, pharm in enumerate(pharmacies):
                inv = db.query(PharmacyInventory).filter(
                    PharmacyInventory.pharmacy_id == pharm.id,
                    PharmacyInventory.medicine_id == med.id
                ).first()

                # Generate realistic batches and stock
                batch_number = f"BAT-{pharm.id:02d}-{med.id:04d}"
                # Expiry 1 to 2.5 years ahead
                expiry = today + timedelta(days=365 + ((idx * 7 + p_idx * 13) % 400))
                
                # Realistic stock variation: 95% plentiful, 5% low/out of stock
                seed_val = (idx * 31 + p_idx * 17) % 100
                if seed_val == 0:
                    stock = 0
                elif seed_val < 5:
                    stock = 6
                else:
                    stock = 45 + ((idx * 3 + p_idx * 7) % 95)

                if not inv:
                    inv = PharmacyInventory(
                        pharmacy_id=pharm.id,
                        medicine_id=med.id,
                        stock_quantity=stock,
                        selling_price=selling_price,
                        mrp=mrp,
                        batch_number=batch_number,
                        expiry_date=expiry,
                        is_available=(stock > 0)
                    )
                    db.add(inv)
                    inventory_count += 1
                else:
                    inv.stock_quantity = stock
                    inv.selling_price = selling_price
                    inv.mrp = mrp
                    inv.is_available = (stock > 0)
                    inv.expiry_date = expiry

            if idx % 50 == 0 or idx == len(REAL_INDIAN_MEDICINES):
                db.commit()
                print(f"  Processed {idx}/{len(REAL_INDIAN_MEDICINES)} pharmaceuticals...")

        db.commit()

        total_meds = db.query(Medicine).count()
        total_inv = db.query(PharmacyInventory).count()

        print("\n" + "=" * 80)
        print("[SUCCESS] Pharmaceutical Seeding Completed!")
        print(f"  * New Medicines Added:     {added_count}")
        print(f"  * Existing Meds Synced:    {updated_count}")
        print(f"  * Total Active Medicines:  {total_meds}")
        print(f"  * Total Inventory Records: {total_inv}")
        print("=" * 80)

    except Exception as e:
        db.rollback()
        print(f"[-] Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_medicines()
