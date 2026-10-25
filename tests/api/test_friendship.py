"""КРИТИЧНОЕ: заявка, самому себе, повторная заявка, принять и отклонить может только адресат, удаление"""
"""Friendship: send / accept / reject / delete, lists, ownership."""
from httpx import AsyncClient

from app.models.friendship import Friendship


BASE = "/api/v1/friendship"


# ---------------------------------------------------------
# send request
# ---------------------------------------------------------

async def test_send_request_requires_auth(client: AsyncClient, make_user):
    user = await make_user()
    r = await client.post(BASE + "/", json={"addressee_id": user.id})
    assert r.status_code == 401


async def test_send_request_success(
    client: AsyncClient, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()

    r = await client.post(
        BASE + "/",
        json={"addressee_id": user_b.id},
        headers=auth_headers(user_a),
    )
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["requester_id"] == user_a.id
    assert data["addressee_id"] == user_b.id
    assert data["status"] == "pending"


async def test_send_request_to_self_forbidden(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    r = await client.post(
        BASE + "/",
        json={"addressee_id": user.id},
        headers=auth_headers(user),
    )
    assert r.status_code == 400


async def test_send_request_duplicate_pending_conflicts(
    client: AsyncClient, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()
    h = auth_headers(user_a)

    r1 = await client.post(
        BASE + "/", json={"addressee_id": user_b.id}, headers=h
    )
    assert r1.status_code == 201

    r2 = await client.post(
        BASE + "/", json={"addressee_id": user_b.id}, headers=h
    )
    assert r2.status_code == 409


async def test_send_request_after_accepted_conflicts(
    client: AsyncClient, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()

    r = await client.post(
        BASE + "/",
        json={"addressee_id": user_b.id},
        headers=auth_headers(user_a),
    )
    fid = r.json()["id"]
    await client.patch(f"{BASE}/{fid}/accept", headers=auth_headers(user_b))

    r = await client.post(
        BASE + "/",
        json={"addressee_id": user_b.id},
        headers=auth_headers(user_a),
    )
    assert r.status_code == 409


# ---------------------------------------------------------
# accept
# ---------------------------------------------------------

async def test_accept_by_addressee_succeeds(
    client: AsyncClient, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()
    r = await client.post(
        BASE + "/",
        json={"addressee_id": user_b.id},
        headers=auth_headers(user_a),
    )
    fid = r.json()["id"]

    r = await client.patch(
        f"{BASE}/{fid}/accept", headers=auth_headers(user_b)
    )
    assert r.status_code == 200
    assert r.json()["status"] == "accepted"


async def test_accept_by_requester_forbidden(
    client: AsyncClient, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()
    r = await client.post(
        BASE + "/",
        json={"addressee_id": user_b.id},
        headers=auth_headers(user_a),
    )
    fid = r.json()["id"]

    r = await client.patch(
        f"{BASE}/{fid}/accept", headers=auth_headers(user_a)
    )
    assert r.status_code == 403


async def test_accept_by_stranger_forbidden(
    client: AsyncClient, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()
    user_c = await make_user()
    r = await client.post(
        BASE + "/",
        json={"addressee_id": user_b.id},
        headers=auth_headers(user_a),
    )
    fid = r.json()["id"]

    r = await client.patch(
        f"{BASE}/{fid}/accept", headers=auth_headers(user_c)
    )
    assert r.status_code == 403


async def test_accept_already_accepted_fails(
    client: AsyncClient, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()
    r = await client.post(
        BASE + "/",
        json={"addressee_id": user_b.id},
        headers=auth_headers(user_a),
    )
    fid = r.json()["id"]
    h_b = auth_headers(user_b)
    await client.patch(f"{BASE}/{fid}/accept", headers=h_b)

    r = await client.patch(f"{BASE}/{fid}/accept", headers=h_b)
    assert r.status_code == 400


# ---------------------------------------------------------
# reject
# ---------------------------------------------------------

async def test_reject_by_addressee_succeeds(
    client: AsyncClient, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()
    r = await client.post(
        BASE + "/",
        json={"addressee_id": user_b.id},
        headers=auth_headers(user_a),
    )
    fid = r.json()["id"]

    r = await client.delete(
        f"{BASE}/{fid}/reject", headers=auth_headers(user_b)
    )
    assert r.status_code == 204

    r = await client.get(
        f"{BASE}/{fid}", headers=auth_headers(user_a)
    )
    assert r.status_code == 404


async def test_reject_by_requester_forbidden(
    client: AsyncClient, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()
    r = await client.post(
        BASE + "/",
        json={"addressee_id": user_b.id},
        headers=auth_headers(user_a),
    )
    fid = r.json()["id"]

    r = await client.delete(
        f"{BASE}/{fid}/reject", headers=auth_headers(user_a)
    )
    assert r.status_code == 403


# ---------------------------------------------------------
# delete_friend
# ---------------------------------------------------------

async def test_delete_friend_by_either_party(
    client: AsyncClient, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()
    r = await client.post(
        BASE + "/",
        json={"addressee_id": user_b.id},
        headers=auth_headers(user_a),
    )
    fid = r.json()["id"]
    await client.patch(f"{BASE}/{fid}/accept", headers=auth_headers(user_b))

    # удаляет addressee
    r = await client.delete(
        f"{BASE}/{fid}", headers=auth_headers(user_b)
    )
    assert r.status_code == 204


async def test_delete_pending_relation_fails(
    client: AsyncClient, make_user, auth_headers
):
    """Удалить друга можно только из accepted, не из pending."""
    user_a = await make_user()
    user_b = await make_user()
    r = await client.post(
        BASE + "/",
        json={"addressee_id": user_b.id},
        headers=auth_headers(user_a),
    )
    fid = r.json()["id"]

    r = await client.delete(
        f"{BASE}/{fid}", headers=auth_headers(user_a)
    )
    assert r.status_code == 400


# ---------------------------------------------------------
# get by id
# ---------------------------------------------------------

async def test_get_by_id_missing_returns_404(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    r = await client.get(
        f"{BASE}/999999", headers=auth_headers(user)
    )
    assert r.status_code == 404


async def test_get_by_id_stranger_forbidden(
    client: AsyncClient, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()
    user_c = await make_user()
    r = await client.post(
        BASE + "/",
        json={"addressee_id": user_b.id},
        headers=auth_headers(user_a),
    )
    fid = r.json()["id"]

    r = await client.get(
        f"{BASE}/{fid}", headers=auth_headers(user_c)
    )
    assert r.status_code == 403


# ---------------------------------------------------------
# lists
# ---------------------------------------------------------

async def test_get_friends_returns_only_accepted(
    client: AsyncClient,
    make_user,
    auth_headers,
    make_friendship,
):
    user_a = await make_user()
    user_b = await make_user()
    user_c = await make_user()

    await make_friendship(requester=user_a, addressee=user_b, status="accepted")
    await make_friendship(requester=user_c, addressee=user_a, status="pending")

    r = await client.get(
        BASE + "/me/friends", headers=auth_headers(user_a)
    )
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 1
    assert rows[0]["status"] == "accepted"


async def test_incoming_requests(
    client: AsyncClient,
    make_user,
    auth_headers,
    make_friendship,
):
    user_a = await make_user()
    user_b = await make_user()
    user_c = await make_user()

    # user_a → user_b (входящая для b)
    await make_friendship(requester=user_a, addressee=user_b, status="pending")
    # user_b → user_c (исходящая для b)
    await make_friendship(requester=user_b, addressee=user_c, status="pending")

    r = await client.get(
        BASE + "/me/requests/incoming", headers=auth_headers(user_b)
    )
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 1
    assert rows[0]["requester_id"] == user_a.id
    assert rows[0]["addressee_id"] == user_b.id


async def test_outgoing_requests(
    client: AsyncClient,
    make_user,
    auth_headers,
    make_friendship,
):
    user_a = await make_user()
    user_b = await make_user()
    user_c = await make_user()

    # user_a → user_b (исходящая для a)
    await make_friendship(requester=user_a, addressee=user_b, status="pending")
    # user_c → user_a (входящая для a)
    await make_friendship(requester=user_c, addressee=user_a, status="pending")

    r = await client.get(
        BASE + "/me/requests/outgoing", headers=auth_headers(user_a)
    )
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 1
    assert rows[0]["requester_id"] == user_a.id
    assert rows[0]["addressee_id"] == user_b.id