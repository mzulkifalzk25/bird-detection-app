# Bird Detection Application Backend

A Django REST Framework backend for a Flutter-based bird detection and collection application. This application uses AI to identify birds from images and sounds, allowing users to build their collection and track their bird-watching achievements.

## 🌟 Features

### Bird Detection

- Image-based bird identification using Gemini Pro Vision
- Audio-based bird identification using ChatGPT-4 with Whisper
- High-accuracy species recognition
- Detailed bird information and characteristics

### User Management

- Email-based authentication
- Social authentication (Google, Apple)
- OTP verification system
- Profile management
- User preferences

### Collection Management

- Personal bird collection tracking
- Rarity scoring system
- Achievement system
- Streak tracking
- Favorite birds
- Location-based collection data

### Additional Features

- Bird search and filtering
- Location-based bird discovery
- Achievement system
- Social sharing capabilities
- Comprehensive bird database

## 🚀 Technology Stack

### Core

- Python 3.12
- Django 4.2.9
- Django REST Framework 3.14.0
- PostgreSQL (Database)
- Redis (Caching & Queue)

### AI/ML

- Google Gemini Pro Vision
- OpenAI GPT-4 & Whisper
- TensorFlow
- NumPy

### Authentication

- JWT Authentication
- OAuth2
- Social Authentication

### Task Processing

- Celery
- Celery Beat
- Redis Queue

## 📋 Prerequisites

- Python 3.12+
- PostgreSQL
- Redis
- Virtual Environment

## 🛠 Installation

1. Clone the repository:

```bash
git clone https://github.com/mzulkifalzk25/bird-detection-app.git
cd bird-detection-app
```

2. Create and activate virtual environment:

```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Unix or MacOS
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations:

```bash
python manage.py migrate
```

6. Create superuser:

```bash
python manage.py createsuperuser
```

7. Run the development server:

```bash
python manage.py runserver
```

## 🌐 API Endpoints

### Authentication

- `POST /api/v2/auth/login/` - User login
- `POST /api/v2/auth/signup/` - User registration
- `POST /api/v2/auth/verify-otp/` - OTP verification
- `POST /api/v2/auth/social/` - Social authentication

### Bird Detection

- `POST /api/v2/birds/identify/` - Identify bird from image
- `POST /api/v2/birds/identify-sound/` - Identify bird from sound
- `GET /api/v2/birds/` - List all birds
- `GET /api/v2/birds/{id}/` - Get bird details

### Collection

- `GET /api/v2/collection/` - User's collection
- `POST /api/v2/collection/` - Add to collection
- `GET /api/v2/collection/stats/` - Collection statistics
- `GET /api/v2/collection/achievements/` - User achievements

## 🔒 Environment Variables

```plaintext
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
GEMINI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key
```

## 🧪 Testing

Run tests with:

```bash
pytest
```

Generate coverage report:

```bash
coverage run -m pytest
coverage report
```

## 📦 Project Structure

```
bird-detection-app/
├── authentication/     # Authentication app
├── birds/             # Bird detection app
├── collection/        # Collection management app
├── config/           # Project configuration
├── utils/            # Utility functions
└── manage.py
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 👥 Authors

- Muhammad Zulkifal Qayyum -

## 🙏 Acknowledgments

- Bird detection models and APIs
- Django and DRF communities
- Contributors
