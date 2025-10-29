from dotenv import load_dotenv
import os, requests

weather_key = os.getenv('WEATHER_API')
city = 'Bethlehem'
state = 'PA'
url = f"http://api.weatherapi.com/v1/current.json?key={weather_key}&q={city},%20{state}"

def load_data():
    response = requests.get(url)
    data = response.json()
    condition = data['current']['condition']['text']
    temp = data['current']['temp_f']
    feels_temp = data['current']['feelslike_f']
    last_updated = data['current']['last_updated']
    location = data['location']['name'] + ", " + data['location']['region'] + ", " + data['location']['country']
    print(f"Location: {location}\nCondition: {condition}\nCurrent Temp: {temp}\nFeels like {feels_temp} degrees\nLast Updated: {last_updated}")


if __name__ == "__main__":
    load_dotenv()
    load_data()