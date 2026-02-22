# Smart Production Scheduler

A web-based production scheduling tool developed using Constraint Programming.

This project models a **Parallel Machine Scheduling problem (P||Cmax)** and solves it using Google OR-Tools.

---

## Overview

The system assigns jobs to machines while:

- Preventing overlap on the same machine
- Respecting machine-job compatibility constraints
- Minimizing total makespan (maximum completion time)

The application provides both:

- A CLI-based version (`main.py`)
- A web-based interface built with Streamlit (`app.py`)

---

## Features

- Dynamic number of machines and jobs
- Machine compatibility constraints
- Real-time input validation
- Makespan minimization
- Schedule table output
- Gantt chart visualization

---

## Optimization Model

**Problem Type:** Parallel Machine Scheduling (P||Cmax)

**Decision Variables:**
- Start time of each job
- Machine assignment of each job

**Constraints:**
- Each job assigned to one allowed machine
- No overlapping jobs on the same machine
- End time = Start time + Duration

**Objective:**
- Minimize makespan

---

## How to Run

### Install dependencies
pip install -r requirements.txt

Run Web App
streamlit run app.py

Run CLI Version
python main.py

Planned Future Improvements:
- Due date and tardiness minimization
- Multi-objective optimization
- Setup times
- CSV data import
- Export functionality

Author
Melisa Subasi
