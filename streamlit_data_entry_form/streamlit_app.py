import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
st.cache_data.clear()
st.cache_resource.clear()
# Title and Description
st.title("Patient Health Record System")
st.markdown("Enter the details of the new patient below. All fields are mandatory.")
# Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1y0qSc2IEj2L4635kFbhr3MruC2U5yn0iP-tM5baA0TM"
WORKSHEET_NAME = "Patients"  # Change if needed
# Read existing patient data
try:
    existing_data = conn.read(worksheet=WORKSHEET_NAME, usecols=list(range(8)), ttl=0)
    existing_data = existing_data.dropna(how="all")
except Exception as e:
    st.warning(f"Could not read existing data: {e}")
    existing_data = pd.DataFrame(columns=[
        "PatientName", "Age", "Gender", "ContactNumber",
        "Symptoms", "DoctorAssigned", "Prescription", "VisitDate"
    ])
GENDER = ["Male", "Female", "Other"]
SYMPTOM = [
    "Fever", "Fatigue", "Loss of Appetite", "Dehydration",
    "Pain (headache, muscle ache, etc.)", "Weakness", "Weight Loss"
]
DOCTOR = [
    "Dr. Mary Edwards Walker", "Dr. John Simpson Kirkpatrick",
    "Dr. Rex Gregor", "Dr. Desmond Doss", "Dr. John Bradley",
    "Dr. Geneviève de Galard", "Dr. Charles L. Kelly", "Dr. Thomas W. Bennett"
]
with st.form(key="patient_form"):
    PatientName = st.text_input("Patient Name*")
    Age = st.slider("Age*", 0, 120, 25)
    Gender = st.selectbox("Gender*", options=GENDER)
    ContactNumber = st.text_input("Contact Number*")
    Symptoms = st.multiselect("Symptoms / Diagnosis*", options=SYMPTOM)
    DoctorAssigned = st.selectbox("Doctor Assigned*", options=DOCTOR)
    VisitDate = st.date_input("Visit Date*")
    Prescription = st.text_area("Prescription / Notes*")

    submit_button = st.form_submit_button("Submit Patient Details")

if submit_button:
    # Check mandatory fields
    if not (PatientName and Age is not None and Gender and ContactNumber and Symptoms and DoctorAssigned and VisitDate and Prescription):
        st.warning("Please fill in all mandatory fields!")
        st.stop()

    # Safe duplicate check
    if "PatientName" in existing_data.columns:
        patient_names = existing_data["PatientName"].tolist()
        patient_names = ["" if pd.isna(name) else str(name) for name in patient_names]

        if any(PatientName.lower() == name.lower() for name in patient_names):
            st.warning("A patient with this name already exists.")
            st.stop()

    # Prepare new patient data
    patient_data = pd.DataFrame([{
        "PatientName": PatientName,
        "Age": Age,
        "Gender": Gender,
        "ContactNumber": ContactNumber,
        "Symptoms": ", ".join(Symptoms),
        "DoctorAssigned": DoctorAssigned,
        "Prescription": Prescription,
        "VisitDate": VisitDate.strftime("%Y-%m-%d"),
    }])

    # Append to existing data
    updated_df = pd.concat([existing_data, patient_data], ignore_index=True)
    updated_df = updated_df.applymap(lambda x: "" if pd.isna(x) else str(x))

    # Update Google Sheet
    try:
        conn.update(worksheet=WORKSHEET_NAME, data=updated_df)
        st.success(f"Patient {PatientName} details successfully submitted!")
    except Exception as e:
        st.error(f"Could not update sheet: {e}")
# Display all patient records
st.subheader("All Patient Records")
st.dataframe(existing_data)
