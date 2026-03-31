from pawpal_system import Pet, Task


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
