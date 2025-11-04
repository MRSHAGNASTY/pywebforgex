
from __future__ import annotations
import jwt
from jwt import PyJWKClient

def validate_bearer(token: str, issuer: str|None, audience: str|None, jwks_url: str|None):
    if not token or not jwks_url or not issuer:
        return {}
    try:
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        data = jwt.decode(token, signing_key.key, algorithms=["RS256"], audience=audience, issuer=issuer)
        return data
    except Exception:
        return {}
