from fastapi import APIRouter

router = APIRouter(prefix="/api/task", tags=["task"])


# @router.post(
#     "/",
#     response_model=TaskResponse,
#     status_code=status.HTTP_201_CREATED,
# )
# async def create_task(
#     task_data: TaskCreate,
#     db: Annotated[AsyncSession, Depends(get_db)],
#     user: Annotated[User, Depends(get_current_user)]
# ):
#     service = Task
#     new_task =

#     await db.commit()
#     await db.refresh(new_user)
#     return new_user
