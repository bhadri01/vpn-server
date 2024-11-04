from fastapi import APIRouter, Depends, HTTPException
import pyotp
import qrcode
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db_session
from sqlalchemy.future import select
from models.admin import Admin
import colorama
from colorama import Fore, Style
from core.config import ADMIN_EMAIL, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM


security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        if not credentials or credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = credentials.credentials
        payload = verify_token(token)
        return payload
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + \
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


router = APIRouter()


def generate_secret_key() -> str:
    """Generate a new base32 secret key for a user."""
    return pyotp.random_base32()


def get_totp_instance(secret_key: str) -> pyotp.TOTP:
    """Create a TOTP instance using the secret key."""
    return pyotp.TOTP(secret_key)


def generate_otp(secret_key: str) -> str:
    """Generate a dynamic OTP based on the secret key."""
    totp = get_totp_instance(secret_key)
    return totp.now()


def verify_otp(secret_key: str, otp: str) -> bool:
    """Verify if the provided OTP is valid."""
    totp = get_totp_instance(secret_key)
    return totp.verify(otp)


def generate_qr_code_uri(secret_key: str, email: str) -> str:
    """Generate a QR code URI for the user's TOTP setup."""
    totp = pyotp.TOTP(secret_key)
    return totp.provisioning_uri(name=email, issuer_name="VPN")


async def generate_secret_key_for_admin(email: str, session: AsyncSession):
    try:
        # Check if a user already exists
        user = await session.execute(select(Admin).filter(Admin.email == email))
        user = user.scalars().first()
        if user:
            qr = qrcode.QRCode()
            qr.add_data(user.uri)
            qr.make()
            print(
                f"{Fore.YELLOW}{Style.BRIGHT}Scan this QR code using an authenticator app.{Style.RESET_ALL}")
            qr.print_ascii()
            print(f"{Fore.BLUE}{Style.BRIGHT}URI: {user.uri}{Style.RESET_ALL}")
            return {
                "email": user.email,
                "uri": user.uri
            }

        secret_key = generate_secret_key()
        uri = generate_qr_code_uri(secret_key, email)
        user = Admin(email=email, secret_key=secret_key, uri=uri)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=str(e))
    qr = qrcode.QRCode()
    qr.add_data(user.uri)
    qr.make()
    print(f"{Fore.YELLOW}{Style.BRIGHT}Scan this QR code using an authenticator app.{Style.RESET_ALL}")
    qr.print_ascii()
    print(f"{Fore.BLUE}{Style.BRIGHT}URI: {user.uri}{Style.RESET_ALL}")
    return {
        "email": user.email,
        "uri": user.uri
    }

colorama.init(autoreset=True)


class OTPVerificationRequest(BaseModel):
    otp: str


@router.post('/verify-otp')
async def verify(data: OTPVerificationRequest, db_session: AsyncSession = Depends(get_db_session)):
    otp = data.otp

    if not otp:
        raise HTTPException(
            status_code=400, detail="Email and OTP are required")

    async with db_session as session:
        try:
            result = await session.execute(select(Admin).filter(Admin.email == ADMIN_EMAIL))
            user = result.scalars().first()
            if not user:
                raise HTTPException(status_code=400, detail="Invalid email")

            if verify_otp(user.secret_key, otp):
                access_token_expires = timedelta(
                    minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = create_access_token(
                    data={"id": user.id}, expires_delta=access_token_expires
                )
                return {"access_token": access_token, "token_type": "bearer"}
            else:
                raise HTTPException(status_code=400, detail="Invalid OTP!")
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=str(e))
