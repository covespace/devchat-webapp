from typing import List
import json

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class JWK(BaseModel):
    kty: str
    e: str
    use: str
    kid: str
    alg: str
    n: str


class JWKS(BaseModel):
    keys: List[JWK]


# TODO: Replace this with your actual JWKS.
jwks = JWKS(keys=[JWK(
    kty="RSA",
    e="AQAB",
    use="sig",
    kid="1234",
    alg="RS256",
    n="your_actual_n_value"
)])


@router.get("/.well-known/jwks.json")
async def read_jwks():
    return json.loads(jwks.json())
