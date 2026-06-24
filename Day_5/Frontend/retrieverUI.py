import streamlit as st
import requests


BACKEND_BASE_URL = "http://localhost:8000"


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
if "messages" not in st.session_state:
	st.session_state.messages = []


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
					json={"email_id": email_id, "password": password},
					timeout=60,
				)
				if response.status_code == 200:
					data = response.json()
					st.session_state.user_id = data.get("userID")
					st.session_state.logged_in = True
					st.session_state.role = data.get("role")
					st.session_state.department = data.get("department")
					st.session_state.page = "chat"
					st.session_state.messages = [
						{
							"role": "assistant",
							"content": "Login successful. Ask a question to start the conversation.",
						}
					]
					st.success("Login successful. Redirecting...")
					st.rerun()
				else:
					st.toast("Invalid user", icon="🚨")
			except requests.exceptions.ConnectionError:
				st.error("Failed to connect to backend on port 8001.")


def render_message(message):
	with st.chat_message(message["role"]):
		st.markdown(message["content"])


def chat_page():
	st.title("Retriever Chat")
	st.write(
		f"**User:** {st.session_state.user_id}  |  **Role:** {st.session_state.role}  |  **Department:** {st.session_state.department}"
	)
	st.markdown("---")

	for message in st.session_state.messages:
		render_message(message)

	user_prompt = st.chat_input("Ask something from the knowledge base...")
	if user_prompt:
		st.session_state.messages.append({"role": "user", "content": user_prompt})

		try:
			response = requests.post(
				f"{BACKEND_BASE_URL}/rag-chat/",
				json={
					"userPrompt": user_prompt,
					"userId": st.session_state.user_id,
					"role": st.session_state.role,
					"department": st.session_state.department,
				},
				timeout=120,
			)
			if response.status_code == 200:
				data = response.json()
				assistant_text = data.get("answer", "No answer returned.")
				if data.get("sources"):
					sources_text = "\n\nSources: " + ", ".join(data["sources"])
					assistant_text = f"{assistant_text}{sources_text}"
				st.session_state.messages.append({"role": "assistant", "content": assistant_text})
				st.rerun()
			else:
				st.session_state.messages.append({"role": "assistant", "content": f"Request failed: {response.text}"})
				st.rerun()
		except requests.exceptions.ConnectionError:
			st.session_state.messages.append(
				{"role": "assistant", "content": "Failed to connect to backend on port 8001."}
			)
			st.rerun()

	if st.button("Logout"):
		st.session_state.logged_in = False
		st.session_state.user_id = None
		st.session_state.role = None
		st.session_state.department = None
		st.session_state.messages = []
		st.session_state.page = "login"
		st.rerun()


def main():
	if not st.session_state.logged_in:
		login_page()
	elif st.session_state.page == "chat":
		chat_page()
	else:
		st.session_state.page = "chat"
		chat_page()


if __name__ == "__main__":
	main()
