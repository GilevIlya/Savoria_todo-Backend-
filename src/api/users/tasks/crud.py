from sqlalchemy import insert, select, update, delete
from sqlalchemy.exc import SQLAlchemyError

from typing import List, Any

from db.engine import SessionDep
from db.models import TasksTable, CompletedTasksTable, TaskPriority
from api.users.tasks.service import serialize_TaskTable_obj_data

async def create_task_in_db(
        session: SessionDep,
        user_uuid: str,
        task_data: dict
):
    async with session.begin():
        task_data['user_id'] = user_uuid
        stmt = insert(TasksTable).values(**task_data).returning(TasksTable.id)

        result = await session.execute(stmt)
        task_id = result.scalar_one_or_none()

        return task_id
    
async def select_all_tasks(
        session: SessionDep,
        user_uuid: str
) -> List[Any]:
    all_tasks: List[Any] = []

    async with session.begin():
        stmt = select(TasksTable).where(TasksTable.user_id == user_uuid)
        stmt1 = select(CompletedTasksTable).where(CompletedTasksTable.user_id == user_uuid)

        result = await session.execute(stmt)
        result1 = await session.execute(stmt1)

        not_completed_tasks = result.scalars().all()
        completed_tasks = result1.scalars().all()

        all_tasks.extend(completed_tasks)
        all_tasks.extend(not_completed_tasks)

        return all_tasks

async def select_vital_tasks(
        session: SessionDep,
        user_uuid: str,
):
    async with session.begin():
        query = select(TasksTable).where(
            TasksTable.user_id == user_uuid,
            TasksTable.priority == TaskPriority.EXTREME.value
        )

        result = await session.execute(query)

        return result.scalars().all()


async def edit_task_data(
        session: SessionDep,
        user_uuid: str,
        task_id: int,
        task_data: dict,
):
    async with session.begin():
        stmt = update(TasksTable).values(**task_data).filter(
            TasksTable.user_id == user_uuid,
            TasksTable.id == task_id)
        result = await session.execute(stmt)

        if result.rowcount == 0:
            raise ValueError('Task not found')

        return {
            'task updated': 'true'
                }

async def replace_task_to_completed(
        session: SessionDep,
        user_uuid: str,
        task_id: int,
):
    async with session.begin():
        query = select(TasksTable).filter(
            TasksTable.user_id == user_uuid,
            TasksTable.id == task_id
        )
        result = await session.execute(
            query
        )
        task = result.scalars().all()

        if not task:
            raise ValueError('Task is absent')
        
        try:
            serialized_task = await serialize_TaskTable_obj_data(
                task_obj=task[0]
            )
            await session.execute(
                insert(CompletedTasksTable)
                .values(**serialized_task)
            )

            query = delete(TasksTable).filter(
                TasksTable.user_id == user_uuid,
                TasksTable.id == task_id)

            await session.execute(
                query
            )
        except:
            raise SQLAlchemyError()

async def search_tasks_by_name(
        session: SessionDep,
        user_uuid: str,
        task_name: str,
):
    async with session.begin():
        try:
            query = select(TasksTable).filter(
                TasksTable.user_id == user_uuid,
                TasksTable.title.ilike(f'%{task_name}%')
            )
            result = await session.execute(query)

            return result.scalars().all()
        except:
            raise SQLAlchemyError()

async def delete_task_db(
        session: SessionDep,
        task_id: int,
        user_uuid: str
):
    async with session.begin():
        try:
            stmt = delete(TasksTable).filter(
                TasksTable.user_id == user_uuid,
                TasksTable.id == task_id
            )

            result = await session.execute(stmt)

            if result.rowcount == 0:
                await session.execute(
                    delete(CompletedTasksTable)
                    .filter(
                        CompletedTasksTable.user_id == user_uuid,
                        CompletedTasksTable.id == task_id
                    )
                )
        except Exception:
            raise ValueError('Task not found')