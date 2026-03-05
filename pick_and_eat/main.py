from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from jose import JWTError, jwt

from database import engine, SessionLocal
from auth import SECRET_KEY, ALGORITHM, hash_password, verify_password, create_access_token
import model
import schemas
from model import Product
from typing import Optional


# ---------------- DATABASE ---------------- #

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- AUTH ---------------- #

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(model.User).filter(
        model.User.username == username
    ).first()

    if user is None:
        raise credentials_exception

    return user


# ---------------- APP INIT ---------------- #

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


model.Base.metadata.create_all(bind=engine)


# ---------------- REGISTER ---------------- #
@app.get("/")
def serve_frontend():
    return FileResponse("pick_and_eat.html")

@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_pwd = hash_password(user.password)

    new_user = model.User(
        username=user.username,
        email=user.email,
        password=hashed_pwd
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="User already exists")

    return {"message": "User created successfully"}


# ---------------- LOGIN ---------------- #

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = db.query(model.User).filter(
        model.User.username == form_data.username
    ).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid username")

    if not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid password")

    access_token = create_access_token(
        data={"sub": db_user.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ---------------- CURRENT USER ---------------- #

@app.get("/me")
def read_current_user(current_user: model.User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email,
        "is_admin": current_user.is_admin
    }

@app.get("/products/search")
def search_products(
    name: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))
    if min_price:
        query = query.filter(Product.price>= min_price)
    if max_price:
        query = query.filter(Product.price<=max_price)
    if sort == "asc":
        query = query.order_by(Product.price.asc())
    elif sort == "desc":
        query = query.order_by(Product.price.desc())
    products = query.all()
    return products
# ---------------- PRODUCTS ---------------- #

@app.post("/products", response_model=schemas.ProductResponse)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can create products")

    new_product = model.Product(**product.dict())

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


@app.get("/products", response_model=list[schemas.ProductResponse])
def get_all_products(
    skip : int = 0,
    limit  : int = 100,
    db: Session = Depends(get_db)
):
    products = db.query(model.Product).offset(skip).limit(limit).all()
    return products


@app.get("/products/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(model.Product).filter(
        model.Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@app.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can delete products")

    product = db.query(model.Product).filter(
        model.Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}


# ---------------- CART ---------------- #

@app.post("/cart")
def add_to_cart(
    item: schemas.CartCreate,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(get_current_user)
):
    product = db.query(model.Product).filter(
        model.Product.id == item.product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.stock < item.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    cart_item = model.Cart(
        user_id=current_user.id,
        product_id=item.product_id,
        quantity=item.quantity
    )

    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)

    return cart_item



@app.get("/cart")
def view_cart(
    db: Session = Depends(get_db),
    current_user: model.User = Depends(get_current_user)
):
    cart_items = db.query(model.Cart).filter(
        model.Cart.user_id == current_user.id
    ).all()

    result = []

    for item in cart_items:
        product = db.query(model.Product).filter(
            model.Product.id == item.product_id
        ).first()

        result.append({
            "product_name": product.name,
            "price": product.price,
            "quantity": item.quantity
        })

    return result



# ---------------- CHECKOUT ---------------- #

@app.post("/checkout")
def checkout(
    current_user: model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cart_items = db.query(model.Cart).filter(
        model.Cart.user_id == current_user.id
    ).all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    new_order = model.Order(
        user_id=current_user.id,
        total_amount=0
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    total = 0

    for item in cart_items:
        product = db.query(model.Product).filter(
            model.Product.id == item.product_id
        ).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {product.name}"
            )

        item_total = product.price * item.quantity
        total += item_total

        product.stock -= item.quantity

        order_item = model.OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=item.quantity,
            price=product.price
        )

        db.add(order_item)

    new_order.total_amount = total
    db.commit()

    db.query(model.Cart).filter(
        model.Cart.user_id == current_user.id
    ).delete()

    db.commit()

    return {"message": "Order placed successfully"}


# ---------------- MY ORDERS ---------------- #

@app.get("/my-orders")
def get_orders(
    current_user: model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    orders = db.query(model.Order).filter(
        model.Order.user_id == current_user.id
    ).all()

    return [
        {
            "id": order.id,
            "total_amount": order.total_amount,
            "status": order.status,
            "items": [
                {
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "price": item.price
                }
                for item in order.items
            ]
        }
        for order in orders
    ]


# ---------------- REVIEWS ---------------- #

@app.post("/add-review")
def add_review(
    product_id: int,
    rating: int,
    comment: str,
    current_user: model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    new_review = model.Review(
        user_id=current_user.id,
        product_id=product_id,
        rating=rating,
        comment=comment
    )

    db.add(new_review)
    db.commit()

    return {"message": "Review added successfully"}


@app.get("/product-reviews")
def get_reviews(product_id: int, db: Session = Depends(get_db)):
    reviews = db.query(model.Review).filter(
        model.Review.product_id == product_id
    ).all()

    return [
        {
            "username": review.user.username,
            "rating": review.rating,
            "comment": review.comment
        }
        for review in reviews
    ]
