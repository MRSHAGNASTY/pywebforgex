from app.server import create_app

def test_health():
    app = create_app()
    client = app.test_client()
    r = client.get("/health")
    assert r.json["status"] == "ok"
