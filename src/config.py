from typing import Dict, List

# Application settings
APP_TITLE = "Salary Analyzer Pro"
APP_DESCRIPTION = """
Analyze salaries based on experience, skills, industry, and company size.
Get detailed insights and recommendations for your career growth.
"""

# Input configurations
EXPERIENCE_RANGE = range(0, 31)  # 0-30 years
COMPANY_SIZES = [
    "Startup (1-50)",
    "Small (51-200)",
    "Medium (201-1000)",
    "Large (1001-5000)",
    "Enterprise (5000+)"
]

# Industry sectors with common roles
INDUSTRY_SECTORS: Dict[str, List[str]] = {
    "Technology": [
        "Software Engineer",
        "AI Engineer",
        "Data Scientist",
        "Product Manager",
        "DevOps Engineer",
        "UI/UX Designer",
        "Prompt Engineer",
        "Data Engineer",
        "Data Analyst",
        
    ],
    "Finance": [
        "Financial Analyst",
        "Investment Banker",
        "Risk Manager",
        "Quantitative Analyst",
        "Financial Software Developer"
    ],
    "Healthcare": [
        "Clinical Data Analyst",
        "Healthcare Administrator",
        "Medical Software Developer",
        "Biostatistician",
        "Health Informatics Specialist"
    ]
}

# Common skills by role category
SKILLS_BY_CATEGORY: Dict[str, List[str]] = {
    "Technical": [
        "Python", "Java", "AI","JavaScript", "SQL", "AWS",
        "Docker", "Kubernetes", "React", "Node.js", "Machine Learning"
    ],
    "Business": [
        "Project Management", "Agile", "Business Analysis",
        "Strategic Planning", "Product Management"
    ],
    "Soft Skills": [
        "Leadership", "Communication", "Problem Solving",
        "Team Management", "Stakeholder Management"
    ]
}

# Analysis parameters
PERCENTILES = [25, 50, 75, 90]
COMPENSATION_COMPONENTS = [
    "Base Salary",
    "Annual Bonus",
    "Stock/Equity",
    "Benefits"
]