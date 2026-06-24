import base64
import streamlit as st
import requests

# --- Configuration ---
BACKEND_BASE_URL = "http://localhost:8000"
DEPARTMENTS = ["HR", "Finance", "Development", "general"]

# --- Session State Initialization ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "role" not in st.session_state:
    st.session_state.role = None
if "department" not in st.session_state:
    st.session_state.department = None
if "page" not in st.session_state:
    st.session_state.page = "login"
if "delete_files" not in st.session_state:
    st.session_state.delete_files = []
if "delete_files_loaded" not in st.session_state:
    st.session_state.delete_files_loaded = False
if "pending_delete_file" not in st.session_state:
    st.session_state.pending_delete_file = None


def fetch_delete_files():
    try:
        response = requests.get(f"{BACKEND_BASE_URL}/delete-files")
        if response.status_code == 200:
            st.session_state.delete_files = response.json().get("files", [])
            st.session_state.delete_files_loaded = True
        else:
            st.error(f"Failed to load files: {response.text}")
            st.session_state.delete_files = []
            st.session_state.delete_files_loaded = True
    except requests.exceptions.ConnectionError:
        st.error("Failed to connect to backend on port 8000.")
        st.session_state.delete_files = []
        st.session_state.delete_files_loaded = True


def login_page():
    st.title("Login")
    with st.form("login_form"):
        email_id = st.text_input("Email ID")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

        if submit_button:
            try:
                response = requests.post(
                    f"{BACKEND_BASE_URL}/login",
                    json={"email_id": email_id, "password": password}
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.user_id = data.get("userID")
                    st.session_state.logged_in = True
                    st.session_state.role = data.get("role")
                    st.session_state.department = data.get("department")
                    st.session_state.page = "dashboard"
                    st.success("Login successful. Redirecting...")
                    st.rerun()
                else:
                    st.toast("Invalid user", icon="🚨")
            except requests.exceptions.ConnectionError:
                st.error("Failed to connect to backend on port 8000.")


def dashboard_page():
    st.title("Welcome")
    st.write(f"**User:** {st.session_state.user_id}  |  **Role:** {st.session_state.role}  |  **Department:** {st.session_state.department}")
    st.markdown("---")

    card_style = """
    <div style='border-radius:18px; padding:24px; background: linear-gradient(180deg, #f7f8ff 0%, #eef3ff 100%); box-shadow: 0 12px 30px rgba(37, 99, 235, 0.12);'>
      <h2 style='margin-bottom:8px;'>📤 Upload data</h2>
      <p style='margin-top:0;color:#334155;'>Upload a file after selecting the correct department.</p>
    </div>
    """

    delete_style = """
    <div style='border-radius:18px; padding:24px; background: linear-gradient(180deg, #fff7ed 0%, #ffefeb 100%); box-shadow: 0 12px 30px rgba(249, 115, 22, 0.12);'>
      <h2 style='margin-bottom:8px;'>🗑️ Delete data</h2>
      <p style='margin-top:0;color:#7c2d12;'>Remove previously uploaded data from the system.</p>
    </div>
    """

    left, right = st.columns(2)
    with left:
        st.markdown(card_style, unsafe_allow_html=True)
        if st.button("Proceed to Upload", key="upload_card"):
            st.session_state.page = "upload"
            st.rerun()
    with right:
        st.markdown(delete_style, unsafe_allow_html=True)
        if st.button("Proceed to Delete", key="delete_card"):
            st.session_state.delete_files_loaded = False
            st.session_state.pending_delete_file = None
            st.session_state.page = "delete"
            st.rerun()


def upload_page():
    st.title("Upload Data")
    st.write("Please choose a department, select a file, and then upload your data.")
    selected_department = st.selectbox("Department", ["Select department"] + DEPARTMENTS)
    uploaded_file = st.file_uploader("Choose a file to upload", type=["csv", "txt", "json", "pdf"])
    st.markdown("---")

    if st.button("Upload to backend"):
        if selected_department == "Select department":
            st.warning("Please select a department before uploading.")
            return
        if not uploaded_file:
            st.warning("Please upload a file before clicking upload.")
            return

        file_bytes = uploaded_file.read()
        encoded_file = base64.b64encode(file_bytes).decode("utf-8")
        payload = {
            "userId": st.session_state.user_id,
            "role": st.session_state.role,
            "department": selected_department,
            "files": {
                "filename": uploaded_file.name,
                "content": encoded_file,
            },
        }

        try:
            response = requests.post(f"{BACKEND_BASE_URL}/upload-data", json=payload)
            if response.status_code == 200:
                st.success("File uploaded successfully.")
            else:
                st.error(f"Upload failed: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Failed to connect to backend on port 8000.")

    if st.button("Back to dashboard"):
        st.session_state.pending_delete_file = None
        st.session_state.page = "dashboard"
        st.rerun()


def delete_page():
    st.title("Delete Data")
    st.write("Select a file to delete from the ingestion container.")

    if not st.session_state.delete_files_loaded:
        with st.spinner("Loading files from blob storage..."):
            fetch_delete_files()

    if st.button("Refresh files"):
        st.session_state.delete_files_loaded = False
        st.rerun()

    if not st.session_state.delete_files:
        st.info("No files found in the blob container.")
    else:
        for index, file_info in enumerate(st.session_state.delete_files):
            file_name = file_info.get("name", "unknown")
            left, right = st.columns([6, 1])
            with left:
                st.button(f"📄 {file_name}", key=f"delete_file_btn_{index}", use_container_width=True,
                          on_click=lambda name=file_name: st.session_state.update({"pending_delete_file": name}))
            with right:
                st.write("")

    if st.session_state.pending_delete_file:
        confirm_delete_dialog()

    if st.button("Back to dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()


@st.dialog("Confirm file deletion")
def confirm_delete_dialog():
    file_name = st.session_state.pending_delete_file
    st.warning(f"Are you sure you want to delete this file?\n\n**{file_name}**")
    st.write("This will delete the matching vectors first and then remove the blob file.")

    left, right = st.columns(2)
    with left:
        if st.button("OK", key="confirm_delete_ok"):
            try:
                response = requests.delete(
                    f"{BACKEND_BASE_URL}/delete-files",
                    json={"fileName": file_name}
                )
                if response.status_code == 200:
                    st.success(response.json().get("message", "File deleted successfully."))
                    st.session_state.pending_delete_file = None
                    st.session_state.delete_files_loaded = False
                    st.rerun()
                else:
                    st.error(f"Delete failed: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Failed to connect to backend on port 8000.")
    with right:
        if st.button("Cancel", key="confirm_delete_cancel"):
            st.session_state.pending_delete_file = None
            st.rerun()


def main():
    if not st.session_state.logged_in:
        login_page()
    elif st.session_state.page == "dashboard":
        dashboard_page()
    elif st.session_state.page == "upload":
        upload_page()
    elif st.session_state.page == "delete":
        delete_page()
    else:
        st.session_state.page = "dashboard"
        dashboard_page()


if __name__ == "__main__":
    main()