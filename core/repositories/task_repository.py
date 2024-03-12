from typing import Optional

from app.models import Task
from core.repositories.abstract_repository import AbstractRepository
from sqlalchemy.orm import Session


class TaskRepository(AbstractRepository):

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_or_none(self, task_id: int) -> Optional[Task]:
        return self.session.get(Task, task_id)

    def get(self, task_id: int) -> Task:
        task = self.get_or_none(task_id)
        if not task:
            raise LookupError(f'Task ID={task_id} not found')
        return task

    def get_active_tasks(self) -> Task:
        tasks = self.session.query(Task).filter_by(archive=False).all()
        return tasks

    def create(self, task_list: list[Task]) -> list[Task]:
        self.session.add_all(task_list)
        self.session.commit()
        return task_list

    def update(self, task: Task) -> Task:
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task
