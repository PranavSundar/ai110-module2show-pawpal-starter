from pawpal_system import Owner, Pet, Task, Scheduler
from datetime import datetime

owner = Owner(name='Alex', available_minutes_per_day=180, preferences={'evening_walk': True}, max_tasks=10)
pet1 = Pet(name='Mochi', species='dog', age=3)
pet2 = Pet(name='Luna', species='cat', age=5)
owner.add_pet(pet1)
owner.add_pet(pet2)

task1 = Task.create('Grooming', 'Brushing and nail trim', duration_minutes=45, frequency='weekly', priority='low', category='grooming')
task2 = Task.create('Feeding', 'Feed both pets', duration_minutes=20, frequency='daily', priority='medium', category='feeding')
task3 = Task.create('Morning walk', 'Walk the dog around the neighborhood', duration_minutes=30, frequency='daily', priority='high', category='walk')

pet1.add_task(task1)
pet1.add_task(task2)
pet2.add_task(task3)

# Add conflict task (same time as task3)
task4 = Task.create('Cat grooming', 'Quick brushing', duration_minutes=30, frequency='daily', priority='medium', category='grooming')
pet2.add_task(task4)

# Assign explicit times for testing sort_by_time
task1.reschedule(datetime(2025, 1, 1, 18, 0))
task2.reschedule(datetime(2025, 1, 1, 8, 0))
task3.reschedule(datetime(2025, 1, 1, 7, 0))
task4.reschedule(datetime(2025, 1, 1, 7, 0))

scheduler = Scheduler(owner)

print("=== Sorted by time ===")
for t in scheduler.sort_by_time():
    print(f"{t.scheduled_at.strftime('%H:%M')} - {t.title} (pet={ 'Mochi' if t in pet1.tasks else 'Luna' })")

print("\n=== Filter pending tasks (not completed) ===")
for t in scheduler.filter_tasks(completed=False):
    print(f"{t.title} - completed={t.completed}")

print("\n=== Filter tasks by pet 'Mochi' ===")
for t in scheduler.filter_tasks(pet_name='Mochi'):
    print(f"{t.title} - pet=Mochi")

plan = scheduler.generate_daily_plan()

print("\nToday's Schedule")
print("---------------")
print(plan.summary())

conflicts = scheduler.detect_conflicts(plan.tasks)
if conflicts:
    print("\nConflict warnings:")
    for warning in conflicts:
        print("- "+warning)
else:
    print("\nNo conflicts detected.")
