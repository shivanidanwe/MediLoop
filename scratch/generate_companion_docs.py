import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def create_template():
    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(0.7)
        s.bottom_margin = Inches(0.7)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)

    NAVY = RGBColor(27, 54, 93)
    SLATE = RGBColor(44, 82, 130)
    CHARCOAL = RGBColor(31, 41, 55)

    def set_cell_background(cell, hex_color):
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shd)

    def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
        tcPr.append(tcMar)

    p0 = doc.add_paragraph()
    p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r0 = p0.add_run("[OFFICIAL PHARMACY / HEALTHCARE ENTERPRISE LETTERHEAD]\n")
    r0.bold = True
    r0.font.size = Pt(14)
    r0.font.color.rgb = NAVY
    r1 = p0.add_run("[PHARMACY / HEALTHCARE ENTERPRISE NAME]\nLicensed Retail Chemists, Druggists & Healthcare Dispensary\n[Shop / Building No., Street, Area, City, State, PIN Code]\nPhone: [Contact Phone] | Official Email: [Email Address]\nDrug Lic. No. (Form 20/21): [XX-XXX-PH-XXXXXX] | GSTIN: [27XXXXXXXXXXXZX]")
    r1.font.size = Pt(9)
    r1.font.color.rgb = SLATE

    p_hr = doc.add_paragraph()
    p_hr.paragraph_format.space_after = Pt(8)
    p_hr_border = parse_xml(r'<w:pBdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:bottom w:val="single" w:sz="16" w:space="1" w:color="1B365D"/></w:pBdr>')
    p_hr._p.get_or_add_pPr().append(p_hr_border)

    p_to = doc.add_paragraph()
    p_to.paragraph_format.space_after = Pt(6)
    p_to.add_run(
        "Ref No.: [ORG/DEPT/SPONSOR/YYYY-YY/XXX]                                        Date: [DD/MM/YYYY]\n\n"
        "To,\n"
        "The Principal / Head of Department,\n"
        "Department of Computer Science & Engineering,\n"
        "[College / Institute of Engineering Name],\n"
        "[Campus Address, City, State, PIN Code]\n\n"
        "SUBJECT: Industry Sponsorship & Technical Collaboration for Final Year Engineering Capstone Project Titled: \"MEDILOOP: AN AGENTIC AI HEALTHCARE & AUTONOMOUS PHARMACY PLATFORM\"\n\n"
        "Respected Sir / Madam,\n\n"
        "We are pleased to formally convey that [Name of Pharmacy / Organization], a licensed retail and community healthcare establishment located at [City, State], has agreed to sponsor and provide technical domain mentorship for the final year engineering capstone project undertaken by your students:\n\n"
        "Candidate Details:\n"
        "- [Student Name 1] (Lead Student Researcher / Project Lead) - Roll No. / PRN: [XXXXXXXX]\n"
        "- [Student Name 2] (Team Member) - Roll No. / PRN: [XXXXXXXX]\n"
        "- [Student Name 3] (Team Member) - Roll No. / PRN: [XXXXXXXX]\n"
        "- [Student Name 4] (Team Member) - Roll No. / PRN: [XXXXXXXX]\n\n"
        "1. Problem Background & Industry Relevance:\n"
        "In our day-to-day retail pharmacy operations, deciphering handwritten physician prescriptions, verifying clinical dosage safety against patient allergy histories, preventing adverse drug-drug interactions (ADEs), and managing unpredictable medication stock depletion represent severe daily operational bottlenecks. The proposed engineering solution directly addresses these critical operational and patient safety challenges.\n\n"
        "2. Scope of Sponsorship & Facilities Provided:\n"
        "a. Clinical & Regulatory Guidance: Access to licensed registered pharmacists to formulate clinical dispensing rules, Indian pharmacopeia standards, and Schedule H/X compliance rules.\n"
        "b. Pharmaceutical Catalog Data: A curated dataset of genuine pharmaceutical formulations (generic names, dosages, strengths, manufacturers, and trade pricing).\n"
        "c. Real-World Prescription Samples: Anonymized historical prescription scans for training and benchmarking optical character recognition pipelines under strict patient confidentiality.\n"
        "d. Pilot Dispensary Testbed: Provision of our retail counter as an experimental pilot environment to evaluate the mobile application and pharmacist web console under realistic dispensary conditions.\n"
        "e. Supply Chain Validation: Pharmacist review and verification of automated stock replenishment algorithms and distributor purchase orders.\n\n"
        "3. Terms of Collaboration:\n"
        "This sponsorship is an industry-academic technical collaboration and facility support agreement with zero financial liability on the students or your academic institution. All intellectual property developed shall be utilized for academic evaluation, research publications, and capstone degree fulfillment in accordance with university norms.\n\n"
        "Yours Faithfully,\n"
        "For [NAME OF PHARMACY / HEALTHCARE ENTERPRISE]\n\n\n"
        "__________________________________________             [ OFFICIAL PHARMACY STAMP / SEAL ]\n"
        "[Authorized Signatory / Proprietor Name]\n"
        "Designation: Chief Pharmacist / Managing Director\n"
        "Qualification: M.Pharm / B.Pharm\n"
        "State Pharmacy Council Reg. No.: [MSPC-XXXXXX]\n"
        "Contact: [Phone / Mobile Number]"
    )

    doc.save("General_Pharmacy_Sponsorship_Template.docx")
    print("Saved General_Pharmacy_Sponsorship_Template.docx")

if __name__ == "__main__":
    create_template()
