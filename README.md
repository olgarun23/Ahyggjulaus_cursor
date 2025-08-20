# Icelandic SSN Usage API

This API processes Icelandic Social Security Numbers (kennitala) and retrieves usage data by querying external systems.

## Features

- **Icelandic SSN Validation**: Validates kennitala format and date components
- **External API Integration**: Retrieves switch and port numbers from external systems
- **Monitoring Data Query**: Queries api for usage statistics
- **RESTful API**: Built with FastAPI for modern, async performance

## Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Ahyggjulaus_cursor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the API:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### GET /
Health check and API information.

**Response:**
```json
{
  "message": "Icelandic SSN Usage API",
  "version": "1.0.0"
}
```

### POST /get-usage-data
Get usage data for a person based on their Icelandic SSN.

**Request Body:**
```json
{
  "kennitala": "010190-1234"
}
```

**Response:**
```json
{
  "kennitala": "0101901234",
  "switch_number": "SW001",
  "port_number": "P001",
  "usage_data": {
    "status": "success",
    "data": {...},
    "query": "switch_number=\"SW001\",port_number=\"P001\"",
    "time_range": {
      "start": "2024-01-01T00:00:00",
      "end": "2024-01-02T00:00:00"
    }
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

## Icelandic SSN (Kennitala) Format

The API accepts Icelandic SSNs in the following formats:
- `DDMMYY-XXXX` (with dash)
- `DDMMYYXXXX` (without dash)

Where:
- `DD` = Day (01-31)
- `MM` = Month (01-12)
- `YY` = Year (last two digits)
- `XXXX` = 4-digit number

### Validation Rules

1. Must be exactly 10 digits (excluding optional dash)
2. Date components must form a valid date
3. Century is determined by the year:
   - Years 00-50: 2000s (2000-2050)
   - Years 51-99: 1900s (1951-1999)

## Configuration

### External API Integration

The `get_switch_port_data()` function in `main.py` needs to be updated with your actual API endpoint. Currently, it returns mock data for testing.

Replace the placeholder implementation with your actual API call:

```python
async def get_switch_port_data(kennitala: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://your-api-endpoint.com/switch-port/{kennitala}")
        if response.status_code == 200:
            data = response.json()
            return {
                "switch_number": data["switch_number"],
                "port_number": data["port_number"],
                "success": True,
                "message": "Success"
            }
```

### Monitoring System Query

The monitoring query in `get_monitoring_data()` function can be customized based on your specific monitoring system's query format. Currently, it uses:

```python
query = f'switch_number="{switch_number}",port_number="{port_number}"'
```

Adjust this query format according to your monitoring system's requirements.

## Development

### Running in Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation

Once the server is running, you can access:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc

## Error Handling

The API includes comprehensive error handling for:
- Invalid kennitala format
- Invalid date components
- External API failures
- Monitoring system connection issues

## Testing

You can test the API using curl:

```bash
# Test with valid kennitala
curl -X POST "http://localhost:8000/get-usage-data" \
     -H "Content-Type: application/json" \
     -d '{"kennitala": "010190-1234"}'

# Test health endpoint
curl "http://localhost:8000/health"
```

## TODO

- [ ] Replace placeholder external API with actual endpoint
- [ ] Add authentication/authorization
- [ ] Add rate limiting
- [ ] Add logging
- [ ] Add unit tests
- [ ] Add Docker support
- [ ] Configure monitoring query format based on actual system

