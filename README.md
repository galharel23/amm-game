# AMM Game

Automated Market Maker (AMM) simulation game with React frontend and FastAPI backend.

## Project Structure

```
amm-game/
├── api/                    # Backend API
│   ├── app/               # FastAPI application
│   ├── migrations/        # Database migrations
│   ├── scripts/           # Utility scripts
│   ├── venv/             # Python virtual environment
│   ├── alembic.ini       # Alembic configuration
│   ├── docker-compose.yml # Docker services
│   ├── requirements.txt  # Python dependencies
│   ├── reset_db.py       # Database reset script
│   └── .env              # Environment variables
│
├── amm-game-frontend/     # React frontend
│   └── src/              # Source files
│
├── .gitignore            # Git ignore rules (Python + Node)
└── README.md             # This file
```

## Running the Application

### 1. Start Docker Services

**Terminal: docker**
```bash
cd api
docker-compose up -d
```

This starts:
- PostgreSQL on port 5433
- pgAdmin on port 5050

### 2. Start Backend API

**Terminal: backend**
```bash
cd api
venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

API Documentation: http://localhost:8000/docs

### 3. Start Frontend

**Terminal: frontend**
```bash
cd amm-game-frontend
npm install
npm run dev
```

Frontend will be available at: http://localhost:5173

## Database Management

### Check Current Migration Status
```bash
cd api
venv\Scripts\Activate.ps1
alembic current
```

### View Migration History
```bash
cd api
venv\Scripts\Activate.ps1
alembic history
```

### Reset Database
```bash
cd api
venv\Scripts\Activate.ps1
python reset_db.py
```

### Run Migrations
```bash
cd api
venv\Scripts\Activate.ps1
alembic upgrade head
```

### Create New Migration (Auto-generate from models)
```bash
cd api
venv\Scripts\Activate.ps1
alembic revision --autogenerate -m "description of changes"
```

### Create Empty Migration (Manual)
```bash
cd api
venv\Scripts\Activate.ps1
alembic revision -m "description"
```

### Downgrade Migration (Rollback one version)
```bash
cd api
venv\Scripts\Activate.ps1
alembic downgrade -1
```

### Migration Workflow
1. **Make changes** to models in `api/app/models/`
2. **Generate migration**: `alembic revision --autogenerate -m "add new field"`
3. **Review migration** file in `api/migrations/versions/`
4. **Apply migration**: `alembic upgrade head`
5. **Test** your changes
6. If needed, **rollback**: `alembic downgrade -1`

## Environment Variables

Create `.env` file in the `api/` directory:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/amm_db
DATABASE_HOST=localhost
DATABASE_PORT=5433
DATABASE_NAME=amm_db
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
```

## Access Points

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- pgAdmin: http://localhost:5050
  - Email: galharel23@gmail.com
  - Password: 0545707588

## Development

**Note:** If you see an old `api/.venv` folder, you can safely delete it manually. The project now uses `api/venv/`.

### Backend Development
```bash
cd api
venv\Scripts\Activate.ps1
# Make changes to Python files
# uvicorn will auto-reload
```

### Frontend Development
```bash
cd amm-game-frontend
# Make changes to TypeScript/React files
# Vite will auto-reload
```
