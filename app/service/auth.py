import aiohttp
from urllib.parse import urlencode
import jwt
from jwt import PyJWKClient
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.core.config import settings
from app.core.error import ExternalAuthError
from app.core.security import create_token_pair
from app.schema.auth import LoginOut, AuthUserSchema


class AuthService:
    def __init__(self, repo):
        self.repo = repo

    @staticmethod
    def get_google_auth_url() -> str:
        params = {
            "client_id": settings.google.client_id,
            "redirect_uri": settings.google.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "select_account",
        }
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        return f"{base_url}?{urlencode(params)}"

    async def authenticate_google(self, code: str) -> LoginOut:
        google_data = await self._fetch_google_user(code)

        user = await self.repo.get_by_google_id(google_data.sub)
        if not user:
            user = await self.repo.get_by_email(google_data.email)
            if user:
                user.google_id = google_data.sub
                user = await self.repo.save_user(user)
            else:
                user = await self.repo.create_via_google(google_data)

        return create_token_pair(str(user.id))

    @staticmethod
    async def _fetch_google_user(code: str) -> AuthUserSchema:
        async with aiohttp.ClientSession() as session:
            payload = {
                "client_id": settings.google.client_id,
                "client_secret": settings.google.client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.google.redirect_uri,
            }
            async with session.post(settings.google.token_url, data=payload) as resp:
                if resp.status != 200:
                    raise ExternalAuthError()
                tokens = await resp.json()

        id_token_raw = tokens.get("id_token")
        if not id_token_raw:
            raise ExternalAuthError()

        request_adapter = google_requests.Request()
        id_info = id_token.verify_oauth2_token(
            id_token_raw,
            request_adapter,
            settings.google.client_id,
        )

        if id_info.get("iss") not in (
            "accounts.google.com",
            "https://accounts.google.com",
        ):
            raise ExternalAuthError()

        return AuthUserSchema(
            email=id_info["email"],
            sub=id_info["sub"],
            email_verified=id_info.get("email_verified", False),
        )

    @staticmethod
    def get_yandex_auth_url() -> str:
        params = {
            "response_type": "code",
            "client_id": settings.yandex.client_id,
            "redirect_uri": settings.yandex.redirect_uri,
        }
        base_url = "https://oauth.yandex.com/authorize"
        return f"{base_url}?{urlencode(params)}"

    async def authenticate_yandex(self, code: str) -> LoginOut:
        async with aiohttp.ClientSession() as session:
            payload = {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": settings.yandex.client_id,
                "client_secret": settings.yandex.client_secret,
            }
            async with session.post(settings.yandex.token_url, data=payload) as resp:
                if resp.status != 200:
                    raise ExternalAuthError()
                tokens = await resp.json()

        id_token_raw = tokens.get("id_token")
        if not id_token_raw:
            raise ExternalAuthError()

        jwks_url = "https://login.yandex.ru/.well-known/jwks.json"
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(id_token_raw).key

        try:
            id_info = jwt.decode(
                id_token_raw,
                signing_key,
                algorithms=["RS256"],
                audience=settings.yandex.client_id
            )
        except jwt.PyJWTError:
            raise ExternalAuthError()

        yandex_user_data = AuthUserSchema(
            email=id_info["email"],
            sub=id_info["sub"],
            email_verified=id_info.get("email_verified", True)
        )

        user = await self.repo.get_by_yandex_id(yandex_user_data.sub)
        if not user:
            user = await self.repo.get_by_email(yandex_user_data.email)
            if user:
                user.yandex_id = yandex_user_data.sub
                user = await self.repo.save_user(user)
            else:
                user = await self.repo.create_via_yandex(yandex_user_data)

        return create_token_pair(str(user.id))
