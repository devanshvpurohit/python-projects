import streamlit as st
import json

def run():
    st.set_page_config(
        page_title="Streamlit Quiz App",
        page_icon="❓",
    )

if __name__ == "__main__":
    run()

# Custom CSS for green and white UI
st.markdown("""
<style>
    body {
        background-color: #e8f5e9;
        color: #1b5e20;
    }
    .stButton > button {
        background-color: #4caf50 !important;
        color: white !important;
        border-radius: 8px;
        padding: 10px;
        font-size: 16px;
    }
    .stProgress > div > div > div {
        background-color: #4caf50 !important;
    }
    .stMetric {
        color: #1b5e20 !important;
    }
    .stTextInput > div > input {
        border: 2px solid #4caf50 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'leaderboard' not in st.session_state:
    st.session_state.leaderboard = []
if 'rerun' not in st.session_state:
    st.session_state.rerun = False

def login():
    users = {"admin": {"password": "ECELL BEST IN IARE", "role": "admin"}}  # Admin password updated
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username]['password'] == password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.role = users[username]['role']
            st.session_state.rerun = True
        elif username == password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.role = "user"
            st.session_state.rerun = True
        else:
            st.error("Invalid username or password")

def logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.rerun = True

if st.session_state.rerun:
    st.session_state.rerun = False
    st.experimental_rerun()

if not st.session_state.authenticated:
    st.title("Login to the Quiz App")
    login()
else:
    # Load quiz data
    with open('content/quiz_data.json', 'r', encoding='utf-8') as f:
        quiz_data = json.load(f)

    default_values = {'current_index': 0, 'score': 0, 'selected_option': None, 'answer_submitted': False}
    for key, value in default_values.items():
        st.session_state.setdefault(key, value)
    
    def restart_quiz():
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.selected_option = None
        st.session_state.answer_submitted = False

    def submit_answer():
        if st.session_state.selected_option is not None:
            st.session_state.answer_submitted = True
            if st.session_state.selected_option == quiz_data[st.session_state.current_index]['answer']:
                st.session_state.score += 10
        else:
            st.warning("Please select an option before submitting.")
    
    def next_question():
        st.session_state.current_index += 1
        st.session_state.selected_option = None
        st.session_state.answer_submitted = False
    
    def update_leaderboard():
        st.session_state.leaderboard.append({"username": st.session_state.username, "score": st.session_state.score})
        st.session_state.leaderboard = sorted(st.session_state.leaderboard, key=lambda x: x['score'], reverse=True)
    
    def add_question():
        question = st.text_input("Enter the question:")
        options = [st.text_input(f"Option {i+1}") for i in range(4)]
        answer = st.selectbox("Select the correct answer:", options)
        if st.button("Add Question"):
            new_question = {"question": question, "options": options, "answer": answer, "information": ""}
            quiz_data.append(new_question)
            with open('content/quiz_data.json', 'w', encoding='utf-8') as f:
                json.dump(quiz_data, f, indent=4)
            st.success("Question added successfully!")
    
    def remove_question():
        question_to_remove = st.selectbox("Select a question to remove:", [q['question'] for q in quiz_data])
        if st.button("Remove Question"):
            quiz_data[:] = [q for q in quiz_data if q['question'] != question_to_remove]
            with open('content/quiz_data.json', 'w', encoding='utf-8') as f:
                json.dump(quiz_data, f, indent=4)
            st.success("Question removed successfully!")
    
    # Logout Button
    st.sidebar.button("Logout", on_click=logout)
    
    if st.session_state.role == "admin":
        st.sidebar.subheader("Admin Panel")
        add_question()
        remove_question()
        st.sidebar.subheader("Leaderboard")
        for entry in st.session_state.leaderboard:
            st.sidebar.write(f"{entry['username']}: {entry['score']}")
    else:
        st.title(f"Welcome {st.session_state.username} to the Quiz App!")
        progress_bar_value = (st.session_state.current_index + 1) / len(quiz_data)
        st.metric(label="Score", value=f"{st.session_state.score} / {len(quiz_data) * 10}")
        st.progress(progress_bar_value)
        
        question_item = quiz_data[st.session_state.current_index]
        st.subheader(f"Question {st.session_state.current_index + 1}")
        st.title(f"{question_item['question']}")
        st.write(question_item['information'])
        
        st.markdown(""" ___""")
        
        options = question_item['options']
        correct_answer = question_item['answer']
        
        if st.session_state.answer_submitted:
            for option in options:
                if option == correct_answer:
                    st.success(f"{option} (Correct answer)")
                elif option == st.session_state.selected_option:
                    st.error(f"{option} (Incorrect answer)")
                else:
                    st.write(option)
        else:
            for i, option in enumerate(options):
                if st.button(option, key=i, use_container_width=True):
                    st.session_state.selected_option = option
        
        st.markdown(""" ___""")
        
        if st.session_state.answer_submitted:
            if st.session_state.current_index < len(quiz_data) - 1:
                st.button('Next', on_click=next_question)
            else:
                update_leaderboard()
                st.write(f"Quiz completed! Your score is: {st.session_state.score} / {len(quiz_data) * 10}")
                if st.button('Restart', on_click=restart_quiz):
                    pass
        else:
            if st.session_state.current_index < len(quiz_data):
                st.button('Submit', on_click=submit_answer)
