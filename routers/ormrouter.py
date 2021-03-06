from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from dblib.database import get_db
from dblib import crud, schemas, models
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


@ormrouter.get("/suppliers", response_model=List[schemas.Supplier])
async def get_suppliers(response: Response, db: Session = Depends(get_db)):
    response.status_code = status.HTTP_200_OK
    return crud.get_suppliers(db)


@ormrouter.get("/suppliers/{supplier_id}", response_model=schemas.SupplierFull)
async def get_supplier(
    response: Response, supplier_id: PositiveInt, db: Session = Depends(get_db)
):
    db_supplier = crud.get_supplier(db, supplier_id)
    if db_supplier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found"
        )
    response.status_code = status.HTTP_200_OK
    return db_supplier


@ormrouter.get("/suppliers/{supplier_id}/products")
async def get_supplier_product(
    response: Response, supplier_id: PositiveInt, db: Session = Depends(get_db)
):
    db_supplier = crud.get_supplier(db, supplier_id)
    if db_supplier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found"
        )
    db_supp_prod = crud.get_suppliers_product(db, supplier_id)
    response.status_code = status.HTTP_200_OK
    db_supp_prod = [
        {
            "ProductID": row.ProductID,
            "ProductName": row.ProductName,
            "Category": {
                "CategoryID": row.CategoryID,
                "CategoryName": row.CategoryName,
            },
            "Discontinued": row.Discontinued,
        }
        for row in db_supp_prod
    ]
    return db_supp_prod


@ormrouter.put("/suppliers/{supplier_id}", response_model=schemas.SupplierFull)
async def put_suppliers(
    request: Request,
    response: Response,
    supplier_id: PositiveInt,
    inp_changes: schemas.SuppliersInputOptional,
    db: Session = Depends(get_db),
):
    db_supplier = crud.get_supplier(db, supplier_id)
    if db_supplier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found"
        )
    crud.put_suppliers(db, supplier_id, inp_changes)
    response.status_code = status.HTTP_200_OK
    db_supplier = crud.get_supplier(db, supplier_id)
    return db_supplier


@ormrouter.delete("/suppliers/{supplier_id}")
async def del_supplier(supplier_id: PositiveInt, db: Session = Depends(get_db)):
    db_supplier = crud.get_supplier(db, supplier_id)
    if db_supplier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found"
        )
    crud.del_suppliers(db, supplier_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@ormrouter.post("/suppliers", response_model=schemas.SupplierFull)
async def post_supplier(
    inp_supp: schemas.SuppliersPostInput,
    response: Response,
    db: Session = Depends(get_db),
):
    new_id = crud.get_suppliers_maxid(db)[0] + 1
    inp_supp.SupplierID = new_id
    crud.post_suppliers(db, models.Supplier(**dict(inp_supp)))
    response.status_code = status.HTTP_201_CREATED
    db_supplier = crud.get_supplier(db, inp_supp.SupplierID)
    return db_supplier
