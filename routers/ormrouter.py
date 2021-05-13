from fastapi import APIRouter

ormrouter = APIRouter()
ormrouter.__name__ = "ORM app!"
yo = 10
### PAMIĘTAĆ W HEROKU DAĆ APLIKACJE I DAĆ DAM NA KOŃCU COŚ
# SQLALCHEMY_DATABASE_URL="postgresql://postgres:DaftAcademy@127.0.0.1:5555/postgres" uvicorn app.main:app --host=0.0.0.0 --port=${PORT:-5000}
