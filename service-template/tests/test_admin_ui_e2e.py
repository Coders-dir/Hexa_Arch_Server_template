import pytest
from src.app.auth import create_access_token
from httpx import AsyncClient, ASGITransport
import redis.asyncio as aioredis
from motor.motor_asyncio import AsyncIOMotorClient
import asyncpg


@pytest.mark.asyncio
async def test_admin_ui_e2e_and_datastores():
    # create admin token
    token = create_access_token('e2e-admin', role='admin', minutes=60)
    headers = {'Authorization': f'Bearer {token}'}

    from src.app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        # create API key
        r = await client.post('/api/admin/api-keys', json={'name': 'e2e', 'owner': 'cto'}, headers=headers)
        assert r.status_code == 200
        body = r.json()
        kid = body.get('kid')
        assert kid

        # list and check
        r = await client.get('/api/admin/api-keys', headers=headers)
        assert r.status_code == 200
        found = [k for k in r.json() if k.get('kid') == kid]
        assert len(found) == 1

        # revoke
        r = await client.post(f'/api/admin/api-keys/{kid}/revoke', headers=headers)
        assert r.status_code == 200

        # list again and ensure revoked_at present
        r = await client.get('/api/admin/api-keys', headers=headers)
        assert r.status_code == 200
        found = [k for k in r.json() if k.get('kid') == kid and k.get('revoked_at')]
        assert len(found) == 1

    # Redis check
    r = aioredis.Redis(host='127.0.0.1', port=6379, db=0)
    pong = await r.ping()
    assert pong is True
    await r.set('e2e:test', 'ok')
    v = await r.get('e2e:test')
    assert v.decode() == 'ok'
    await r.aclose()

    # Mongo check
    m = AsyncIOMotorClient('mongodb://127.0.0.1:27017')
    db = m['test_db']
    col = db['e2e_tests']
    res = await col.insert_one({'ok': True})
    doc = await col.find_one({'_id': res.inserted_id})
    assert doc.get('ok') is True
    m.close()

    # Postgres check
    conn = await asyncpg.connect(user='test', password='test', database='test_db', host='127.0.0.1')
    await conn.execute('CREATE TABLE IF NOT EXISTS e2e_test (id serial primary key, v text)')
    rec = await conn.fetchrow("INSERT INTO e2e_test (v) VALUES ($1) RETURNING id,v", 'ok')
    assert rec['v'] == 'ok'
    await conn.close()
