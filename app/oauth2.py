from jose import JWTError, jwt
from datetime import datetime, timedelta
from app import database

from app.database import SessionLocal
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings

# The password "flow" is one of the ways ("flows") defined in OAuth2, to handle security and authentication.
# OAuth2 was designed so that the backend or API could be independent of the server that authenticates the user.
# But in this case, the same FastAPI application will handle the API and the authentication.
# In this example we are going to use OAuth2, with the Password flow, using a Bearer token. We do that using the OAuth2PasswordBearer class.
# The user types the username and password in the frontend, and hits Enter.
# The frontend (running in the user's browser) sends that username and password to a specific URL in our API (declared with tokenUrl="token").
# The API checks that username and password, and responds with a "token
# The frontend needs to fetch some more data from the API.
# But it needs authentication for that specific endpoint.
# So, to authenticate with our API, it sends a header Authorization with a value of Bearer plus the token.
# If the token contains foobar, the content of the Authorization header would be: Bearer foobar.
# FastAPI provides several tools, at different levels of abstraction, to implement these security features.

# In this example we are going to use OAuth2, with the Password flow, using a Bearer token. We do that using the OAuth2PasswordBearer class.
# When we create an instance of the OAuth2PasswordBearer class we pass in the tokenUrl parameter. This parameter contains the URL that the client (the frontend running in the user's browser) will use to send the username and password in order to get a token.
# The oauth2_scheme variable is an instance of OAuth2PasswordBearer, but it is also a "callable".
# It could be called as:  oauth2_scheme(some, parameters) So, it can be used with Depends.

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

# We will need 3 things to create access token
# SECRET_KEY
# Algorithm
# Expiration Time

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
# This is set to 30 minutes
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# function that generates jwt token, takes in an input (here we just give user.id) of type dict
def create_access_token(data: dict):
    # copying the data parameter and storing it in a variable
    to_encode = data.copy()

    # using datetime to convert the accesstoken expire time to python datetime using timedelta
    expire = datetime.utcnow() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    # adding the expiration time as dictionary to to_encode variable
    to_encode.update({"exp": expire})
    # calling the jwt module with encode method to generate access token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

# this function validates the token specially the id as token can be read by anyone access to payload (after it is extracted by get_current_user)
def verify_access_token(token: str, credentials_exception):
    try:
        # we decode the the token and save it in a varialbe called payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        # we extract the id from the payload and save it in id which is of type str
        id: str = payload.get("user_id")

        # raise an exception if id is not found in payload
        if id is None:
             raise credentials_exception
        # we cross-validate the id with the pydantic schema and store it in variable token_data 
        token_data = schemas.TokenData(id=id)

    # raise credentials exception if something else goes wrong in token validation.
    except JWTError as e:
        print(e)
        raise credentials_exception 

    return token_data 
    # this returns the token data id to the api endpoint which depends on user to be logged in and provide token
# This function is used to get the token when the user logs in
# It will go and look in the request for that Authorization header, check if the value is Bearer plus some token, 
# and will return the token as a str. If it doesn't see an Authorization header, 
# or the value doesn't have a Bearer token, it will respond with a 401 status code error (UNAUTHORIZED) directly.

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not Validate Credentials",
                            headers = {"WWW-Authenticate":"Bearer"})

    # we will call verify_access_token which will return token_data which is basically user id
    token = verify_access_token(token, credentials_exception)

    # we will use the user id from the token to retrieve user details from the database
    user = db.query(models.User).filter(models.User.id == token.id).first()
    #  now we will return the user details from db instead of the user id from the verify_access_token
    return user