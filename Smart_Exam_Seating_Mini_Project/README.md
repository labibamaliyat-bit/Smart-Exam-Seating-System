# AI-Based Smart Exam Hall Seating System (Mini Project)

A small Python + Flask + SQLite mini project. It manages students and halls,
then creates a seating allocation using a subject-interleaving heuristic.

## Features
- Add/delete students (Student ID, name, subject)
- Add/delete halls (name and capacity)
- Check total seating capacity before allocation
- Generate a seating plan
- View hall-wise seating results
- Reset allocation

## Setup
1. Install Python 3.10+.
2. Open a terminal in this project folder.
3. (Recommended) create a virtual environment:
   - Windows: `python -m venv .venv` then `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `python app.py`
6. Open `http://127.0.0.1:5000` in your browser.

The SQLite database `exam_seating.db` is created automatically.

## Demo data idea
Add students with subjects such as CSE101, EEE101, MAT101, then add halls
with capacities. Click **Generate Seating Plan**.

## AI/optimization explanation
The optimizer uses a greedy heuristic with round-robin subject interleaving to
reduce consecutive same-subject seats. It is an optimization heuristic, not
machine learning. It is intentionally lightweight for a mini project.
