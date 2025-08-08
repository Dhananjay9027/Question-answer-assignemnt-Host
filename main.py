from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from certificate_utils import send_certificate_email
from dotenv import load_dotenv
import os
app = FastAPI()
load_dotenv()
# CORS (allow Unity app to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MySQL config (change these)
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", 3306))
}

# Pydantic models
class Registration(BaseModel):
    name: str
    class_name: str
    mobile: str
    email: str

class AnswerSubmission(BaseModel):
    student_id: int
    question_id: int
    selected_option: str
    is_correct: bool

class ScoreSubmission(BaseModel):
    student_id: int
    score: int

class Question(BaseModel):
    id: int
    category: str
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str

# Routes
@app.post("/login-or-register")
def login_or_register(data: Registration):
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)

        # Check for existing user
        query = """
        SELECT id FROM students
        WHERE name = %s AND class = %s AND mobile = %s AND email = %s
        """
        cursor.execute(query, (data.name, data.class_name, data.mobile, data.email))
        result = cursor.fetchone()

        if result:
            student_id = result['id']
            message = "login"
        else:
            # Register new student
            insert_query = """
            INSERT INTO students (name, class, mobile, email)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (data.name, data.class_name, data.mobile, data.email))
            db.commit()
            student_id = cursor.lastrowid
            message = "register"

        cursor.close()
        db.close()
        return {"status": "success", "student_id": student_id, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/questions", response_model=List[Question])
def get_questions():
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM questions ORDER BY RAND() LIMIT 50")
        questions = cursor.fetchall()
        cursor.close()
        db.close()
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



from datetime import datetime

@app.post("/submit-score")
def submit_score(data: ScoreSubmission):
    try:
        print(f"▶Received score submission: student_id={data.student_id}, score={data.score}")

        # Connect to database
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()

        # Fetch student info
        cursor.execute("SELECT name, email FROM students WHERE id = %s", (data.student_id,))
        result = cursor.fetchone()

        if not result:
            print("Student not found.")
            raise HTTPException(status_code=404, detail="Student not found")

        name, email = result
        print(f"Student found: {name}, {email}")

        # Update score and time_of_play
        now = datetime.now()
        update_query = "UPDATE students SET score = %s, time_of_play = %s WHERE id = %s"
        cursor.execute(update_query, (data.score, now, data.student_id))
        db.commit()
        print(" Score and time updated in database.")

        cursor.close()
        db.close()

        # Try sending the certificate
        try:
            print(" Sending certificate...")
            send_certificate_email(email, name)
            print("Certificate sent successfully.")
        except Exception as cert_err:
            print(f" Failed to send certificate: {cert_err}")

        return {"status": "Score saved and certificate processed"}

    except Exception as e:
        print(f" ERROR during score submission: {e}")
        raise HTTPException(status_code=500, detail=str(e))


