import aiohttp
import json

async def get_food_info(food_name):
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": "af9ed57e",
        "x-app-key": "bc4bbfbb81351dfbde8884f8ddf9c859",
        "Content-Type": "application/json"
    }

    payload = {"query": food_name}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=json.dumps(payload)) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                return {"error": "Не удалось получить данные о продукте"}

