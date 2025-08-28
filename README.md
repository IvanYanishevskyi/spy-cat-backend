# Spy Cat Agency API

REST API for managing spy cats, missions, and targets. Built with FastAPI and MySQL.

## Installation

```bash
pip install -r requirements.txt
```

## Database Setup


### Environment Configuration
Create `.env`:
```
SQLALCHEMY_DATABASE_URL=mysql+pymysql://root:password123@localhost:3306/spy_cat_agency
```

## Run

```bash
python main.py
```

API runs on http://localhost:8000

## API Documentation

 http://localhost:8000/docs

## Endpoints

### Spy Cats
- `GET /spy-cats/` - List all cats
- `POST /spy-cats/` - Create cat (validates breed with TheCatAPI)
- `GET /spy-cats/{id}` - Get cat by ID
- `PUT /spy-cats/{id}` - Update cat salary
- `DELETE /spy-cats/{id}` - Delete cat

### Missions
- `GET /missions/` - List all missions
- `POST /missions/` - Create mission with targets
- `GET /missions/{id}` - Get mission by ID
- `DELETE /missions/{id}` - Delete mission (only if unassigned)
- `PUT /missions/{id}/assign/{cat_id}` - Assign mission to cat

### Targets
- `PUT /missions/{id}/targets/{target_id}/notes` - Update target notes
- `PUT /missions/{id}/targets/{target_id}/complete` - Mark target complete

## Business Rules

- One active mission per cat
- Mission must have 1-3 targets
- Cannot edit notes on completed targets/missions
- Cannot delete assigned missions
- Mission auto-completes when all targets complete
- Cat breeds validated against TheCatAPI

## Tech Stack

- FastAPI
- SQLAlchemy ORM
- MySQL database
- Pydantic validation
- PyMySQL driver
- httpx for external API calls

## Project Structure

```
spy-cat-backend/
├── main.py              # FastAPI application
├── db.py               # Database configuration
├── database_models.py   # SQLAlchemy models
├── api_models.py       # Pydantic schemas
├── create_database.py  # DB setup script
├── requirements.txt    # Dependencies
└── .env               # Environment variables
```

## Testing

```bash
python test_examples.py
```

## Requirements

- Python 3.8+
- MySQL 5.7+
- Internet connection (for TheCatAPI validation)
