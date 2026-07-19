import streamlit as st
import mysql.connector
import os
from datetime import date, datetime, timedelta
import time


# ============================================================
# DATABASE CONNECTION
# ============================================================
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("MEDIPAL_DB_PASSWORD", "Sukrit2006"),
        database="Medipal"
    )


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def get_next_id(table, column, prefix):
    """Generic auto-ID generator for any table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT {column} FROM {table} ORDER BY {column} DESC LIMIT 1")
    last_id = cursor.fetchone()
    cursor.close()
    conn.close()
    if last_id:
        last_num = int(last_id[0][len(prefix):])
        digits = max(3, len(str(last_num + 1)))
        return f"{prefix}{str(last_num + 1).zfill(digits)}"
    return f"{prefix}001"


def get_all_family_drug_ids(conn, root_drug_id):
    """Recursively find all drugs in a drug family tree."""
    all_ids = set()
    to_check = [root_drug_id]
    while to_check:
        current = to_check.pop()
        all_ids.add(current)
        cur = conn.cursor()
        cur.execute("SELECT drug_id FROM Drugs WHERE super_drug_id = %s", (current,))
        children = [row[0] for row in cur.fetchall()]
        cur.close()
        for child in children:
            if child not in all_ids:
                to_check.append(child)
    return all_ids


def get_dashboard_metrics():
    """Fetch key metrics for the dashboard sidebar."""
    conn = get_db_connection()
    cur = conn.cursor()
    metrics = {}
    cur.execute("SELECT COUNT(*) FROM Patient")
    metrics["patients"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Doctor")
    metrics["doctors"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Prescription WHERE end_date IS NULL OR end_date >= CURDATE()")
    metrics["active_prescriptions"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Severity_Change_Log WHERE status = 'proposed'")
    metrics["pending_reviews"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Pair_Feedback")
    metrics["total_feedback"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Interaction_Evidence_Stats WHERE distinct_patients >= 5")
    metrics["analyzed_pairs"] = cur.fetchone()[0]
    cur.close()
    conn.close()
    return metrics


# ============================================================
# PREMIUM CSS THEME
# ============================================================
def inject_premium_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        /* ── Global Reset ── */
        *, *::before, *::after { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }

        .stApp {
            background: linear-gradient(135deg, #0a0e1a 0%, #0d1326 30%, #111827 70%, #0f172a 100%);
            color: #e2e8f0;
        }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f1629 0%, #131b36 50%, #0d1326 100%);
            border-right: 1px solid rgba(99, 102, 241, 0.15);
        }
        [data-testid="stSidebar"] .stMarkdown h1,
        [data-testid="stSidebar"] .stMarkdown h2,
        [data-testid="stSidebar"] .stMarkdown h3 {
            background: linear-gradient(135deg, #818cf8, #6366f1, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
            letter-spacing: -0.5px;
        }

        /* ── Typography ── */
        h1 {
            background: linear-gradient(135deg, #818cf8, #6366f1, #a78bfa) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            font-size: 2.2rem !important;
            font-weight: 800 !important;
            letter-spacing: -0.8px !important;
        }
        h2, h3 {
            color: #c7d2fe !important;
            font-weight: 700 !important;
            letter-spacing: -0.3px;
        }
        p, span, label, div { color: #cbd5e1; }

        /* ── Glass Cards ── */
        .glass-card {
            background: rgba(30, 41, 79, 0.45);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(99, 102, 241, 0.18);
            border-radius: 16px;
            padding: 22px 26px;
            margin: 12px 0;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .glass-card:hover {
            border-color: rgba(99, 102, 241, 0.35);
            box-shadow: 0 8px 32px rgba(99, 102, 241, 0.08);
            transform: translateY(-1px);
        }

        /* ── Metric Cards ── */
        .metric-card {
            background: rgba(30, 41, 79, 0.5);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 14px;
            padding: 18px 20px;
            text-align: center;
            transition: all 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 40px rgba(99, 102, 241, 0.12);
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #818cf8, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 4px 0;
        }
        .metric-label {
            font-size: 0.78rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }

        /* ── Severity Badges ── */
        .badge-high {
            background: linear-gradient(135deg, #ef4444, #dc2626);
            color: white;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: inline-block;
            animation: pulse-red 2s ease-in-out infinite;
        }
        .badge-medium {
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: white;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: inline-block;
        }
        .badge-low {
            background: linear-gradient(135deg, #22c55e, #16a34a);
            color: white;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: inline-block;
        }
        .badge-na {
            background: rgba(100, 116, 139, 0.3);
            color: #94a3b8;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
        }

        @keyframes pulse-red {
            0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
            50% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
        }

        /* ── Alert Boxes ── */
        .alert-danger {
            background: linear-gradient(135deg, rgba(127, 29, 29, 0.6), rgba(153, 27, 27, 0.4));
            border-left: 4px solid #ef4444;
            border-radius: 12px;
            padding: 18px 22px;
            margin: 14px 0;
            backdrop-filter: blur(12px);
        }
        .alert-success {
            background: linear-gradient(135deg, rgba(20, 83, 45, 0.5), rgba(22, 101, 52, 0.35));
            border-left: 4px solid #22c55e;
            border-radius: 12px;
            padding: 18px 22px;
            margin: 14px 0;
            backdrop-filter: blur(12px);
        }
        .alert-info {
            background: linear-gradient(135deg, rgba(30, 58, 138, 0.4), rgba(29, 78, 216, 0.25));
            border-left: 4px solid #3b82f6;
            border-radius: 12px;
            padding: 18px 22px;
            margin: 14px 0;
            backdrop-filter: blur(12px);
        }
        .alert-warning {
            background: linear-gradient(135deg, rgba(120, 53, 15, 0.5), rgba(146, 64, 14, 0.35));
            border-left: 4px solid #f59e0b;
            border-radius: 12px;
            padding: 18px 22px;
            margin: 14px 0;
            backdrop-filter: blur(12px);
        }

        /* ── Form Inputs ── */
        [data-testid="stTextInput"] input,
        [data-testid="stDateInput"] input,
        [data-testid="stNumberInput"] input {
            background: rgba(15, 23, 42, 0.7) !important;
            border: 1px solid rgba(99, 102, 241, 0.2) !important;
            border-radius: 10px !important;
            color: #e2e8f0 !important;
            padding: 10px 14px !important;
            transition: all 0.3s ease !important;
        }
        [data-testid="stTextInput"] input:focus,
        [data-testid="stDateInput"] input:focus,
        [data-testid="stNumberInput"] input:focus {
            border-color: rgba(99, 102, 241, 0.5) !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
        }
        [data-testid="stSelectbox"] > div > div {
            background: rgba(15, 23, 42, 0.7) !important;
            border: 1px solid rgba(99, 102, 241, 0.2) !important;
            border-radius: 10px !important;
            color: #e2e8f0 !important;
        }
        textarea {
            background: rgba(15, 23, 42, 0.7) !important;
            border: 1px solid rgba(99, 102, 241, 0.2) !important;
            border-radius: 10px !important;
            color: #e2e8f0 !important;
        }
        textarea:focus {
            border-color: rgba(99, 102, 241, 0.5) !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
        }

        /* ── Buttons ── */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
            border: 1px solid rgba(99, 102, 241, 0.5) !important;
            border-radius: 10px !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 8px 24px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            letter-spacing: 0.3px !important;
        }
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #818cf8, #6366f1) !important;
            box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3) !important;
            transform: translateY(-1px) !important;
        }
        .stButton > button[kind="secondary"] {
            background: rgba(30, 41, 79, 0.5) !important;
            border: 1px solid rgba(99, 102, 241, 0.2) !important;
            border-radius: 10px !important;
            color: #c7d2fe !important;
            font-weight: 500 !important;
        }
        .stButton > button[kind="secondary"]:hover {
            background: rgba(30, 41, 79, 0.8) !important;
            border-color: rgba(99, 102, 241, 0.4) !important;
        }
        .stButton > button:disabled {
            background: rgba(30, 41, 59, 0.4) !important;
            border-color: rgba(51, 65, 85, 0.3) !important;
            color: #475569 !important;
        }

        /* ── Approve/Reject Buttons ── */
        .approve-btn > button {
            background: linear-gradient(135deg, #22c55e, #16a34a) !important;
            border: 1px solid rgba(34, 197, 94, 0.5) !important;
            color: white !important;
            font-weight: 600 !important;
        }
        .reject-btn > button {
            background: linear-gradient(135deg, #ef4444, #dc2626) !important;
            border: 1px solid rgba(239, 68, 68, 0.5) !important;
            color: white !important;
            font-weight: 600 !important;
        }

        /* ── DataFrames ── */
        [data-testid="stDataFrame"] {
            border: 1px solid rgba(99, 102, 241, 0.15) !important;
            border-radius: 12px !important;
            overflow: hidden;
        }

        /* ── Dividers ── */
        hr {
            border-color: rgba(99, 102, 241, 0.1) !important;
            margin: 20px 0 !important;
        }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background: rgba(15, 23, 42, 0.5);
            border-radius: 12px;
            padding: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            color: #94a3b8;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            background: rgba(99, 102, 241, 0.2) !important;
            color: #c7d2fe !important;
        }

        /* ── Star Rating Display ── */
        .star-display { font-size: 1.5rem; letter-spacing: 2px; }
        .star-filled { color: #f59e0b; }
        .star-empty { color: #334155; }

        /* ── Symptom Tags ── */
        .symptom-tag {
            display: inline-block;
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #fca5a5;
            padding: 3px 12px;
            border-radius: 16px;
            font-size: 0.78rem;
            font-weight: 500;
            margin: 3px 4px;
        }
        .symptom-tag-none {
            display: inline-block;
            background: rgba(34, 197, 94, 0.15);
            border: 1px solid rgba(34, 197, 94, 0.3);
            color: #86efac;
            padding: 3px 12px;
            border-radius: 16px;
            font-size: 0.78rem;
            font-weight: 500;
            margin: 3px 4px;
        }

        /* ── Progress Bar ── */
        .severity-bar {
            height: 8px;
            border-radius: 4px;
            background: rgba(30, 41, 59, 0.5);
            overflow: hidden;
            margin: 6px 0;
        }
        .severity-bar-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.6s ease;
        }

        /* ── Layout ── */
        .block-container {
            padding-top: 2rem !important;
            max-width: 1200px;
        }

        /* ── Caption ── */
        [data-testid="stCaptionContainer"] { color: #64748b !important; }

        /* ── Radio buttons (navigation) ── */
        [data-testid="stSidebar"] .stRadio label {
            color: #94a3b8 !important;
            font-weight: 500 !important;
            padding: 6px 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)


def severity_badge(severity):
    """Return HTML badge for a severity level."""
    if severity == "High":
        return '<span class="badge-high">⚠ High</span>'
    elif severity == "Medium":
        return '<span class="badge-medium">● Medium</span>'
    elif severity == "Low":
        return '<span class="badge-low">✓ Low</span>'
    return '<span class="badge-na">— N/A</span>'


def star_rating_display(rating, max_stars=5):
    """Return HTML star display for a rating."""
    filled = "★" * rating
    empty = "★" * (max_stars - rating)
    return f'<span class="star-display"><span class="star-filled">{filled}</span><span class="star-empty">{empty}</span></span>'


def render_metric_card(label, value, icon=""):
    """Render a single metric card with glassmorphism."""
    return f"""
    <div class="metric-card">
        <div style="font-size:1.5rem;margin-bottom:4px;">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """


# ============================================================
# PAGE: DOCTOR PORTAL
# ============================================================
def doctors_page():
    st.title("🩺 Doctor Portal")
    st.caption("Prescribe medications with real-time drug interaction checking")
    st.markdown("---")

    if "reset_counter" not in st.session_state:
        st.session_state["reset_counter"] = 0

    conn = get_db_connection()

    cur1 = conn.cursor()
    cur1.execute("SELECT doctor_id, name, specialisation FROM Doctor")
    all_doctors = cur1.fetchall()
    cur1.close()

    st.markdown("### 👨‍⚕️ Prescribing Doctor")
    current_doc = st.selectbox(
        "Logged in as:",
        all_doctors,
        format_func=lambda x: f"{x[1]}  ·  {x[2]}  ({x[0]})",
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### 📋 New Prescription")

    cur2 = conn.cursor()
    cur2.execute("SELECT patient_id, name FROM Patient")
    patients = cur2.fetchall()
    cur2.close()

    cur3 = conn.cursor()
    cur3.execute("SELECT drug_id, drug_name FROM Drugs")
    drugs = cur3.fetchall()
    cur3.close()

    auto_id = get_next_id("Prescription", "prescription_id", "pre")
    counter = st.session_state["reset_counter"]

    col1, col2 = st.columns(2)
    with col1:
        patient_choice = st.selectbox(
            "Select Patient",
            [None] + patients,
            format_func=lambda x: "— Select Patient —" if x is None else f"{x[0]}  ·  {x[1]}",
            key=f"patient_select_{counter}"
        )
    with col2:
        drug_choice = st.selectbox(
            "Select Drug",
            [None] + drugs,
            format_func=lambda x: "— Select Drug —" if x is None else f"{x[0]}  ·  {x[1]}",
            key=f"drug_select_{counter}"
        )

    col3, col4, col5 = st.columns([2, 2, 3])
    with col3:
        st.date_input("Start Date", value=date.today(), disabled=True)
    with col4:
        end_date = st.date_input(
            "End Date",
            value=date.today() + timedelta(days=30),
            min_value=date.today(),
            key=f"end_date_{counter}",
            help="Defaults to 30 days from today. Select another date if needed."
        )
    with col5:
        st.text_input("Prescription ID", value=auto_id, disabled=True)

    # ── Conflict Detection ──
    is_conflict = False
    conflict_message = ""
    conflicting_drugs = []

    if patient_choice is not None and drug_choice is not None:
        # Check 1: Exact duplicate
        cur4 = conn.cursor()
        cur4.execute("""
            SELECT d.drug_name, p.start_date, p.end_date
            FROM Has h
            JOIN Prescription p ON h.prescription_id = p.prescription_id
            JOIN Drugs d ON h.drug_id = d.drug_id
            WHERE p.patient_id = %s
            AND h.drug_id = %s
            AND (p.end_date IS NULL OR p.end_date >= CURDATE())
        """, (patient_choice[0], drug_choice[0]))
        exact_duplicate = cur4.fetchone()
        cur4.close()

        if exact_duplicate:
            is_conflict = True
            end_str = exact_duplicate[2] if exact_duplicate[2] else "No end date"
            conflict_message = f"""
            <div class="alert-danger">
                <strong style="color:#fca5a5;font-size:1.05rem;">🚫 Duplicate Prescription Blocked</strong><br><br>
                <span style="color:#fecaca;">
                    <strong>{exact_duplicate[0]}</strong> is already actively prescribed to this patient.<br>
                    Started: <strong>{exact_duplicate[1]}</strong> &nbsp;|&nbsp; Ends: <strong>{end_str}</strong>
                </span>
            </div>
            """

        # Check 2: Clinician-approved drug-pair interaction
        if not is_conflict:
            cur_pair = conn.cursor()
            cur_pair.execute("""
                SELECT d.drug_name, di.interaction_severity, di.clinical_note
                FROM Prescription p
                JOIN Has h ON h.prescription_id = p.prescription_id
                JOIN Drugs d ON d.drug_id = h.drug_id
                JOIN Drug_Interaction di ON
                    di.drug_id_1 = LEAST(%s, h.drug_id) AND di.drug_id_2 = GREATEST(%s, h.drug_id)
                WHERE p.patient_id = %s
                  AND (p.end_date IS NULL OR p.end_date >= CURDATE())
                  AND di.interaction_severity IN ('Medium', 'High')
            """, (drug_choice[0], drug_choice[0], patient_choice[0]))
            known_interactions = cur_pair.fetchall()
            cur_pair.close()
            if known_interactions:
                is_conflict = True
                details = "".join(
                    f"<li><strong>{name}</strong> — {severity} interaction"
                    f"{': ' + note if note else ''}</li>" for name, severity, note in known_interactions
                )
                conflict_message = f"""
                <div class="alert-danger">
                    <strong style="color:#fca5a5;font-size:1.05rem;">⚠️ Known Drug Interaction</strong><br><br>
                    <span style="color:#fecaca;">The selected drug has a clinician-approved interaction with an active medication:</span>
                    <ul style="color:#fecaca;margin-bottom:0;">{details}</ul>
                </div>
                """

        # Check 3: Drug family conflict
        if not is_conflict:
            cur5 = conn.cursor()
            cur5.execute("SELECT super_drug_id FROM Drugs WHERE drug_id = %s", (drug_choice[0],))
            new_super_id = cur5.fetchone()[0]
            cur5.close()

            if new_super_id is not None:
                root_id = new_super_id
                while True:
                    cur_temp = conn.cursor()
                    cur_temp.execute("SELECT super_drug_id FROM Drugs WHERE drug_id = %s", (root_id,))
                    parent = cur_temp.fetchone()[0]
                    cur_temp.close()
                    if parent is None:
                        break
                    root_id = parent
            else:
                root_id = drug_choice[0]

            family_ids = get_all_family_drug_ids(conn, root_id)
            family_ids.discard(drug_choice[0])

            if family_ids:
                format_strings = ','.join(['%s'] * len(family_ids))
                cur6 = conn.cursor()
                cur6.execute(f"""
                    SELECT d.drug_name, d.severity, d.drug_id
                    FROM Has h
                    JOIN Prescription p ON h.prescription_id = p.prescription_id
                    JOIN Drugs d ON h.drug_id = d.drug_id
                    WHERE p.patient_id = %s
                    AND h.drug_id IN ({format_strings})
                    AND (p.end_date IS NULL OR p.end_date >= CURDATE())
                """, (patient_choice[0], *family_ids))
                conflicting_drugs = cur6.fetchall()
                cur6.close()

            if conflicting_drugs:
                is_conflict = True
                drug_badges = ""
                for drug_name, severity, drug_id in conflicting_drugs:
                    badge = severity_badge(severity)
                    # Check for community feedback on this pair
                    pair_info = ""
                    cur_pair = conn.cursor()
                    d1 = min(drug_choice[0], drug_id)
                    d2 = max(drug_choice[0], drug_id)
                    cur_pair.execute("""
                        SELECT total_reports, avg_side_effect_severity
                        FROM Drug_Pair_Stats
                        WHERE drug_id_1 = %s AND drug_id_2 = %s
                    """, (d1, d2))
                    pair_data = cur_pair.fetchone()
                    cur_pair.close()
                    if pair_data and pair_data[0] > 0:
                        pair_info = f'<br><span style="color:#94a3b8;font-size:0.8rem;">📊 {pair_data[0]} patient reports · Avg side-effect: {pair_data[1]}/5</span>'

                    drug_badges += f"""
                    <div style="margin:8px 0;padding:10px 14px;background:rgba(0,0,0,0.2);border-radius:10px;">
                        <strong style="color:#fecaca;">{drug_name}</strong>&nbsp;&nbsp;{badge}
                        {pair_info}
                    </div>
                    """
                conflict_message = f"""
                <div class="alert-danger">
                    <strong style="color:#fca5a5;font-size:1.05rem;">⚠️ Drug Family Conflict Detected</strong><br><br>
                    <span style="color:#e2e8f0;font-size:0.9rem;">
                        Patient is currently taking conflicting medication(s) from the same drug family:
                    </span>
                    {drug_badges}
                </div>
                """

        if is_conflict:
            st.markdown(conflict_message, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-success">
                <strong style="color:#86efac;font-size:1.05rem;">✅ No Conflicts Detected</strong><br>
                <span style="color:#bbf7d0;">This prescription is safe to issue. No active drug interactions found.</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Current Medications ──
    if patient_choice is not None:
        st.markdown("---")
        st.markdown(f"### 💊 Current Medications — {patient_choice[1]}")

        cur7 = conn.cursor()
        cur7.execute("""
            SELECT d.drug_name, d.severity, p.start_date, p.end_date, doc.name
            FROM Has h
            JOIN Prescription p ON h.prescription_id = p.prescription_id
            JOIN Drugs d ON h.drug_id = d.drug_id
            JOIN Doctor doc ON p.doctor_id = doc.doctor_id
            WHERE p.patient_id = %s
            ORDER BY p.start_date DESC
        """, (patient_choice[0],))
        history = cur7.fetchall()
        cur7.close()

        if history:
            st.dataframe(
                data=[{
                    "Drug": r[0],
                    "Severity": r[1] if r[1] else "N/A",
                    "Start": r[2],
                    "End": r[3] if r[3] else "Ongoing",
                    "Prescribed By": r[4],
                    "Status": "🟢 Active" if (r[3] is None or r[3] >= date.today()) else "⚪ Ended"
                } for r in history],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.markdown("""
            <div class="alert-info">
                <span style="color:#93c5fd;">No prescriptions found for this patient.</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        btn_col, _ = st.columns([1, 3])
        with btn_col:
            confirm = st.button(
                "✓  Confirm Prescription",
                type="primary",
                use_container_width=True,
                disabled=(is_conflict or drug_choice is None)
            )

        if confirm:
            if end_date is None:
                st.error("Please select an end date before confirming.")
            elif drug_choice is None:
                st.error("Please select a drug before confirming.")
            else:
                try:
                    cur8 = conn.cursor()
                    cur8.execute(
                        "INSERT INTO Prescription (prescription_id, doctor_id, patient_id, start_date, end_date) VALUES (%s, %s, %s, CURDATE(), %s)",
                        (auto_id, current_doc[0], patient_choice[0], end_date)
                    )
                    conn.commit()
                    cur8.execute(
                        "INSERT INTO Has (drug_id, prescription_id) VALUES (%s, %s)",
                        (drug_choice[0], auto_id)
                    )
                    conn.commit()
                    cur8.close()
                    st.session_state["success_message"] = f"✅ Prescription {auto_id} issued for {patient_choice[1]} — {drug_choice[1]} until {end_date}"
                    st.session_state["reset_counter"] += 1
                    st.rerun()
                except Exception as e:
                    conn.rollback()
                    st.error(f"Database Error: {e}")
                finally:
                    conn.close()


# ============================================================
# PAGE: STRUCTURED PATIENT FEEDBACK
# ============================================================
def patient_feedback_page():
    st.title("📝 Patient Feedback")
    st.caption("Submit structured daily feedback on your prescriptions")
    st.markdown("---")

    conn = get_db_connection()

    cur1 = conn.cursor()
    cur1.execute("SELECT patient_id, name FROM Patient")
    patients = cur1.fetchall()
    cur1.close()

    st.markdown("### 🧑 Select Patient")
    patient_choice = st.selectbox(
        "Patient:",
        [None] + patients,
        format_func=lambda x: "— Select Patient —" if x is None else f"{x[0]}  ·  {x[1]}",
        key="feedback_patient"
    )

    if patient_choice is None:
        conn.close()
        return

    # ── Check if already submitted today ──
    cur_check = conn.cursor()
    cur_check.execute("""
        SELECT feedback_id FROM Structured_Feedback
        WHERE patient_id = %s AND feedback_date = CURDATE()
    """, (patient_choice[0],))
    already_today = cur_check.fetchone()
    cur_check.close()

    # ── Show active prescriptions ──
    cur2 = conn.cursor()
    cur2.execute("""
        SELECT p.prescription_id, d.drug_name, d.drug_id, d.severity, p.start_date, p.end_date
        FROM Prescription p
        JOIN Has h ON p.prescription_id = h.prescription_id
        JOIN Drugs d ON h.drug_id = d.drug_id
        WHERE p.patient_id = %s
        AND (p.end_date IS NULL OR p.end_date >= CURDATE())
        ORDER BY p.start_date DESC
    """, (patient_choice[0],))
    active_prescriptions = cur2.fetchall()
    cur2.close()

    if not active_prescriptions:
        st.markdown("""
        <div class="alert-info">
            <span style="color:#93c5fd;">No active prescriptions found for this patient.</span>
        </div>
        """, unsafe_allow_html=True)
        conn.close()
        return

    st.markdown("---")
    st.markdown(f"### 💊 Active Medications — {patient_choice[1]}")

    # Display active medications as cards
    med_html = ""
    for rx in active_prescriptions:
        badge = severity_badge(rx[3])
        end_str = rx[5] if rx[5] else "Ongoing"
        med_html += f"""
        <div style="display:inline-block;background:rgba(30,41,79,0.4);border:1px solid rgba(99,102,241,0.15);
                    border-radius:12px;padding:12px 18px;margin:6px 8px 6px 0;min-width:220px;">
            <strong style="color:#e2e8f0;font-size:0.95rem;">{rx[1]}</strong>&nbsp;&nbsp;{badge}<br>
            <span style="color:#64748b;font-size:0.78rem;">Rx: {rx[0]} · Since: {rx[4]} · Until: {end_str}</span>
        </div>
        """
    st.markdown(med_html, unsafe_allow_html=True)

    if already_today:
        st.markdown("""
        <div class="alert-warning" style="margin-top:20px;">
            <strong style="color:#fcd34d;font-size:1.05rem;">⏳ Feedback Already Submitted Today</strong><br>
            <span style="color:#fde68a;">You have already submitted feedback today. Please come back tomorrow for your next daily check-in.</span>
        </div>
        """, unsafe_allow_html=True)

        # Show today's feedback
        cur_today = conn.cursor()
        cur_today.execute("""
            SELECT overall_effectiveness, side_effect_severity, nausea, dizziness, headache,
                   fatigue, stomach_upset, insomnia, mood_changes, skin_reaction, additional_notes
            FROM Structured_Feedback
            WHERE patient_id = %s AND feedback_date = CURDATE()
        """, (patient_choice[0],))
        today_fb = cur_today.fetchone()
        cur_today.close()

        if today_fb:
            st.markdown("#### Today's Submission")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""
                <div class="glass-card">
                    <div style="color:#94a3b8;font-size:0.78rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Effectiveness</div>
                    {star_rating_display(today_fb[0])}
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""
                <div class="glass-card">
                    <div style="color:#94a3b8;font-size:0.78rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Side Effect Severity</div>
                    {star_rating_display(today_fb[1])}
                </div>
                """, unsafe_allow_html=True)

            symptom_names = ["Nausea", "Dizziness", "Headache", "Fatigue", "Stomach Upset", "Insomnia", "Mood Changes", "Skin Reaction"]
            reported = [symptom_names[i] for i in range(8) if today_fb[2 + i]]
            if reported:
                tags = "".join(f'<span class="symptom-tag">{s}</span>' for s in reported)
            else:
                tags = '<span class="symptom-tag-none">No symptoms reported</span>'
            st.markdown(f"""
            <div class="glass-card">
                <div style="color:#94a3b8;font-size:0.78rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Reported Symptoms</div>
                {tags}
            </div>
            """, unsafe_allow_html=True)

            if today_fb[10]:
                st.markdown(f"""
                <div class="glass-card">
                    <div style="color:#94a3b8;font-size:0.78rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Additional Notes</div>
                    <span style="color:#cbd5e1;font-style:italic;">"{today_fb[10]}"</span>
                </div>
                """, unsafe_allow_html=True)

        conn.close()
        return

    # ── Feedback Form ──
    st.markdown("---")
    st.markdown("### 📊 Daily Feedback Form")

    st.markdown("""
    <div class="alert-info">
        <span style="color:#93c5fd;">Rate your experience with your current medications. This feedback helps improve drug interaction assessments for all patients.</span>
    </div>
    """, unsafe_allow_html=True)

    # Select which prescription to give feedback on
    prescription_choice = st.selectbox(
        "Feedback for prescription:",
        active_prescriptions,
        format_func=lambda x: f"{x[1]}  ·  Rx {x[0]}  (Since: {x[4]})",
        key="feedback_prescription_select"
    )

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("##### How effective is this medication?")
        effectiveness = st.slider(
            "Effectiveness",
            min_value=1, max_value=5, value=3,
            help="1 = Not effective, 5 = Very effective",
            label_visibility="collapsed"
        )
        eff_labels = {1: "Not Effective", 2: "Slightly Effective", 3: "Moderately Effective", 4: "Effective", 5: "Very Effective"}
        st.caption(f"{'⭐' * effectiveness} — {eff_labels[effectiveness]}")

    with col_r2:
        st.markdown("##### How severe are side effects?")
        side_effects = st.slider(
            "Side Effects",
            min_value=1, max_value=5, value=1,
            help="1 = None, 5 = Very severe",
            label_visibility="collapsed"
        )
        sev_labels = {1: "None", 2: "Mild", 3: "Moderate", 4: "Severe", 5: "Very Severe"}
        st.caption(f"{'🔴' * side_effects}{'⚪' * (5 - side_effects)} — {sev_labels[side_effects]}")

    st.markdown("##### Symptoms experienced")
    st.caption("Select all that apply")
    sym_cols = st.columns(4)
    symptoms = {}
    symptom_list = [
        ("nausea", "🤢 Nausea"),
        ("dizziness", "💫 Dizziness"),
        ("headache", "🤕 Headache"),
        ("fatigue", "😴 Fatigue"),
        ("stomach_upset", "🫃 Stomach Upset"),
        ("insomnia", "🌙 Insomnia"),
        ("mood_changes", "🎭 Mood Changes"),
        ("skin_reaction", "🩹 Skin Reaction"),
    ]
    for i, (key, label) in enumerate(symptom_list):
        with sym_cols[i % 4]:
            symptoms[key] = st.checkbox(label, key=f"sym_{key}")

    additional_notes = st.text_area(
        "Additional notes (optional)",
        placeholder="Any other observations about your medication experience...",
        height=100
    )

    st.markdown("---")
    btn_col, _ = st.columns([1, 3])
    with btn_col:
        submit_feedback = st.button("📤  Submit Feedback", type="primary", use_container_width=True)

    if submit_feedback:
        try:
            feedback_id = get_next_id("Structured_Feedback", "feedback_id", "sf")
            cur3 = conn.cursor()
            cur3.execute("""
                INSERT INTO Structured_Feedback
                (feedback_id, prescription_id, patient_id, feedback_date,
                 overall_effectiveness, side_effect_severity,
                 nausea, dizziness, headache, fatigue, stomach_upset, insomnia, mood_changes, skin_reaction,
                 additional_notes)
                VALUES (%s, %s, %s, CURDATE(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                feedback_id,
                prescription_choice[0],
                patient_choice[0],
                effectiveness,
                side_effects,
                symptoms["nausea"],
                symptoms["dizziness"],
                symptoms["headache"],
                symptoms["fatigue"],
                symptoms["stomach_upset"],
                symptoms["insomnia"],
                symptoms["mood_changes"],
                symptoms["skin_reaction"],
                additional_notes.strip() if additional_notes.strip() else None
            ))
            conn.commit()

            # Call the stored procedure to update Drug_Pair_Stats
            cur3.callproc("recalculate_drug_pair_stats", [
                patient_choice[0],
                prescription_choice[0],
                side_effects,
                effectiveness
            ])
            conn.commit()

            # Call evaluate_severity_changes to check thresholds
            cur3.callproc("evaluate_severity_changes")
            conn.commit()

            cur3.close()
            st.session_state["success_message"] = f"✅ Feedback submitted successfully for {prescription_choice[1]}!"
            st.rerun()
        except Exception as e:
            conn.rollback()
            error_str = str(e)
            if "DAILY_LIMIT" in error_str:
                st.markdown("""
                <div class="alert-warning">
                    <strong style="color:#fcd34d;">⏳ Daily Limit Reached</strong><br>
                    <span style="color:#fde68a;">You have already submitted feedback today. Please try again tomorrow.</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"Database Error: {e}")

    # ── Feedback History ──
    st.markdown("---")
    st.markdown("### 📜 Feedback History")

    cur_hist = conn.cursor()
    cur_hist.execute("""
        SELECT sf.feedback_date, d.drug_name, sf.overall_effectiveness, sf.side_effect_severity,
               sf.nausea, sf.dizziness, sf.headache, sf.fatigue, sf.stomach_upset,
               sf.insomnia, sf.mood_changes, sf.skin_reaction, sf.additional_notes
        FROM Structured_Feedback sf
        JOIN Prescription p ON sf.prescription_id = p.prescription_id
        JOIN Has h ON p.prescription_id = h.prescription_id
        JOIN Drugs d ON h.drug_id = d.drug_id
        WHERE sf.patient_id = %s
        ORDER BY sf.feedback_date DESC
        LIMIT 10
    """, (patient_choice[0],))
    history = cur_hist.fetchall()
    cur_hist.close()

    if history:
        for fb in history:
            symptom_names = ["Nausea", "Dizziness", "Headache", "Fatigue", "Stomach Upset", "Insomnia", "Mood Changes", "Skin Reaction"]
            reported = [symptom_names[i] for i in range(8) if fb[4 + i]]
            if reported:
                tags = "".join(f'<span class="symptom-tag">{s}</span>' for s in reported)
            else:
                tags = '<span class="symptom-tag-none">No symptoms</span>'
            notes_html = f'<br><span style="color:#94a3b8;font-style:italic;">"{fb[12]}"</span>' if fb[12] else ""
            st.markdown(f"""
            <div class="glass-card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <strong style="color:#c7d2fe;font-size:1rem;">{fb[1]}</strong>
                    <span style="color:#64748b;font-size:0.8rem;">{fb[0]}</span>
                </div>
                <div style="display:flex;gap:30px;margin:8px 0;">
                    <div>
                        <span style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase;">Effectiveness</span><br>
                        {star_rating_display(fb[2])}
                    </div>
                    <div>
                        <span style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase;">Side Effects</span><br>
                        {star_rating_display(fb[3])}
                    </div>
                </div>
                {tags}
                {notes_html}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-info">
            <span style="color:#93c5fd;">No feedback history yet. Submit your first daily feedback above!</span>
        </div>
        """, unsafe_allow_html=True)

    conn.close()


# ============================================================
# PAGE: INTERACTION ANALYTICS
# ============================================================
def pair_feedback_page():
    """Daily, pair-specific feedback used by the interaction-evidence pipeline."""
    st.title("📝 Daily Interaction Check-in")
    st.caption("One structured check-in per day. Reports are reviewed before any interaction level changes.")
    st.markdown("---")
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT patient_id, name FROM Patient ORDER BY name")
        patients = cur.fetchall()
        cur.close()
        patient = st.selectbox("Patient", [None] + patients,
                               format_func=lambda x: "— Select Patient —" if x is None else f"{x[1]} ({x[0]})")
        if patient is None:
            return

        cur = conn.cursor()
        cur.execute("""
            SELECT d.drug_id, d.drug_name
            FROM Prescription p JOIN Has h ON h.prescription_id = p.prescription_id
            JOIN Drugs d ON d.drug_id = h.drug_id
            WHERE p.patient_id = %s AND (p.end_date IS NULL OR p.end_date >= CURDATE())
            ORDER BY d.drug_name
        """, (patient[0],))
        medications = cur.fetchall()
        cur.execute("SELECT pair_feedback_id FROM Pair_Feedback WHERE patient_id = %s AND feedback_date = CURDATE()",
                    (patient[0],))
        already_submitted = cur.fetchone() is not None
        cur.close()

        if len(medications) < 2:
            st.info("This check-in becomes available when the patient has at least two active medications.")
            return
        pairs = [(a, b) for index, a in enumerate(medications) for b in medications[index + 1:]]
        st.markdown("### Active medication pair")
        selected_pair = st.selectbox(
            "Which two medicines are you reporting on?",
            pairs,
            format_func=lambda pair: f"{pair[0][1]}  +  {pair[1][1]}",
        )
        if already_submitted:
            st.warning("A daily interaction check-in has already been submitted for this patient. Please return tomorrow.")
            return

        st.markdown("### What changed while taking this pair?")
        timing_label = st.radio(
            "Did any symptom start or become worse after taking both medicines?",
            ["Yes", "Probably", "No", "Not sure"], horizontal=True,
            help="Choose ‘Probably’ only when the timing suggests a connection, but you are not certain."
        )
        impact = st.slider(
            "How much did these symptoms affect daily activities?",
            1, 5, 1,
            help="1 = no impact; 3 = some activities affected; 5 = unable to carry out usual activities."
        )
        if timing_label in ("Yes", "Probably") and impact >= 4:
            st.error("Severe or worsening symptoms need prompt clinical advice. This app is not emergency care.")

        st.markdown("##### Symptoms noticed")
        symptom_options = [
            ("nausea", "Nausea"), ("dizziness", "Dizziness"), ("headache", "Headache"),
            ("fatigue", "Fatigue"), ("stomach_upset", "Stomach upset"), ("insomnia", "Insomnia"),
            ("mood_changes", "Mood changes"), ("skin_reaction", "Skin reaction"),
        ]
        columns = st.columns(4)
        selected_symptoms = {}
        for index, (key, label) in enumerate(symptom_options):
            with columns[index % 4]:
                selected_symptoms[key] = st.checkbox(label, key=f"pair_feedback_{key}")
        notes = st.text_area("Additional observations (optional)", max_chars=500,
                             placeholder="For example: when the symptom began, how long it lasted, or anything that helped.")

        if st.button("Submit daily check-in", type="primary"):
            if timing_label in ("Yes", "Probably") and not any(selected_symptoms.values()):
                st.error("Select at least one symptom, or choose ‘No’ / ‘Not sure’.")
                return
            d1, d2 = sorted((selected_pair[0][0], selected_pair[1][0]))
            timing = {"Yes": "yes", "Probably": "likely", "No": "no", "Not sure": "unsure"}[timing_label]
            cur = conn.cursor()
            try:
                cur.execute("""
                    INSERT INTO Pair_Feedback
                    (patient_id, drug_id_1, drug_id_2, feedback_date, symptom_timing, impact_severity,
                     nausea, dizziness, headache, fatigue, stomach_upset, insomnia, mood_changes, skin_reaction, additional_notes)
                    VALUES (%s, %s, %s, CURDATE(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (patient[0], d1, d2, timing, impact,
                      *[selected_symptoms[key] for key, _ in symptom_options], notes.strip() or None))
                cur.callproc("refresh_interaction_evidence", [d1, d2])
                cur.callproc("evaluate_interaction_changes")
                conn.commit()
                st.session_state["success_message"] = "Daily interaction check-in submitted. Thank you."
                st.rerun()
            except Exception as error:
                conn.rollback()
                st.error(f"Could not submit check-in: {error}")
            finally:
                cur.close()
    finally:
        conn.close()


def analytics_page():
    st.title("📊 Interaction Analytics")
    st.caption("Community-driven drug interaction intelligence powered by patient feedback")
    st.markdown("---")

    conn = get_db_connection()

    tab1, tab2, tab3 = st.tabs(["📈 Drug Pair Statistics", "🔄 Severity Change Proposals", "📋 Change History"])

    # ── Tab 1: Drug Pair Stats ──
    with tab1:
        st.markdown("### Community-Reported Drug Pair Interactions")
        st.markdown("""
        <div class="alert-info">
            <span style="color:#93c5fd;">
                These statistics are aggregated from structured, pair-specific patient feedback. When enough
                distinct patients report a consistent interaction signal, the system proposes a clinician review.
                <br><strong>Threshold: 5+ distinct patients and at least 60% positive interaction reports.</strong>
            </span>
        </div>
        """, unsafe_allow_html=True)

        cur1 = conn.cursor()
        cur1.execute("""
            SELECT dps.drug_id_1, d1.drug_name, dps.drug_id_2, d2.drug_name,
                   dps.distinct_patients, dps.avg_positive_impact, 0,
                   dps.high_impact_reports, dps.likely_interaction_reports, dps.no_interaction_reports
            FROM Interaction_Evidence_Stats dps
            JOIN Drugs d1 ON dps.drug_id_1 = d1.drug_id
            JOIN Drugs d2 ON dps.drug_id_2 = d2.drug_id
            ORDER BY dps.total_reports DESC
        """)
        pair_stats = cur1.fetchall()
        cur1.close()

        if pair_stats:
            for ps in pair_stats:
                total = ps[4]
                avg_sev = float(ps[5])
                avg_eff = float(ps[6])
                high = ps[7]
                med = ps[8]
                low = ps[9]

                # Determine bar color based on avg severity
                if avg_sev >= 4.0:
                    bar_color = "linear-gradient(90deg, #ef4444, #dc2626)"
                    sev_label = "High Concern"
                elif avg_sev >= 2.5:
                    bar_color = "linear-gradient(90deg, #f59e0b, #d97706)"
                    sev_label = "Moderate Concern"
                else:
                    bar_color = "linear-gradient(90deg, #22c55e, #16a34a)"
                    sev_label = "Low Concern"

                bar_width = min(avg_sev / 5 * 100, 100)
                threshold_met = "✅ Evidence threshold met" if total >= 5 else f"⏳ {5 - total} more patients needed"

                st.markdown(f"""
                <div class="glass-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <strong style="color:#e2e8f0;font-size:1.05rem;">{ps[1]}</strong>
                            <span style="color:#6366f1;margin:0 8px;">⇆</span>
                            <strong style="color:#e2e8f0;font-size:1.05rem;">{ps[3]}</strong>
                        </div>
                        <span style="color:#94a3b8;font-size:0.85rem;">{total} distinct patients · {threshold_met}</span>
                    </div>
                    <div style="margin-top:12px;display:flex;gap:24px;">
                        <div style="flex:1;">
                            <span style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase;">Avg impact (positive reports)</span>
                            <div class="severity-bar">
                                <div class="severity-bar-fill" style="width:{bar_width}%;background:{bar_color};"></div>
                            </div>
                            <span style="color:#cbd5e1;font-size:0.85rem;font-weight:600;">{avg_sev:.2f}/5 — {sev_label}</span>
                        </div>
                        <div style="flex:1;">
                            <span style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase;">Evidence rule</span><br>
                            <span style="color:#cbd5e1;font-size:0.85rem;font-weight:600;">5+ patients and ≥60% positive reports</span>
                        </div>
                    </div>
                    <div style="margin-top:10px;display:flex;gap:12px;">
                        <span style="color:#fca5a5;font-size:0.78rem;">🔴 {high} high-impact</span>
                        <span style="color:#fcd34d;font-size:0.78rem;">🟡 {med} positive signals</span>
                        <span style="color:#86efac;font-size:0.78rem;">🟢 {low} no interaction</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-info">
                <span style="color:#93c5fd;">No interaction evidence yet. Evidence is generated after structured daily pair check-ins.</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Tab 2: Pending Proposals ──
    with tab2:
        st.markdown("### ⚡ Pending Severity Change Proposals")
        st.markdown("""
        <div class="alert-warning">
            <span style="color:#fde68a;">
                These proposals are generated automatically when community feedback reaches the threshold.
                <strong>Approve</strong> to update the drug's severity level, or <strong>Reject</strong> to dismiss.
            </span>
        </div>
        """, unsafe_allow_html=True)

        cur2 = conn.cursor()
        cur2.execute("""
            SELECT scl.log_id, scl.drug_id, d1.drug_name, scl.related_drug_id, d2.drug_name,
                   scl.old_severity, scl.proposed_severity, scl.reason, scl.feedback_count,
                   scl.avg_reported_severity, scl.created_at
            FROM Severity_Change_Log scl
            JOIN Drugs d1 ON scl.drug_id = d1.drug_id
            LEFT JOIN Drugs d2 ON scl.related_drug_id = d2.drug_id
            WHERE scl.status = 'proposed'
            ORDER BY scl.created_at DESC
        """)
        proposals = cur2.fetchall()
        cur2.close()

        if proposals:
            for prop in proposals:
                old_badge = severity_badge(prop[5])
                new_badge = severity_badge(prop[6])

                st.markdown(f"""
                <div class="glass-card" style="border-color:rgba(245,158,11,0.3);">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <strong style="color:#e2e8f0;font-size:1.1rem;">{prop[2]}</strong>
                        <span style="color:#64748b;font-size:0.8rem;">Proposal #{prop[0]} · {prop[10]}</span>
                    </div>
                    <div style="margin:12px 0;">
                        <span style="color:#94a3b8;">Related to:</span>
                        <strong style="color:#c7d2fe;"> {prop[4] if prop[4] else 'N/A'}</strong>
                    </div>
                    <div style="display:flex;align-items:center;gap:12px;margin:10px 0;">
                        <span style="color:#94a3b8;">Current:</span> {old_badge}
                        <span style="color:#6366f1;font-size:1.2rem;">→</span>
                        <span style="color:#94a3b8;">Proposed:</span> {new_badge}
                    </div>
                    <div style="margin:10px 0;padding:10px 14px;background:rgba(0,0,0,0.2);border-radius:8px;">
                        <span style="color:#cbd5e1;font-size:0.88rem;">{prop[7]}</span>
                    </div>
                    <div style="color:#94a3b8;font-size:0.82rem;">
                        📊 Based on {prop[8]} patient reports · Avg reported severity: {prop[9]}/5
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col_a, col_r, _ = st.columns([1, 1, 3])
                with col_a:
                    if st.button(f"✓ Approve", key=f"approve_{prop[0]}", type="primary", use_container_width=True):
                        try:
                            cur_a = conn.cursor()
                            procedure = "apply_interaction_change" if str(prop[7]).startswith("PAIR_EVIDENCE:") else "apply_severity_change"
                            cur_a.callproc(procedure, [prop[0]])
                            conn.commit()
                            cur_a.close()
                            st.session_state["success_message"] = f"✅ Severity for {prop[2]} updated to {prop[6]}!"
                            st.rerun()
                        except Exception as e:
                            conn.rollback()
                            st.error(f"Error: {e}")
                with col_r:
                    if st.button(f"✗ Reject", key=f"reject_{prop[0]}", use_container_width=True):
                        try:
                            cur_r = conn.cursor()
                            cur_r.callproc("reject_severity_change", [prop[0]])
                            conn.commit()
                            cur_r.close()
                            st.session_state["success_message"] = f"Proposal #{prop[0]} rejected."
                            st.rerun()
                        except Exception as e:
                            conn.rollback()
                            st.error(f"Error: {e}")

                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-success">
                <strong style="color:#86efac;">All Clear</strong><br>
                <span style="color:#bbf7d0;">No pending severity change proposals. The system will generate proposals when community feedback reaches the threshold (5+ reports).</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Tab 3: Change History ──
    with tab3:
        st.markdown("### 📋 Severity Change History")

        cur3 = conn.cursor()
        cur3.execute("""
            SELECT scl.log_id, d1.drug_name, d2.drug_name, scl.old_severity, scl.proposed_severity,
                   scl.status, scl.feedback_count, scl.created_at, scl.resolved_at
            FROM Severity_Change_Log scl
            JOIN Drugs d1 ON scl.drug_id = d1.drug_id
            LEFT JOIN Drugs d2 ON scl.related_drug_id = d2.drug_id
            WHERE scl.status != 'proposed'
            ORDER BY scl.resolved_at DESC
        """)
        history = cur3.fetchall()
        cur3.close()

        if history:
            st.dataframe(
                data=[{
                    "#": h[0],
                    "Drug": h[1],
                    "Related To": h[2] if h[2] else "N/A",
                    "Old Severity": h[3] if h[3] else "N/A",
                    "New Severity": h[4],
                    "Status": "✅ Approved" if h[5] == "approved" else ("❌ Rejected" if h[5] == "rejected" else "⚡ Auto-Applied"),
                    "Reports": h[6],
                    "Date": h[8] if h[8] else h[7]
                } for h in history],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.markdown("""
            <div class="alert-info">
                <span style="color:#93c5fd;">No severity changes have been processed yet.</span>
            </div>
            """, unsafe_allow_html=True)

    conn.close()


# ============================================================
# PAGE: LEGACY FEEDBACK (kept for backward compatibility)
# ============================================================
def legacy_feedback_page():
    st.title("📋 Legacy Feedback")
    st.caption("View and manage text-based feedback from the original system")
    st.markdown("---")

    conn = get_db_connection()

    cur1 = conn.cursor()
    cur1.execute("SELECT patient_id, name FROM Patient")
    patients = cur1.fetchall()
    cur1.close()

    patient_choice = st.selectbox(
        "Select Patient:",
        [None] + patients,
        format_func=lambda x: "— Select Patient —" if x is None else f"{x[0]}  ·  {x[1]}",
        key="legacy_feedback_patient"
    )

    if patient_choice is not None:
        cur2 = conn.cursor()
        cur2.execute("""
            SELECT p.prescription_id, d.drug_name, p.start_date, p.end_date,
                   f.feedback_no, f.comments, f.last_updated
            FROM Prescription p
            JOIN Has h ON p.prescription_id = h.prescription_id
            JOIN Drugs d ON h.drug_id = d.drug_id
            LEFT JOIN Feedback f ON p.prescription_id = f.prescription_id
            WHERE p.patient_id = %s
            ORDER BY p.start_date DESC
        """, (patient_choice[0],))
        prescriptions = cur2.fetchall()
        cur2.close()

        if prescriptions:
            st.dataframe(
                data=[{
                    "Rx ID": r[0],
                    "Drug": r[1],
                    "Start": r[2],
                    "End": r[3] if r[3] else "Ongoing",
                    "Feedback": r[5] if r[5] else "No feedback",
                    "Last Updated": r[6] if r[6] else "—"
                } for r in prescriptions],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No prescriptions found.")

    conn.close()


# ============================================================
# PAGE: ADD NEW PATIENT
# ============================================================
def add_patient_page():
    st.title("🧑 Add New Patient")
    st.caption("Register a new patient in the MediPal system")
    st.markdown("---")

    conn = get_db_connection()

    new_patient_id = get_next_id("Patient", "patient_id", "pat")

    st.markdown("### Patient Details")

    st.text_input("Patient ID (Auto-generated)", value=new_patient_id, disabled=True)

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name")
    with col2:
        age = st.number_input("Age", min_value=0, max_value=120, step=1)

    col3, col4 = st.columns(2)
    with col3:
        gender = st.selectbox(
            "Gender",
            [None, "M", "F"],
            format_func=lambda x: "— Select Gender —" if x is None else ("Male" if x == "M" else "Female")
        )
    with col4:
        blood_group = st.selectbox(
            "Blood Group",
            [None, "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "AB"],
            format_func=lambda x: "— Select Blood Group —" if x is None else x
        )

    weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, step=0.1, format="%.2f")

    st.markdown("---")
    btn_col, _ = st.columns([1, 3])
    with btn_col:
        submit = st.button("➕  Add Patient", type="primary", use_container_width=True)

    if submit:
        if not name.strip():
            st.error("Please enter the patient's name.")
        elif gender is None:
            st.error("Please select a gender.")
        elif blood_group is None:
            st.error("Please select a blood group.")
        elif weight <= 0:
            st.error("Please enter a valid weight.")
        else:
            try:
                cur2 = conn.cursor()
                cur2.execute(
                    "INSERT INTO Patient (patient_id, name, age, gender, weight, blood_group) VALUES (%s, %s, %s, %s, %s, %s)",
                    (new_patient_id, name.strip(), int(age), gender, float(weight), blood_group)
                )
                conn.commit()
                cur2.close()
                st.session_state["success_message"] = f"✅ Patient {name.strip()} added with ID {new_patient_id}"
                st.rerun()
            except Exception as e:
                conn.rollback()
                st.error(f"Database Error: {e}")
            finally:
                conn.close()

    conn.close()


# ============================================================
# PAGE: ADD NEW DOCTOR
# ============================================================
def add_doctor_page():
    st.title("👨‍⚕️ Add New Doctor")
    st.caption("Register a new doctor in the MediPal system")
    st.markdown("---")

    conn = get_db_connection()

    new_doctor_id = get_next_id("Doctor", "doctor_id", "doc")

    st.markdown("### Doctor Details")

    st.text_input("Doctor ID (Auto-generated)", value=new_doctor_id, disabled=True)

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name")
    with col2:
        age = st.number_input("Age", min_value=20, max_value=100, step=1)

    specialisation = st.selectbox("Specialisation", [
        None, "Cardiologist", "Neurologist", "Dermatologist", "Pediatrician",
        "Oncologist", "Gastroenterologist", "Endocrinologist", "Orthopedic",
        "Psychiatrist", "General Physician"
    ], format_func=lambda x: "— Select Specialisation —" if x is None else x)

    st.markdown("#### 📞 Phone Numbers")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        phone1 = st.text_input("Phone Number 1", max_chars=10)
    with col_p2:
        phone2 = st.text_input("Phone Number 2 (optional)", max_chars=10)

    st.markdown("---")
    btn_col, _ = st.columns([1, 3])
    with btn_col:
        submit = st.button("➕  Add Doctor", type="primary", use_container_width=True)

    if submit:
        if not name.strip():
            st.error("Please enter the doctor's name.")
        elif specialisation is None:
            st.error("Please select a specialisation.")
        elif not phone1.strip() or not phone1.strip().isdigit() or len(phone1.strip()) != 10:
            st.error("Please enter a valid 10-digit phone number.")
        else:
            try:
                cur2 = conn.cursor()
                cur2.execute(
                    "INSERT INTO Doctor (doctor_id, name, age, specialisation) VALUES (%s, %s, %s, %s)",
                    (new_doctor_id, name.strip(), int(age), specialisation)
                )
                conn.commit()
                cur2.execute(
                    "INSERT INTO Doc_Phone_no (doctor_id, phone_no) VALUES (%s, %s)",
                    (new_doctor_id, phone1.strip())
                )
                conn.commit()
                if phone2.strip() and phone2.strip().isdigit() and len(phone2.strip()) == 10:
                    cur2.execute(
                        "INSERT INTO Doc_Phone_no (doctor_id, phone_no) VALUES (%s, %s)",
                        (new_doctor_id, phone2.strip())
                    )
                    conn.commit()
                cur2.close()
                st.session_state["success_message"] = f"✅ Doctor {name.strip()} added with ID {new_doctor_id}"
                st.rerun()
            except Exception as e:
                conn.rollback()
                st.error(f"Database Error: {e}")
            finally:
                conn.close()

    conn.close()


# ============================================================
# MAIN APP
# ============================================================
def main():
    st.set_page_config(
        page_title="MediPal — Drug Interaction Manager",
        page_icon="💊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    inject_premium_css()

    # ── Success Toast ──
    if "success_message" not in st.session_state:
        st.session_state["success_message"] = ""
    if st.session_state["success_message"]:
        st.sidebar.success(st.session_state["success_message"])
        st.session_state["success_message"] = ""

    # ── Sidebar ──
    st.sidebar.markdown("## 💊 MediPal")
    st.sidebar.caption("Drug Interaction Management System")
    st.sidebar.markdown("---")

    # Dashboard Metrics in Sidebar
    try:
        metrics = get_dashboard_metrics()
        # Streamlit can render a trailing closing tag as text when nested HTML
        # cards are passed in one Markdown block. Native columns avoid that.
        metric_col_1, metric_col_2 = st.sidebar.columns(2)
        with metric_col_1:
            st.markdown(render_metric_card("Patients", metrics["patients"], "🧑"), unsafe_allow_html=True)
            st.markdown(render_metric_card("Active Rx", metrics["active_prescriptions"], "💊"), unsafe_allow_html=True)
        with metric_col_2:
            st.markdown(render_metric_card("Doctors", metrics["doctors"], "👨‍⚕️"), unsafe_allow_html=True)
            st.markdown(render_metric_card("Feedback", metrics["total_feedback"], "📝"), unsafe_allow_html=True)

        if metrics["pending_reviews"] > 0:
            st.sidebar.markdown(f"""
            <div style="background:linear-gradient(135deg, rgba(245,158,11,0.2), rgba(217,119,6,0.1));
                        border:1px solid rgba(245,158,11,0.3);border-radius:10px;padding:10px 14px;
                        margin-bottom:12px;text-align:center;">
                <span style="color:#fcd34d;font-weight:700;font-size:0.9rem;">
                    ⚡ {metrics["pending_reviews"]} Pending Review{"s" if metrics["pending_reviews"] > 1 else ""}
                </span>
            </div>
            """, unsafe_allow_html=True)
    except Exception:
        pass

    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        [
            "🩺 Doctor Portal",
            "📝 Daily Interaction Check-in",
            "📊 Interaction Analytics",
            "📋 Legacy Feedback",
            "🧑 Add Patient",
            "👨‍⚕️ Add Doctor"
        ],
        label_visibility="collapsed",
        key="main_navigation"
    )

    if page == "🩺 Doctor Portal":
        doctors_page()
    elif page == "📝 Daily Interaction Check-in":
        pair_feedback_page()
    elif page == "📊 Interaction Analytics":
        analytics_page()
    elif page == "📋 Legacy Feedback":
        legacy_feedback_page()
    elif page == "🧑 Add Patient":
        add_patient_page()
    elif page == "👨‍⚕️ Add Doctor":
        add_doctor_page()


if __name__ == "__main__":
    main()
