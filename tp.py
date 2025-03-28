import streamlit as st
import json
import os

quiz_file = "quiz_data.json"
data_file = "quizee_data.json"

# Load and Save Functions
def load_quiz_data():
    if not os.path.exists(quiz_file):
        return {"questions": []}
    with open(quiz_file, "r") as file:
        return json.load(file)

def save_quiz_data(data):
    with open(quiz_file, "w") as file:
        json.dump(data, file, indent=4)

def load_user_data():
    if not os.path.exists(data_file):
        return {"leaderboard": {}, "users": {}}
    with open(data_file, "r") as file:
        return json.load(file)

def save_user_data(data):
    with open(data_file, "w") as file:
        json.dump(data, file, indent=4)

# Login System
def login():
    st.title("Quiz Login")
    user_data = load_user_data()

    username = st.text_input("Enter Username")
    password = st.text_input("Enter Password", type="password")
    admin_code = st.text_input("Enter Admin Code (Optional)", type="password")

    if st.button("Login"):
        if username and password:
            if username not in user_data["users"]:
                user_data["users"][username] = password  # Register new user
                save_user_data(user_data)

            if user_data["users"].get(username) == password:
                st.session_state["admin"] = (admin_code == "ECELL IS GREAT")
                st.session_state["user"] = username
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("Invalid password.")
        else:
            st.error("Username and password are required.")

# Quiz Interface
def quiz():
    quiz_data = load_quiz_data()
    user_data = load_user_data()
    st.title("Class Quiz")

    username = st.session_state["user"]
    
    if username not in user_data["leaderboard"]:
        user_data["leaderboard"][username] = 0
    
    score = 0
    for q in quiz_data["questions"]:
        answer = st.radio(q["question"], q["options"], key=q["question"])
        if st.button("Submit Answer", key=f"submit_{q['question']}"):
            if answer == q["answer"]:
                score += 1
                st.success("Correct!")
            else:
                st.error("Wrong answer!")

    if st.button("Finish Quiz"):
        user_data["leaderboard"][username] += score
        save_user_data(user_data)
        st.success(f"Your score: {score}")
        st.rerun()

# Admin Panel for Managing Questions and Scores
def admin_panel():
    user_data = load_user_data()
    quiz_data = load_quiz_data()
    
    st.title("Admin Panel")

    # Manage Questions
    st.subheader("Manage Questions")
    question = st.text_input("Enter Question")
    options = st.text_area("Enter Options (comma-separated)").split(",")
    answer = st.text_input("Enter Correct Answer")
    
    if st.button("Add Question"):
        if question and options and answer:
            quiz_data["questions"].append({"question": question, "options": options, "answer": answer})
            save_quiz_data(quiz_data)
            st.success("Question added!")
            st.rerun()

    st.subheader("Existing Questions")
    for idx, q in enumerate(quiz_data["questions"]):
        st.write(f"{idx+1}. {q['question']}")
        if st.button(f"Remove {idx+1}", key=f"remove_{idx}"):
            del quiz_data["questions"][idx]
            save_quiz_data(quiz_data)
            st.rerun()

    # Manage Leaderboard & Scores
    st.subheader("Leaderboard & Score Management")
    for user, score in user_data["leaderboard"].items():
        new_score = st.number_input(f"{user}: {score} points", min_value=0, value=score, key=f"score_{user}")
        if st.button(f"Update {user} Score", key=f"update_{user}"):
            user_data["leaderboard"][user] = new_score
            save_user_data(user_data)
            st.success(f"Updated {user}'s score to {new_score}")
            st.rerun()

# Main App Logic
def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["user"] = None
        st.session_state["admin"] = False
        login()
    else:
        if st.session_state["admin"]:
            admin_panel()
        else:
            quiz()

if __name__ == "__main__":
    main()
