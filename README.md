# Standards Agents API

A FastAPI-based REST API for querying Safety and Quality Standards Agents.

## API Documentation

FastAPI provides automatic interactive API documentation. Once the server is running, you can access:

- Swagger UI documentation: [http://localhost:8080/docs](http://localhost:8080/docs)
- ReDoc documentation: [http://localhost:8080/redoc](http://localhost:8080/redoc)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint with API information |
| `/health` | GET | Health check endpoint |
| `/safety/ask` | POST | Ask a question to the Safety Standards Agent |
| `/quality/ask` | POST | Ask a question to the Quality Standards Agent |
| `/team/ask` | POST | Ask a question to the Team Agent |

### Request Examples

#### Safety Agent
```json
POST /safety/ask
{
  "query": "What are basic safety protocols?",
  "model_id": "o3-mini"
}
```

#### Quality Agent
```json
POST /quality/ask
{
  "query": "What is quality assurance?",
  "model_id": "o3-mini"
}
```

#### Team Agent
```json
POST /team/ask
{
  "query": "Tell me about safety and quality standards.",
  "model_id": "o3-mini",
  "team_mode": "collaborate"
}
```

## Environment Setup

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (optional for containerized deployment)
- LanceDB cloud account with API key

### Configuration

Create a `.env` file based on the provided `.env.example`:

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file with your LanceDB credentials
nano .env
```

## Local Development

### Virtual Environment Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --port 8080 --loop asyncio
```

### Running Tests

```bash
python test_api.py
```

### Using the Console App

The repository includes a console application for testing the API:

```bash
python api_console.py
```

This interactive console app allows you to:
- Select an agent (Safety, Quality, or Team)
- Choose team modes for the Team Agent
- Ask questions to the selected agent
- View the responses

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start the container
docker compose build
docker compose up -d

# View logs
docker compose logs -f

# Stop the container
docker compose down
```

### Using Docker Directly

```bash
# Build the Docker image
docker build -t standards-api .

# Run the container
docker run -p 8080:8080 --env-file .env standards-api
```

## Troubleshooting

### LanceDB and Uvloop Compatibility

If you encounter errors related to nest_asyncio and uvloop compatibility, use the `--loop asyncio` flag when running uvicorn to use the standard asyncio event loop instead of uvloop:

```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --loop asyncio
```

### API Connection Issues

Make sure your LanceDB credentials in the `.env` file are correct and that you have access to the required tables.

### FTS Index Error

If you see an error with `RemoteTable.create_fts_index()`, this may be related to version compatibility between dependencies. Check your LanceDB version and update if necessary. 