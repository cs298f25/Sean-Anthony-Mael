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

5. Run the application outside of the REPL:
```bash
python src/app.py
```
6. The application will be up and running at `http://localhost:8000` in your web browser.

# EC2 Deployment Guide - Gunicorn on Ubuntu AWS EC2

Simple guide to deploy the DevOps Skill Test Simulator to an Ubuntu AWS EC2 instance using Gunicorn.

## Prerequisites

- AWS account with EC2 access
- SSH key pair (.pem file)
- Git repository access

## Step 1: Launch EC2 Instance

1. Go to **AWS Console** → **EC2** → **Launch Instance**

2. Configure:
   - **AMI:** Ubuntu 22.04 LTS
   - **Instance Type:** t2.micro or t3.micro
   - **Key Pair:** Select or create a key pair (save the .pem file)
   - **Security Group:** Add rule for **Custom TCP port 8000** from **0.0.0.0/0**
   - **Storage:** Default 8GB

3. Click **Launch Instance**

4. Note your instance's **Public IP** address

## Step 2: Connect to EC2

```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

## Step 3: Initial Setup & Deploy Application via Gunicorn

Run the setup script to install dependencies:

```bash
cd ~
git clone YOUR_REPO_URL
cd Sean-Anthony-Mael
bash deployment/deploy.sh
```






This will:
- Create Python virtual environment
- Install dependencies
- Create `.env` file with Flask secret key
- Test the application



Your app is now running! Visit `http://YOUR_EC2_PUBLIC_IP:8000` in your browser.


## Troubleshooting

**Can't connect?**
- Check Security Group allows port 8000
- Verify app is running: `ps aux | grep gunicorn`


**Permission errors?**
```bash
sudo chown -R ubuntu:ubuntu ~/Sean-Anthony-Mael
```
