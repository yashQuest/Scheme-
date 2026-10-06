import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and draw total page count and professional running footer/header.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#555555"))
        
        # Header on later pages
        if self._pageNumber > 1:
            self.drawString(54, 11 * inch - 36, "OurScheme – Government Scheme Finder | Project Documentation & API Reference")
            self.setStrokeColor(colors.HexColor("#D0D7DE"))
            self.setLineWidth(0.5)
            self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)

        # Footer on all pages
        self.setStrokeColor(colors.HexColor("#D0D7DE"))
        self.setLineWidth(0.5)
        self.line(54, 46, 8.5 * inch - 54, 46)
        
        footer_left = "OurScheme Project Documentation — Flask & MySQL"
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawString(54, 34, footer_left)
        self.drawRightString(8.5 * inch - 54, 34, page_str)
        self.restoreState()


def build_pdf(filename="OurScheme_Project_Documentation.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    PRIMARY = colors.HexColor("#0F2C59")    # Deep Navy
    SECONDARY = colors.HexColor("#1976D2")  # Tech Blue
    DARK = colors.HexColor("#212529")       # Charcoal Body
    LIGHT_BG = colors.HexColor("#F8F9FA")   # Card BG
    BORDER_COL = colors.HexColor("#E2E8F0")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=23,
        leading=27,
        textColor=PRIMARY,
        spaceAfter=5
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=SECONDARY,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=PRIMARY,
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=SECONDARY,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=DARK,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=DARK,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=2.5
    )

    tbl_head_style = ParagraphStyle(
        'TblHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.white
    )

    tbl_cell_style = ParagraphStyle(
        'TblCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=DARK
    )

    tbl_bold_style = ParagraphStyle(
        'TblBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=DARK
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#A71D5D")
    )

    story = []

    # =========================================================================
    # HEADER / COVER TITLE
    # =========================================================================
    story.append(Paragraph("OurScheme – Government Scheme Finder", title_style))
    story.append(Paragraph("Complete Technical Documentation, File-by-File Architecture & API Guide", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))

    meta_data = [
        [
            Paragraph("<b>Project:</b> OurScheme Government Portal", tbl_cell_style),
            Paragraph("<b>Architecture:</b> Flask MVC + MySQL 8.0 + Google GenAI + Translate", tbl_cell_style)
        ],
        [
            Paragraph("<b>Categories:</b> Exactly 16 Validated Categories", tbl_cell_style),
            Paragraph("<b>Schemes Catalog:</b> 100 Government Welfare Schemes", tbl_cell_style)
        ],
        [
            Paragraph("<b>Key Features:</b> AI & Rule Eligibility, Multilingual, Admin Panel", tbl_cell_style),
            Paragraph("<b>Admin URL:</b> http://localhost:5000/admin (admin / admin123)", tbl_cell_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[245, 259])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_COL),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 1: PROJECT SUMMARY
    # =========================================================================
    story.append(Paragraph("1. Project Executive Summary", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=SECONDARY, spaceAfter=6))
    
    summary_text = (
        "<b>OurScheme</b> is an end-to-end, citizen-centric government scheme aggregation and eligibility discovery platform. "
        "Citizens in India frequently miss out on central and state welfare programs due to fragmented information, complex criteria, "
        "and language barriers. OurScheme resolves this by consolidating over 100 welfare programs across <b>16 distinct socioeconomic "
        "categories</b>, delivering instant personalized eligibility evaluation through both a structured 5-step demographic wizard "
        "and an AI-powered conversational query engine, providing live multi-language accessibility across 10 Indian languages, "
        "and providing a secure administrative portal for scheme governance."
    )
    story.append(Paragraph(summary_text, body_style))

    story.append(Paragraph("Core Functionalities:", h2_style))
    pillars = [
        "<b>Categorized Scheme Browsing:</b> Organized into 16 verified categories (Agriculture, Education, Healthcare, Social Welfare, Women & Child Development, Employment, Housing, Financial Services, etc.) with scheme counts and details.",
        "<b>5-Step Deterministic Eligibility Checker:</b> Analyzes age, gender, caste (General/OBC/SC/ST), employment, income ceiling, state, and house ownership to match qualifying schemes with pass/fail reasons.",
        "<b>Conversational AI Profile Extraction:</b> Citizens can describe their situation in natural language (e.g., 'I am a 21yo female student from Maharashtra with family income under 1.5 lakhs'); Google GenAI (Gemini) extracts structured parameters with offline regex fallback.",
        "<b>Dual-Layer Multilingual Architecture:</b> Instant client-side DOM translation for essential navigation and buttons paired with Google Website Translation Element API for deep page translation across 10 Indian languages (Hindi, Marathi, Gujarati, Bengali, Tamil, Telugu, Kannada, Malayalam, Punjabi, English).",
        "<b>Citizen Account Management:</b> Secure user registration, authentication, and a personal 'Saved Schemes' bookmarking dashboard.",
        "<b>Comprehensive Admin Dashboard:</b> Located at <code>/admin</code> with summary metric cards (Total Schemes, Total Categories, Total Contact Messages), full Scheme CRUD (Add/Edit/Delete), category monitoring, and contact inquiry message management."
    ]
    for p in pillars:
        story.append(Paragraph(f"• {p}", bullet_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 2: APIS & INTEGRATIONS USED
    # =========================================================================
    story.append(Paragraph("2. APIs and Integrations Used", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=SECONDARY, spaceAfter=6))

    apis_intro = (
        "The project integrates external cloud APIs, client-side translation APIs, database communication layers, "
        "and internal cryptographic frameworks as detailed below:"
    )
    story.append(Paragraph(apis_intro, body_style))

    api_table_data = [
        [
            Paragraph("API / Integration", tbl_head_style),
            Paragraph("Type / Source", tbl_head_style),
            Paragraph("Purpose & Implementation Details", tbl_head_style),
            Paragraph("Security & Resilience", tbl_head_style)
        ],
        [
            Paragraph("<b>Google Website Translation Element API</b>", tbl_bold_style),
            Paragraph("Client-Side API<br/>Google LLC", tbl_cell_style),
            Paragraph("Dynamically translates DOM content across 10 Indian languages via <code>//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit</code>. Synchronized with active language select dropdown in navbar.", tbl_cell_style),
            Paragraph("Persists language in <code>googtrans</code> cookie. Paired with instant client dictionary for immediate UI feedback.", tbl_cell_style)
        ],
        [
            Paragraph("<b>Google GenAI API (Gemini 2.5 Flash)</b>", tbl_bold_style),
            Paragraph("Cloud AI SDK<br/>Google DeepMind", tbl_cell_style),
            Paragraph("Used in <code>ai_extractor.py</code> to interpret freeform conversational text into structured demographic parameters (age, income, category, gender, state). Also used for backend translations in <code>translator.py</code>.", tbl_cell_style),
            Paragraph("Built-in offline regex NLP fallback parser guarantees 100% uptime if <code>GEMINI_API_KEY</code> is unset or offline.", tbl_cell_style)
        ],
        [
            Paragraph("<b>MySQL Connector Python API</b>", tbl_bold_style),
            Paragraph("Database Driver<br/>Oracle MySQL", tbl_cell_style),
            Paragraph("Handles TCP connections to MySQL database <code>government_schemes</code>. Executes parameterized SQL statements for public scheme discovery, user authentication, and admin CRUD operations.", tbl_cell_style),
            Paragraph("Strict parameterized statements (<code>%s</code> placeholders) preventing SQL injection attacks.", tbl_cell_style)
        ],
        [
            Paragraph("<b>Werkzeug Security API</b>", tbl_bold_style),
            Paragraph("Crypto Library<br/>Pallets Projects", tbl_cell_style),
            Paragraph("Manages one-way cryptographic password hashing for citizen accounts (<code>users</code>) and administrative accounts (<code>admins</code>) using <code>generate_password_hash</code> and <code>check_password_hash</code>.", tbl_cell_style),
            Paragraph("Salted PBKDF2/scrypt hashes prevent plain-text exposure even if database is compromised.", tbl_cell_style)
        ],
        [
            Paragraph("<b>Flask Session & Context API</b>", tbl_bold_style),
            Paragraph("Internal Web API<br/>Flask Framework", tbl_cell_style),
            Paragraph("Manages authenticated sessions for citizens (<code>user_id</code>) and admins (<code>admin_logged_in</code>). Context processor injects active language state into every rendered Jinja2 template.", tbl_cell_style),
            Paragraph("Cryptographically signed client-side session cookies using server <code>SECRET_KEY</code>.", tbl_cell_style)
        ]
    ]

    api_table = Table(api_table_data, colWidths=[110, 80, 194, 120])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_COL),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
    ]))
    story.append(api_table)
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 3: PURPOSE OF EACH FILE IN PROJECT
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("3. Purpose of Each File in the Project", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=SECONDARY, spaceAfter=6))

    files_table_data = [
        [
            Paragraph("File Path", tbl_head_style),
            Paragraph("Role", tbl_head_style),
            Paragraph("Detailed Purpose and Responsibilities", tbl_head_style)
        ],
        # Backend & Logic
        [
            Paragraph("<code>app.py</code>", code_style),
            Paragraph("Core Controller", tbl_bold_style),
            Paragraph("Central application hub. Configures Flask app, database connection helper, session lifecycle, error handlers, and context processors. Defines all routes for scheme browsing, search, user authentication, 5-step eligibility assessment, AI query processing, bookmarking, multilingual sync (<code>/set_language</code>), and the entire <code>/admin</code> control suite.", tbl_cell_style)
        ],
        [
            Paragraph("<code>eligibility_engine.py</code>", code_style),
            Paragraph("Business Logic", tbl_bold_style),
            Paragraph("Deterministic rules engine. Compares user profiles against database criteria (age range, gender, caste, employment, max income ceiling, state, house ownership). Calculates match percentages and generates human-readable explanations of why the citizen is eligible.", tbl_cell_style)
        ],
        [
            Paragraph("<code>ai_extractor.py</code>", code_style),
            Paragraph("AI / NLP Module", tbl_bold_style),
            Paragraph("Extracts structured demographic attributes from natural language queries using Google GenAI (Gemini 2.5 Flash). Includes an integrated offline regex extractor to ensure offline resilience for age, income (LPA, k, lakhs), gender, and caste.", tbl_cell_style)
        ],
        [
            Paragraph("<code>translator.py</code>", code_style),
            Paragraph("Localization", tbl_bold_style),
            Paragraph("Defines dictionary of 10 supported Indian languages (code, English name, native script). Provides backend translation caching and fallback translation functions using Google GenAI.", tbl_cell_style)
        ],
        # Database & Migration Scripts
        [
            Paragraph("<code>create_admin_table.py</code>", code_style),
            Paragraph("DB Setup", tbl_bold_style),
            Paragraph("Creates the <code>admins</code> table in MySQL with secure hashed password storage. Seeds the default super-administrator account (<code>admin</code> / <code>admin123</code>).", tbl_cell_style)
        ],
        [
            Paragraph("<code>run_migrations.py</code>", code_style),
            Paragraph("DB Migration", tbl_bold_style),
            Paragraph("Schema migration runner: ensures <code>schemes</code> table has criteria columns, creates <code>users</code> and <code>saved_schemes</code> tables, cleans and normalizes categories to exactly 16 unique entries, and sets realistic eligibility criteria for 100 schemes.", tbl_cell_style)
        ],
        [
            Paragraph("<code>migrations.sql</code>", code_style),
            Paragraph("SQL Script", tbl_bold_style),
            Paragraph("Raw SQL migration containing DDL statements for creating tables and DML updates for criteria seeding.", tbl_cell_style)
        ],
        # Automated Tests
        [
            Paragraph("<code>test_complete_flow.py</code>", code_style),
            Paragraph("Test Suite", tbl_bold_style),
            Paragraph("Automated integration test verifying all public citizen journeys: homepage, category loading, search queries, registration/login, 5-step wizard, AI extraction, and scheme saving.", tbl_cell_style)
        ],
        [
            Paragraph("<code>test_admin_suite.py</code>", code_style),
            Paragraph("Test Suite", tbl_bold_style),
            Paragraph("Automated test suite verifying the Admin Dashboard: session security, login/logout, metric card calculations, scheme addition, editing, deletion, and contact message management.", tbl_cell_style)
        ],
        # Static CSS and JS
        [
            Paragraph("<code>static/style.css</code>", code_style),
            Paragraph("Frontend CSS", tbl_bold_style),
            Paragraph("Global stylesheet for public website: navbar, hero carousel, category cards, buttons, footer, responsive grids, and cleanly hiding Google Translate default top banners.", tbl_cell_style)
        ],
        [
            Paragraph("<code>static/admin.css</code>", code_style),
            Paragraph("Admin CSS", tbl_bold_style),
            Paragraph("Dedicated styles for the Admin Panel: dark sidebar, modern stat cards, structured data tables, status badges, modal dialogs, and clean admin login UI.", tbl_cell_style)
        ],
        [
            Paragraph("<code>static/eligibility.css</code>", code_style),
            Paragraph("Frontend CSS", tbl_bold_style),
            Paragraph("Styles the 5-step interactive eligibility popup modal, progress bar, radio badges, step indicators, and AI prompt input tab.", tbl_cell_style)
        ],
        [
            Paragraph("<code>static/eligibility.js</code>", code_style),
            Paragraph("Frontend JS", tbl_bold_style),
            Paragraph("Client-side controller for the eligibility wizard: step navigation, form validation, AJAX submission to <code>/check_eligibility</code>, and conversational AI prompt handling.", tbl_cell_style)
        ],
        [
            Paragraph("<code>static/language.js</code>", code_style),
            Paragraph("Frontend JS", tbl_bold_style),
            Paragraph("Dual-layer language switcher: provides instant client dictionary translation for UI navigation and triggers Google Website Translation Element API with cookie synchronization.", tbl_cell_style)
        ],
        [
            Paragraph("<code>static/test.css</code>", code_style),
            Paragraph("Frontend CSS", tbl_bold_style),
            Paragraph("Styles scheme catalog cards, category tags, eligibility criteria pill badges, and bookmark icons in <code>test.html</code>.", tbl_cell_style)
        ],
        [
            Paragraph("<code>static/ContactUs.css</code>", code_style),
            Paragraph("Frontend CSS", tbl_bold_style),
            Paragraph("Styles the Contact Us inquiry page: office information cards, form layout, and status alerts.", tbl_cell_style)
        ],
        [
            Paragraph("<code>static/AboutUs.css</code>", code_style),
            Paragraph("Frontend CSS", tbl_bold_style),
            Paragraph("Styles the About Us page, mission statement, platform benefits, and team vision cards.", tbl_cell_style)
        ],
        # Public Templates
        [
            Paragraph("<code>templates/base.html</code>", code_style),
            Paragraph("Base Template", tbl_bold_style),
            Paragraph("Master public HTML layout containing top navigation, search bar, language switcher dropdown, citizen auth buttons, flash alert containers, and footer.", tbl_cell_style)
        ],
        [
            Paragraph("<code>templates/home.html</code>", code_style),
            Paragraph("Public HTML", tbl_bold_style),
            Paragraph("Landing homepage featuring hero banner carousel, quick CTA for eligibility check, and dynamic cards for the 16 government scheme categories.", tbl_cell_style)
        ],
        [
            Paragraph("<code>templates/test.html</code>", code_style),
            Paragraph("Public HTML", tbl_bold_style),
            Paragraph("Scheme catalog listing displaying schemes in cards with category badges, description, eligibility criteria, and 'Save Scheme' bookmarking.", tbl_cell_style)
        ],
        [
            Paragraph("<code>templates/eligibility.html</code>", code_style),
            Paragraph("Public HTML", tbl_bold_style),
            Paragraph("Interactive 5-step eligibility modal questionnaire and conversational AI prompt tab.", tbl_cell_style)
        ],
        [
            Paragraph("<code>templates/eligibility_results.html</code>", code_style),
            Paragraph("Public HTML", tbl_bold_style),
            Paragraph("Results page displaying matched qualifying schemes, eligibility match percentages, specific qualification reasons, and application links.", tbl_cell_style)
        ],
        [
            Paragraph("<code>templates/login.html</code>", code_style),
            Paragraph("Public HTML", tbl_bold_style),
            Paragraph("Citizen authentication login form with email/password validation.", tbl_cell_style)
        ],
        [
            Paragraph("<code>templates/register.html</code>", code_style),
            Paragraph("Public HTML", tbl_bold_style),
            Paragraph("Citizen registration form capturing account credentials and optional demographic profile.", tbl_cell_style)
        ],
        [
            Paragraph("<code>templates/saved_schemes.html</code>", code_style),
            Paragraph("Public HTML", tbl_bold_style),
            Paragraph("Personalized bookmark dashboard where authenticated citizens access their saved schemes.", tbl_cell_style)
        ],
        [
            Paragraph("<code>templates/contactUs.html</code>", code_style),
            Paragraph("Public HTML", tbl_bold_style),
            Paragraph("Citizen feedback and inquiry submission form connecting directly to the database.", tbl_cell_style)
        ],
        [
            Paragraph("<code>templates/AboutUs.html</code>", code_style),
            Paragraph("Public HTML", tbl_bold_style),
            Paragraph("Informational page describing platform objectives, background, and government initiatives.", tbl_cell_style)
        ],
        # Admin Templates
        [
            Paragraph("<code>templates/admin/admin_base.html</code>", code_style),
            Paragraph("Admin Base", tbl_bold_style),
            Paragraph("Master layout for the Admin Panel: sidebar navigation, active page indicator, admin header, and secure logout link.", tbl_cell_style)
        ],
        [
            Paragraph("<code>templates/admin/admin_login.html</code>", code_style),
            Paragraph("Admin HTML", tbl_bold_style),
            Paragraph("Dedicated login page for portal administrators at <code>/admin/login</code>.", tbl_cell_style)
        ],
        [
            Paragraph("<code>templates/admin/dashboard.html</code>", code_style),
            Paragraph("Admin HTML", tbl_bold_style),
            Paragraph("Admin overview dashboard displaying 3 real-time summary KPI cards (Total Schemes, Total Categories, Total Contact Messages) and quick links.", tbl_cell_style)
        ],
        [
            Paragraph("<code>templates/admin/schemes.html</code>", code_style),
            Paragraph("Admin HTML", tbl_bold_style),
            Paragraph("Comprehensive scheme data table with live search, category filter, and edit/delete actions.", tbl_cell_style)
        ],
        [
            Paragraph("<code>templates/admin/add_scheme.html</code>", code_style),
            Paragraph("Admin HTML", tbl_bold_style),
            Paragraph("Form for administrators to create new welfare schemes with category selection and criteria.", tbl_cell_style)
        ],
        [
            Paragraph("<code>templates/admin/edit_scheme.html</code>", code_style),
            Paragraph("Admin HTML", tbl_bold_style),
            Paragraph("Form pre-populated with existing scheme details allowing updates to criteria and information.", tbl_cell_style)
        ],
        [
            Paragraph("<code>templates/admin/categories.html</code>", code_style),
            Paragraph("Admin HTML", tbl_bold_style),
            Paragraph("Category overview table presenting the 16 active categories and scheme counts per category.", tbl_cell_style)
        ],
        [
            Paragraph("<code>templates/admin/contacts.html</code>", code_style),
            Paragraph("Admin HTML", tbl_bold_style),
            Paragraph("Message inbox displaying citizen inquiries from Contact Us with timestamp and delete actions.", tbl_cell_style)
        ]
    ]

    files_table = Table(files_table_data, colWidths=[115, 80, 309])
    files_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_COL),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
    ]))
    story.append(files_table)
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 4: DATABASE SCHEMA & OPERATIONS
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("4. Database Architecture & Table Structure", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=SECONDARY, spaceAfter=6))

    db_data = [
        [
            Paragraph("Table Name", tbl_head_style),
            Paragraph("Primary Key", tbl_head_style),
            Paragraph("Columns & Datatypes", tbl_head_style),
            Paragraph("Purpose & Constraints", tbl_head_style)
        ],
        [
            Paragraph("<b>schemes</b>", tbl_bold_style),
            Paragraph("<code>id</code> (INT AUTO)", tbl_cell_style),
            Paragraph("<code>scheme_name</code>, <code>category</code>, <code>description</code>, <code>min_age</code>, <code>max_age</code>, <code>gender</code>, <code>caste_category</code>, <code>employment_status</code>, <code>max_income</code>, <code>house_owner</code>, <code>state</code>", tbl_cell_style),
            Paragraph("Houses 100 government welfare schemes with structured eligibility criteria.", tbl_cell_style)
        ],
        [
            Paragraph("<b>categories</b>", tbl_bold_style),
            Paragraph("<code>id</code> (INT AUTO)", tbl_cell_style),
            Paragraph("<code>category_name</code> (VARCHAR 100), <code>description</code>, <code>icon_path</code>", tbl_cell_style),
            Paragraph("Exactly 16 distinct categories organizing schemes.", tbl_cell_style)
        ],
        [
            Paragraph("<b>users</b>", tbl_bold_style),
            Paragraph("<code>id</code> (INT AUTO)", tbl_cell_style),
            Paragraph("<code>username</code>, <code>email</code>, <code>password_hash</code>, <code>gender</code>, <code>age</code>, <code>caste</code>, <code>state</code>, <code>income</code>", tbl_cell_style),
            Paragraph("Stores citizen profiles and credentials with secure hashing.", tbl_cell_style)
        ],
        [
            Paragraph("<b>admins</b>", tbl_bold_style),
            Paragraph("<code>id</code> (INT AUTO)", tbl_cell_style),
            Paragraph("<code>username</code> (VARCHAR 50 UNIQUE), <code>password_hash</code> (VARCHAR 255), <code>email</code>, <code>created_at</code>", tbl_cell_style),
            Paragraph("Administrative accounts managing portal access at <code>/admin</code>.", tbl_cell_style)
        ],
        [
            Paragraph("<b>contacts</b>", tbl_bold_style),
            Paragraph("<code>id</code> (INT AUTO)", tbl_cell_style),
            Paragraph("<code>name</code>, <code>email</code>, <code>phone</code>, <code>message</code>, <code>submitted_at</code>", tbl_cell_style),
            Paragraph("Stores citizen feedback and contact inquiries.", tbl_cell_style)
        ],
        [
            Paragraph("<b>saved_schemes</b>", tbl_bold_style),
            Paragraph("<code>id</code> (INT AUTO)", tbl_cell_style),
            Paragraph("<code>user_id</code> (INT), <code>scheme_id</code> (INT), <code>saved_at</code>", tbl_cell_style),
            Paragraph("Junction table managing citizen bookmarks with unique compound constraint.", tbl_cell_style)
        ]
    ]

    db_table = Table(db_data, colWidths=[85, 75, 204, 140])
    db_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_COL),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
    ]))
    story.append(db_table)
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 5: TECHNICAL SUMMARY & VERIFICATION
    # =========================================================================
    story.append(Paragraph("5. Technical Verification & Execution Instructions", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=SECONDARY, spaceAfter=6))

    run_instructions = [
        "<b>Run Flask Server:</b> Execute <code>python app.py</code> in the workspace. Access the portal at <code>http://127.0.0.1:5000</code>.",
        "<b>Access Admin Dashboard:</b> Visit <code>http://localhost:5000/admin</code>. Sign in with username: <code>admin</code> and password: <code>admin123</code>.",
        "<b>Run End-to-End Test Suite:</b> Run <code>python test_complete_flow.py</code> to verify citizen journeys.",
        "<b>Run Admin Test Suite:</b> Run <code>python test_admin_suite.py</code> to verify admin CRUD operations and security authorization.",
        "<b>Multilingual Functionality:</b> Use the top navbar language dropdown to switch among 10 languages (Hindi, Marathi, Gujarati, etc.).",
        "<b>AI Eligibility Evaluation:</b> Enter natural language text into the eligibility modal AI tab. The system extracts demographic parameters using Google GenAI or offline regex fallback."
    ]
    for r in run_instructions:
        story.append(Paragraph(f"• {r}", bullet_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF documentation generated successfully: {filename}")

if __name__ == "__main__":
    out_path = os.path.join(r"c:\Users\HP\Downloads\Myscheme", "OurScheme_Project_Documentation.pdf")
    build_pdf(out_path)
