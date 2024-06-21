import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('dataentry-426412-c98ed9d12447.json', scope)
client = gspread.authorize(creds)

# Open the main sheet and the product sheet
data_sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1yR9v0S4fDE7IgoxC8hbiCOuVmTb12uf66w8vgLQJQAg/edit?gid=0#gid=0").worksheet("Data")
product_sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1yR9v0S4fDE7IgoxC8hbiCOuVmTb12uf66w8vgLQJQAg/edit?gid=0#gid=0").worksheet("Product")

# Helper function to convert Google Sheets datetime string to datetime.date
def convert_datetime(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date()

# Form submission
st.title("Patient Data Entry")

with st.form("patient_form"):
    date = st.date_input("Date")
    name = st.text_input("Patient Name")
    gender = st.radio("Gender", options=["male", "female"])
    phone = st.text_input("Phone Number")
    date_of_admission = st.date_input("Date of Admission")
    date_of_discharge = st.date_input("Date of Discharge")
    diagnose = st.text_input("Diagnose")
    summary = st.text_input("Summary")
    products = product_sheet.col_values(1)
    add_product = st.checkbox("Add New Product")
    if add_product:
        new_product = st.text_input("New Product")
        product = new_product
    else:
        product = st.selectbox("Product", options=products)

    submitted = st.form_submit_button("Submit")

    if submitted:
        if add_product and new_product:
            product_sheet.append_row([new_product])
        # Append current datetime as Createdon
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data_sheet.append_row([
            current_datetime,
            date.strftime('%Y-%m-%d'),
            name,
            gender,
            phone,
            date_of_admission.strftime('%Y-%m-%d'),
            date_of_discharge.strftime('%Y-%m-%d'),
            diagnose,
            summary,
            product
        ])
        st.success("Form submitted successfully!")

# Data display with pagination and filtering
st.title("Patient Data")

start_date = st.date_input("Start Date", key='start')
end_date = st.date_input("End Date", key='end')

# Pagination controls
page = st.number_input("Page", min_value=1, value=1)
limit = 10
offset = (page - 1) * limit

all_data = data_sheet.get_all_values()

# Convert start_date and end_date to datetime.date objects
start_date = start_date
end_date = end_date

# Filter data based on date range
filtered_data = [row for row in all_data[1:] if convert_datetime(row[0]) >= start_date and convert_datetime(row[0]) <= end_date]
paginated_data = filtered_data[offset:offset+limit]

# Display table
if paginated_data:
    st.table(paginated_data)
else:
    st.write("No data available for the selected date range.")

# Edit functionality
edit_row_id = st.number_input("Enter Row ID to Edit", min_value=1, step=1)

if st.button("Edit"):
    if 1 <= edit_row_id <= len(all_data):
        row_data = all_data[edit_row_id]
        with st.form("edit_form"):
            date = st.date_input("Date", value=datetime.strptime(row_data[1], '%Y-%m-%d').date())
            name = st.text_input("Patient Name", value=row_data[2])
            gender = st.radio("Gender", options=["male", "female"], index=0 if row_data[3] == "male" else 1)
            phone = st.text_input("Phone Number", value=row_data[4])
            date_of_admission = st.date_input("Date of Admission", value=datetime.strptime(row_data[5], '%Y-%m-%d').date())
            date_of_discharge = st.date_input("Date of Discharge", value=datetime.strptime(row_data[6], '%Y-%m-%d').date())
            diagnose = st.text_input("Diagnose", value=row_data[7])
            summary = st.text_input("Summary", value=row_data[8])
            product = st.selectbox("Product", options=products, index=products.index(row_data[9]))
            updated = st.form_submit_button("Update")

            if updated:
                current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data_sheet.update(f'A{edit_row_id}:J{edit_row_id}', [[
                    current_datetime,
                    date.strftime('%Y-%m-%d'),
                    name,
                    gender,
                    phone,
                    date_of_admission.strftime('%Y-%m-%d'),
                    date_of_discharge.strftime('%Y-%m-%d'),
                    diagnose,
                    summary,
                    product
                ]])
                st.success("Data updated successfully!")
    else:
        st.error("Invalid Row ID.")

# Pagination buttons
if page > 1:
    if st.button("Previous Page"):
        st.experimental_set_query_params(page=page-1)

if (page * limit) < len(filtered_data):
    if st.button("Next Page"):
        st.experimental_set_query_params(page=page+1)

