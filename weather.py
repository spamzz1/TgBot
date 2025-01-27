import httpx

from config import weather_key, weather_url


def get_current_weather(KEY, weather_url, CITY_NAME):
    params = {
        'q': CITY_NAME,
        'appid': KEY,
        'units': 'metric'
    }

    response = httpx.get(weather_url, params=params)

    if response.status_code == 200:

        current_weather = response.json()
        current_weather = current_weather['main']['temp']
        return current_weather

    else:
        print(f"{response.status_code}")
        return None


if __name__ == "__main__":
    temp = get_current_weather(KEY=weather_key,
                               weather_url=weather_url,
                               CITY_NAME="Moscow")
    print(temp)
