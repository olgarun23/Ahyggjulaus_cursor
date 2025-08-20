from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
import httpx
import re
from typing import Optional
from datetime import datetime, timedelta

app = FastAPI(title="Icelandic SSN Usage API", version="1.0.0")

class SSNRequest(BaseModel):
    kennitala: str
    
    @validator('kennitala')
    def validate_kennitala(cls, v):
        # Icelandic SSN format: DDMMYY-XXXX
        # Where DD is day, MM is month, YY is year, and XXXX is a 4-digit number
        pattern = r'^\d{6}-?\d{4}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid kennitala format. Expected format: DDMMYY-XXXX or DDMMYYXXXX')
        
        # Remove dash if present
        clean_ssn = v.replace('-', '')
        
        # Basic validation for Icelandic SSN
        if len(clean_ssn) != 10:
            raise ValueError('Kennitala must be exactly 10 digits')
        
        # Validate date components
        day = int(clean_ssn[:2])
        month = int(clean_ssn[2:4])
        year = int(clean_ssn[4:6])
        
        # Add century based on the year
        if year > 50:
            full_year = 1900 + year
        else:
            full_year = 2000 + year
        
        try:
            datetime(full_year, month, day)
        except ValueError:
            raise ValueError('Invalid date in kennitala')
        
        return clean_ssn

class SwitchPortResponse(BaseModel):
    switch_number: str
    port_number: str
    success: bool
    message: str

class UsageDataResponse(BaseModel):
    kennitala: str
    switch_number: str
    port_number: str
    usage_data: dict
    timestamp: datetime

@app.get("/")
async def root():
    return {"message": "Icelandic SSN Usage API", "version": "1.0.0"}

@app.post("/get-usage-data", response_model=UsageDataResponse)
async def get_usage_data(request: SSNRequest):
    """
    Get usage data for a person based on their Icelandic SSN (kennitala).
    
    This endpoint:
    1. Validates the Icelandic SSN
    2. Calls an external API to get switch and port numbers
    3. Queries monitor01.gagnaveita.is for usage data
    """
    try:
        # Step 1: Get switch and port numbers from external API
        # TODO: Replace with actual API endpoint when provided
        switch_port_data = await get_switch_port_data(request.kennitala)
        
        if not switch_port_data['success']:
            raise HTTPException(status_code=404, detail=switch_port_data['message'])
        
        # Step 2: Query monitoring system for usage data
        usage_data = await get_monitoring_data(
            switch_port_data['switch_number'],
            switch_port_data['port_number']
        )
        
        return UsageDataResponse(
            kennitala=request.kennitala,
            switch_number=switch_port_data['switch_number'],
            port_number=switch_port_data['port_number'],
            usage_data=usage_data,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

async def get_switch_port_data(kennitala: str) -> dict:
    """
    Get switch number and port number from external API based on kennitala.
    
    TODO: Replace the placeholder with actual API endpoint when provided.
    """
    # Placeholder implementation - replace with actual API call
    # Example structure:
    # async with httpx.AsyncClient() as client:
    #     response = await client.get(f"https://your-api-endpoint.com/switch-port/{kennitala}")
    #     if response.status_code == 200:
    #         data = response.json()
    #         return {
    #             "switch_number": data["switch_number"],
    #             "port_number": data["port_number"],
    #             "success": True,
    #             "message": "Success"
    #         }
    
    # For now, return mock data for testing
    return {
        "switch_number": "SW001",
        "port_number": "P001",
        "success": True,
        "message": "Success"
    }

async def get_monitoring_data(switch_number: str, port_number: str) -> dict:
    """
    Query monitor01.gagnaveita.is:9090/api/v1/query_range for usage data.
    """
    try:
        # Calculate time range (last 24 hours)
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        # Convert to Unix timestamp (seconds since epoch)
        start_ts = int(start_time.timestamp())
        end_ts = int(end_time.timestamp())
        
        # Construct query for the monitoring system
        # Adjust the query based on your specific monitoring system's format
        query = f'switch_number="{switch_number}",port_number="{port_number}"'
        
        params = {
            'query': query,
            'start': start_ts,
            'end': end_ts,
            'step': '1h'  # 1-hour intervals
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                'http://monitor01.gagnaveita.is:9090/api/v1/query_range',
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "data": data,
                    "query": query,
                    "time_range": {
                        "start": start_time.isoformat(),
                        "end": end_time.isoformat()
                    }
                }
            else:
                return {
                    "status": "error",
                    "error": f"Monitoring API returned status {response.status_code}",
                    "response": response.text
                }
                
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to query monitoring system: {str(e)}"
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

