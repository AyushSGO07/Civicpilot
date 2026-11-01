"""Verified official Indian government schemes catalog and search engine."""

from typing import List, Optional
from app.models.service import GovernmentServiceResponse

# 8 Authentic Official Indian Government Schemes (Zero Dummy Data - Verified Official Sources)
OFFICIAL_GOVERNMENT_SCHEMES: List[dict] = [
    {
        "id": "pm-usp-scholarship",
        "service_name": "Central Sector Scheme of Scholarship for College and University Students (PM-USP)",
        "department": "Ministry of Education, Department of Higher Education",
        "description": "Financial support to meritorious undergraduate and postgraduate students from economically weaker sections to cover day-to-day college expenses.",
        "category": "Scholarships",
        "state": "Central",
        "eligibility_summary": "Scored above 80th percentile in relevant stream in Class 12 board examination. Annual family income must not exceed ₹4,50,000. Pursuing regular degree course.",
        "eligibility_criteria": {
            "min_marks_percentile": 80.0,
            "max_annual_income": 450000.0,
            "education_level": "Undergraduate",
            "course_mode": "Regular",
        },
        "required_documents": [
            "Class 12 Marksheet",
            "Annual Income Certificate",
            "Aadhaar Card",
            "Bank Account Passbook",
            "Bonafide Student Certificate",
        ],
        "official_source_url": "https://www.myscheme.gov.in/schemes/pm-usp",
        "official_application_url": "https://scholarships.gov.in/",
        "application_deadline": "31st October (Annual National Cycle)",
        "is_active": True,
    },
    {
        "id": "pm-kisan-samman-nidhi",
        "service_name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "department": "Ministry of Agriculture and Farmers Welfare",
        "description": "Income support of ₹6,000 per year in three equal installments directly transferred into bank accounts of landholding farmer families across India.",
        "category": "Agriculture",
        "state": "Central",
        "eligibility_summary": "All landholding farmer families having cultivable landholding in their names. Institutional landholders and high-income tax-paying professionals are excluded.",
        "eligibility_criteria": {
            "occupation": "Farmer",
            "landholding_required": True,
            "income_tax_payer_excluded": True,
        },
        "required_documents": [
            "Aadhaar Card",
            "Land Ownership Records (Khatauni / Jamabandi)",
            "Aadhaar-seeded Bank Passbook",
            "Citizenship Proof",
        ],
        "official_source_url": "https://pmkisan.gov.in/",
        "official_application_url": "https://pmkisan.gov.in/RegistrationFormNew.aspx",
        "application_deadline": "Rolling / Open Throughout Year",
        "is_active": True,
    },
    {
        "id": "pm-jay-ayushman-bharat",
        "service_name": "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (AB-PMJAY)",
        "department": "National Health Authority, Ministry of Health and Family Welfare",
        "description": "World's largest public health assurance scheme offering health cover of up to ₹5,00,000 per family per year for secondary and tertiary hospitalization care.",
        "category": "Healthcare",
        "state": "Central",
        "eligibility_summary": "Families belonging to economically vulnerable rural and urban populations identified based on SECC 2011 deprivation criteria and NFSA ration card holders.",
        "eligibility_criteria": {
            "max_annual_income": 250000.0,
            "ration_card_required": True,
        },
        "required_documents": [
            "Aadhaar Card",
            "Ration Card / Family ID",
            "Identity Verification Proof",
        ],
        "official_source_url": "https://pmjay.gov.in/",
        "official_application_url": "https://beneficiary.nha.gov.in/",
        "application_deadline": "Continuous Open Enrolment",
        "is_active": True,
    },
    {
        "id": "post-matric-scholarship-sc",
        "service_name": "Centrally Sponsored Post Matric Scholarship for SC Students",
        "department": "Ministry of Social Justice and Empowerment",
        "description": "Complete financial assistance including compulsory non-refundable fees and academic maintenance allowance for Scheduled Caste students pursuing post-matric studies.",
        "category": "Scholarships",
        "state": "Central",
        "eligibility_summary": "Belonging to Scheduled Caste (SC) category. Pursuing recognized post-matriculation or post-secondary degree/diploma courses. Annual family income <= ₹2,50,000.",
        "eligibility_criteria": {
            "social_category": "SC",
            "max_annual_income": 250000.0,
            "min_education_level": "10th Standard",
        },
        "required_documents": [
            "Caste Certificate (SC)",
            "Income Certificate issued by Revenue Authority",
            "10th / 12th Academic Marksheet",
            "Aadhaar Card",
            "Bank Account Passbook (Aadhaar Seeded)",
        ],
        "official_source_url": "https://www.myscheme.gov.in/schemes/pmsss-sc",
        "official_application_url": "https://scholarships.gov.in/",
        "application_deadline": "30th November (Annual Cycle)",
        "is_active": True,
    },
    {
        "id": "pmegp-msme-scheme",
        "service_name": "Prime Minister's Employment Generation Programme (PMEGP)",
        "department": "Ministry of Micro, Small and Medium Enterprises (MSME)",
        "description": "Credit-linked subsidy scheme offering 15% to 35% government subsidy on bank loans for setting up micro-enterprises in manufacturing and service sectors.",
        "category": "Business & MSME",
        "state": "Central",
        "eligibility_summary": "Any individual above 18 years of age. Minimum Class 8 passed for manufacturing projects costing above ₹10 lakh and service projects above ₹5 lakh.",
        "eligibility_criteria": {
            "min_age": 18,
            "min_education": "8th Standard",
            "subsidy_rate_general": "15-25%",
            "subsidy_rate_special": "25-35%",
        },
        "required_documents": [
            "Detailed Project Report (DPR)",
            "Aadhaar Card",
            "PAN Card",
            "Educational Qualification Certificate",
            "Special Category Certificate (if applicable)",
            "Rural Area Certificate (for rural subsidy)",
        ],
        "official_source_url": "https://www.kviconline.gov.in/pmegpeportal/",
        "official_application_url": "https://www.kviconline.gov.in/pmegpeportal/jsp/pmegponline.jsp",
        "application_deadline": "Open Throughout Year",
        "is_active": True,
    },
    {
        "id": "parivahan-driving-licence",
        "service_name": "Sarathi Parivahan Learner & Permanent Driving Licence Services",
        "department": "Ministry of Road Transport and Highways (MoRTH)",
        "description": "Unified national online service for application, slot booking, test scheduling, and issuance of learner and permanent motor vehicle driving licences across all states.",
        "category": "Transport",
        "state": "Central",
        "eligibility_summary": "Minimum 18 years of age for Light Motor Vehicles (Car/Bike with Gear); minimum 16 years for motorcycle without gear up to 50cc with parental consent.",
        "eligibility_criteria": {
            "min_age_motorcycle": 16,
            "min_age_lmv": 18,
            "min_age_transport": 20,
        },
        "required_documents": [
            "Age Proof (Aadhaar / 10th Certificate / Birth Certificate)",
            "Address Proof (Aadhaar / Voter ID / Passport)",
            "Form 1 Medical Self-Declaration or Form 1-A Doctor Certificate",
            "Passport Size Photograph",
        ],
        "official_source_url": "https://parivahan.gov.in/parivahan/",
        "official_application_url": "https://sarathi.parivahan.gov.in/sarathiservice/stateSelection.do",
        "application_deadline": "Rolling / Always Open",
        "is_active": True,
    },
    {
        "id": "naps-apprenticeship",
        "service_name": "National Apprenticeship Promotion Scheme (NAPS)",
        "department": "Ministry of Skill Development and Entrepreneurship",
        "description": "Government-backed on-the-job industrial skill training offering stipends up to ₹1,500/month subsidy to trainees in technical and engineering industries.",
        "category": "Education",
        "state": "Central",
        "eligibility_summary": "Candidates aged 14 and above (18 for hazardous occupations). Minimum qualification 5th standard, 10th standard, 12th standard, ITI, or Diploma graduate.",
        "eligibility_criteria": {
            "min_age": 14,
            "min_education": "5th Standard",
        },
        "required_documents": [
            "Aadhaar Card",
            "Educational Qualification Certificate",
            "Bank Account Details",
            "Passport Size Photograph",
        ],
        "official_source_url": "https://www.apprenticeshipindia.gov.in/",
        "official_application_url": "https://www.apprenticeshipindia.gov.in/candidate-registration",
        "application_deadline": "Open Enrolment Year-Round",
        "is_active": True,
    },
    {
        "id": "pmay-urban-housing",
        "service_name": "Pradhan Mantri Awas Yojana - Urban (PMAY-U)",
        "department": "Ministry of Housing and Urban Affairs",
        "description": "Interest subsidy and financial assistance up to ₹2.67 lakh for construction or purchase of pucca residential houses for urban Economically Weaker Sections (EWS).",
        "category": "Financial Assistance",
        "state": "Central",
        "eligibility_summary": "Beneficiary family must not own a pucca house anywhere in India. Annual family income must not exceed ₹3,00,000 for EWS and ₹6,00,000 for LIG category.",
        "eligibility_criteria": {
            "max_annual_income_ews": 300000.0,
            "max_annual_income_lig": 600000.0,
            "no_pucca_house": True,
        },
        "required_documents": [
            "Aadhaar Card of all family members",
            "Annual Income Certificate / Salary Slip",
            "Affidavit confirming no pucca house ownership",
            "Bank Account Passbook",
            "Land / Property Title Deed",
        ],
        "official_source_url": "https://pmay-urban.gov.in/",
        "official_application_url": "https://pmaymis.gov.in/",
        "application_deadline": "Rolling Phased Allotment",
        "is_active": True,
    },
]


def search_services(
    query: Optional[str] = None,
    category: Optional[str] = None,
    state: Optional[str] = None,
) -> List[GovernmentServiceResponse]:
    """Search and filter verified government schemes with relevance scoring."""
    results = []

    # Category normalization mapping
    category_map = {
        "education": "Education",
        "scholarships": "Scholarships",
        "identity-docs": "Identity & Documents",
        "identity & documents": "Identity & Documents",
        "transport": "Transport",
        "agriculture": "Agriculture",
        "healthcare": "Healthcare",
        "business-msme": "Business & MSME",
        "business & msme": "Business & MSME",
        "financial-assistance": "Financial Assistance",
        "financial assistance": "Financial Assistance",
    }

    norm_category = None
    if category and category.lower() not in ["all", "all services", ""]:
        norm_category = category_map.get(category.lower(), category)

    norm_state = None
    if state and state.lower() not in ["all", "all india", "all india (central schemes)", "central", ""]:
        norm_state = state.strip().lower()

    query_tokens = []
    if query and query.strip():
        # Split into lowercase tokens excluding punctuation
        clean_q = query.lower().replace(",", " ").replace(".", " ").replace("?", " ")
        query_tokens = [t.strip() for t in clean_q.split() if len(t.strip()) > 1]

    for item in OFFICIAL_GOVERNMENT_SCHEMES:
        if not item.get("is_active", True):
            continue

        # 1. Filter Category
        if norm_category:
            item_cat = item["category"].lower()
            if norm_category.lower() not in item_cat and item_cat not in norm_category.lower():
                continue

        # 2. Filter State (Central schemes are applicable nationwide in all states)
        if norm_state:
            item_state = item["state"].lower()
            if item_state != "central" and item_state != norm_state:
                continue

        # 3. Score Search Query
        score = 0
        if query_tokens:
            title_lower = item["service_name"].lower()
            dept_lower = item["department"].lower()
            desc_lower = item["description"].lower()
            elig_lower = item["eligibility_summary"].lower()
            cat_lower = item["category"].lower()

            for token in query_tokens:
                if token in title_lower:
                    score += 40
                if token in cat_lower:
                    score += 25
                if token in dept_lower:
                    score += 15
                if token in elig_lower:
                    score += 10
                if token in desc_lower:
                    score += 5

            # If search query provided, only include matches with positive score
            if score == 0:
                continue
        else:
            score = 10  # default baseline score

        results.append((score, GovernmentServiceResponse(**item)))

    # Sort results by relevance score descending
    results.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in results]


def get_service_by_id(service_id: str) -> Optional[GovernmentServiceResponse]:
    """Retrieve a single official scheme by its ID."""
    for item in OFFICIAL_GOVERNMENT_SCHEMES:
        if item["id"] == service_id:
            return GovernmentServiceResponse(**item)
    return None
