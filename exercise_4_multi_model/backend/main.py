import uvicorn

from app import app
from app.config import config

if __name__ == "__main__":
    print("Starting Multi-Model Chat API...")
    print(f"API will be available at http://{config.API_HOST}:{config.API_PORT}")

    issues = config.validate()
    if issues:
        print("\nConfiguration warnings:")
        for issue in issues:
            print(f"  - {issue}")
        print()

    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT
    )
