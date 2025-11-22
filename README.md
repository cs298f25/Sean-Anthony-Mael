# DevOps Skill Test Simulator

**AUTHORS: Sean Creveling, Anthony Dayoub, Mael Tshiyonga**

## Project Overview

A full-stack web application designed to help developers practice and assess their DevOps skills through interactive quizzes. The platform provides multiple skill test categories covering essential DevOps topics, tracks user performance over time, and offers detailed feedback on quiz results.

## Key Features

- **User Authentication**: Secure registration and login system with password hashing
- **Multiple Skill Test Categories**: 
  - Terminal commands and CLI navigation
  - Python Virtual Environments and Maven workflows
  - AWS deployment strategies and services
  - And more...
- **Interactive Quiz System**: 
  - Start quiz sessions with randomized questions
  - Submit answers and receive immediate feedback
  - View detailed results with correct/incorrect answers breakdown
- **Performance Tracking**:
  - User quiz history and session tracking
  - Score calculation and progress monitoring
  - Question-level statistics
- **Modern Web Interface**: Clean, responsive UI with intuitive navigation

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Deployment**: Gunicorn, AWS EC2 Instance
- **Testing**: pytest

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Sean-Anthony-Mael
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python src/app.py
```

The application will be available at `http://localhost:8000`

### Environment Variables

- `FLASK_KEY`: Secret key for Flask sessions (optional, defaults to dev key for local development)

## Usage

1. **Register/Login**: Create an account or log in with existing credentials
2. **Select Skill Test**: Choose a category from the available skill tests
3. **Take Quiz**: Answer questions one by one, submitting answers as you go
4. **View Results**: After completing the quiz, review your score and see which answers were correct/incorrect
5. **Track Progress**: View your quiz history to monitor improvement over time

## Database Schema

- **users**: User accounts with authentication
- **skill_tests**: Available quiz categories
- **questions**: Questions for each skill test
- **quiz_results**: Quiz session records
- **quiz_result_questions**: Individual question answers within sessions
- **user_skill_stats**: Aggregate performance statistics

## Deployment

<!-- For detailed deployment instructions to AWS EC2 with Gunicorn, see [Deployment Guide](deployment/DEPLOYMENT.md). -->

<!-- **Quick deployment on EC2:**
```bash
# After connecting to EC2 and cloning the repo
bash deployment/setup.sh      # Initial system setup (run once)
bash deployment/deploy.sh     # Deploy application
sudo bash deployment/create-service.sh  # Create systemd service
sudo systemctl start flask-app  # Start the service
``` -->

<!-- ## Development -->

<!-- For development workflows and guidelines, see [Developer Information](developers.md). -->

## Testing

Run tests with:
```bash
pytest tests/
```
