from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers import vpn,auth
from core.database import engine, Base
from core.database import get_db_session
from routers.auth import generate_secret_key_for_admin
from utils.banner import rainbow_text, ascii_banner
from core.config import ADMIN_EMAIL

@asynccontextmanager
async def lifespan(app: FastAPI):
    print()
    print(rainbow_text(ascii_banner))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Generate secret key for admin at startup
    async with get_db_session() as session:
        await generate_secret_key_for_admin(ADMIN_EMAIL, session)
    yield

app = FastAPI(lifespan=lifespan)

# Include your VPN router at the /api/vpn path
app.include_router(vpn.router, prefix="/api/vpn", tags=["VPN"])
# Include your VPN router at the /api/auth path
app.include_router(auth.router, prefix="/api/auth", tags=["AUTH"])
@app.get("/")
async def read_root():
    return {"message": "This is the root path of the VPN API"}
