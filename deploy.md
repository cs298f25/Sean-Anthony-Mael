# Deploy Processes

We will be using AWS to deploy our project onto a server and will also be deploying locally to our machine. We are going to implement a CI/CD pipeline (on manual trigger) to make a clean, easy, and efficient integration and deployment processes to our project while it's running so we do not have to tear it down for each update.

# Local Deployment
### React
1. Go to the [WeatherAPI](https://www.weatherapi.com/) website and create an API key by creating an account.
2. Insert that API key into a file named `.env` that is located in the root directory of the project with the following format:\
`WEATHER_API={insert API key}`
3. In a terminal window or in your designated IDE terminal, activate a virtual environment with the following commands in order:
- `python3 -m venv .venv`
- `source .venv/bin/activate`
- `pip install -r requirements.txt`
- `python src/app.py`

4. In a separate terminal window located in the [/frontend](/frontend/) directory, run:\
 `npm install -D @vitejs/plugin-react`
5. In the same terminal window as step 4, run:\
`npm run dev`
6. Put the link that is shown in the terminal window into a web browser to display the web page.