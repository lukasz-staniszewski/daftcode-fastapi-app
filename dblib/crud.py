from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from dblib import models, schemas


def get_shippers(db: Session):
    return db.query(models.Shipper).all()


def get_shipper(db: Session, shipper_id: int):
    return (
        db.query(models.Shipper).filter(models.Shipper.ShipperID == shipper_id).first()
    )


def get_suppliers(db: Session):
    return db.query(models.Supplier).order_by(models.Supplier.SupplierID.asc()).all()


def get_supplier(db: Session, supplier_id: int):
    return (
        db.query(models.Supplier)
        .filter(models.Supplier.SupplierID == supplier_id)
        .first()
    )


def get_suppliers_product(db: Session, supplier_id: int):
    return (
        db.query(
            models.Product.ProductName,
            models.Product.ProductID,
            models.Category.CategoryID,
            models.Category.CategoryName,
            models.Product.Discontinued,
        )
        .join(models.Supplier, models.Supplier.SupplierID == models.Product.SupplierID)
        .join(models.Category, models.Category.CategoryID == models.Product.CategoryID)
        .filter(models.Product.SupplierID == supplier_id)
        .order_by(models.Product.ProductID.desc())
        .all()
    )


def post_suppliers(db: Session, new_supplier: models.Supplier):
    db.add(new_supplier)
    db.commit()


def put_suppliers(
    db: Session, supplier_id: int, modified_things: schemas.SuppliersInput
):
    dict_of_changes = {k: v for k, v in dict(modified_things).items() if v is not None}
    if dict_of_changes:
        db.query(models.Supplier).filter(
            models.Supplier.SupplierID == supplier_id
        ).update(values=dict_of_changes)
        db.commit()


def del_suppliers(db: Session, supplier_id: int):
    db.query(models.Supplier).filter(models.Supplier.SupplierID == supplier_id).delete()
    db.commit()


def get_suppliers_maxid(db: Session):
    return db.query(func.max(models.Supplier.SupplierID)).first()
