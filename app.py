import streamlit as st
import mysql.connector
from datetime import date

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sukrit2006",
        database="Medipal"
    )

def get_next_prescription_id():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT prescription_id FROM Prescription ORDER BY prescription_id DESC LIMIT 1")
    last_id = cursor.fetchone()
    cursor.close()
    conn.close()
    if last_id:
        last_num = int(last_id[0][3:])
        digits = max(3, len(str(last_num + 1)))
        new_id = f"pre{str(last_num + 1).zfill(digits)}"
    else:
        new_id = "pre000"
    return new_id

def get_all_family_drug_ids(conn, root_drug_id):
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

def doctors_page():
    st.title("MediPal — Doctor Portal")
    st.markdown("---")

    if "reset_counter" not in st.session_state:
        st.session_state["reset_counter"] = 0

    conn = get_db_connection()

    cur1 = conn.cursor()
    cur1.execute("SELECT doctor_id, name FROM Doctor")
    all_doctors = cur1.fetchall()
    cur1.close()

    st.markdown("### Prescribing Doctor")
    current_doc = st.selectbox(
        "Logged in as:",
        all_doctors,
        format_func=lambda x: f"{x[1]} ({x[0]})",
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### New Prescription")

    cur2 = conn.cursor()
    cur2.execute("SELECT patient_id, name FROM Patient")
    patients = cur2.fetchall()
    cur2.close()

    cur3 = conn.cursor()
    cur3.execute("SELECT drug_id, drug_name FROM Drugs")
    drugs = cur3.fetchall()
    cur3.close()

    auto_id = get_next_prescription_id()
    counter = st.session_state["reset_counter"]

    col1, col2 = st.columns(2)
    with col1:
        patient_choice = st.selectbox(
            "Select Patient",
            [None] + patients,
            format_func=lambda x: "-- Select Patient --" if x is None else f"{x[0]} — {x[1]}",
            key=f"patient_select_{counter}"
        )
    with col2:
        drug_choice = st.selectbox(
            "Select Drug",
            [None] + drugs,
            format_func=lambda x: "-- Select Drug --" if x is None else f"{x[0]} — {x[1]}",
            key=f"drug_select_{counter}"
        )

    col3, col4 = st.columns(2)
    with col3:
        st.date_input("Start Date", value=date.today(), disabled=True)
    with col4:
        end_date = st.date_input("End Date", value=None, min_value=date.today(), key=f"end_date_{counter}")

    st.text_input("Prescription ID (Auto-generated)", value=auto_id, disabled=True)

    is_conflict = False
    conflict_message = ""
    conflicting_drugs = []

    if patient_choice is not None and drug_choice is not None:

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
            end_str = exact_duplicate[2] if exact_duplicate[2] else "No end date set"
            conflict_message = (
                f"**{exact_duplicate[0]}** is already actively prescribed. "
                f"Started: **{exact_duplicate[1]}** | Ends: **{end_str}**"
            )

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
                    SELECT d.drug_name, d.severity
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
                conflict_details = ""
                for drug_name, severity in conflicting_drugs:
                    if severity == "High":
                        badge_color = "#e74c3c"
                    elif severity == "Medium":
                        badge_color = "#e67e22"
                    elif severity == "Low":
                        badge_color = "#f1c40f"
                    else:
                        badge_color = "#95a5a6"
                    severity_label = severity if severity else "N/A"
                    conflict_details += f"""
                    <span style="display:inline-block;margin:4px 0;">
                        <strong>{drug_name}</strong>
                        <span style="background:{badge_color};color:white;padding:2px 8px;
                        border-radius:12px;font-size:0.8em;margin-left:6px;">
                            {severity_label}
                        </span>
                    </span><br>
                    """
                conflict_message = f"Patient is already actively taking conflicting drug(s):<br>{conflict_details}"

        if is_conflict:
            st.markdown(f"""
            <div style="background:#4a1010;border-left:5px solid #e74c3c;padding:14px 18px;border-radius:8px;margin:12px 0;">
                <strong style="color:#e74c3c;">Prescription Blocked</strong><br><br>
                <span style="color:#f5b7b1;">{conflict_message}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#0d3b1e;border-left:5px solid #2ecc71;padding:14px 18px;border-radius:8px;margin:12px 0;">
                <strong style="color:#2ecc71;">No Conflicts Detected</strong><br>
                <span style="color:#a9dfbf;">This prescription is safe to issue.</span>
            </div>
            """, unsafe_allow_html=True)

    if patient_choice is not None:
        st.markdown("---")
        st.markdown(f"### Current Medications for {patient_choice[1]}")

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
                    "Start Date": r[2],
                    "End Date": r[3] if r[3] else "Ongoing",
                    "Prescribed By": r[4],
                    "Active": "Yes" if (r[3] is None or r[3] >= date.today()) else "No"
                } for r in history],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No prescriptions found for this patient.")

        st.markdown("---")
        btn_col, _ = st.columns([1, 3])
        with btn_col:
            confirm = st.button(
                "Confirm Prescription",
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
                    st.session_state["success_message"] = f"Prescription {auto_id} issued successfully until {end_date}!"
                    st.session_state["reset_counter"] += 1
                    st.rerun()
                except Exception as e:
                    conn.rollback()
                    st.error(f"Database Error: {e}")
                finally:
                    conn.close()


def patient_feedback_page():
    st.title("MediPal — Patient Feedback")
    st.markdown("---")

    conn = get_db_connection()

    cur1 = conn.cursor()
    cur1.execute("SELECT patient_id, name FROM Patient")
    patients = cur1.fetchall()
    cur1.close()

    st.markdown("### Select Patient")
    patient_choice = st.selectbox(
        "Patient:",
        [None] + patients,
        format_func=lambda x: "-- Select Patient --" if x is None else f"{x[0]} — {x[1]}",
        key="feedback_patient"
    )

    if patient_choice is not None:

        cur2 = conn.cursor()
        cur2.execute("""
            SELECT p.prescription_id, d.drug_name, p.start_date, p.end_date,
                   f.feedback_no, f.comments
            FROM Prescription p
            JOIN Has h ON p.prescription_id = h.prescription_id
            JOIN Drugs d ON h.drug_id = d.drug_id
            LEFT JOIN Feedback f ON p.prescription_id = f.prescription_id
            WHERE p.patient_id = %s
            ORDER BY p.start_date DESC
        """, (patient_choice[0],))
        prescriptions = cur2.fetchall()
        cur2.close()

        if not prescriptions:
            st.info("No prescriptions found for this patient.")
            conn.close()
            return

        st.markdown("---")
        st.markdown(f"### All Prescriptions and Feedback for {patient_choice[1]}")
        st.dataframe(
            data=[{
                "Prescription ID": r[0],
                "Drug": r[1],
                "Start Date": r[2],
                "End Date": r[3] if r[3] else "Ongoing",
                "Feedback No": r[4] if r[4] else "None",
                "Comments": r[5] if r[5] else "No feedback yet"
            } for r in prescriptions],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        st.markdown("### Add / Edit / Delete Feedback")

        prescription_choice = st.selectbox(
            "Select Prescription:",
            [None] + prescriptions,
            format_func=lambda x: "-- Select Prescription --" if x is None else (
                f"{x[0]} — {x[1]} "
                f"(Started: {x[2]}, Ends: {x[3] if x[3] else 'Ongoing'})"
            ),
            key="feedback_prescription"
        )

        if prescription_choice is not None:
            presc_id = prescription_choice[0]
            existing_feedback_no = prescription_choice[4]
            existing_comment = prescription_choice[5] if prescription_choice[5] else ""

            if existing_comment:
                st.markdown("""
                <div style="background:#1a2f4a;border-left:5px solid #3498db;padding:10px 16px;border-radius:8px;margin:8px 0;">
                    <strong style="color:#3498db;">Existing Feedback</strong><br>
                    <span style="color:#aed6f1;">This prescription already has feedback. You can edit or delete it below.</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background:#1e3a1e;border-left:5px solid #2ecc71;padding:10px 16px;border-radius:8px;margin:8px 0;">
                    <strong style="color:#2ecc71;">No Feedback Yet</strong><br>
                    <span style="color:#a9dfbf;">Add your feedback for this prescription below.</span>
                </div>
                """, unsafe_allow_html=True)

            new_comment = st.text_area(
                "Your feedback / comments:",
                value=existing_comment,
                height=150,
                placeholder="Enter your feedback about this prescription here..."
            )
            st.caption(f"{len(new_comment)} characters")

            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                save = st.button("Save Feedback", type="primary", use_container_width=True)
            with col2:
                delete = st.button(
                    "Delete Feedback",
                    use_container_width=True,
                    disabled=not existing_comment
                )

            if save:
                if not new_comment.strip():
                    st.error("Please enter some feedback before saving.")
                else:
                    try:
                        cur3 = conn.cursor()
                        if existing_feedback_no:
                            cur3.execute(
                                "UPDATE Feedback SET comments = %s WHERE feedback_no = %s",
                                (new_comment.strip(), existing_feedback_no)
                            )
                        else:
                            cur3.execute("SELECT feedback_no FROM Feedback ORDER BY feedback_no DESC LIMIT 1")
                            last_f = cur3.fetchone()
                            if last_f:
                                last_num = int(last_f[0][1:])
                                new_f_no = f"f{str(last_num + 1).zfill(3)}"
                            else:
                                new_f_no = "f001"
                            cur3.execute(
                                "INSERT INTO Feedback (feedback_no, prescription_id, comments) VALUES (%s, %s, %s)",
                                (new_f_no, presc_id, new_comment.strip())
                            )
                        conn.commit()
                        cur3.close()
                        st.session_state["success_message"] = "Feedback saved successfully!"
                        st.rerun()
                    except Exception as e:
                        conn.rollback()
                        error_str = str(e)
                        if "FEEDBACK:" in error_str:
                            st.markdown("""
                            <div style="background:#4a1010;border-left:5px solid #e74c3c;padding:14px 18px;border-radius:8px;margin:12px 0;">
                                <strong style="color:#e74c3c;">Edit Blocked</strong><br>
                                <span style="color:#f5b7b1;">You have already edited this feedback today. Please try again tomorrow.</span>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error(f"Database Error: {e}")

            if delete:
                try:
                    cur4 = conn.cursor()
                    cur4.execute(
                        "DELETE FROM Feedback WHERE feedback_no = %s",
                        (existing_feedback_no,)
                    )
                    conn.commit()
                    cur4.close()
                    st.session_state["success_message"] = "Feedback deleted successfully!"
                    st.rerun()
                except Exception as e:
                    conn.rollback()
                    st.error(f"Database Error: {e}")

    conn.close()


def add_patient_page():
    st.title("MediPal — Add New Patient")
    st.markdown("---")

    conn = get_db_connection()

    st.markdown("### Patient Details")

    cur1 = conn.cursor()
    cur1.execute("SELECT patient_id FROM Patient ORDER BY patient_id DESC LIMIT 1")
    last_id = cur1.fetchone()
    cur1.close()
    if last_id:
        last_num = int(last_id[0][3:])
        new_patient_id = f"pat{str(last_num + 1).zfill(3)}"
    else:
        new_patient_id = "pat001"

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
            format_func=lambda x: "-- Select Gender --" if x is None else ("Male" if x == "M" else "Female")
        )
    with col4:
        blood_group = st.selectbox(
            "Blood Group",
            [None, "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "AB"],
            format_func=lambda x: "-- Select Blood Group --" if x is None else x
        )

    weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, step=0.1, format="%.2f")

    st.markdown("---")
    btn_col, _ = st.columns([1, 3])
    with btn_col:
        submit = st.button("Add Patient", type="primary", use_container_width=True)

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
                st.session_state["success_message"] = f"Patient {name.strip()} added successfully with ID {new_patient_id}!"
                st.rerun()
            except Exception as e:
                conn.rollback()
                st.error(f"Database Error: {e}")
            finally:
                conn.close()

    conn.close()


def add_doctor_page():
    st.title("MediPal — Add New Doctor")
    st.markdown("---")

    conn = get_db_connection()

    st.markdown("### Doctor Details")

    cur1 = conn.cursor()
    cur1.execute("SELECT doctor_id FROM Doctor ORDER BY doctor_id DESC LIMIT 1")
    last_id = cur1.fetchone()
    cur1.close()
    if last_id:
        last_num = int(last_id[0][3:])
        new_doctor_id = f"doc{str(last_num + 1).zfill(3)}"
    else:
        new_doctor_id = "doc001"

    st.text_input("Doctor ID (Auto-generated)", value=new_doctor_id, disabled=True)

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name")
    with col2:
        age = st.number_input("Age", min_value=20, max_value=100, step=1)

    specialisation = st.selectbox("Specialisation", [
        None,
        "Cardiologist",
        "Neurologist",
        "Dermatologist",
        "Pediatrician",
        "Oncologist",
        "Gastroenterologist",
        "Endocrinologist",
        "Orthopedic",
        "Psychiatrist",
        "General Physician"
    ], format_func=lambda x: "-- Select Specialisation --" if x is None else x)

    st.markdown("#### Phone Numbers")
    phone1 = st.text_input("Phone Number 1", max_chars=10)
    phone2 = st.text_input("Phone Number 2 (optional)", max_chars=10)

    st.markdown("---")
    btn_col, _ = st.columns([1, 3])
    with btn_col:
        submit = st.button("Add Doctor", type="primary", use_container_width=True)

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
                st.session_state["success_message"] = f"Doctor {name.strip()} added successfully with ID {new_doctor_id}!"
                st.rerun()
            except Exception as e:
                conn.rollback()
                st.error(f"Database Error: {e}")
            finally:
                conn.close()

    conn.close()


def main():
    st.set_page_config(
        page_title="MediPal",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    if "success_message" not in st.session_state:
        st.session_state["success_message"] = ""
    if st.session_state["success_message"]:
        st.sidebar.success(st.session_state["success_message"])
        st.session_state["success_message"] = ""

    st.markdown("""
    <style>
        [data-testid="stSidebar"] { background-color: #0f1117; border-right: 1px solid #2a2a3a; }
        .stApp { background-color: #0d1117; color: #e6edf3; }
        h1 { color: #58a6ff !important; font-size: 2rem !important; font-weight: 700 !important; }
        h2, h3 { color: #cdd9e5 !important; font-weight: 600 !important; }
        [data-testid="stTextInput"] input, [data-testid="stDateInput"] input {
            background-color: #161b22 !important; border: 1px solid #30363d !important;
            border-radius: 8px !important; color: #e6edf3 !important; }
        [data-testid="stSelectbox"] > div > div {
            background-color: #161b22 !important; border: 1px solid #30363d !important;
            border-radius: 8px !important; color: #e6edf3 !important; }
        .stButton > button[kind="primary"] {
            background-color: #238636 !important; border: 1px solid #2ea043 !important;
            border-radius: 8px !important; color: white !important; font-weight: 600 !important; }
        .stButton > button[kind="primary"]:hover { background-color: #2ea043 !important; }
        .stButton > button[kind="secondary"] {
            background-color: #21262d !important; border: 1px solid #30363d !important;
            border-radius: 8px !important; color: #e6edf3 !important; }
        .stButton > button:disabled {
            background-color: #21262d !important; border-color: #30363d !important;
            color: #484f58 !important; }
        [data-testid="stDataFrame"] { border: 1px solid #30363d !important; border-radius: 10px !important; }
        hr { border-color: #21262d !important; }
        textarea { background-color: #161b22 !important; border: 1px solid #30363d !important;
            border-radius: 8px !important; color: #e6edf3 !important; }
        [data-testid="stCaptionContainer"] { color: #8b949e !important; }
        .block-container { padding-top: 2rem !important; max-width: 1100px; }
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("MediPal")
    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "Navigation",
        ["Doctor Portal", "Patient Feedback", "Add New Patient", "Add New Doctor"],
        label_visibility="collapsed",
        key="main_navigation"
    )

    if page == "Doctor Portal":
        doctors_page()
    elif page == "Patient Feedback":
        patient_feedback_page()
    elif page == "Add New Patient":
        add_patient_page()
    elif page == "Add New Doctor":
        add_doctor_page()


if __name__ == "__main__":
    main()