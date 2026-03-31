from datetime import date, datetime, timedelta
from pawpal_system import Pet, Task, Owner, Scheduler, DailyPlan


def test_task_completion_marks_as_completed():
    task = Task.create(
        title='Test task',
        description='A simple test task',
        duration_minutes=15,
        frequency='once',
        priority='low',
        category='test',
    )

    assert not task.completed

    task.mark_complete()

    assert task.completed


def test_pet_add_task_increases_task_count():
    pet = Pet(name='TestPet', species='cat', age=2)
    initial_count = len(pet.tasks)

    task = Task.create(
        title='Feed',
        description='Feed the test pet',
        duration_minutes=10,
        frequency='daily',
        priority='medium',
        category='feeding',
    )

    pet.add_task(task)

    assert len(pet.tasks) == initial_count + 1


def test_sort_by_time_orders_tasks_chronologically():
    pet = Pet(name='SchedPet', species='dog', age=4)
    owner = Owner(name='Owner', available_minutes_per_day=120)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    morning = Task.create(
        title='Morning walk',
        description='Take the dog out',
        duration_minutes=30,
        frequency='once',
        priority='medium',
        category='exercise',
    )
    morning.scheduled_at = datetime(2026, 1, 1, 9, 0)
    morning.scheduled_end = morning.scheduled_at + timedelta(minutes=30)

    noon = Task.create(
        title='Noon meal',
        description='Feed the pet',
        duration_minutes=20,
        frequency='once',
        priority='high',
        category='feeding',
    )
    noon.scheduled_at = datetime(2026, 1, 1, 12, 0)
    noon.scheduled_end = noon.scheduled_at + timedelta(minutes=20)

    afternoon = Task.create(
        title='Afternoon play',
        description='Playtime',
        duration_minutes=20,
        frequency='once',
        priority='low',
        category='play',
    )
    afternoon.scheduled_at = datetime(2026, 1, 1, 15, 0)
    afternoon.scheduled_end = afternoon.scheduled_at + timedelta(minutes=20)

    pet.add_task(afternoon)
    pet.add_task(morning)
    pet.add_task(noon)

    sorted_tasks = scheduler.sort_by_time()

    assert [t.title for t in sorted_tasks] == ['Morning walk', 'Noon meal', 'Afternoon play']


def test_complete_daily_task_creates_next_day_task():
    pet = Pet(name='RecursivePet', species='cat', age=3)
    owner = Owner(name='Owner', available_minutes_per_day=120)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    daily = Task.create(
        title='Daily grooming',
        description='Brush the pet',
        duration_minutes=10,
        frequency='daily',
        priority='medium',
        category='grooming',
    )
    daily.scheduled_at = datetime(2026, 4, 1, 8, 0)
    daily.scheduled_end = daily.scheduled_at + timedelta(minutes=10)

    pet.add_task(daily)

    next_task = scheduler.complete_task(daily)

    assert daily.completed
    assert next_task is not None
    assert next_task.frequency == 'daily'
    assert next_task.scheduled_at == datetime(2026, 4, 2, 8, 0)
    assert len(pet.tasks) == 2


def test_detect_conflicts_reports_overlapping_tasks():
    pet = Pet(name='ConflictPet', species='dog', age=5)
    owner = Owner(name='Owner', available_minutes_per_day=120)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    t1 = Task.create(
        title='Task 1',
        description='First task',
        duration_minutes=30,
        frequency='once',
        priority='low',
        category='other',
    )
    t1.scheduled_at = datetime(2026, 7, 1, 10, 0)
    t1.scheduled_end = t1.scheduled_at + timedelta(minutes=30)

    t2 = Task.create(
        title='Task 2',
        description='Overlapping task',
        duration_minutes=30,
        frequency='once',
        priority='medium',
        category='other',
    )
    t2.scheduled_at = datetime(2026, 7, 1, 10, 15)
    t2.scheduled_end = t2.scheduled_at + timedelta(minutes=30)

    pet.add_task(t1)
    pet.add_task(t2)

    scheduler.schedule = DailyPlan(date.today())
    scheduler.schedule.tasks = [t1, t2]

    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert "conflicts" in conflicts[0]

