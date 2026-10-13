from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from database.database import get_db
from schemas import User
from database import models
from hashing import hashed,verify
from fastapi import Depends, HTTPException, status
from auth2 import create_access_token,get_current_user 
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
router=APIRouter()
@router.post("/Signup")
def user_registration(user_data:User,db:Session=Depends(get_db)):
    hashed_password = hashed(user_data.password)
    new_user = models.Users(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password,
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {'data':user_data}

@router.post("/Signin")
def user_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.email == form_data.username).first()    
    print(user)
    print(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )
    print(form_data.password)
    print(verify(form_data.password, user.password))
    if not verify(form_data.password, user.password):
    
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )
    access_token = create_access_token(data={"id": str(user.id)})
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }
@router.get('/getuser')
def user_data(get_user:int=Depends(get_current_user),db:Session=Depends(get_db)):
    user_data=db.query(models.Users).filter(get_user.id==models.Users.id).first()
    return{"data":user_data}