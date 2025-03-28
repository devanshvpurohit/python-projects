import streamlit as st
import json
import os

data_file = "quizee_data.json"

def load_quiz_data():
    if not os.path.exists(data_file):
        return {"questions": [], "leaderboard": {}, "users": {}}
    with open(data_file, "r") as file:
        return json.load(file)

def save_quiz_data(data):
    with open(data_file, "w") as file:
        json.dump(data, file, indent=4)

def login():
    st.title("Quiz Login")
    data = load_quiz_data()
    username = st.text_input("Enter Username")
    password = st.text_input("Enter Password", type="password")
    admin_code = st.text_input("Enter Admin Code (Optional)", type="password")
    
    if st.button("Login"):
        if username and password:
            if username not in data["users"]:
                data["users"][username] = password  # Register new user
                save_quiz_data(data)
            
            if data["users"].get(username) == password:
                if admin_code == "ECELL IS GREAT":
                    st.session_state["admin"] = True
                else:
                    st.session_state["admin"] = False
                st.session_state["user"] = username
                st.session_state["logged_in"] = True
                st.experimental_rerun()
            else:
                st.error("Invalid password.")
        else:
            st.error("Username and password are required.")

def quiz():
    data = load_quiz_data()
    st.title("Class Quiz")
    username = st.session_state["user"]
    
    if username not in data["leaderboard"]:
        data["leaderboard"][username] = 0
    
    score = 0
    for q in data["questions"]:
        answer = st.radio(q["question"], q["options"], key=q["question"])
        if st.button("Submit Answer", key=f"submit_{q['question']}"):
            if answer == q["answer"]:
                score += 1
                st.success("Correct!")
            else:
                st.error("Wrong answer!")
    
    if st.button("Finish Quiz"):
        data["leaderboard"][username] += score
        save_quiz_data(data)
        st.success(f"Your score: {score}")
        st.rerun()

def admin_panel():
    data = load_quiz_data()
    st.title("Admin Panel")
    st.subheader("Manage Questions")
    
    question = st.text_input("Enter Question")
    options = st.text_area("Enter Options (comma-separated)").split(",")
    answer = st.text_input("Enter Correct Answer")
    
    if st.button("Add Question"):
        if question and options and answer:
            data["questions"].append({"question": question, "options": options, "answer": answer})
            save_quiz_data(data)
            st.success("Question added!")
            st.experimental_rerun()
    
    st.subheader("Existing Questions")
    for idx, q in enumerate(data["questions"]):
        st.write(f"{idx+1}. {q['question']}")
        if st.button(f"Remove {idx+1}"):
            del data["questions"][idx]
            save_quiz_data(data)
            st.experimental_rerun()
    
    st.subheader("Leaderboard")
    for user, score in data["leaderboard"].items():
        st.write(f"{user}: {score} points")

def main():
    if "logged_in" not in st.session_state:
        login()
    else:
        if st.session_state["admin"]:
            admin_panel()
        else:
            quiz()

if __name__ == "__main__":
    main()
