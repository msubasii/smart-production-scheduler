import streamlit as st
from ortools.sat.python import cp_model
import pandas as pd
import matplotlib.pyplot as plt


# -----------------------------
# UI CONFIGURATION
# -----------------------------

st.title("Smart Production Scheduler")
st.header("Input Data")

# Basic system parameters
num_machines = st.number_input("Number of machines", min_value=1, value=3)
num_jobs = st.number_input("Number of jobs", min_value=1, value=3)

durations = []
allowed_machines = {}

st.subheader("Job Configuration")

# Collect job durations and machine compatibility
for i in range(num_jobs):
    duration = st.number_input(
        f"Duration of Job {i}",
        min_value=1,
        value=1,
        key=f"dur_{i}"
    )
    durations.append(duration)

    machines_for_job = st.multiselect(
        f"Allowed Machines for Job {i}",
        options=list(range(num_machines)),
        default=list(range(num_machines)),
        key=f"mach_{i}"
    )

    allowed_machines[i] = machines_for_job


# -----------------------------
# REAL-TIME VALIDATION
# -----------------------------

# Ensure each job has at least one feasible machine
valid = True
for i in range(num_jobs):
    if len(allowed_machines[i]) == 0:
        st.error(f"Job {i} must have at least one allowed machine.")
        valid = False


# -----------------------------
# OPTIMIZATION MODEL
# -----------------------------

run = st.button("Run Optimization", disabled=not valid)

if run:

    model = cp_model.CpModel()
    horizon = sum(durations)  # Upper bound for scheduling time

    starts = {}
    ends = {}
    machine_vars = {}

    # Decision variables
    for job_id in range(num_jobs):

        # Start and end time variables
        starts[job_id] = model.NewIntVar(0, horizon, f"start_{job_id}")
        ends[job_id] = model.NewIntVar(0, horizon, f"end_{job_id}")

        # Machine assignment restricted to allowed machines
        machine_vars[job_id] = model.NewIntVarFromDomain(
            cp_model.Domain.FromValues(allowed_machines[job_id]),
            f"machine_{job_id}"
        )

        # Processing time constraint
        model.Add(ends[job_id] == starts[job_id] + durations[job_id])

    # No-overlap constraints per machine
    for m in range(num_machines):

        intervals = []

        for job_id in range(num_jobs):

            if m in allowed_machines[job_id]:

                is_on_machine = model.NewBoolVar(
                    f"job_{job_id}_on_machine_{m}"
                )

                model.Add(machine_vars[job_id] == m).OnlyEnforceIf(is_on_machine)
                model.Add(machine_vars[job_id] != m).OnlyEnforceIf(is_on_machine.Not())

                interval = model.NewOptionalIntervalVar(
                    starts[job_id],
                    durations[job_id],
                    ends[job_id],
                    is_on_machine,
                    f"interval_{job_id}_{m}"
                )

                intervals.append(interval)

        if intervals:
            model.AddNoOverlap(intervals)

    # Objective: minimize makespan (P||Cmax)
    makespan = model.NewIntVar(0, horizon, "makespan")
    model.AddMaxEquality(makespan, [ends[j] for j in range(num_jobs)])
    model.Minimize(makespan)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # -----------------------------
    # RESULTS
    # -----------------------------

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:

        st.success("Optimal Schedule Found!")
        st.metric("Total Makespan", solver.Value(makespan))

        # Build results table
        data = []
        for job_id in range(num_jobs):
            data.append({
                "Job": job_id,
                "Machine": solver.Value(machine_vars[job_id]),
                "Start": solver.Value(starts[job_id]),
                "End": solver.Value(ends[job_id])
            })

        df = pd.DataFrame(data)

        st.subheader("Schedule Table")
        st.dataframe(df)

        # Gantt chart visualization
        st.subheader("Gantt Chart")

        fig, ax = plt.subplots()

        for _, row in df.iterrows():
            ax.barh(
                y=f"Machine {row['Machine']}",
                width=row["End"] - row["Start"],
                left=row["Start"]
            )

        ax.set_xlabel("Time")
        ax.set_ylabel("Machines")
        ax.set_title("Production Schedule")

        st.pyplot(fig)

    else:
        st.error("No feasible solution found.")