from sqlalchemy.orm import Session

from dblib import models


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
        .order_by(models.Product.ProductID.desc())
        .all()
    )
