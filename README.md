# Task Management API

A FastAPI-based REST API for managing tasks with user authentication.

## Prerequisites

- Python 3.12+
- PostgreSQL
- pip (Python package installer)

## Installation

### From GitHub

```bash
# Clone the repository
git clone https://github.com/imakashy00/byte_backend.git
cd byte
```
## or
### From zip folder
- Unzip the folder
- ` cd byte `

### Create virtual environment

```bash
python -m venv env
source env/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Setup .env file 
- Set following variables
    - `POSTGRES_DATABASE_URL`
    - `SECRET_KEY`
        - Get SECRET_KEY by running 
            ```bash
            openssl rand -hex 32    
            ```
    - `ALGORITHM` Example: "HS256" 
    - `ACCESS_TOKEN_EXPIRE_MINUTES`  -> Int                          
### Database Setup
```bash
# Initialize Alembic
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Run migrations
alembic upgrade head
```

### Run the project
- Open terminal and run

```bash
fastapi dev
```

### Server will run on [ ` http://127.0.0.1:8000 ` ]

### Change url to [`http://127.0.0.1:8000/docs for swaggerUI api testing `]

## APIs

### User Authentication APIs

1. `POST:/register -> Register the user`

2. `POST:/token -> To get token for logging`

### Task APIs

1. `POST:/tasks -> Adding task to database`

2. `GET:/tasks -> Getting all tasks of the user`

3. `GET:/task/{task_id} -> Getting a particular task`

4. `PUT:/tasks/{task_id} -> To updat title or desc or status of the task`

5. `DELETE:/tasks/{task_id} -> Delete a particular task`


![APIs](/assests/images/api.png)
