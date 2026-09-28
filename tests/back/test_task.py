import uuid

from httpx import AsyncClient

from backend.models.task import Task
from backend.models.user import User

# ========== CREATE ==========


async def test_create_task_success(
    client: AsyncClient, auth_headers: dict, test_user: User
):
    response = await client.post(
        "/api/tasks",
        json={"title": "Buy milk", "description": "2 liters"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy milk"
    assert data["description"] == "2 liters"
    assert "oid" in data


async def test_create_task_without_description(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/tasks",
        json={"title": "No description"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert not response.json()["description"]


async def test_create_task_empty_title(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/tasks",
        json={"title": "", "description": "desc"},
        headers=auth_headers,
    )
    assert response.status_code == 422


async def test_create_task_whitespace_title(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/tasks",
        json={"title": "   ", "description": "desc"},
        headers=auth_headers,
    )
    assert response.status_code == 422


async def test_create_task_title_stripped(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/tasks",
        json={"title": "  Buy milk  ", "description": "desc"},
        headers=auth_headers,
    )
    assert response.status_code == 422


async def test_create_task_unauthorized(client: AsyncClient):
    response = await client.post(
        "/api/tasks",
        json={"title": "Buy milk"},
    )
    assert response.status_code == 401


# ========== GET ONE ==========


async def test_get_task_success(
    client: AsyncClient, auth_headers: dict, test_task: Task
):
    response = await client.get(
        f"/api/tasks/{test_task.oid}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["oid"] == str(test_task.oid)
    assert data["title"] == test_task.title


async def test_get_task_not_found(client: AsyncClient, auth_headers: dict):
    response = await client.get(
        f"/api/tasks/{uuid.uuid4()}",
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_get_task_invalid_uuid(client: AsyncClient, auth_headers: dict):
    response = await client.get(
        "/api/tasks/not-a-uuid",
        headers=auth_headers,
    )
    assert response.status_code == 422


async def test_get_task_unauthorized(client: AsyncClient, test_task: Task):
    response = await client.get(f"/api/tasks/{test_task.oid}")
    assert response.status_code == 401


async def test_get_task_of_another_user(
    client: AsyncClient,
    auth_headers: dict,
    db_session,
    other_user: User,
):
    other_task = Task(
        title="Other user's task",
        description="secret",
        user_oid=other_user.oid,
    )
    db_session.add(other_task)
    await db_session.commit()
    await db_session.refresh(other_task)

    response = await client.get(
        f"/api/tasks/{other_task.oid}",
        headers=auth_headers,
    )
    assert response.status_code == 404


# ========== GET LIST ==========


async def test_get_all_tasks_empty(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/tasks", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


async def test_get_all_tasks_success(
    client: AsyncClient, auth_headers: dict, test_task: Task
):
    response = await client.get("/api/tasks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["oid"] == str(test_task.oid)


async def test_get_all_tasks_only_own(
    client: AsyncClient,
    auth_headers: dict,
    test_task: Task,
    db_session,
    other_user: User,
):
    other_task = Task(
        title="Other task",
        description="secret",
        user_oid=other_user.oid,
    )
    db_session.add(other_task)
    await db_session.commit()

    response = await client.get("/api/tasks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["oid"] == str(test_task.oid)


async def test_get_all_tasks_unauthorized(client: AsyncClient):
    response = await client.get("/api/tasks")
    assert response.status_code == 401


# ========== UPDATE ==========


async def test_update_task_title(
    client: AsyncClient, auth_headers: dict, test_task: Task
):
    response = await client.patch(
        f"/api/tasks/{test_task.oid}",
        json={"title": "Updated title"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated title"
    assert data["description"] == test_task.description


async def test_update_task_description(
    client: AsyncClient, auth_headers: dict, test_task: Task
):
    response = await client.patch(
        f"/api/tasks/{test_task.oid}",
        json={"description": "Updated description"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated description"
    assert data["title"] == test_task.title


async def test_update_task_both_fields(
    client: AsyncClient, auth_headers: dict, test_task: Task
):
    response = await client.patch(
        f"/api/tasks/{test_task.oid}",
        json={"title": "New", "description": "New desc"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New"
    assert data["description"] == "New desc"


async def test_update_task_empty_body(
    client: AsyncClient, auth_headers: dict, test_task: Task
):
    response = await client.patch(
        f"/api/tasks/{test_task.oid}",
        json={},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == test_task.title
    assert data["description"] == test_task.description


async def test_update_task_not_found(client: AsyncClient, auth_headers: dict):
    response = await client.patch(
        f"/api/tasks/{uuid.uuid4()}",
        json={"title": "New"},
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_update_task_invalid_title(
    client: AsyncClient, auth_headers: dict, test_task: Task
):
    response = await client.patch(
        f"/api/tasks/{test_task.oid}",
        json={"title": "   "},
        headers=auth_headers,
    )
    assert response.status_code == 422


async def test_update_task_of_another_user(
    client: AsyncClient,
    auth_headers: dict,
    db_session,
    other_user: User,
):
    other_task = Task(
        title="Other task",
        description="secret",
        user_oid=other_user.oid,
    )
    db_session.add(other_task)
    await db_session.commit()
    await db_session.refresh(other_task)

    response = await client.patch(
        f"/api/tasks/{other_task.oid}",
        json={"title": "Hacked"},
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_update_task_unauthorized(client: AsyncClient, test_task: Task):
    response = await client.patch(
        f"/api/tasks/{test_task.oid}",
        json={"title": "Hacked"},
    )
    assert response.status_code == 401


# ========== DELETE ==========


async def test_delete_task_success(
    client: AsyncClient,
    auth_headers: dict,
    test_task: Task,
    db_session,
):
    response = await client.delete(
        f"/api/tasks/{test_task.oid}",
        headers=auth_headers,
    )
    assert response.status_code == 204
    assert response.content == b""

    # Проверяем, что задача реально удалена
    from sqlalchemy import select

    result = await db_session.execute(select(Task).where(Task.oid == test_task.oid))
    assert result.scalar_one_or_none() is None


async def test_delete_task_not_found(client: AsyncClient, auth_headers: dict):
    response = await client.delete(
        f"/api/tasks/{uuid.uuid4()}",
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_delete_task_of_another_user(
    client: AsyncClient,
    auth_headers: dict,
    db_session,
    other_user: User,
):
    other_task = Task(
        title="Other task",
        description="secret",
        user_oid=other_user.oid,
    )
    db_session.add(other_task)
    await db_session.commit()
    await db_session.refresh(other_task)

    response = await client.delete(
        f"/api/tasks/{other_task.oid}",
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_delete_task_unauthorized(client: AsyncClient, test_task: Task):
    response = await client.delete(f"/api/tasks/{test_task.oid}")
    assert response.status_code == 401


async def test_update_is_done_true(
    client: AsyncClient, auth_headers: dict, test_task: Task
):
    assert test_task.is_done is False  # по дефолту

    response = await client.patch(
        f"/api/tasks/{test_task.oid}",
        json={"is_done": True},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["is_done"] is True
    assert test_task.is_done is True


async def test_update_is_done_false_after_true(
    client: AsyncClient, auth_headers: dict, test_task: Task
):
    await client.patch(
        f"/api/tasks/{test_task.oid}",
        json={"is_done": True},
        headers=auth_headers,
    )
    assert test_task.is_done is True
    response = await client.patch(
        f"/api/tasks/{test_task.oid}",
        json={"is_done": False},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["is_done"] is False


async def test_update_is_done_already_false(
    client: AsyncClient, auth_headers: dict, test_task: Task
):
    # false → false — no-op, но должно вернуть 200
    response = await client.patch(
        f"/api/tasks/{test_task.oid}",
        json={"is_done": False},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["is_done"] is False
