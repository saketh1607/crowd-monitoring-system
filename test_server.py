"""
Simple test server to verify FastAPI setup
"""
from fastapi import FastAPI

app = FastAPI(title="Emergency Management Test Server")

@app.get("/")
async def root():
    return {"message": "Emergency Management System Test Server", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
