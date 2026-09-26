"""
ai_extractor.py
Natural language extraction module for OurScheme.
Extracts structured demographic and social fields from free-form user text.
Supports Gemini/OpenAI API via environment variables, with a resilient rule-based/regex NLP fallback.
"""

import os
import re
import json

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Delhi", "Jammu and Kashmir", "Ladakh"
]

def extract_profile_with_llm(text):
    """
    Attempts to extract structured profile using Gemini or OpenAI API if key is available in environment.
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = f"""
            Extract the following parameters from this user description into pure JSON:
            - age (integer, default 0 if not mentioned)
            - gender (string: "Male", "Female", or "Other", default "Other")
            - state (string: Indian state name, default "")
            - district (string, default "")
            - category (string: "General", "OBC", "SC", or "ST", default "General")
            - income (numeric annual income in rupees, e.g. 2 lakh is 200000, default 0)
            - disability (string: "Yes" or "No", default "No")
            - education (string: e.g. "10th", "12th", "Undergraduate", "Graduate", etc., default "")
            - occupation (string: e.g. "Student", "Farmer", "Unemployed", etc., default "")
            - farmer (string: "Yes" or "No", default "No")
            - area_type (string: "Rural" or "Urban", default "All")
            - house_owner (string: "Yes" or "No", default "No")
            - business_interest (string: "Yes" or "No", default "No")
            - employment_seeking (string: "Yes" or "No", default "No")

            User description: "{text}"
            Return ONLY a valid JSON object without markdown or code fences.
            """
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            raw = response.text.strip()
            # Clean possible markdown formatting
            if raw.startswith("```"):
                raw = re.sub(r"^```[a-z]*\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)
            return json.loads(raw)
        except Exception:
            pass

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You extract user demographic profile from text into JSON with keys: age, gender, state, district, category, income, disability, education, occupation, farmer, area_type, house_owner, business_interest, employment_seeking."},
                    {"role": "user", "content": text}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content)
        except Exception:
            pass

    return None


def extract_profile_with_regex(text):
    """
    Robust rule-based and regular expression extractor for Indian citizen profiles.
    Works offline with zero external dependencies.
    """
    text_lower = text.lower()
    profile = {
        "age": 0,
        "gender": "Other",
        "state": "",
        "district": "",
        "category": "General",
        "income": 0,
        "disability": "No",
        "education": "",
        "occupation": "",
        "farmer": "No",
        "area_type": "All",
        "house_owner": "No",
        "business_interest": "No",
        "employment_seeking": "No"
    }

    # 1. Age extraction
    age_match = re.search(r'\b(\d{1,2})\s*(?:years?\s*old|yrs?\s*old|year\s*old|age)\b', text_lower)
    if not age_match:
        age_match = re.search(r'\bage\s*(?:is|:)?\s*(\d{1,2})\b', text_lower)
    if not age_match:
        # e.g., "i am 21"
        age_match = re.search(r'\bi\s*(?:am|m)\s*(\d{1,2})\b', text_lower)
    if age_match:
        val = int(age_match.group(1))
        if 0 < val <= 120:
            profile['age'] = val

    # 2. Gender
    if re.search(r'\b(female|woman|girl|lady|daughter|mother|sister|she)\b', text_lower):
        profile['gender'] = "Female"
    elif re.search(r'\b(male|man|boy|son|father|brother|he)\b', text_lower):
        profile['gender'] = "Male"

    # 3. State
    for st in INDIAN_STATES:
        if re.search(r'\b' + re.escape(st.lower()) + r'\b', text_lower):
            profile['state'] = st
            break

    # 4. Social Category (OBC, SC, ST, General)
    if re.search(r'\bobc\b', text_lower):
        profile['category'] = "OBC"
    elif re.search(r'\bsc\b', text_lower) and not re.search(r'\bscheme\b', text_lower):
        profile['category'] = "SC"
    elif re.search(r'\bst\b', text_lower) and not re.search(r'\bstudent\b', text_lower):
        profile['category'] = "ST"
    elif re.search(r'\bgeneral\b', text_lower):
        profile['category'] = "General"

    # 5. Income
    # "2 lakh", "1.5 lac", "2,50,000", "50 thousand"
    lakh_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|lac|lacs)\b', text_lower)
    if lakh_match:
        profile['income'] = float(lakh_match.group(1)) * 100000
    else:
        thousand_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:thousand|k)\b', text_lower)
        if thousand_match:
            profile['income'] = float(thousand_match.group(1)) * 1000
        else:
            raw_num_match = re.search(r'(?:rs\.?|inr|₹|income(?:\s*is|:)?)\s*(\d[\d,]+)', text_lower)
            if raw_num_match:
                clean_num = raw_num_match.group(1).replace(',', '')
                try:
                    profile['income'] = float(clean_num)
                except ValueError:
                    pass

    # 6. Disability
    neg_dis = re.search(r'(?:no|not|without|don\'t have|dont have|do not have|does not have|no any|without any)\s*(?:a\s*)?(?:disability|handicap|disabled)', text_lower)
    if not neg_dis and re.search(r'\b(disability|disabled|divyang|handicapped|blind|deaf|pwd)\b', text_lower):
        profile['disability'] = "Yes"
    else:
        profile['disability'] = "No"

    # 7. Farmer
    neg_far = re.search(r'(?:not|no|without|don\'t have|dont have|do not have)\s*(?:a\s*)?(?:farmer|kisan)', text_lower)
    if not neg_far and re.search(r'\b(farmer|kisan|agriculture|farming|cultivator)\b', text_lower):
        profile['farmer'] = "Yes"
        if not profile['occupation']:
            profile['occupation'] = "Farmer"
    else:
        profile['farmer'] = "No"

    # 8. Occupation
    if re.search(r'\bstudent\b', text_lower):
        profile['occupation'] = "Student"
        if not profile['education']:
            profile['education'] = "Undergraduate"
    elif re.search(r'\b(business\s*owner|shopkeeper|entrepreneur)\b', text_lower):
        profile['occupation'] = "Business Owner"
        profile['business_interest'] = "Yes"
    elif re.search(r'\bunemployed\b', text_lower):
        profile['occupation'] = "Unemployed"
        profile['employment_seeking'] = "Yes"
    elif re.search(r'\b(self\s*employed|freelancer)\b', text_lower):
        profile['occupation'] = "Self Employed"
    elif re.search(r'\bhomemaker\b', text_lower):
        profile['occupation'] = "Homemaker"
    elif re.search(r'\bretired\b', text_lower):
        profile['occupation'] = "Retired"

    # 9. Area Type
    if re.search(r'\b(rural|village|gramin|panchayat)\b', text_lower):
        profile['area_type'] = "Rural"
    elif re.search(r'\b(urban|city|metro|town)\b', text_lower):
        profile['area_type'] = "Urban"

    # 10. House Ownership
    if re.search(r'\b(own\s*a\s*house|own\s*house|have\s*a\s*house)\b', text_lower):
        profile['house_owner'] = "Yes"
    elif re.search(r'\b(no\s*house|without\s*a?\s*house|homeless|rented|don\'t\s*own\s*a?\s*house)\b', text_lower):
        profile['house_owner'] = "No"

    # 11. Business Interest
    if re.search(r'\b(interested in business|start a business|want to start business|startup|msme)\b', text_lower):
        profile['business_interest'] = "Yes"

    # 12. Employment Seeking
    if re.search(r'\b(looking for (?:a )?job|seeking employment|job seeker|need (?:a )?job|looking for work)\b', text_lower):
        profile['employment_seeking'] = "Yes"

    return profile


def extract_user_profile(user_text):
    """
    Main extraction interface. Tries LLM first, falls back to robust regex NLP.
    """
    if not user_text or not user_text.strip():
        return {
            "age": 0, "gender": "Other", "state": "", "district": "",
            "category": "General", "income": 0, "disability": "No",
            "education": "", "occupation": "", "farmer": "No",
            "area_type": "All", "house_owner": "No",
            "business_interest": "No", "employment_seeking": "No"
        }

    # Try LLM
    profile = extract_profile_with_llm(user_text)
    if profile and isinstance(profile, dict) and profile.get("age"):
        return profile

    # Fallback to regex NLP
    return extract_profile_with_regex(user_text)
