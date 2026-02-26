import aiohttp
import urllib.parse
from app.core.config import settings
from app.core.error import ExternalAuthError
from app.core.security import create_token_pair
from app.schema.auth import GoogleUserSchema, LoginOut


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
            "prompt": "select_account"
        }
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

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
    async def _fetch_google_user(code: str) -> GoogleUserSchema:
        async with aiohttp.ClientSession() as session:
            token_payload = {
                "client_id": settings.google.client_id,
                "client_secret": settings.google.client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.google.redirect_uri,
            }

            async with session.post(settings.google.token_url, data=token_payload) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    print(f"[Google Auth Error] Token Exchange: {resp.status} - {error_text}")
                    raise ExternalAuthError()

                tokens = await resp.json()

            headers = {"Authorization": f"Bearer {tokens['access_token']}"}
            async with session.get(settings.google.userinfo_url, headers=headers) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    print(f"[Google Auth Error] User Info: {resp.status} - {error_text}")
                    raise ExternalAuthError()

                user_info = await resp.json()

            return GoogleUserSchema(
                email=user_info.get("email"),
                sub=str(user_info.get("id") or user_info.get("sub")),
                email_verified=user_info.get("verified_email") or user_info.get("email_verified", False)
            )
