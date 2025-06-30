import uvicorn

# Entrypoint for starting the FastAPI server
if __name__ == "__main__":
    # Reference app object from src/api/main.py
    from src.api.main import app

    # Start the server at 0.0.0.0 for container deployments, port defaults to 8000
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
