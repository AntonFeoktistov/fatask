from httpx import AsyncClient

from backend.models.user import User

# ========== РЕГИСТРАЦИЯ ==========


async def test_register_success(client: AsyncClient):
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "hashed_password" not in data


async def test_register_duplicate_email(client: AsyncClient, test_user: User):
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "newuser2",
            "password": "password123",
        },
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


async def test_register_duplicate_username(client: AsyncClient, test_user: User):
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "newuser2@example.com",
            "username": "testuser",
            "password": "password123",
        },
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


async def test_register_short_password(client: AsyncClient):
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "12",
        },
    )
    assert response.status_code == 422


async def test_register_invalid_email(client: AsyncClient):
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "invalid-email",
            "username": "newuser",
            "password": "password123",
        },
    )
    assert response.status_code == 422


# ========== ЛОГИН (OAuth2 password flow) ==========


async def test_login_success(client: AsyncClient, test_user: User):
    response = await client.post(
        "/api/auth/token",
        data={
            "username": "testuser",
            "password": "password123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient, test_user: User):
    response = await client.post(
        "/api/auth/token",
        data={
            "username": "testuser",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    assert "username or password" in response.json()["detail"]


async def test_login_nonexistent_user(client: AsyncClient):
    response = await client.post(
        "/api/auth/token",
        data={
            "username": "nonexistent",
            "password": "password123",
        },
    )
    assert response.status_code == 401
    assert "username or password" in response.json()["detail"]


async def test_login_empty_username(client: AsyncClient):
    response = await client.post(
        "/api/auth/token",
        data={
            "username": "",
            "password": "password123",
        },
    )
    assert response.status_code == 422


async def test_login_empty_password(client: AsyncClient):
    response = await client.post(
        "/api/auth/token",
        data={
            "username": "testuser",
            "password": "",
        },
    )
    assert response.status_code == 422


# ========== ПОЛУЧЕНИЕ ТЕКУЩЕГО ПОЛЬЗОВАТЕЛЯ ==========


async def test_get_me_success(client: AsyncClient, auth_headers: dict):
    response = await client.get(
        "/api/auth/me",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


async def test_get_me_unauthorized(client: AsyncClient):
    response = await client.get("/api/auth/me")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


async def test_get_me_invalid_token(client: AsyncClient):
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token_123"},
    )
    assert response.status_code == 401


# ========== ВЫХОД ==========


async def test_logout_success(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/auth/logout",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"


async def test_logout_unauthorized(client: AsyncClient):
    response = await client.post("/api/auth/logout")
    assert response.status_code == 401


# ========== ОБНОВЛЕНИЕ ТОКЕНА ==========


async def test_refresh_token_success(client: AsyncClient, test_user: User):
    login_response = await client.post(
        "/api/auth/token",
        data={"username": "testuser", "password": "password123"},
    )
    assert login_response.status_code == 200

    login_data = login_response.json()
    assert "access_token" in login_data
    assert "refresh_token" not in login_data
    assert "refresh_token" in client.cookies

    response = await client.post("/api/auth/refresh")
    assert response.status_code == 200


async def test_refresh_token_invalid(client: AsyncClient):
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": "invalid_token_123"},
    )
    assert response.status_code == 401


async def test_refresh_token_missing(client: AsyncClient):
    response = await client.post("/api/auth/refresh", json={})
    assert response.status_code == 401
