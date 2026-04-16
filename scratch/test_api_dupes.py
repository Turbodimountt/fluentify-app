
import httpx
import asyncio

async def test_api():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/users/professional-contexts")
            if response.status_code == 200:
                data = response.json()
                print(f"Items returned: {len(data)}")
                for item in data:
                    print(f"- {item.get('name')} ({item.get('slug')})")
            else:
                print(f"Error: {response.status_code}")
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())
