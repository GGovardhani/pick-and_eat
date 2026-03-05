from pydantic import BaseModel
from typing import Optional
class UserCreate(BaseModel):
    username : str
    email : str
    password : str
class Userlogin(BaseModel):
    username: str
    password: str
class ProductCreate(BaseModel):
    name : str
    description : str
    price : float
    category : str
    stock : int
    image_url : str
class ProductResponse(BaseModel):
    id : int
    name : str
    description : str
    price : float
    category : str
    stock : int
    image_url : str
    
    class Config:
        from_attributes = True
class ProductUpdate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    stock: int
    image_url: str
class CartCreate(BaseModel):
    product_id: int
    quantity: int
class CartResponse(BaseModel):
    id : int
    product_id : int
    quantity :int
    class Config:
        from_attributes = True
class CartUpdate(BaseModel):
    quantity :int
