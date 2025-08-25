from fastapi.testclient import TestClient
from src.app.main import app
from src.app.auth import create_access_token


client = TestClient(app)


def test_create_list_revoke_key():
    token = create_access_token('test-admin', role='admin', minutes=60)
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/api/admin/api-keys", json={"name": "test", "owner": "quant"}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data and "kid" in data
    kid = data["kid"]

    resp2 = client.get("/api/admin/api-keys", headers=headers)
    assert resp2.status_code == 200
    keys = resp2.json()
    assert any(k["kid"] == kid for k in keys)

    resp3 = client.post(f"/api/admin/api-keys/{kid}/revoke", headers=headers)
    assert resp3.status_code == 200
    assert resp3.json()["status"] == "revoked"
