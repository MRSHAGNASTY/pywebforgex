import os
from .server import create_app

def main():
    app = create_app()
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    app.logger.info("PyWebForge ΩX starting on %s:%s", host, port)
    app.run(host=host, port=port, debug=True)

if __name__ == "__main__":
    main()
