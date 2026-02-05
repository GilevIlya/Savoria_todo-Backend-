from typing import Any, List

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import SQLAlchemyError

from api.users.tasks.service import serialize_TaskTable_obj_data
from db.engine import SessionDep
from db.models import CompletedTasksTable, TaskPriority, TasksTable


async def create_task_in_db(
    session: SessionDep, 
    user_uuid: str, 
    task_data: dict
) -> int:
    async with session.begin():
        task_data["user_id"] = user_uuid
        stmt = insert(TasksTable).values(
            **task_data).returning(
            TasksTable.id)

        result = await session.execute(stmt)
        task_id = result.scalar_one_or_none()

        return task_id


async def change_task_status(
    session: SessionDep, user_uuid: str, task_id: int, new_status: str = "IN_PROGRESS"
) -> None:
    async with session.begin():
        stmt = (
            update(TasksTable)
            .values(status=new_status)
            .filter(TasksTable.user_id == user_uuid, TasksTable.id == task_id)
        )
        result = await session.execute(stmt)

        if result.rowcount == 0:
            raise ValueError("Task not found")


async def select_all_tasks(
    session: SessionDep, 
    user_uuid: str
) -> List[Any]:
    all_tasks: List[Any] = []

    async with session.begin():
        stmt = select(TasksTable).where(TasksTable.user_id == user_uuid)
        stmt1 = select(CompletedTasksTable).where(
            CompletedTasksTable.user_id == user_uuid
        )

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
            TasksTable.priority == TaskPriority.EXTREME.value,
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
        stmt = (
            update(TasksTable)
            .values(**task_data)
            .filter(TasksTable.user_id == user_uuid, TasksTable.id == task_id)
        )
        result = await session.execute(stmt)

        if result.rowcount == 0:
            raise ValueError("Task not found")

        return {"task updated": "true"}


async def get_task_to_complete(
    session: SessionDep, 
    user_uuid: str, 
    task_id: int
) -> dict:
    async with session.begin():
        query = select(TasksTable).filter(
            TasksTable.user_id == user_uuid, TasksTable.id == task_id
        )
        result = await session.execute(query)
        task = result.scalars().all()

        if not task:
            raise ValueError("Task is absent")

        serialized_task = await serialize_TaskTable_obj_data(task_obj=task[0])

        return serialized_task


async def replace_tasks_between_tables(
    session: SessionDep, 
    task: dict, 
    user_uuid: str, 
    task_id: int
) -> tuple[bool | None, int | None]:
    img_to_delete: bool | None = None
    task_id_to_delete: int | None = None

    try:
        async with session.begin():
            stmt = (
                select(CompletedTasksTable)
                .filter(CompletedTasksTable.user_id == user_uuid)
                .order_by(CompletedTasksTable.created_at.asc())
            )

            result = await session.execute(stmt)
            completed_tasks_list = result.scalars().all()

            if len(completed_tasks_list) >= 5:
                oldest_task = completed_tasks_list[0]
                await session.delete(oldest_task)
                await session.flush()
                task_id_to_delete = oldest_task.id
                img_to_delete = True

            new_task = CompletedTasksTable(**task)
            session.add(new_task)

            stmt = await delete_task_from_Task_table(task_id=task_id, user_uuid=user_uuid)
            await session.execute(stmt)

        return img_to_delete, task_id_to_delete

    except :
        raise SQLAlchemyError()



async def delete_task_from_Task_table(task_id: int, user_uuid: str):
    return (
        delete(TasksTable)
        .where(TasksTable.id == task_id)
        .where(TasksTable.user_id == user_uuid)
    )


async def search_tasks_by_name(
    session: SessionDep,
    user_uuid: str,
    task_name: str,
):
    async with session.begin():
        try:
            query = select(TasksTable).filter(
                TasksTable.user_id == user_uuid,
                TasksTable.title.ilike(f"%{task_name}%"),
            )
            result = await session.execute(query)

            return result.scalars().all()
        except:
            raise SQLAlchemyError()


async def delete_task_db(
    session: SessionDep, 
    task_id: int, 
    user_uuid: str
) -> None:
    async with session.begin():
        try:
            stmt = delete(TasksTable).filter(
                TasksTable.user_id == user_uuid, TasksTable.id == task_id
            )

            result = await session.execute(stmt)

            if result.rowcount == 0:
                await session.execute(
                    delete(CompletedTasksTable).filter(
                        CompletedTasksTable.user_id == user_uuid,
                        CompletedTasksTable.id == task_id,
                    )
                )
        except Exception:
            raise ValueError("Task not found")
