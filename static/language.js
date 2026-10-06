/**
 * language.js
 * Comprehensive client-side multilingual translation engine for OurScheme.
 * Provides instant dictionary translation for UI strings, categories, forms, and cards,
 * while seamlessly synchronizing with Google Translate API, cookies, and Flask session.
 */

// Global Google Translate Init Callback
function googleTranslateElementInit() {
    try {
        new google.translate.TranslateElement({
            pageLanguage: 'en',
            includedLanguages: 'en,hi,mr,bn,gu,ta,te,kn,pa,ml',
            autoDisplay: false
        }, 'google_translate_element');
    } catch (e) {
        // Suppress Google Translate loading error if blocked or offline
    }
}

// Built-in Translation Dictionaries for Instant, Network-Independent Localization
const TRANSLATIONS = {
    "hi": {
        // Navigation & Brand
        "OurScheme": "आवरस्कीम (OurScheme)",
        "Find,Check": "खोजें, जांचें",
        "Right Government scheme for you": "आपके लिए सही सरकारी योजनाएं",
        "Search scheme": "सरकारी योजना खोजें...",
        "Search": "खोजें",
        "Home": "होम",
        "Schemes": "योजनाएं",
        "Check Eligibility": "पात्रता जांचें",
        "Saved Schemes": "सहेजी गई योजनाएं",
        "Contact Us": "संपर्क करें",
        "About Us": "हमारे बारे में",
        "Admin": "प्रशासक",
        "Login": "लॉगिन",
        "Register": "पंजीकरण",
        "Logout": "लॉगआउट",
        "2026 OurScheme | All Right Reserved": "2026 आवरस्कीम | सर्वाधिकार सुरक्षित",

        // Categories
        "Student & Education": "छात्र एवं शिक्षा",
        "Explore scholarships, education loans, free learning programs, and skill development schemes that help students achieve their academic and career goals.": "छात्रवृत्ति, शिक्षा ऋण, निःशुल्क शिक्षण कार्यक्रम और कौशल विकास योजनाओं का अन्वेषण करें जो छात्रों को अपने लक्ष्यों को प्राप्त करने में मदद करती हैं।",

        "Farmer & Agriculture": "किसान एवं कृषि",
        "Find schemes that provide financial support, crop insurance, farming equipment subsidies, irrigation assistance, and agricultural loans for farmers.": "किसानों के लिए वित्तीय सहायता, फसल बीमा, कृषि उपकरण सब्सिडी, सिंचाई सहायता और कृषि ऋण प्रदान करने वाली योजनाएं खोजें।",

        "Women Empowerment": "महिला सशक्तिकरण",
        "Discover schemes that promote women's education, entrepreneurship, financial independence, healthcare, and social security.": "महिलाओं की शिक्षा, उद्यमिता, वित्तीय स्वतंत्रता, स्वास्थ्य सेवा और सामाजिक सुरक्षा को बढ़ावा देने वाली योजनाएं जानें।",

        "Employment & Skill Development": "रोजगार एवं कौशल विकास",
        "Access government programs offering skill training, employment opportunities, startup support, and self-employment assistance.": "कौशल प्रशिक्षण, रोजगार के अवसर, स्टार्टअप सहायता और स्वरोजगार के अवसर प्रदान करने वाले सरकारी कार्यक्रमों तक पहुंचें।",

        "Senior Citizens": "वरिष्ठ नागरिक",
        "Browse pension plans, healthcare benefits, savings schemes, and welfare programs designed to support senior citizens.": "वरिष्ठ नागरिकों की सहायता के लिए बनाई गई पेंशन योजनाओं, स्वास्थ्य लाभों, बचत योजनाओं और कल्याणकारी कार्यक्रमों को देखें।",

        "Healthcare": "स्वास्थ्य सेवा",
        "Explore health insurance, affordable medicines, medical assistance, and healthcare initiatives for individuals and families.": "व्यक्तियों और परिवारों के लिए स्वास्थ्य बीमा, सस्ती दवाएं, चिकित्सा सहायता और स्वास्थ्य पहलों का अन्वेषण करें।",

        "Housing": "आवास योजना",
        "Find affordable housing schemes, home loan subsidies, and financial assistance programs to help you own a home.": "अपना घर बनाने में मदद करने के लिए किफायती आवास योजनाएं, गृह ऋण सब्सिडी और वित्तीय सहायता कार्यक्रम खोजें।",

        "Business & MSME": "व्यवसाय एवं एमएसएमई",
        "Discover government support for startups, small businesses, MSMEs, business loans, and entrepreneurship development.": "स्टार्टअप, लघु व्यवसाय, एमएसएमई, व्यवसाय ऋण और उद्यमिता विकास के लिए सरकारी सहायता खोजें।",

        "Financial Assistance": "वित्तीय सहायता",
        "Learn about savings schemes, insurance plans, pension programs, and banking initiatives that improve financial security.": "बचत योजनाओं, बीमा योजनाओं, पेंशन कार्यक्रमों और बैंकिंग पहलों के बारे में जानें जो वित्तीय सुरक्षा बढ़ाती हैं।",

        "SC / ST / OBC Welfare": "एससी / एसटी / ओबीसी कल्याण",
        "Access scholarships, skill development, business support, and welfare schemes created for SC, ST, and OBC communities.": "एससी, एसटी और ओबीसी समुदायों के लिए बनाई गई छात्रवृत्ति, कौशल विकास, व्यापार सहायता और कल्याणकारी योजनाओं का लाभ उठाएं।",

        "Disability (Divyang)": "दिव्यांग कल्याण",
        "Explore schemes that provide education, employment opportunities, financial aid, healthcare, and assistive devices for persons with disabilities.": "दिव्यांग व्यक्तियों के लिए शिक्षा, रोजगार के अवसर, वित्तीय सहायता, स्वास्थ्य सेवा और सहायक उपकरण प्रदान करने वाली योजनाएं देखें।",

        "Child Welfare": "बाल कल्याण",
        "Find schemes supporting child nutrition, education, healthcare, protection, and overall development for a brighter future.": "उज्ज्वल भविष्य के लिए बाल पोषण, शिक्षा, स्वास्थ्य सेवा, संरक्षण और समग्र विकास का समर्थन करने वाली योजनाएं खोजें।",

        "Rural Development": "ग्रामीण विकास",
        "Discover initiatives focused on rural employment, infrastructure, clean drinking water, roads, and sustainable village development.": "ग्रामीण रोजगार, बुनियादी ढांचे, स्वच्छ पेयजल, सड़कों और सतत ग्रामीण विकास पर केंद्रित पहलों की खोज करें।",

        "Urban Development": "शहरी विकास",
        "Learn about smart city projects, sanitation, affordable housing, public transport, and urban infrastructure improvement schemes.": "स्मार्ट सिटी परियोजनाओं, स्वच्छता, किफायती आवास, सार्वजनिक परिवहन और शहरी बुनियादी ढांचा योजनाओं के बारे में जानें।",

        "Environment & Energy": "पर्यावरण एवं ऊर्जा",
        "Explore renewable energy, solar power, environmental conservation, and sustainable development schemes for a greener future.": "हरित भविष्य के लिए नवीकरणीय ऊर्जा, सौर ऊर्जा, पर्यावरण संरक्षण और सतत विकास योजनाओं का अन्वेषण करें।",

        "Social Welfare": "समाज कल्याण",
        "Browse welfare programs offering financial assistance, food security, pensions, and social support for vulnerable citizens.": "कमजोर नागरिकों के लिए वित्तीय सहायता, खाद्य सुरक्षा, पेंशन और सामाजिक सुरक्षा प्रदान करने वाले कल्याणकारी कार्यक्रमों को देखें।",

        // Action Buttons
        "Go somewhere": "योजनाएं देखें →",
        "View Details": "विवरण देखें",
        "Official Website": "आधिकारिक वेबसाइट ↗",
        "☆ Save": "☆ सहेजें",
        "★ Saved": "★ सहेजा गया",
        "Check Eligibility (Step-by-Step Form)": "पात्रता जांचें (चरण-दर-चरण फॉर्म)",
        "Evaluate with AI": "एआई से जांचें",
        "Edit Details / Check Again": "विवरण बदलें / पुनः जांचें",
        "Next": "आगे बढ़ें",
        "Back": "पीछे जाएं",
        "Cancel": "रद्द करें",
        "Submit": "सबमिट करें",

        // Scheme Details Labels
        "Eligibility:": "पात्रता:",
        "Benefits:": "लाभ:",
        "Required Documents:": "आवश्यक दस्तावेज:",
        "Why recommended:": "सिफारिश का कारण:",
        "Matched Profile:": "मिलान किया गया प्रोफाइल:",
        "Found": "उपलब्ध",
        "relevant scheme(s)": "प्रासंगिक योजनाएं",
        "Scheme Eligibility Recommendations": "योजना पात्रता सिफारिशें",
        "Based on the information you provided, these schemes may be relevant to you.": "आपके द्वारा दी गई जानकारी के आधार पर, ये योजनाएं आपके लिए उपयुक्त हो सकती हैं।",
        "No matching schemes were found based on the information provided.": "दी गई जानकारी के आधार पर कोई योजना नहीं मिली।",

        // Form Labels & Steps
        "Personal Details": "व्यक्तिगत विवरण",
        "Age:": "आयु:",
        "Gender:": "लिंग:",
        "--Select--": "--चुनें--",
        "Male": "पुरुष",
        "Female": "महिला",
        "Other": "अन्य",
        "State:": "राज्य:",
        "-- Select State --": "-- राज्य चुनें --",
        "District:": "जिला:",
        "Social Details": "सामाजिक विवरण",
        "Category:": "श्रेणी:",
        "-- Select Category --": "-- श्रेणी चुनें --",
        "Annual Family Income (Rs.):": "वार्षिक पारिवारिक आय (रु.):",
        "Disability:": "दिव्यांगता:",
        "Yes": "हाँ",
        "No": "नहीं",
        "Education & Work": "शिक्षा एवं कार्य",
        "Education:": "शिक्षा:",
        "--Select Education--": "--शिक्षा चुनें--",
        "Occupation:": "पेशा / व्यवसाय:",
        "--Select Occupation--": "--व्यवसाय चुनें--",
        "Are You a Farmer?": "क्या आप किसान हैं?",
        "Housing & Location": "आवास एवं स्थान",
        "Area Type:": "क्षेत्र का प्रकार:",
        "-- Select Area Type --": "-- क्षेत्र चुनें --",
        "Rural": "ग्रामीण",
        "Urban": "शहरी",
        "Do you own a pucca house?": "क्या आपके पास पक्का मकान है?",
        "Other Information": "अन्य जानकारी",
        "Are you interested in business?": "क्या आप व्यवसाय में रुचि रखते हैं?",
        "Are you looking for employment?": "क्या आप रोजगार की तलाश में हैं?"
    },

    "mr": {
        // Navigation & Brand
        "OurScheme": "आवरस्कीम (OurScheme)",
        "Find,Check": "शोधा, तपासा",
        "Right Government scheme for you": "तुमच्यासाठी योग्य सरकारी योजना",
        "Search scheme": "सरकारी योजना शोधा...",
        "Search": "शोधा",
        "Home": "मुख्यपृष्ठ",
        "Schemes": "योजना",
        "Check Eligibility": "पात्रता तपासा",
        "Saved Schemes": "जतन केलेल्या योजना",
        "Contact Us": "संपर्क साधा",
        "About Us": "आमच्याबद्दल",
        "Admin": "प्रशासक",
        "Login": "लॉगिन",
        "Register": "नोंदणी",
        "Logout": "लॉगआउट",
        "2026 OurScheme | All Right Reserved": "2026 अवरस्कीम | सर्व हक्क राखीव",

        // Categories
        "Student & Education": "विद्यार्थी आणि शिक्षण",
        "Farmer & Agriculture": "शेतकरी आणि कृषी",
        "Women Empowerment": "महिला सक्षमीकरण",
        "Employment & Skill Development": "रोजगार आणि कौशल्य विकास",
        "Senior Citizens": "ज्येष्ठ नागरिक",
        "Healthcare": "आरोग्य सेवा",
        "Housing": "गृहनिर्माण योजना",
        "Business & MSME": "व्यवसाय आणि एमएसएमई",
        "Financial Assistance": "आर्थिक सहाय्य",
        "SC / ST / OBC Welfare": "एससी / एसटी / ओबीसी कल्याण",
        "Disability (Divyang)": "दिव्यांग कल्याण",
        "Child Welfare": "बालकल्याण",
        "Rural Development": "ग्रामीण विकास",
        "Urban Development": "शहरी विकास",
        "Environment & Energy": "पर्यावरण आणि ऊर्जा",
        "Social Welfare": "समाज कल्याण",

        // Action Buttons
        "Go somewhere": "योजना पहा →",
        "View Details": "तपशील पहा",
        "Official Website": "अधिकृत संकेतस्थळ ↗",
        "☆ Save": "☆ जतन करा",
        "★ Saved": "★ जतन केले",
        "Check Eligibility (Step-by-Step Form)": "पात्रता तपासा (टप्प्याटप्प्याने फॉर्म)",
        "Evaluate with AI": "एआय द्वारे तपासा",
        "Edit Details / Check Again": "तपशील संपादित करा / पुन्हा तपासा",
        "Next": "पुढे",
        "Back": "मागे",
        "Cancel": "रद्द करा",
        "Submit": "सबमिट करा",

        // Details
        "Eligibility:": "पात्रता:",
        "Benefits:": "फायदे:",
        "Required Documents:": "आवश्यक कागदपत्रे:",
        "Why recommended:": "शिफारस करण्याचे कारण:",
        "Matched Profile:": "जुळलेली माहिती:",
        "Based on the information you provided, these schemes may be relevant to you.": "आपण दिलेल्या माहितीच्या आधारे, या योजना आपल्यासाठी उपयुक्त ठरू शकतात.",
        "No matching schemes were found based on the information provided.": "दिलेल्या माहितीच्या आधारे कोणतीही जुळणारी योजना आढळली नाही.",

        // Form
        "Personal Details": "वैयक्तिक तपशील",
        "Age:": "वय:",
        "Gender:": "लिंग:",
        "Male": "पुरुष",
        "Female": "महिला",
        "Other": "इतर",
        "State:": "राज्य:",
        "District:": "जिल्हा:",
        "Social Details": "सामाजिक तपशील",
        "Category:": "प्रवर्ग:",
        "Annual Family Income (Rs.):": "वार्षिक कौटुंबिक उत्पन्न (रु.):",
        "Disability:": "दिव्यांगत्व:",
        "Yes": "होय",
        "No": "नाही",
        "Education & Work": "शिक्षण आणि काम",
        "Education:": "शिक्षण:",
        "Occupation:": "व्यवसाय:",
        "Are You a Farmer?": "तुम्ही शेतकरी आहात का?",
        "Housing & Location": "घर आणि ठिकाण",
        "Area Type:": "भागाचा प्रकार:",
        "Rural": "ग्रामीण",
        "Urban": "शहरी",
        "Do you own a pucca house?": "तुमच्याकडे पक्के घर आहे का?",
        "Other Information": "इतर माहिती",
        "Are you interested in business?": "तुम्हाला व्यवसायात स्वारस्य आहे का?",
        "Are you looking for employment?": "तुम्ही रोजगाराच्या शोधात आहात का?"
    },

    "gu": {
        "OurScheme": "અવરસ્કીમ (OurScheme)",
        "Find,Check": "શોધો, તપાસો",
        "Right Government scheme for you": "તમારા માટે યોગ્ય સરકારી યોજનાઓ",
        "Search scheme": "યોજના શોધો...",
        "Search": "શોધો",
        "Home": "હોમ",
        "Schemes": "યોજનાઓ",
        "Check Eligibility": "પાત્રતા તપાસો",
        "Saved Schemes": "સાચવેલી યોજનાઓ",
        "Contact Us": "સંપર્ક કરો",
        "About Us": "અમારા વિશે",
        "Login": "લૉગિન",
        "Register": "નોંધણી",
        "Logout": "લૉગઆઉટ",
        "Student & Education": "વિદ્યાર્થી અને શિક્ષણ",
        "Farmer & Agriculture": "ખેડૂત અને કૃષિ",
        "Women Empowerment": "મહિલા સશક્તિકરણ",
        "Employment & Skill Development": "રોજગાર અને કૌશલ્ય વિકાસ",
        "Senior Citizens": "વરિષ્ઠ નાગરિકો",
        "Healthcare": "આરોગ્ય સંભાળ",
        "Housing": "આવાસ યોજના",
        "Business & MSME": "વ્યાપાર અને MSME",
        "Go somewhere": "યોજનાઓ જુઓ →",
        "Official Website": "સત્તાવાર વેબસાઇટ ↗",
        "Next": "આગળ",
        "Back": "પાછળ",
        "Submit": "સબમિટ કરો"
    }
};

// Store original English texts so switching back to English restores the exact original page
const originalTextNodes = new Map();
const originalPlaceholders = new Map();

function saveOriginalTexts() {
    if (originalTextNodes.size > 0) return;

    function walk(node) {
        if (node.nodeType === Node.TEXT_NODE) {
            let trimmed = node.nodeValue.trim();
            if (trimmed.length > 0) {
                originalTextNodes.set(node, node.nodeValue);
            }
        } else if (node.nodeType === Node.ELEMENT_NODE) {
            // Do not translate scripts or styles
            if (node.tagName === "SCRIPT" || node.tagName === "STYLE" || node.tagName === "NOSCRIPT") {
                return;
            }
            if (node.placeholder) {
                originalPlaceholders.set(node, node.placeholder);
            }
            node.childNodes.forEach(walk);
        }
    }
    walk(document.body);
}

function translateDOM(langCode) {
    saveOriginalTexts();

    if (langCode === "en") {
        // Restore exact original English text
        originalTextNodes.forEach((origVal, node) => {
            if (node.parentNode) {
                node.nodeValue = origVal;
            }
        });
        originalPlaceholders.forEach((origVal, node) => {
            node.placeholder = origVal;
        });
        return;
    }

    const dict = TRANSLATIONS[langCode];
    if (!dict) return;

    // Apply translations to text nodes
    originalTextNodes.forEach((origVal, node) => {
        if (!node.parentNode) return;
        let trimmed = origVal.trim();

        // Exact phrase match
        if (dict[trimmed]) {
            node.nodeValue = origVal.replace(trimmed, dict[trimmed]);
            return;
        }

        // Substring dictionary replacement for composite phrases
        let replaced = origVal;
        let changed = false;
        for (let [enKey, transVal] of Object.entries(dict)) {
            if (enKey.length > 2 && replaced.includes(enKey)) {
                replaced = replaced.split(enKey).join(transVal);
                changed = true;
            }
        }
        if (changed) {
            node.nodeValue = replaced;
        }
    });

    // Update input placeholders
    originalPlaceholders.forEach((origVal, node) => {
        let trimmed = origVal.trim();
        if (dict[trimmed]) {
            node.placeholder = dict[trimmed];
        }
    });
}

function setCookie(name, value, days) {
    let expires = "";
    if (days) {
        let date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    let host = window.location.hostname;
    document.cookie = name + "=" + (value || "") + expires + "; path=/;";
    if (host && host !== "localhost" && host !== "127.0.0.1") {
        document.cookie = name + "=" + (value || "") + expires + "; domain=." + host + "; path=/;";
    }
}

function getCookie(name) {
    let nameEQ = name + "=";
    let ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

function applyLanguage(langCode) {
    // 1. Instantly translate the DOM on screen
    translateDOM(langCode);

    // 2. Persist in localStorage and Flask session
    localStorage.setItem("ourscheme_lang", langCode);
    fetch('/set_language/' + langCode, { method: 'POST' }).catch(() => {});

    // 3. Set Google Translate cookie
    if (langCode === 'en') {
        setCookie('googtrans', '/en/en', 30);
    } else {
        setCookie('googtrans', '/en/' + langCode, 30);
    }

    // 4. Trigger Google Translate combo if active
    let googleCombo = document.querySelector('.goog-te-combo');
    if (googleCombo) {
        googleCombo.value = langCode;
        googleCombo.dispatchEvent(new Event('change'));
    }
}

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", function () {
    let langSelect = document.getElementById("lang-select");
    if (!langSelect) return;

    // Detect saved language preference (localStorage > cookie)
    let savedLang = localStorage.getItem("ourscheme_lang");
    if (!savedLang) {
        let cookieVal = getCookie("googtrans");
        if (cookieVal) {
            let parts = cookieVal.split("/");
            if (parts.length >= 3 && parts[2]) {
                savedLang = parts[2];
            }
        }
    }

    if (!savedLang) {
        savedLang = "en";
    }

    langSelect.value = savedLang;

    // Apply translation immediately
    if (savedLang !== "en") {
        translateDOM(savedLang);
    }

    // Handle user selecting language from dropdown
    langSelect.addEventListener("change", function () {
        applyLanguage(this.value);
    });
});
