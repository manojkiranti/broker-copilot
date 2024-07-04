import httpx
from authlib.jose import jwt

class TokenValidator:
    def __init__(self):
        self.public_keys = None

    def fetch_keys(self):
        url = 'https://login.microsoftonline.com/common/discovery/v2.0/keys'
        try:
            with httpx.Client() as client:
                response = client.get(url)
                response.raise_for_status()
                self.public_keys = response.json()['keys']
        except httpx.HTTPStatusError as e:
            self.public_keys = []
        except Exception as e:
            self.public_keys = []
            raise RuntimeError(f'Failed to fetch keys: {str(e)}')

    def validate_token(self, token):
        if not token:
            raise ValueError('Authorization token is missing')

        if not self.public_keys:
            try:
                self.fetch_keys()
            except Exception as e:
                raise RuntimeError(f'Failed to fetch keys: {str(e)}')

            if not self.public_keys:
                raise RuntimeError('Unable to fetch public keys')

        try:
            decoded_token = jwt.decode(token, self.public_keys, claims_options={
                    'aud': {'essential': True, 'value': '90f18c66-c807-487e-b544-36f30af759be'},
                    'iss': {'essential': True, 'value': 'https://login.microsoftonline.com/common/v2.0'}
                })
            return decoded_token
        except Exception as e:
            raise ValueError(f'JWT validation failed: {str(e)}')
        except Exception as e:
            raise ValueError(f'Unexpected error during token validation: {str(e)}')
