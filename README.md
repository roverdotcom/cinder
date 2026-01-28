# Cinder API Client

Python async API client wrapper for the Cinder API.

## Features

- Async/await support
- Type-safe request/response models using Pydantic
- Automatic request/response validation
- Authentication handling

## Installation

### From Git Repository

```bash
# Using pip
pip install git+https://github.com/roverdotcom/cinder.git

# Using uv
uv pip install git+https://github.com/roverdotcom/cinder.git
```

### From Local Path (Development)

```bash
# Using pip
pip install -e /path/to/cinder

# Using uv
uv pip install -e /path/to/cinder
```

### In Django

Add to your `requirements.txt`:

```txt
cinder @ git+https://github.com/roverdotcom/cinder.git@master
```

Or with uv in `pyproject.toml`:

```toml
[project]
dependencies = [
    "cinder @ git+https://github.com/roverdotcom/cinder.git",
]
```

## Configuration

### Environment Variables

The client can be configured using environment variables:

```bash
export CINDER_API_BASE_URL="https://rover-staging.cinderapp.com"
export CINDER_API_TOKEN="XXXXXXXXXXXXXX"
```

### Django Settings

Add to settings:

```python
# Cinder API Configuration
CINDER_API_BASE_URL = os.environ.get("CINDER_API_BASE_URL")
CINDER_API_TOKEN = os.environ.get("CINDER_API_TOKEN")
```

## Usage

### Synchronous Usage (Recommended for Django)

```python
from cinder import SyncCinderClient

# Basic usage
with SyncCinderClient(
    base_url="https://rover-staging.cinderapp.com/",
    token="XXXXXXXXX"
) as client:
    # Get graph schema
    schema = client.get_graph_schema()
    print(f"Found {len(schema.entity_schemas)} entity schemas")

    # List decisions
    decisions = client.list_decisions(limit=10)
    print(f"Found {decisions.total} decisions")

    # Get specific decision
    decision = client.get_decision("decision-id")
    print(f"Decision: {decision.id}")
```

### Synchronous with Environment Variables

```python
from cinder import get_sync_client

# Reads from CINDER_API_BASE_URL and CINDER_API_TOKEN env vars
client = get_sync_client()

with client:
    schema = client.get_graph_schema()
    print(schema.model_dump_json(indent=2))
```

### Async Usage

```python
import asyncio
from cinder import CinderClient

async def main():
    async with CinderClient(
        base_url="https://rover-staging.cinderapp.com/",
        token="XXXXXXXXX"
    ) as client:
        # Get graph schema
        schema = await client.get_graph_schema()
        print(f"Found {len(schema.entity_schemas)} entity schemas")

        # List decisions
        decisions = await client.list_decisions(limit=10)
        print(f"Found {decisions.total} decisions")

asyncio.run(main())
```

### Client Methods

#### Reports

- `create_report(report: CreateReportSchema) -> Report`
- `list_reports(limit, offset, **filters) -> PagedReport`

#### Graph Schema

- `get_graph_schema() -> SchemaResponse`

#### Generic

- `request(method: str, path: str, **kwargs) -> httpx.Response`

## Development

### Setup

This covers the `uv` setup, alternatively you can use requirements.txt and
the environment manager of your choice.

```bash
# Clone the repository
git clone https://github.com/roverdotcom/cinder.git
cd cinder

uv sync --frozen
```

### Running Tests

```bash
# Run all tests
make test

# Run with verbose output
make test-verbose

# Run with coverage report
make test-coverage
```

### Regenerating Models

When the OpenAPI spec changes:

```bash
# Update openapi.json with the new spec
# Then regenerate models
make regenerate-models
```

### Generate Requirements File

```bash
# Generate requirements.txt from uv.lock
make requirements
```
