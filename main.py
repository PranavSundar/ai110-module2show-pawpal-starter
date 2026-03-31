from pawpal_system import Owner, Pet, Task, Scheduler

owner = Owner(name='Alex', available_minutes_per_day=180, preferences={'evening_walk': True}, max_tasks=10)
pet1 = Pet(name='Mochi', species='dog', age=3)
pet2 = Pet(name='Luna', species='cat', age=5)
owner.add_pet(pet1)
owner.add_pet(pet2)

task1 = Task.create('Morning walk', 'Walk the dog around the neighborhood', duration_minutes=30, frequency='daily', priority='high', category='walk')
task2 = Task.create('Feeding', 'Feed both pets', duration_minutes=20, frequency='daily', priority='medium', category='feeding')
task3 = Task.create('Grooming', 'Brushing and nail trim', duration_minutes=45, frequency='weekly', priority='low', category='grooming')

pet1.add_task(task1)
pet1.add_task(task2)
pet2.add_task(task3)

scheduler = Scheduler(owner)
plan = scheduler.generate_daily_plan()

print("Today's Schedule")
print("---------------")
print(plan.summary())
