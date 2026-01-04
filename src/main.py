import os
from .server import app

import uvicorn

def main():
    host = os.getenv("HOST", "localhost")  # ✅ Uses env var
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()