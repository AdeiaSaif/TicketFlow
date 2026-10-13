import bcrypt
def hashed(password:str):
    return bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()).decode('utf-8')
def verify(password:str,hashed:str):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))