import os

ADMIN_EMAIL = "admin@vpnserver.local"
SECRET_KEY = os.urandom(24).hex()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440