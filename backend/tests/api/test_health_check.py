from httpx import AsyncClient


async def test_health_route_success(client: AsyncClient) -> None:
    response = await client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'healthy', 'version': '1.0.0'}
