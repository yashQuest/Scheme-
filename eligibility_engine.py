"""
eligibility_engine.py
Deterministic Python rule engine for evaluating government scheme eligibility.
Compares a user's sanitized demographic and social profile with structured scheme requirements.
"""

def normalize_user_profile(data):
    """
    Normalizes and cleans user profile dictionary into standard Python types.
    """
    profile = {}

    # Age
    try:
        profile['age'] = int(data.get('age', 0))
    except (ValueError, TypeError):
        profile['age'] = 0

    # Gender: 'Male', 'Female', 'Other'
    raw_gen = str(data.get('gender', '')).strip().upper()
    if raw_gen in ['M', 'MALE']:
        profile['gender'] = 'Male'
    elif raw_gen in ['F', 'FEMALE']:
        profile['gender'] = 'Female'
    else:
        profile['gender'] = 'Other'

    # State & District
    profile['state'] = str(data.get('state', '')).strip()
    profile['district'] = str(data.get('district', '')).strip()

    # Category: General, OBC, SC, ST
    profile['category'] = str(data.get('category', 'General')).strip()

    # Annual family income
    try:
        profile['income'] = float(data.get('income', 0.0))
    except (ValueError, TypeError):
        profile['income'] = 0.0

    # Disability: 'Yes', 'No'
    raw_dis = str(data.get('disability', '')).strip().lower()
    if raw_dis in ['yes', 'dis_yes', 'true', '1']:
        profile['disability'] = 'Yes'
    else:
        profile['disability'] = 'No'

    # Education
    profile['education'] = str(data.get('education', '')).strip()

    # Occupation
    profile['occupation'] = str(data.get('occupation', '')).strip()

    # Farmer: 'Yes', 'No'
    raw_far = str(data.get('farmer', '')).strip().lower()
    if raw_far in ['yes', 'true', '1'] or profile['occupation'].lower() == 'farmer':
        profile['farmer'] = 'Yes'
    else:
        profile['farmer'] = 'No'

    # Area type: 'Rural', 'Urban'
    raw_area = str(data.get('area_type', '')).strip().capitalize()
    if raw_area in ['Rural', 'Urban']:
        profile['area_type'] = raw_area
    else:
        profile['area_type'] = 'All'

    # House owner: 'Yes', 'No'
    raw_house = str(data.get('house_owner', '')).strip().lower()
    if raw_house in ['yes', 'true', '1']:
        profile['house_owner'] = 'Yes'
    else:
        profile['house_owner'] = 'No'

    # Other preferences
    raw_biz = str(data.get('business_interest', '')).strip().lower()
    profile['business_interest'] = 'Yes' if raw_biz in ['yes', 'true', '1'] else 'No'

    raw_emp = str(data.get('employment_seeking', '')).strip().lower()
    profile['employment_seeking'] = 'Yes' if raw_emp in ['yes', 'true', '1'] else 'No'

    return profile


def evaluate_scheme(scheme, user):
    """
    Evaluates a single scheme against the user profile.
    Returns:
        dict: {
            'is_eligible': bool,
            'match_score': int,
            'status_badge': str,  # 'Eligible', 'Potentially relevant', 'Check official eligibility'
            'match_reasons': list of str,
            'unmatched_reasons': list of str
        }
    """
    reasons = []
    unmatched = []
    score = 10  # Baseline score

    # 1. Age Check
    user_age = user.get('age', 0)
    min_age = scheme.get('min_age')
    max_age = scheme.get('max_age')

    if min_age is not None and user_age < min_age:
        unmatched.append(f"Requires minimum age of {min_age} (you are {user_age})")
        return {'is_eligible': False, 'match_score': 0, 'status_badge': 'Not Eligible', 'reasons': [], 'unmatched': unmatched}

    if max_age is not None and user_age > max_age:
        unmatched.append(f"Requires maximum age of {max_age} (you are {user_age})")
        return {'is_eligible': False, 'match_score': 0, 'status_badge': 'Not Eligible', 'reasons': [], 'unmatched': unmatched}

    if min_age is not None or max_age is not None:
        reasons.append(f"Within age criteria ({min_age or 0} - {max_age or 'any'})")
        score += 15

    # 2. Gender Check
    scheme_gender = str(scheme.get('gender') or 'Any').strip().capitalize()
    user_gender = user.get('gender', 'Other')

    if scheme_gender not in ['Any', 'All', '']:
        if scheme_gender == 'Female' and user_gender != 'Female':
            unmatched.append("Scheme is reserved for women/female beneficiaries")
            return {'is_eligible': False, 'match_score': 0, 'status_badge': 'Not Eligible', 'reasons': [], 'unmatched': unmatched}
        elif scheme_gender == 'Male' and user_gender != 'Male':
            unmatched.append("Scheme is reserved for male beneficiaries")
            return {'is_eligible': False, 'match_score': 0, 'status_badge': 'Not Eligible', 'reasons': [], 'unmatched': unmatched}
        else:
            reasons.append(f"Meets gender criterion ({scheme_gender})")
            score += 25

    # 3. Income Check
    max_income = scheme.get('max_income')
    user_income = user.get('income', 0.0)
    if max_income is not None and max_income > 0:
        if user_income > float(max_income):
            unmatched.append(f"Income exceeds limit of Rs. {max_income:,.0f} (your income: Rs. {user_income:,.0f})")
            return {'is_eligible': False, 'match_score': 0, 'status_badge': 'Not Eligible', 'reasons': [], 'unmatched': unmatched}
        else:
            reasons.append(f"Within income limit (Rs. {max_income:,.0f})")
            score += 20

    # 4. Farmer Requirement
    scheme_farmer = str(scheme.get('farmer') or 'Any').strip().capitalize()
    user_farmer = user.get('farmer', 'No')
    if scheme_farmer == 'Yes':
        if user_farmer != 'Yes':
            unmatched.append("Scheme is exclusively for farmers")
            return {'is_eligible': False, 'match_score': 0, 'status_badge': 'Not Eligible', 'reasons': [], 'unmatched': unmatched}
        else:
            reasons.append("Farmer status confirmed")
            score += 30

    # 5. Disability Requirement
    scheme_disability = str(scheme.get('disability') or 'Any').strip().capitalize()
    user_disability = user.get('disability', 'No')
    if scheme_disability == 'Yes':
        if user_disability != 'Yes':
            unmatched.append("Scheme is exclusively for persons with disabilities (Divyang)")
            return {'is_eligible': False, 'match_score': 0, 'status_badge': 'Not Eligible', 'reasons': [], 'unmatched': unmatched}
        else:
            reasons.append("Disability criterion matched")
            score += 35

    # 6. House Ownership Requirement (e.g. Housing schemes for people with no pucca house)
    scheme_house = str(scheme.get('house_owner') or 'Any').strip().capitalize()
    user_house = user.get('house_owner', 'No')
    if scheme_house == 'No':
        if user_house == 'Yes':
            unmatched.append("Scheme is for families without a pucca house")
            return {'is_eligible': False, 'match_score': 0, 'status_badge': 'Not Eligible', 'reasons': [], 'unmatched': unmatched}
        else:
            reasons.append("Eligible for housing assistance (non-homeowner)")
            score += 25

    # 7. Area Type (Rural / Urban)
    scheme_area = str(scheme.get('area_type') or 'Any').strip().capitalize()
    user_area = user.get('area_type', 'All')
    if scheme_area not in ['Any', 'All', ''] and user_area not in ['Any', 'All', '']:
        if scheme_area != user_area:
            unmatched.append(f"Scheme is designated for {scheme_area} areas (your area: {user_area})")
            return {'is_eligible': False, 'match_score': 0, 'status_badge': 'Not Eligible', 'reasons': [], 'unmatched': unmatched}
        else:
            reasons.append(f"Matches {scheme_area} area development")
            score += 15

    # 8. Social Category
    scheme_soc = str(scheme.get('social_category') or 'Any').strip().upper()
    user_cat = user.get('category', 'General').upper()
    if scheme_soc not in ['ANY', 'ALL', '']:
        allowed_cats = [c.strip() for c in scheme_soc.split(',')]
        if user_cat not in allowed_cats:
            unmatched.append(f"Scheme is for {scheme_soc} category (your category: {user_cat})")
            return {'is_eligible': False, 'match_score': 0, 'status_badge': 'Not Eligible', 'reasons': [], 'unmatched': unmatched}
        else:
            reasons.append(f"Category matched ({user_cat})")
            score += 25

    # 9. Occupation Matching & Alignment
    scheme_occ = str(scheme.get('occupation') or 'Any').strip()
    user_occ = user.get('occupation', '')

    if scheme_occ not in ['Any', 'All', '']:
        if scheme_occ.lower() == user_occ.lower():
            reasons.append(f"Direct match for occupation: {user_occ}")
            score += 30
        elif scheme_occ == 'Business Owner' and user.get('business_interest') == 'Yes':
            reasons.append("Matches your interest in starting or running a business")
            score += 20
        elif scheme_occ == 'Farmer' and user.get('farmer') == 'Yes':
            reasons.append("Farmer occupation matched")
            score += 25
        elif user_occ.lower() in ['unemployed', 'student'] and scheme.get('category_id') == 4:
            # Employment / skill development schemes
            reasons.append("Skill development opportunity for job seekers")
            score += 20
        else:
            # Not an absolute blocker if other fields pass, but reduced score
            pass

    # 10. State Match
    scheme_state = str(scheme.get('state') or 'All').strip()
    user_state = user.get('state', '').strip()
    if scheme_state not in ['All', 'Any', '']:
        if user_state and scheme_state.lower() != user_state.lower():
            unmatched.append(f"Available only in {scheme_state}")
            return {'is_eligible': False, 'match_score': 0, 'status_badge': 'Not Eligible', 'reasons': [], 'unmatched': unmatched}
        elif user_state and scheme_state.lower() == user_state.lower():
            reasons.append(f"Applicable in your state: {user_state}")
            score += 15

    # Additional bonus for category context
    cat_id = scheme.get('category_id')
    if cat_id == 1 and user_occ.lower() == 'student':
        score += 25
    if cat_id == 4 and user.get('employment_seeking') == 'Yes':
        score += 20
    if cat_id == 8 and user.get('business_interest') == 'Yes':
        score += 20

    # Determine status badge text based on score and criteria
    if score >= 45:
        status_badge = "Eligible"
    elif score >= 25:
        status_badge = "Potentially relevant"
    else:
        status_badge = "Check official eligibility"

    return {
        'is_eligible': True,
        'match_score': score,
        'status_badge': status_badge,
        'reasons': reasons,
        'unmatched': []
    }


def find_matching_schemes(all_schemes, raw_user_data):
    """
    Evaluates all schemes in the database against the user profile.
    Returns:
        tuple: (matching_schemes_list, normalized_profile)
    """
    user_profile = normalize_user_profile(raw_user_data)
    results = []

    for scheme in all_schemes:
        eval_result = evaluate_scheme(scheme, user_profile)
        if eval_result['is_eligible']:
            scheme_copy = dict(scheme)
            scheme_copy['match_score'] = eval_result['match_score']
            scheme_copy['status_badge'] = eval_result['status_badge']
            scheme_copy['reasons'] = eval_result['reasons']
            results.append(scheme_copy)

    # Sort primarily by match score descending, secondarily by scheme_name
    results.sort(key=lambda s: (-s['match_score'], s['scheme_name']))
    return results, user_profile
