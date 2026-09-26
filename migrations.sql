-- Database Schema Migration for OurScheme (government_schemes)

-- 1. Add missing structured columns to schemes table if not present
ALTER TABLE schemes ADD COLUMN IF NOT EXISTS gender VARCHAR(20) DEFAULT 'Any';
ALTER TABLE schemes ADD COLUMN IF NOT EXISTS house_owner VARCHAR(20) DEFAULT 'Any';
ALTER TABLE schemes ADD COLUMN IF NOT EXISTS state VARCHAR(100) DEFAULT 'All';

-- 2. Create users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create saved_schemes table for bookmarking
CREATE TABLE IF NOT EXISTS saved_schemes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    scheme_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_scheme (user_id, scheme_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (scheme_id) REFERENCES schemes(id) ON DELETE CASCADE
);

-- 4. Set category-based default structured eligibility criteria
-- Category 1: Student & Education
UPDATE schemes SET min_age=14, max_age=35, occupation='Student', gender='Any', farmer='Any', disability='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=1;

-- Category 2: Farmer & Agriculture
UPDATE schemes SET min_age=18, max_age=80, farmer='Yes', occupation='Farmer', gender='Any', disability='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=2;

-- Category 3: Women Empowerment
UPDATE schemes SET min_age=0, max_age=80, gender='Female', farmer='Any', disability='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=3;

-- Category 4: Employment & Skill Development
UPDATE schemes SET min_age=18, max_age=45, occupation='Any', gender='Any', farmer='Any', disability='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=4;

-- Category 5: Senior Citizens
UPDATE schemes SET min_age=60, max_age=100, gender='Any', farmer='Any', disability='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=5;

-- Category 6: Healthcare
UPDATE schemes SET min_age=0, max_age=100, max_income=500000, gender='Any', farmer='Any', disability='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=6;

-- Category 7: Housing
UPDATE schemes SET min_age=18, max_age=80, house_owner='No', max_income=600000, gender='Any', farmer='Any', disability='Any', area_type='Any', social_category='Any', state='All' WHERE category_id=7;

-- Category 8: Business & MSME
UPDATE schemes SET min_age=18, max_age=70, occupation='Business Owner', gender='Any', farmer='Any', disability='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=8;

-- Category 9: Financial Assistance
UPDATE schemes SET min_age=18, max_age=70, gender='Any', farmer='Any', disability='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=9;

-- Category 10: SC / ST / OBC Welfare
UPDATE schemes SET min_age=14, max_age=70, social_category='SC,ST,OBC', gender='Any', farmer='Any', disability='Any', area_type='Any', house_owner='Any', state='All' WHERE category_id=10;

-- Category 11: Disability (Divyang)
UPDATE schemes SET min_age=0, max_age=100, disability='Yes', gender='Any', farmer='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=11;

-- Category 12: Child Welfare
UPDATE schemes SET min_age=0, max_age=18, gender='Any', farmer='Any', disability='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=12;

-- Category 13: Rural Development
UPDATE schemes SET min_age=18, max_age=80, area_type='Rural', gender='Any', farmer='Any', disability='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=13;

-- Category 14: Urban Development
UPDATE schemes SET min_age=18, max_age=80, area_type='Urban', gender='Any', farmer='Any', disability='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=14;

-- Category 15: Environment & Energy
UPDATE schemes SET min_age=18, max_age=80, gender='Any', farmer='Any', disability='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=15;

-- Category 16: Social Welfare
UPDATE schemes SET min_age=18, max_age=80, max_income=300000, gender='Any', farmer='Any', disability='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=16;

-- Specific scheme refinements
-- Sukanya Samriddhi Account (girl children up to 10 years)
UPDATE schemes SET min_age=0, max_age=10, gender='Female' WHERE scheme_name LIKE '%Sukanya Samriddhi%';

-- Post Matric Scholarship for OBC / SC
UPDATE schemes SET social_category='OBC', occupation='Student', min_age=15, max_age=30, max_income=250000 WHERE scheme_name LIKE '%OBC Students%';
UPDATE schemes SET social_category='SC', occupation='Student', min_age=14, max_age=30, max_income=250000 WHERE scheme_name LIKE '%SC Students%';
UPDATE schemes SET social_category='SC', occupation='Student', min_age=21, max_age=35 WHERE scheme_name LIKE '%National Fellowship for SC%';

-- Atal Pension Yojana (18 to 40 years)
UPDATE schemes SET min_age=18, max_age=40 WHERE scheme_name LIKE '%Atal Pension Yojana%';

-- PMJJBY (18 to 50 years)
UPDATE schemes SET min_age=18, max_age=50 WHERE scheme_name LIKE '%Jeevan Jyoti%';

-- PMSBY (18 to 70 years)
UPDATE schemes SET min_age=18, max_age=70 WHERE scheme_name LIKE '%Suraksha Bima%';

-- PM SVANidhi (street vendors in urban areas)
UPDATE schemes SET occupation='Self Employed', area_type='Urban', min_age=18 WHERE scheme_name LIKE '%SVANidhi%';

-- Stand-Up India (SC/ST or Women entrepreneurs)
UPDATE schemes SET min_age=18, social_category='SC,ST' WHERE scheme_name LIKE '%Stand-Up India%';

-- Old Age Pension (age 60+, low income)
UPDATE schemes SET min_age=60, max_age=100, max_income=200000 WHERE scheme_name LIKE '%Old Age Pension%' OR scheme_name LIKE '%Annapurna%';
