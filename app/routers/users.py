from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import  engine, get_db
from .. import models, schemas, utils

router = APIRouter(
    prefix = "/users",
    tags = ['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserInfo)
def create_users(user: schemas.CreateUser,db: Session = Depends(get_db)):


    # hash the password - user password
    hashed_password = utils.hash(user.password)
    # override the password entered by user by hashed password
    user.password = hashed_password
    new_user = models.User(**user.dict()) 
    # post data stored in new_post is now added to db
    db.add(new_user)
    # committing the db changes
    db.commit()
    # this works like returning in sql statement and gets the post that just got added and stores in new_post
    db.refresh(new_user)
    return new_user

@router.get("/{id}", response_model=schemas.UserInfo)
def get_user(id:int, db: Session = Depends(get_db)):
    # we are validating the post id as int but have to convert it into str
    # cursor.execute(""" SELECT * from posts WHERE id = %s""", (str(id),))
    # post = cursor.fetchone()

    # Using query and fitlering the id and returning the first match

    user = db.query(models.User).filter(models.User.id == id).first()
    print(user)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail = f"user with id:{id} was not found")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'message': f"post with id: {id} was not found"}
    return user