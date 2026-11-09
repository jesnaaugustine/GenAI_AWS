import logging
from typing import Any

import jwt
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError

from app.core.config import get_settings
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


class CognitoJWTVerifier:
    def __init__(self, user_pool_id: str,client_id: str,region: str,):
        self.client_id = client_id
        self.issuer = (
            f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}"
        )
        self.jwks_url = f"{self.issuer}/.well-known/jwks.json"

        self.jwks_client = PyJWKClient(self.jwks_url)

        logger.info("Cognito JWT verifier initialized")

    def verify(self, token: str) -> dict[str, Any]:
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)

            payload = jwt.decode(token,signing_key.key,algorithms=["RS256"],issuer=self.issuer,
                options={
                    "require": [
                        "exp",
                        "iss",
                        "sub",
                        "token_use",
                        "client_id",
                    ]
                },
            )
            if payload.get("token_use") != "access":
                raise AppException(
                    code="INVALID_TOKEN",
                    message="Invalid authentication token",
                    status_code=401,
                )

            if payload.get("client_id") != self.client_id:
                raise AppException(
                    code="INVALID_TOKEN",
                    message="Invalid authentication token",
                    status_code=401,
                )

            return payload

        except AppException:
            raise

        except InvalidTokenError:
            logger.warning("Cognito JWT validation failed")
            raise AppException(
                code="INVALID_TOKEN",
                message="Invalid authentication token",
                status_code=401,
            ) from None

        except Exception:
            logger.exception("Unexpected Cognito JWT verification failure")
            raise AppException(
                code="AUTHENTICATION_FAILED",
                message="Unable to authenticate request",
                status_code=401,
            ) from None