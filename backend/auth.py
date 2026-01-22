from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import jwt
import requests

AUTH0_DOMAIN = "";
AUTH0_CLIENT_ID = "";
API_AUDIENCE = ""
ALGORITHMS = ["RS256"]

security = HTTPBearer()

jwks = requests.get(
    f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
).json()

def verify_token(token=Depends(security)):
    try:
        unverified_header = jwt.get_unverified_header(token.credentials)

        rsa_key = next(
            (
                {
                    "kty": k["kty"],
                    "kid": k["kid"],
                    "use": k["use"],
                    "n": k["n"],
                    "e": k["e"],
                }
                for k in jwks["keys"]
                if k["kid"] == unverified_header["kid"]
            ),
            None,
        )

        if rsa_key is None:
            raise HTTPException(status_code=401)

        payload = jwt.decode(
            token.credentials,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )

        return payload

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
