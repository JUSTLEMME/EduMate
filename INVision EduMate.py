import google.generativeai as genai
import customtkinter as ctk
import json
import time

# --------------------------
# 🖥️ Setup main window
# --------------------------
app = ctk.CTk()
app.title("Lesson")
app.geometry("1000x600")

# --------------------------
# 🤖 Setup Google Gemini AI
# --------------------------
genai.configure(api_key="AIzaSyAV1RGXaRvKIEHtPNsunonHATULHjJW414")  # Gemini API Key
model = genai.GenerativeModel("gemini-2.0-flash-lite")

# --------------------------
# ✨ Function: Ask AI for response
# --------------------------
def ai_response(summary):
    response = model.generate_content(summary)
    return response.text

# --------------------------
# 🚀 Function: When "Teach Me!" button is clicked
# --------------------------
def submit_input():
    # Get values entered by the user
    name = name_input.get()
    grade = grade_input.get()
    subject = subject_input.get()
    topic = topic_input.get()

    # Ask AI if the topic belongs to the subject
    subject_topic = ai_response(f"Is the topic {topic} in the subject {subject}? Only answer 'True' or 'False'.")
    print(subject_topic)

    # ✅ Check if input is valid
    if (
        name != "" and grade != "" and subject != "" and topic != ""  # Nothing is empty
        and grade.isdigit()                                           # Grade is a number
        and "true" in subject_topic.lower()):                         # AI confirmed topic belongs to subject
        grade = int(grade)
        if 0 < grade < 13:  # Valid school grade
            print("Data Stored")

            # Close first window
            app.destroy()

            # --------------------------
            # 📖 Lesson Page
            # --------------------------
            gui = ctk.CTk()
            gui.title("EduMate")
            gui.geometry("1000x600")

            header_gui = ctk.CTkLabel(gui, text="EduMate", font=("TT Espina", 40, "bold"))
            header_gui.pack(pady=(10, 10), side="top")

            # Two sections: left for lesson, right for chat
            frame_left = ctk.CTkFrame(gui, width=600, height=550)
            frame_left.pack(side="left", padx=10, pady=10)
            frame_left.pack_propagate(False)

            frame_right = ctk.CTkFrame(gui, width=400, height=550)
            frame_right.pack(side="right", padx=10, pady=10)
            frame_right.pack_propagate(False)

            # --------------------------
            # 📝 Get AI Lesson
            # --------------------------
            prompt = (
                f"Teach a student on {topic} in the subject {subject}. "
                f"Limit the answer to 300 words and make it fun, easy, and understandable for Grade {grade} student {name}."
            )
            ai = ai_response(prompt)

            # Show AI lesson on left side
            response_box = ctk.CTkTextbox(frame_left, wrap="word")
            response_box.pack(side="top", fill="both", expand=True, padx=20, pady=20)
            response_box.insert("1.0", ai)
            response_box.configure(state="disabled")

            # --------------------------
            # 🎯 Quiz Mode
            # --------------------------
            quiz_finished = False

            def quiz_mode():
                nonlocal quiz_finished
                gui.destroy()
                quiz = ctk.CTk()
                quiz.title("Quiz Mode")
                quiz.geometry("1000x600")

                header_quiz = ctk.CTkLabel(quiz, text="EduMate", font=("TT Espina", 40, "bold"))
                header_quiz.pack(pady=(10, 10), side="top")

                # Ask user how many questions
                questions_input_label = ctk.CTkLabel(quiz, text="How many questions should your quiz have?", font=("Segoe UI", 18))
                questions_input_label.pack(padx=10, pady=10)
                questions_input = ctk.CTkEntry(quiz, placeholder_text="Enter a number and press Enter")
                questions_input.pack(padx=10, pady=10)

                # Variables to store quiz data
                questions = []
                index = 0
                answer = ""
                score = 0
                total = 0

                # UI elements for quiz
                q_label = ctk.CTkLabel(quiz, text="")
                a_button = ctk.CTkButton(quiz, text="")
                b_button = ctk.CTkButton(quiz, text="")
                c_button = ctk.CTkButton(quiz, text="")
                d_button = ctk.CTkButton(quiz, text="")

                # Show each question
                quiz_question = ""
                def show_question(i):
                    nonlocal answer, quiz_question
                    q = questions[i]
                    quiz_question = q["question"]
                    q_label.configure(text=quiz_question, font=("Segoe UI", 18))
                    answer = q["answer"]
                    a_button.configure(text=q["options"][0], font=("Segoe UI", 18), state="normal", command=lambda: on_click(q["options"][0]))
                    b_button.configure(text=q["options"][1], font=("Segoe UI", 18), state="normal", command=lambda: on_click(q["options"][1]))
                    c_button.configure(text=q["options"][2], font=("Segoe UI", 18), state="normal", command=lambda: on_click(q["options"][2]))
                    d_button.configure(text=q["options"][3], font=("Segoe UI", 18), state="normal", command=lambda: on_click(q["options"][3]))

                # Handle answer clicks
                questions_wrong = {
                    "question":[],
                    "user_ans":[],
                    "correct_ans":[],
                }
                def on_click(chosen):
                    nonlocal answer, score, questions_wrong
                    if chosen == answer:
                        score += 1
                    else:
                        questions_wrong["question"].append(quiz_question)
                        questions_wrong["user_ans"].append(chosen)
                        questions_wrong["correct_ans"].append(answer)

                    quiz.after(500, next_question)

                # Go to next question
                def next_question():
                    nonlocal index, score, questions_wrong, quiz_finished

                    if quiz_finished:
                        return

                    a_button.configure(state="disabled")
                    b_button.configure(state="disabled")
                    c_button.configure(state="disabled")
                    d_button.configure(state="disabled")

                    if index < len(questions) - 1:
                        index += 1
                        show_question(index)
                    else:
                        # End of quiz – show summary
                        quiz_finished = True
                        q_label.pack_forget()
                        a_button.pack_forget()
                        b_button.pack_forget()
                        c_button.pack_forget()
                        d_button.pack_forget()
                        summary_label = ctk.CTkLabel(quiz, text="Quiz Summary", font=("Segoe UI", 25, "bold"))
                        summary_label.pack(padx=10, pady=20)
                        
                        feedback = ai_response(f"Give 15 words personalised feedback for someone who got {score}/{total} in {topic}, {subject}")
                        result_label = ctk.CTkLabel(quiz, text=feedback, font=("Segoe UI", 18))
                        result_label.pack(padx=10, pady=10)

                        score_label = ctk.CTkLabel(quiz, text=f"Score: {score}/{total}", font=("Arial", 20))
                        score_label.pack(padx=10, pady=10)

                        q_wrong_label = ctk.CTkLabel(quiz, text=f"You got {total-score} questions wrong ☹️", font=("Segoe UI", 18))
                        q_wrong_label.pack(padx=10, pady=10)

                        question_wrong_label = ctk.CTkLabel(quiz, text="", font=("Segoe UI", 18))
                        question_wrong_label.pack(padx=10, pady=10)
                        user_ans_label = ctk.CTkLabel(quiz, text="", font=("Segoe UI", 18))
                        user_ans_label.pack(padx=10, pady=10)
                        correct_ans_label = ctk.CTkLabel(quiz, text="", font=("Segoe UI", 18))
                        correct_ans_label.pack(padx=10, pady=10)
                        i = 0  # Start at first wrong question

                        def cycle_wrong_questions():
                            nonlocal i
                            if questions_wrong["question"]:  # Only if there are wrong answers
                                question_wrong_label.configure(text=f"Question: {questions_wrong['question'][i]}")
                                user_ans_label.configure(text=f"You answered: {questions_wrong['user_ans'][i]}")
                                correct_ans_label.configure(text=f"Correct answer: {questions_wrong['correct_ans'][i]}")

                                # Move to next index (wrap around using modulo)
                                i = (i + 1) % len(questions_wrong["question"])

                                # Call this function again after 2000ms (2 seconds)
                                quiz.after(3000, cycle_wrong_questions)

                        cycle_wrong_questions()  # Start the cycle

                        print(f"Score: {score}")

                # Generate quiz from AI
                def generate_quiz(event=None):
                    nonlocal questions, total, index
                    try:
                        num_questions = int(questions_input.get().strip())
                    except ValueError:
                        return

                    questions_input_label.pack_forget()
                    questions_input.pack_forget()

                    response = model.generate_content(
                        f"Generate a MCQ quiz on {topic} in subject {subject} of {num_questions} questions in valid JSON format only. "
                        "No markdown, no extra text. The JSON should have structure: "
                        "{\"quizTitle\": \"...\", \"questions\": [{\"question\": \"...\", \"options\": [\"...\"], \"answer\": \"...\"}]}"
                    )

                    # Fix raw response if it has ```json``` wrapping
                    raw_text = response.text.strip()
                    if raw_text.startswith("```"):
                        raw_text = raw_text.strip("`")
                        if raw_text.lower().startswith("json"):
                            raw_text = raw_text[4:].strip()

                    quiz_data = json.loads(raw_text)
                    questions = quiz_data["questions"]
                    total = len(questions)
                    index = 0

                    q_label.pack(pady=20)
                    a_button.pack(pady=10)
                    b_button.pack(pady=10)
                    c_button.pack(pady=10)
                    d_button.pack(pady=10)

                    show_question(index)

                questions_input.bind("<Return>", generate_quiz)
                quiz.mainloop()

            # Button for quiz mode
            quiz_button = ctk.CTkButton(frame_left, text="Quiz Mode", font=("Segoe UI", 18), command=quiz_mode)
            quiz_button.pack(side="bottom", padx=10, pady=10)

            # --------------------------
            # 💬 Chat Section (Right side)
            # --------------------------
            chat_box = ctk.CTkTextbox(frame_right, wrap="word", font=("Segoe UI", 14))
            chat_box.pack(side="top", fill="both", expand=True, padx=20, pady=20)

            input_frame = ctk.CTkFrame(frame_right)
            input_frame.pack(side="bottom", padx=10, pady=10)

            user_input = ctk.CTkEntry(input_frame, height=25
            , width=500, placeholder_text=f"Ask Anything about {topic}")
            user_input.pack(side="left", padx=10, pady=10)

            # Send messages to AI
            def send_message(event=None):
                q = user_input.get()
                if not q:
                    return
                chat_box.insert("end", f"{name.capitalize()}: {q}\n")
                ans = ai_response(q)
                chat_box.insert("end", f"EduMate: {ans}\n\n")
                chat_box.see("end")
                user_input.delete(0, "end")

            user_input.bind("<Return>", send_message)

            gui.mainloop()
        else:
            print("Grade must be between 1 and 12")
    else:
        print("Invalid input")

# --------------------------
# 🖊️ Input Form UI (First Page)
# --------------------------
header_app = ctk.CTkLabel(app, text="EduMate", font=("TT Espina", 40, "bold"))
header_app.pack(pady=(10, 10), side="top")

label = ctk.CTkLabel(app, text="Which topic do you want a lesson on?", font=("Segoe UI", 18))
label.pack(padx=10, pady=10)

name_label = ctk.CTkLabel(app, text="Name", font=("Segoe UI", 18))
name_label.pack()
name_input = ctk.CTkEntry(app)
name_input.pack(pady=10)

grade_label = ctk.CTkLabel(app, text="Grade", font=("Segoe UI", 18))
grade_label.pack()
grade_input = ctk.CTkEntry(app)
grade_input.pack(pady=10)

subject_label = ctk.CTkLabel(app, text="Subject", font=("Segoe UI", 18))
subject_label.pack()
subject_input = ctk.CTkEntry(app)
subject_input.pack(pady=10)

topic_label = ctk.CTkLabel(app, text="Topic", font=("Segoe UI", 18))
topic_label.pack()
topic_input = ctk.CTkEntry(app)
topic_input.pack(pady=10)

submit_button = ctk.CTkButton(app, text="Teach Me!", font=("Segoe UI", 18), command=submit_input)
submit_button.pack(pady=10)

# --------------------------
# 🔁 Start App
# --------------------------
app.mainloop()