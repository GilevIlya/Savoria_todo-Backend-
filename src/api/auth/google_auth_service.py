import aiohttp
import jwt
import urllib.parse
from api.auth.config import google_auth_config

class GoogleOAuth():
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, token_url: str, auth_form_base_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token_url = token_url
        self.auth_base_url = auth_form_base_url

    def get_auth_url(self) -> str:
        query_params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': "openid profile email"
        }
        query_string = urllib.parse.urlencode(query_params, quote_via=urllib.parse.quote)
        return f"{self.auth_base_url}?{query_string}"

    async def exchange_code_for_token(self, code: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.token_url,
                data={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'grant_type': 'authorization_code',
                    'redirect_uri': self.redirect_uri,
                    'code': code
                }
            ) as response:
                return await response.json()

    async def parse_id_token(self, id_token: str) -> dict:
        payload = jwt.decode(
            id_token,
            algorithms="RS256",
            options={'verify_signature': False}
        )
        return {
                "email": payload.get("email", ""),
                "firstname": payload.get("given_name", ""),
                "lastname": payload.get("family_name", ""),
                "google_sub": payload.get("sub", ""),
                "profile_pic": payload.get("picture", "")
            }

    

_google_oauth_instance = GoogleOAuth(
    client_id=google_auth_config.CLIENT_ID,
    client_secret=google_auth_config.CLIENT_SECRET,
    redirect_uri=google_auth_config.REDIRECT_URI,
    token_url=google_auth_config.GOOGLE_TOKEN_URL,
    auth_form_base_url=google_auth_config.GOOGLE_AUTH_FORM_BASE_URL
)

def get_google_oauth() -> GoogleOAuth:
    return _google_oauth_instance