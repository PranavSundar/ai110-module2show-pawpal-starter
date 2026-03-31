from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import uuid


@dataclass
class Task:
    task_id: str
    title: str
    description: str
    duration_minutes: int
    frequency: Optional[str]
    priority: str
    category: str
    deadline: Optional[datetime] = None
    is_mandatory: bool = False
    completed: bool = False
    scheduled_at: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None

    @classmethod
    def create(cls, title: str, description: str, duration_minutes: int, frequency: Optional[str], priority: str, category: str, deadline: Optional[datetime] = None, is_mandatory: bool = False) -> 'Task':
        return cls(
            task_id=str(uuid.uuid4()),
            title=title,
            description=description,
            duration_minutes=duration_minutes,
            frequency=frequency,
            priority=priority,
            category=category,
            deadline=deadline,
            is_mandatory=is_mandatory,
        )

    def score(self, priority_weights: Dict[str, int]) -> int:
        base = priority_weights.get(self.priority.lower(), 0)
        if self.is_mandatory:
            base += 100
        if self.completed:
            base -= 1000
        return base

    def mark_complete(self) -> Optional[Task]:
        """Mark this task as completed.

        If the task is recurring ('daily' or 'weekly'), create and return a new
        Task instance for the next occurrence. Otherwise return None.
        """
        self.completed = True

        # If task recurs daily or weekly, create the next occurrence
        if self.frequency in ('daily', 'weekly'):
            delta = timedelta(days=1 if self.frequency == 'daily' else 7)

            # Keep time of existing scheduled time if available, otherwise midnight
            if self.scheduled_at:
                next_start = self.scheduled_at + delta
            else:
                next_start = datetime.combine(date.today() + delta, datetime.min.time())

            next_deadline = None
            if self.deadline:
                next_deadline = self.deadline + delta

            next_task = Task.create(
                title=self.title,
                description=self.description,
                duration_minutes=self.duration_minutes,
                frequency=self.frequency,
                priority=self.priority,
                category=self.category,
                deadline=next_deadline,
                is_mandatory=self.is_mandatory,
            )
            next_task.scheduled_at = next_start
            next_task.scheduled_end = next_start + timedelta(minutes=self.duration_minutes)
            return next_task

        return None

    def conflicts(self, other: "Task") -> bool:
        if self.scheduled_at and self.scheduled_end and other.scheduled_at and other.scheduled_end:
            return not (self.scheduled_end <= other.scheduled_at or other.scheduled_end <= self.scheduled_at)
        return False

    def to_dict(self) -> Dict[str, any]:
        return {
            'task_id': self.task_id,
            'title': self.title,
            'description': self.description,
            'duration_minutes': self.duration_minutes,
            'frequency': self.frequency,
            'priority': self.priority,
            'category': self.category,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'is_mandatory': self.is_mandatory,
            'completed': self.completed,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'scheduled_end': self.scheduled_end.isoformat() if self.scheduled_end else None,
        }

    def reschedule(self, new_time: datetime) -> None:
        self.scheduled_at = new_time
        self.scheduled_end = new_time + timedelta(minutes=self.duration_minutes)


@dataclass
class Pet:
    name: str
    species: str
    age: int
    special_needs: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def get_tasks(self) -> List[Task]:
        return list(self.tasks)

    def get_pending_tasks(self) -> List[Task]:
        return [t for t in self.tasks if not t.completed]

    def needs_tasks(self) -> List[str]:
        return list(self.special_needs)

    def is_high_energy(self) -> bool:
        return self.species.lower() == 'dog' and self.age < 5

    def describe(self) -> str:
        return f"{self.name} is a {self.age}-year-old {self.species}."


@dataclass
class Owner:
    name: str
    available_minutes_per_day: int
    preferences: Dict[str, any] = field(default_factory=dict)
    max_tasks: Optional[int] = None
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        self.pets = [p for p in self.pets if p.name != pet_name]

    def get_all_tasks(self) -> List[Task]:
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks())
        return tasks

    def get_uncompleted_tasks(self) -> List[Task]:
        return [t for t in self.get_all_tasks() if not t.completed]

    def update_preferences(self, new_prefs: Dict[str, any]) -> None:
        self.preferences.update(new_prefs)

    def available_for(self, minutes: int) -> bool:
        return self.available_minutes_per_day >= minutes

    def add_time(self, minutes: int) -> None:
        self.available_minutes_per_day += minutes


@dataclass
class DailyPlan:
    date: date
    tasks: List[Task] = field(default_factory=list)
    total_minutes: int = 0
    notes: Optional[str] = None

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)
        self.total_minutes += task.duration_minutes

    def is_within_budget(self, budget: int) -> bool:
        return self.total_minutes <= budget

    def summary(self) -> str:
        lines = [f"DailyPlan for {self.date.isoformat()}: {len(self.tasks)} tasks, {self.total_minutes} minutes"]
        for task in self.tasks:
            at = task.scheduled_at.isoformat() if task.scheduled_at else 'unscheduled'
            lines.append(f"- {task.title} ({task.duration_minutes}m) at {at}")
        return "\n".join(lines)


class ConstraintEngine:
    @staticmethod
    def apply_constraints(owner: Owner, tasks: List[Task]) -> List[Task]:
        filtered = [t for t in tasks if not t.completed]
        if owner.max_tasks is not None:
            filtered = filtered[:owner.max_tasks]
        return [t for t in filtered if t.duration_minutes <= owner.available_minutes_per_day]


class Scheduler:
    PRIORITY_WEIGHTS = {'low': 10, 'medium': 50, 'high': 100}

    def __init__(self, owner: Owner):
        self.owner = owner
        self.time_budget = owner.available_minutes_per_day
        self.schedule: Optional[DailyPlan] = None
        self.system_prompt: Optional[str] = None

    def get_tasks(self) -> List[Task]:
        return self.owner.get_all_tasks()

    def get_pending_tasks(self) -> List[Task]:
        return self.owner.get_uncompleted_tasks()

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return tasks sorted by scheduled time (HH:MM)."""
        tasks = tasks or self.get_tasks()

        def key(task: Task):
            if task.scheduled_at:
                return task.scheduled_at.strftime('%H:%M')
            return '23:59'

        return sorted(tasks, key=key)

    def filter_tasks(self, completed: Optional[bool] = None, pet_name: Optional[str] = None) -> List[Task]:
        """Return tasks filtered by completion status and/or owning pet."""

        tasks = self.get_tasks()
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        if pet_name is not None:
            tasks = [t for t in tasks if any(p.name == pet_name and t in p.tasks for p in self.owner.pets)]
        return tasks

    def generate_daily_plan(self) -> DailyPlan:
        tasks = self.get_pending_tasks()
        tasks = ConstraintEngine.apply_constraints(self.owner, tasks)

        tasks.sort(key=lambda t: (-self.PRIORITY_WEIGHTS.get(t.priority.lower(), 0), t.deadline or datetime.max))

        plan = DailyPlan(date=date.today())
        start_time = datetime.combine(date.today(), datetime.min.time()) + timedelta(hours=6)

        for task in tasks:
            if plan.total_minutes + task.duration_minutes > self.time_budget:
                continue
            task.reschedule(start_time)
            plan.add_task(task)
            start_time = task.scheduled_end

        self.schedule = plan
        return plan

    def explain_plan(self) -> str:
        if not self.schedule:
            return 'No schedule generated.'

        conflicts = self.detect_conflicts()
        if conflicts:
            return self.schedule.summary() + "\n\nWARNINGS:\n" + "\n".join(conflicts)

        return self.schedule.summary()

    def detect_conflicts(self, tasks: Optional[List[Task]] = None) -> List[str]:
        """Return a list of warning strings for overlapping scheduled tasks."""
        tasks = tasks or (self.schedule.tasks if self.schedule else [])
        warnings = []
        for i, t1 in enumerate(tasks):
            if not t1.scheduled_at or not t1.scheduled_end:
                continue
            for t2 in tasks[i + 1 :]:
                if not t2.scheduled_at or not t2.scheduled_end:
                    continue
                # time overlap detection
                overlap = not (t1.scheduled_end <= t2.scheduled_at or t2.scheduled_end <= t1.scheduled_at)
                if overlap:
                    warnings.append(
                        f"Task '{t1.title}' conflicts with '{t2.title}' at {t1.scheduled_at.strftime('%H:%M')}"
                    )
        return warnings

    def llm_explain(self, plan: DailyPlan) -> str:
        return f"Plan has {len(plan.tasks)} tasks and {plan.total_minutes} minutes."

    def validate(self) -> bool:
        if self.schedule is None:
            return False
        return self.schedule.is_within_budget(self.time_budget)

    def complete_task(self, task: Task) -> Optional[Task]:
        next_task = task.mark_complete()
        if next_task is None:
            return None

        for pet in self.owner.pets:
            if task in pet.tasks:
                pet.add_task(next_task)
                break

        return next_task


class PawPalApp:
    def __init__(self, scheduler: Scheduler):
        self.scheduler = scheduler

    def collect_input(self) -> None:
        pass

    def run_scheduler(self) -> DailyPlan:
        return self.scheduler.generate_daily_plan()

    def display_plan(self, plan: DailyPlan) -> None:
        print(plan.summary())

    def edit_task(self, task_id: str, **kwargs) -> None:
        for pet in self.scheduler.owner.pets:
            for task in pet.tasks:
                if task.task_id == task_id:
                    for key, value in kwargs.items():
                        if hasattr(task, key):
                            setattr(task, key, value)
                    return
        raise ValueError('Task not found')

