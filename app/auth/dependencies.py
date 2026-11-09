import logging
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.cognito import CognitoJWTVerifier
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthenticatedPrincipal:
    cognito_sub: str


def get_cognito_verifier(request: Request) -> CognitoJWTVerifier:
    return request.app.state.cognito_verifier


async def get_current_principal(
    credentials: Annotated[HTTPAuthorizationCredentials | None,Depends(bearer_scheme)],
    verifier: Annotated[CognitoJWTVerifier, Depends(get_cognito_verifier)]
    ) -> AuthenticatedPrincipal:


    if credentials is None:
        raise AppException(
            code="AUTHENTICATION_REQUIRED",
            message="Authentication required",
            status_code=401,
        )

    if credentials.scheme.lower() != "bearer":
        raise AppException(
            code="INVALID_AUTHENTICATION_SCHEME",
            message="Invalid authentication scheme",
            status_code=401,
        )

    payload = verifier.verify(credentials.credentials)
    cognito_sub = payload.get("sub")

    if not cognito_sub:
        logger.warning("Authenticated token missing subject")
        raise AppException(
            code="INVALID_TOKEN",
            message="Invalid authentication token",
            status_code=401,
        )
    print("before return in get_current_principal")
    return AuthenticatedPrincipal(
        cognito_sub=cognito_sub
    )

principalDep = Annotated[AuthenticatedPrincipal, Depends(get_current_principal)]