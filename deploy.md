# Deploy Processes

We will be using AWS to deploy our project onto a server and will also be deploying locally to our machine. We are going to implement a CI/CD pipeline (on manual trigger) to make a clean, easy, and efficient integration and deployment processes to our project while it's running so we do not have to tear it down for each update.

# Local Deployment

1. Clone the repository:
```bash
git clone <repository-url>
cd Sean-Anthony-Mael
```

2. Create and activate the virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

(*Optional*)
4. In a terminal window with the virtual environment active:
```bash
python3
import secrets
secrets.token_hex(32)
```
Put the following key inside a file called .env located in the root directory of your project
with the following name:
`FLASK_KEY=<insert key>`

5. Run the application outside of the REP:
```bash
python src/app.py
```
6. The application will be up and running at `http://localhost:8000` in your web browser.

# EC2 Deployment Guide

## Step 1: Launch EC2 Instance

1. Go to AWS Console → EC2 → **Launch Instance**
2. Choose **Ubuntu 22.04 LTS** (free tier: t2.micro or t3.micro)
3. **Important:** When configuring Security Group, add these rules:
   - **SSH** (port 22) from **My IP**
   - **HTTP** (port 80) from **the internet**
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
FLASK_KEY=<your_secret_key_here>
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

**App crashes?**
- Check the terminal for error messages
- Make sure the `.env` file has the optional but highly recommended `FLASK_KEY`
- Make sure frontend is built: `ls frontend/dist` should show files
- Check that database was initialized: `ls database/app.db` should show the database file
- If database issues occur, you can reinitialize: `python3 init_db.py`

**Database issues?**
- The database is automatically initialized when the app starts, but you can also run `python3 init_db.py` manually
- The database file is located at `database/app.db`
- If you need to reset the database, delete `database/app.db` and restart the app (it will recreate it)