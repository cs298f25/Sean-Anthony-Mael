# Deploy Processes

We will be using AWS to deploy our project onto a server and will also be deploying locally to our machine. We are going to implement a CI/CD pipeline (on manual trigger) to make a clean, easy, and efficient integration and deployment processes to our project while it's running so we do not have to tear it down for each update.

# Local Deployment
### React
1. Go to the [WeatherAPI](https://www.weatherapi.com/) website and create an API key by creating an account.

2. Insert that API key into a file named `.env` that is located in the root directory of the project with the following format:\
`WEATHER_API={insert API key}`

3. Go to the [Google Cloud Console](https://console.cloud.google.com) website and create an API key by creating an account.

4. Insert the API key within the same `.env` file as the Weather API key in the following format on the next line:\
`GOOGLE_MAPS_KEY={insert API key}`

5. Go to the [Last.fm](https://www.last.fm/api/account/create) website and create an account to receive an API key.

6. Insert the API key within the same `.env` file as the previous APIs in the following format on the next line:\
`MUSIC_KEY={insert API key}`

7. Go to the [OpenRouter](https://openrouter.ai/) website and create an account to receive an API key.

8. Insert the API key within the same `.env` file in the following format in the next line:\
`OPEN_AI_API={insert API key}`

9. In a terminal window or in your designated IDE terminal, activate a virtual environment with the following commands in order:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/app.py
```

10. In the same terminal window, run `python3`, and then input the following commands in order:
```bash
import secrets
secrets.token_hex(32)
```
   Add the long string into your .env file located in your root directory with the following format:\
   `FLASK_KEY={insert secrets key}`

11. In a separate terminal window located in the [/frontend](/frontend/) directory, run:
```bash
npm install -D @vitejs/plugin-react
 ```

12. In the same terminal window as step 4, run:
```bash
npm run dev
```

13. Put the link that is shown in the terminal window into a web browser to display the web page.

# EC2 Deployment Guide

## Step 1: Launch EC2 Instance

1. Go to AWS Console → EC2 → **Launch Instance**
2. Choose **Ubuntu 22.04 LTS** (free tier: t2.micro or t3.micro)
3. **Important:** When configuring Security Group, add these rules:
   - **SSH** (port 22) from **My IP**
   - **Custom TCP** (port 8000) from **Anywhere (0.0.0.0/0)**
      - This must be configured in **Security Groups** on left-hand side of EC2 Dashboard
      - Match up the security group being used for your EC2 IP and configure these edits
4. Select or create a key pair for SSH
5. Click **Launch Instance**

## Step 2: Connect to Your Instance

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip-address
```

Replace:
- `your-key.pem` with your actual key file path
- `your-ec2-ip-address` with your EC2 public IP

## Step 3: Upload Your Project

**Option A: Using Git (if your code is on GitHub)**
```bash
cd ~
git clone https://github.com/yourusername/your-repo.git
cd your-repo-name
```

**Option B: Using SCP (from your local machine)**
On your **local machine**, run:
```bash
scp -i your-key.pem -r /path/to/your/project ubuntu@your-ec2-ip:~/
```

Then on EC2:
```bash
cd ~/project-folder-name
```

## Step 4: Setup Environment Variables

```bash
nano .env
```

Add the following environment variables:

```
WEATHER_API=your_weather_api_key_here
GOOGLE_MAPS_KEY=your_google_maps_key_here
OPEN_AI_API=your_openrouter_api_key_here
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free
MUSIC_KEY=your_last_fm_music_api_key_here
FLASK_KEY=your_secret_key_here
```

**Important:** For `FLASK_KEY`, generate a secure random key. You can do this on your local machine or on EC2:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and use it as your `FLASK_KEY` value. This is required for Flask sessions (used by the chat feature).

Save: Press `Ctrl + o`, then press Enter and then press 'Ctrl + x'

## Step 5: Run the Deployment Script

**This automates everything!** Just run:

```bash
sh ec2-deploy.sh
```

This script will:
- Check for .env file and verify required environment variables
- Install Python and Node.js (if needed)
- Setup virtual environment
- Install all dependencies
- Initialize the database (creates tables and populates initial data)
- Build the frontend

## Step 6: Run the App

After the deployment script completes, start the app:

```bash
sh run-app.sh
```

Or manually:
```bash
source .venv/bin/activate
python3 src/app.py
```

You should see something like:
```
 * Running on http://0.0.0.0:8000
```

**Keep this terminal open!** The app is now running.

## Step 7: Access in Browser

Open your browser and go to:
```
http://your-ec2-ip-address:8000
```

Replace `your-ec2-ip-address` with your actual EC2 public IP.

## That's It! 🎉

Your app should now be accessible in your browser.

---

## Troubleshooting

**Can't connect?**
- Check Security Group has port 8000 open (Step 1)
- Make sure the app is still running in your terminal
- Try accessing `http://your-ec2-ip:8000` (with the port number)

**App crashes?**
- Check the terminal for error messages
- Make sure `.env` file has all required API keys (including `FLASK_KEY`)
- Make sure frontend is built: `ls frontend/dist` should show files
- Check that database was initialized: `ls database/app.db` should show the database file
- If database issues occur, you can reinitialize: `python3 init_db.py`

**Database issues?**
- The database is automatically initialized when the app starts, but you can also run `python3 init_db.py` manually
- The database file is located at `database/app.db`
- If you need to reset the database, delete `database/app.db` and restart the app (it will recreate it)