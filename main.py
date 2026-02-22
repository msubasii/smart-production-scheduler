from ortools.sat.python import cp_model


# --------------------------------
# CLI INPUT
# --------------------------------

def get_user_input():
    """Collect basic scheduling data from terminal input."""

    print("=== Smart Production Scheduler ===")

    num_machines = int(input("Number of machines: "))
    num_jobs = int(input("Number of jobs: "))

    jobs = {}

    for i in range(num_jobs):
        duration = int(input(f"Duration of job {i}: "))
        jobs[i] = duration

    return num_machines, jobs


# --------------------------------
# OPTIMIZATION MODEL
# --------------------------------

def build_and_solve(num_machines, jobs):
    """Build and solve a parallel machine scheduling problem (P||Cmax)."""

    model = cp_model.CpModel()

    machines = list(range(num_machines))
    horizon = sum(jobs.values())  # Upper bound on total schedule length

    starts = {}
    ends = {}
    machine_vars = {}

    # Decision variables
    for job_id, duration in jobs.items():

        # Start and end time variables
        starts[job_id] = model.NewIntVar(0, horizon, f"start_{job_id}")
        ends[job_id] = model.NewIntVar(0, horizon, f"end_{job_id}")

        # Machine assignment variable
        machine_vars[job_id] = model.NewIntVar(
            0, num_machines - 1, f"machine_{job_id}"
        )

        # Processing time constraint
        model.Add(ends[job_id] == starts[job_id] + duration)

    # No-overlap constraint per machine
    for m in machines:

        machine_intervals = []

        for job_id in jobs:

            is_on_machine = model.NewBoolVar(
                f"job_{job_id}_on_machine_{m}"
            )

            model.Add(machine_vars[job_id] == m).OnlyEnforceIf(is_on_machine)
            model.Add(machine_vars[job_id] != m).OnlyEnforceIf(is_on_machine.Not())

            optional_interval = model.NewOptionalIntervalVar(
                starts[job_id],
                jobs[job_id],
                ends[job_id],
                is_on_machine,
                f"opt_interval_{job_id}_{m}"
            )

            machine_intervals.append(optional_interval)

        model.AddNoOverlap(machine_intervals)

    # Objective: minimize makespan
    makespan = model.NewIntVar(0, horizon, "makespan")
    model.AddMaxEquality(makespan, [ends[j] for j in jobs])
    model.Minimize(makespan)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # --------------------------------
    # RESULTS
    # --------------------------------

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:

        print("\nOptimal Schedule:\n")

        for job_id in jobs:
            print(
                f"Job {job_id} | "
                f"Machine {solver.Value(machine_vars[job_id])} | "
                f"Start {solver.Value(starts[job_id])} | "
                f"End {solver.Value(ends[job_id])}"
            )

        print(f"\nTotal makespan: {solver.Value(makespan)}")

    else:
        print("No feasible solution found.")


# --------------------------------
# MAIN ENTRY POINT
# --------------------------------

def main():
    num_machines, jobs = get_user_input()
    build_and_solve(num_machines, jobs)


if __name__ == "__main__":
    main()