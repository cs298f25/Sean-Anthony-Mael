from dotenv import load_dotenv
import os, requests


def load_data():
    weather_key = os.getenv('WEATHER_API')
    city = 'Bethlehem'
    state = 'PA'
    url = f"http://api.weatherapi.com/v1/current.json?key={weather_key}&q={city},%20{state}"

    response = requests.get(url)
    data = response.json()
    print(data)

if __name__ == "__main__":
    load_dotenv()
    load_data()