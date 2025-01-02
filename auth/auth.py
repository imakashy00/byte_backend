from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import EmailStr
from database.database import get_db
from sqlalchemy.orm import Session
from schema.schema import Token, UserDatabase, UserRegister
from database.database import Users
from dotenv import load_dotenv
import os
load_dotenv()

router = APIRouter()

# Credentials for authentication
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM') # Example: HS256
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))

pass_cont = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Function to verify password received from user
def verify_password(plain_password:str, hashed_password:str) -> bool:
    '''
    Args:
    plain_password: plain text password from user
    hashed_password: hashed password from database
    
    Returns:
    True if password is correct else False
    '''
    return pass_cont.verify(plain_password, hashed_password)

# Function to hash password received from user
def password_hash(password) -> str:
    '''
    Args:
    password: plain text password from user
    
    Returns:
    hashed password
    '''
    return pass_cont.hash(password)

#  Get user from database
async def get_user(email: str,db:Session) -> UserDatabase:
    '''
    Args:
    email: user email
    db: database session
    
    Returns:
    user from database if available else raise error 404 -> User not found
    '''
    try:
        user = db.query(Users).filter(Users.email == email).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email {email} not found"
            )
        return UserDatabase(**user.__dict__) 
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e)

# Fuenction to authenticate user
async def authenticate_user(email:EmailStr, password:str, db:Session ):
    '''
    Args:
    email: user email
    password: plain text password from user
    db: database session
    
    Returns:
    user from database if available else raise error 404 -> User not found
    '''
    try:
        user = await get_user(email, db)
        
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )        
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e)

# Function to create access token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to get current user
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_db)) -> UserDatabase :
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = {"email": email}
    except JWTError:
        raise credentials_exception
    user = await get_user(email=token_data["email"],db=db)
    if user is None:
        raise credentials_exception
    return user

# Route to register the user in database

@router.post("/register")
async def register_user(user:UserRegister,db:Session = Depends(get_db)) -> JSONResponse:
    '''
    Args:
    user: UserRegister schema-> email and password
    db: database session

    Returns:
    JSONResponse -> status code and message
    '''
    # find if user already exists in database
    try: 
        existing_user = db.query(Users).filter(Users.email == user.email).first()
        if existing_user:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "User already exists"
                }
            )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)   
    

    # Adding user in database
    try:
        hash_password = password_hash(user.password)    
        new_user = Users(email=user.email, hashed_password=hash_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "status": status.HTTP_201_CREATED,
                    "message": f'User {user.email} created successfully'
                }
            )
    except:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong while creating user")
    
# Route to login the user
@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],db:Session = Depends(get_db)) ->Token:
    '''
    '''
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
  

