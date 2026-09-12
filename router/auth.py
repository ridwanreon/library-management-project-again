from fastapi import FastAPI,Depends,HTTPException,APIRouter
from database import SessionLocal
from typing import Annotated,Optional
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from models import Users
from passlib.context import CryptContext
from datetime import timedelta,datetime,timezone
from jose import jwt
from pydantic import BaseModel,Field
from fastapi.responses import JSONResponse

router = APIRouter()


bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated = 'auto')
Oauth2_bearer = OAuth2PasswordBearer(tokenUrl='login')

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]



SECRET_KEY = '1fa63670a3f144dfc78e4ed7deac1837c6f4fd8473dd05ef4d2604196c52b4bc'
ALGORITHM = 'HS256'

class CreateUser(BaseModel):
    email : str
    username : str
    firstname : str
    lastname : str
    password : str
    role : str
    
    
class UpdateUser(BaseModel):
    email : Optional[str] = Field(default=None)
    username : Optional[str] = Field(default=None)
    firstname : Optional[str] = Field(default=None)
    lastname: Optional[str] = Field(default=None)

class UpdatePassword(BaseModel):
    current_password : str
    new_password : str


def  create_access_token(username:str,user_id:int,role:str,expires_time:timedelta):
    encode = {'sub':username,'id': user_id,'role':role}
    expire = datetime.now(timezone.utc) + expires_time
    encode.update({'exp':expire})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)


def get_current_user(Token : Annotated[str,Depends(Oauth2_bearer)]):
    try:
        payload = jwt.decode(Token,SECRET_KEY,algorithms=[ALGORITHM])
        username :  str = payload.get('sub')
        user_id : int = payload.get('id')
        role : str = payload.get('role')
        
        if username is None or user_id is None:
            raise HTTPException(status_code=404,detail='User not found')
        return {'username' : username, 'user_id' : user_id, 'role' : role}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail='User not found')
        
user_dependency = Annotated[dict,Depends(get_current_user)]

def authenticate_user(username, password, db):
    user = db.query(Users).filter(Users.username == username).first()
    
    if user is None:
        return False
    if bcrypt_context.verify(password,user.hash_password):
        return user
    
    return False
    


@router.post('/login')
def login_user(db : db_dependency,form_data : Annotated[OAuth2PasswordRequestForm,Depends()]):
    user = authenticate_user(form_data.username, form_data.password,db)
    
    if not user:
        raise HTTPException(status_code=401,detail='Failed Authentication')
    
    token = create_access_token(user.username,user.id,user.role,timedelta(minutes=30))
    return {'access_token' : token, 'token_type' : 'bearer'}

@router.post('/createuser')
def create_user(db : db_dependency, newUser : CreateUser):
    new_user = Users(
        email = newUser.email,
        username =  newUser.username,
        firstname = newUser.firstname,
        lastname = newUser.lastname,
        hash_password = bcrypt_context.hash(newUser.password),
        role = newUser.role
    )
    
    db.add(new_user)
    db.commit()
    
    raise HTTPException(status_code=200,detail='User created successfully')

@router.put('/edituser')
def Update_user(user: user_dependency, db: db_dependency, update_user: UpdateUser):
    if user is None:
        raise HTTPException(status_code=401,detail='Failed Authentication')
    
    User = db.query(Users).filter(Users.id == user.get('user_id')).first()
    
    updateUser = update_user.model_dump(exclude_unset=True)
    
    for key,value in updateUser.items():
        setattr(User,key,value)
    db.commit()
    return JSONResponse(status_code=200, content={'message' : 'User updated successfully'})

@router.put('/passwordchange')
def change_password(user: user_dependency, db: db_dependency, updatepassword: UpdatePassword):
    if user is None:
        raise HTTPException(status_code=401,detail='Failed Authentication')
    
    User = db.query(Users).filter(Users.id == user.get('user_id')).first()
    
    if not bcrypt_context.verify(updatepassword.current_password,User.hash_password):
        raise HTTPException(status_code=401, detail='Wrong password')
    User.hash_password = bcrypt_context.hash(updatepassword.new_password)
    db.commit()
    
    return JSONResponse(status_code=200, content={'message':'Password change successfully'})