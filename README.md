📚 University of Nottingham Exam Scheduling Project

This project explores how university final exam schedules can be built more fairly and systematically using optimization techniques. Using the University of Nottingham’s real exam timetabling dataset, we analyze why students often experience stressful schedules (e.g., multiple exams in one day) and build optimization models to generate more balanced timetables.

You can look at our slides here: https://docs.google.com/presentation/d/1IiUhD3Mf-zWZHj7MJAd-qVUnMkSFlUGdaP7I0HLV4iE/edit?usp=sharing

🔍 What We Did

Preprocessed Nottingham’s dataset (800 exams, 7,896 students, 33,997 enrollments).

Built a series of optimization models that add constraints step-by-step:

Basic feasible scheduling

Coincidence constraints

Room assignments & capacity limits

Avoiding consecutive exams

Departmental & institutional rules

Ran sensitivity analysis to understand bottlenecks (temporal constraints, not room size).

🎯 Goal

Create a feasible exam timetable that:

Avoids exam conflicts

Reduces same-day and overnight consecutive exams

Respects room capacities and department requirements

Provides insight into how similar models could improve Denison’s scheduling system

📁 Repository Contents

model.ipynb – Main notebook with data processing & optimization models

Slides and proposal documents

Cleaned data files (if included)

▶️ How to Run

Clone the repo

Install dependencies (pip install -r requirements.txt)

Run model.ipynb in Jupyter Notebook
