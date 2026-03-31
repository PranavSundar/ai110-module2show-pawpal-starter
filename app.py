import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Persist owner in session state
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes_per_day=180, preferences={})

st.subheader("Owner")
owner = st.session_state.owner
owner_name = st.text_input("Owner name", value=owner.name)
available_time = st.number_input("Available minutes/day", min_value=30, max_value=1440, value=owner.available_minutes_per_day)

if st.button("Update owner"):
    owner.name = owner_name
    owner.available_minutes_per_day = int(available_time)
    st.session_state.owner = owner
    st.success("Owner updated")

st.write(f"Current owner: {owner.name} ({owner.available_minutes_per_day} min/day)")

st.divider()

st.subheader("Add a Pet")
new_pet_name = st.text_input("Pet name", value="")
new_pet_species = st.selectbox("Species", ["dog", "cat", "other"])
new_pet_age = st.number_input("Age", min_value=0, max_value=30, value=1)

if st.button("Add pet"):
    if not new_pet_name.strip():
        st.error("Enter a pet name")
    else:
        pet = Pet(name=new_pet_name.strip(), species=new_pet_species, age=int(new_pet_age))
        owner.add_pet(pet)
        st.session_state.owner = owner
        st.success(f"Added pet {pet.name}")

if owner.pets:
    st.write("### Pets")
    for p in owner.pets:
        st.write(f"- {p.name} ({p.species}, age {p.age}) - tasks: {len(p.tasks)}")
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Add a Task to a Pet")
if owner.pets:
    pet_choices = {p.name: p for p in owner.pets}
    selected_pet_name = st.selectbox("Select pet", list(pet_choices.keys()))
    selected_pet = pet_choices[selected_pet_name]

    task_title = st.text_input("Task title", value="")
    task_desc = st.text_input("Description", value="")
    task_duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    task_priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
    task_category = st.selectbox("Category", ["walk", "feeding", "meds", "grooming", "enrichment"], index=0)

    if st.button("Add task to pet"):
        if not task_title.strip():
            st.error("Task title is required")
        else:
            task = Task.create(
                title=task_title.strip(),
                description=task_desc.strip(),
                duration_minutes=int(task_duration),
                frequency="daily",
                priority=task_priority,
                category=task_category,
            )
            selected_pet.add_task(task)
            st.session_state.owner = owner
            st.success(f"Added task '{task.title}' to {selected_pet.name}")

    st.write("#### Selected Pet Tasks")
    if selected_pet.tasks:
        for t in selected_pet.tasks:
            st.write(f"- {t.title} ({t.duration_minutes}m) [priority={t.priority}]")
    else:
        st.info("This pet has no tasks yet.")
else:
    st.info("Add a pet first before adding tasks.")

st.divider()

st.subheader("Build Schedule")
if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    schedule = scheduler.generate_daily_plan()

    st.write("### Today\'s schedule")

    if not schedule.tasks:
        st.info("No tasks fit in available time or no tasks exist.")
    else:
        # Display the schedule in a table for readability
        rows = []
        for task in scheduler.sort_by_time(schedule.tasks):
            rows.append({
                "Task": task.title,
                "Pet": next((p.name for p in owner.pets if task in p.tasks), "unknown"),
                "Start": task.scheduled_at.strftime("%Y-%m-%d %H:%M") if task.scheduled_at else "unscheduled",
                "Duration": task.duration_minutes,
                "Priority": task.priority,
                "Completed": task.completed,
            })
        st.table(rows)

        warning_messages = scheduler.detect_conflicts(schedule.tasks)
        if warning_messages:
            st.warning("Task conflicts detected. Please review the overlapping tasks:")
            for msg in warning_messages:
                st.warning(msg)
        else:
            st.success("No conflicts detected in today's schedule.")

        if scheduler.validate():
            st.success("Schedule is valid and within available time")
        else:
            st.error("Schedule exceeds available time")

        st.markdown("#### Full resolution schedule summary")
        st.code(schedule.summary())

