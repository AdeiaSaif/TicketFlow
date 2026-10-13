from jose import JWTError,jwt
from datetime import datetime,timedelta
from schemas import TokenData,settings

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
oauth2_scheme=OAuth2PasswordBearer(tokenUrl='Signin')

def create_access_token(data:dict):
    to_encode=data.copy()
    to_encode.update({'exp':datetime.utcnow()+timedelta(minutes=30)})
    return jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM)

def verify_access_token(token:str,credential_exception):
    try:
        payload=jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        id:str=payload.get('id')
        token_data=TokenData(id=int(id))
    except JWTError:
        raise credential_exception
        
    return token_data

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},)
    return verify_access_token(token, credentials_exception)