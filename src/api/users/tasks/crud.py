from sqlalchemy import insert, select, update

from db.engine import SessionDep
from db.models import TasksTable

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

        await session.commit()
        return task_id
    
async def select_all_tasks(
        session: SessionDep,
        user_uuid: str
):
    async with session.begin():
        stmt = select(TasksTable).where(TasksTable.user_id == user_uuid)
        result = await session.execute(stmt)
        tasks = result.scalars().all()
        return tasks

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
        await session.commit()

        return {
            'task updated': 'true'
                }