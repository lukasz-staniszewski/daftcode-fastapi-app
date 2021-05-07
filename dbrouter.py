from fastapi import APIRouter, Request, Response, status, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3
from pydantic import BaseModel


class Customer(BaseModel):
    company_name: str


class Shipper(BaseModel):
    company_name: str


class CategoryInput(BaseModel):
    name: str


class CategoryOutput(BaseModel):
    id: int
    name: str


dbrouter = APIRouter()
dbrouter.__name__ = "DataBase app!"
templates = Jinja2Templates(directory="templates")
db_path = "northwind.db"


@dbrouter.get("/", response_class=HTMLResponse)
def welcome_jinja(request: Request):
    return templates.TemplateResponse(
        "welcome.html.j2",
        {"request": request},
    )


@dbrouter.on_event("startup")
async def startup():
    dbrouter.db_connection = sqlite3.connect(db_path)
    dbrouter.db_connection.text_factory = lambda b: b.decode(
        errors="ignore"
    )  # northwind specific


@dbrouter.on_event("shutdown")
async def shutdown():
    dbrouter.db_connection.close()


@dbrouter.get("/products")
async def products():
    products = dbrouter.db_connection.execute(
        "SELECT ProductName FROM Products"
    ).fetchall()
    return {"products": products, "products_counter": len(products)}


@dbrouter.get("/suppliers/{supplier_id}")
async def single_supplier(supplier_id: int):
    dbrouter.db_connection.row_factory = sqlite3.Row
    data = dbrouter.db_connection.execute(
        f"SELECT CompanyName, Address FROM Suppliers WHERE SupplierID = {supplier_id}"
    ).fetchone()
    return data


@dbrouter.get("/employee_with_region")
async def employee_with_region():
    dbrouter.db_connection.row_factory = sqlite3.Row
    data = dbrouter.db_connection.execute(
        """
        SELECT Employees.LastName, Employees.FirstName, Territories.TerritoryDescription 
        FROM Employees JOIN EmployeeTerritories ON Employees.EmployeeID = EmployeeTerritories.EmployeeID
        JOIN Territories ON EmployeeTerritories.TerritoryID = Territories.TerritoryID;
     """
    ).fetchall()
    return [
        {
            "employee": f"{x['FirstName']} {x['LastName']}",
            "region": x["TerritoryDescription"],
        }
        for x in data
    ]


@dbrouter.get("/employee_with_region_order")
async def employee_with_region():
    dbrouter.db_connection.row_factory = sqlite3.Row
    data = dbrouter.db_connection.execute(
        """
        SELECT Employees.LastName, Employees.FirstName, Territories.TerritoryDescription 
        FROM Employees JOIN EmployeeTerritories ON Employees.EmployeeID = EmployeeTerritories.EmployeeID
        JOIN Territories ON EmployeeTerritories.TerritoryID = Territories.TerritoryID
        ORDER BY Employees.LastName;
     """
    ).fetchall()
    return [
        {
            "employee": f"{x['FirstName']} {x['LastName']}",
            "region": x["TerritoryDescription"],
        }
        for x in data
    ]


# @dbrouter.get("/customers")
# async def customers():
#     dbrouter.db_connection.row_factory = lambda cursor, x: x[0]
#     artists = dbrouter.db_connection.execute("SELECT CompanyName FROM Customers").fetchall()
#     return artists


@dbrouter.post("/customers/add")
async def artists_add(customer: Customer):
    cursor = dbrouter.db_connection.execute(
        f"INSERT INTO Customers (CompanyName) VALUES ('{customer.company_name}')"
    )
    dbrouter.db_connection.commit()
    new_customer_id = cursor.lastrowid
    dbrouter.db_connection.row_factory = sqlite3.Row
    customer = dbrouter.db_connection.execute(
        """SELECT CustomerID AS customer_id, CompanyName AS company_name
         FROM Customers WHERE CustomerID = ?""",
        (new_customer_id,),
    ).fetchone()
    return customer


@dbrouter.patch("/shippers/edit/{shipper_id}")
async def artists_add(shipper_id: int, shipper: Shipper):
    cursor = dbrouter.db_connection.execute(
        "UPDATE Shippers SET CompanyName = ? WHERE ShipperID = ?",
        (shipper.company_name, shipper_id),
    )
    dbrouter.db_connection.commit()

    app.db_connection.row_factory = sqlite3.Row
    data = dbrouter.db_connection.execute(
        """SELECT ShipperID AS shipper_id, CompanyName AS company_name
         FROM Shippers WHERE ShipperID = ?""",
        (shipper_id,),
    ).fetchone()

    return data


@dbrouter.get("/orders")
async def orders():
    dbrouter.db_connection.row_factory = sqlite3.Row
    orders = dbrouter.db_connection.execute("SELECT * FROM Orders").fetchall()
    return {
        "orders_counter": len(orders),
        "orders": orders,
    }


@dbrouter.delete("/orders/delete/{order_id}")
async def order_delete(order_id: int):
    cursor = dbrouter.db_connection.execute(
        "DELETE FROM Orders WHERE OrderID = ?", (order_id,)
    )
    dbrouter.db_connection.commit()
    return {"deleted": cursor.rowcount}


@dbrouter.get("/region_count")
async def root():
    dbrouter.db_connection.row_factory = lambda cursor, x: x[0]
    regions = dbrouter.db_connection.execute(
        "SELECT RegionDescription FROM Regions ORDER BY RegionDescription DESC"
    ).fetchall()
    count = dbrouter.db_connection.execute("SELECT COUNT(*) FROM Regions").fetchone()

    return {"regions": regions, "regions_counter": count}


### HOMEWORK STARTS HERE
@dbrouter.get("/categories")
async def get_categories(response: Response):
    response.status_code = status.HTTP_200_OK
    dbrouter.db_connection.row_factory = sqlite3.Row
    categories = dbrouter.db_connection.execute(
        "SELECT CategoryID, CategoryName FROM Categories ORDER BY CategoryID"
    ).fetchall()
    categories = [
        {"id": x["CategoryID"], "name": x["CategoryName"]} for x in categories
    ]
    return {
        "categories": categories,
    }


def validate_address(x):
    if x["Address"] and x["PostalCode"] and x["City"] and x["Country"]:
        return f'{x["Address"]} {x["PostalCode"]} {x["City"]} {x["Country"]}'
    else:
        return None


@dbrouter.get("/customers")
async def get_customers(response: Response):
    response.status_code = status.HTTP_200_OK
    dbrouter.db_connection.row_factory = sqlite3.Row
    customers = dbrouter.db_connection.execute(
        """
        SELECT CustomerID, CompanyName, Address, PostalCode, City, Country
        FROM Customers
        """
    ).fetchall()
    customers = [
        {
            "id": x["CustomerID"],
            "name": x["CompanyName"],
            "full_address": validate_address(x),
        }
        for x in customers
    ]
    return {
        "customers": customers,
    }


@dbrouter.get("/products/{product_id}")
async def get_product_by_id(response: Response, product_id: int):
    dbrouter.db_connection.row_factory = sqlite3.Row
    data = dbrouter.db_connection.execute(
        f"SELECT ProductID, ProductName FROM Products WHERE ProductID = {product_id}"
    ).fetchone()
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no product with such id",
        )
    else:
        response.status_code = status.HTTP_200_OK
        return {"id": data["ProductID"], "name": data["ProductName"]}


@dbrouter.get("/employees")
async def get_employees(
    response: Response,
    limit: int = Query(None),
    offset: int = Query(None),
    order: str = Query("id"),
):
    order_dict = {
        "id": "EmployeeID",
        "first_name": "FirstName",
        "last_name": "LastName",
        "city": "City",
    }
    offset_sql = ""
    limit_sql = ""
    order_sql = ""
    if offset:
        offset_sql += f" OFFSET {offset}"
    if limit:
        limit_sql += f" LIMIT {limit}"
    try:
        order_sql = f" ORDER BY {order_dict[order]}"
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong order param!",
        )
    response.status_code = status.HTTP_200_OK
    dbrouter.db_connection.row_factory = sqlite3.Row
    employees = dbrouter.db_connection.execute(
        "SELECT EmployeeID, LastName, FirstName, City FROM Employees"
        + order_sql
        + limit_sql
        + offset_sql
    ).fetchall()
    employees = [
        {
            "id": x["EmployeeID"],
            "last_name": x["LastName"],
            "first_name": x["FirstName"],
            "city": x["City"],
        }
        for x in employees
    ]
    return {"employees": employees}


@dbrouter.get("/products_extended")
async def get_products_ext(response: Response):
    response.status_code = status.HTTP_200_OK
    dbrouter.db_connection.row_factory = sqlite3.Row
    prod_ext = dbrouter.db_connection.execute(
        """
    SELECT ProductID, ProductName, CategoryName, CompanyName
    FROM Products p 
    JOIN Suppliers s USING (SupplierID)
    JOIN Categories c USING (CategoryID);
    """
    )
    prod_ext = [
        {
            "id": x["ProductID"],
            "name": x["ProductName"],
            "category": x["CategoryName"],
            "supplier": x["CompanyName"],
        }
        for x in prod_ext
    ]
    return {"products_extended": prod_ext}


@dbrouter.get("/products/{product_id}/orders")
async def get_products_orders(response: Response, product_id: int):
    dbrouter.db_connection.row_factory = sqlite3.Row
    ord_id_check = dbrouter.db_connection.execute(
        f"SELECT ProductID from Products WHERE ProductID = {product_id}"
    )
    if ord_id_check is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product with such id doesnt exist!",
        )
    response.status_code = status.HTTP_200_OK
    prod_ord = dbrouter.db_connection.execute(
        """
    SELECT o.OrderID as OrderID, CompanyName, Quantity, ROUND((UnitPrice * Quantity) - (Discount * (UnitPrice * Quantity)),2) as TotalPrice
    FROM Orders o 
    JOIN Customers c USING (CustomerID)
    JOIN "Order Details" od WHERE (od.OrderID = o.OrderID AND od.ProductID = ?) """,
        (product_id,),
    )
    prod_ord = [
        {
            "id": x["OrderID"],
            "customer": x["CompanyName"],
            "quantity": x["Quantity"],
            "total_price": x["TotalPrice"],
        }
        for x in prod_ord
    ]
    return {"orders": prod_ord}


@dbrouter.post("/categories")
async def post_categories(response: Response, category: CategoryInput):
    cursor = dbrouter.db_connection.execute(
        f"INSERT INTO Categories (CategoryName) VALUES ('{category.name}')"
    )
    dbrouter.db_connection.commit()
    response.status_code = status.HTTP_201_CREATED
    return CategoryOutput(id=cursor.lastrowid, name=category.name)


async def check_category_id(category_id):
    dbrouter.db_connection.row_factory = sqlite3.Row
    cat_check = dbrouter.db_connection.execute(
        f"SELECT CategoryID from Categories WHERE CategoryID = {category_id}"
    )
    if cat_check is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category with such id doesnt exist!",
        )


@dbrouter.put("/categories/{category_id}")
async def put_categories(response: Response, category: CategoryInput, category_id: int):
    check_category_id(category_id)
    response.status_code = status.HTTP_200_OK
    dbrouter.db_connection.execute(
        "UPDATE Categories SET CategoryName = ? WHERE CategoryID = ?",
        (category.name, category_id),
    )
    dbrouter.db_connection.commit()
    return CategoryOutput(id=category_id, name=category.name)


@dbrouter.delete("/categories/{category_id}")
async def del_categories(response: Response, category: CategoryInput, category_id: int):
    check_category_id(category_id)
    response.status_code = status.HTTP_200_OK
    dbrouter.db_connection.execute(
        "DELETE FROM Categories WHERE CategoryID = ?", (category_id,)
    )
    dbrouter.db_connection.commit()
    return {"deleted": 1}
