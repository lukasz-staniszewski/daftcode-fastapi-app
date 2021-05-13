from fastapi import APIRouter, Depends, HTTPException
from dblib.database import get_db
from dblib import crud, schemas
from typing import List
from pydantic import PositiveInt
from sqlalchemy.orm import Session


ormrouter = APIRouter()
ormrouter.__name__ = "ORM app!"


@ormrouter.get("/shippers/{shipper_id}", response_model=schemas.Shipper)
async def get_shipper(shipper_id: PositiveInt, db: Session = Depends(get_db)):
    db_shipper = crud.get_shipper(db, shipper_id)
    if db_shipper is None:
        raise HTTPException(status_code=404, detail="Shipper not found")
    return db_shipper


@ormrouter.get("/shippers", response_model=List[schemas.Shipper])
async def get_shippers(db: Session = Depends(get_db)):
    return crud.get_shippers(db)
