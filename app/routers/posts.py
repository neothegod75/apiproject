from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional, List

from ..database import  engine, get_db
from ..import models, schemas, utils, oauth2

router = APIRouter(
    prefix = "/posts",
    tags = ['Posts']
)


@router.get("/", response_model=List[schemas.PostOut])
# @router.get("/")
def get_posts(db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user), 
limit:int = 5, skip:int =0, search : Optional[str]=""):   
    # cursor.execute(""" SELECT * FROM posts """)
    # posts = cursor.fetchall()
    # old query without the votes
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter = True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
        
    return posts

# to get post data from body we need to use a variable of type dict = Body which converts json
# to python dictionary . this need to imported from fastapi.param_functions import Body
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)

# first depency ensures that we are connected to db and 2nd function ensures that the user is logged in
def create_posts(post: schemas.PostCreate,db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):
    
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, 
    #     (post.title, post.content, post.published,))
    # new_post = cursor.fetchone()
    # conn.commit()
    # when a post is made the post should also be returned
    # getting post data from api &&& post. is used as it refrences the pydantic model class  and checks if
    # it is according to the schema we have set 
    # and it works like dictionary
    # refrences the models.Post table model created by sqlalchemy
    # **************** new_post = models.Post(title = post.title, content=post.content, published=post.published) *****
    
    new_post = models.Post(user_id = current_user.id, **post.dict()) 
    # post data stored in new_post is now added to db
    db.add(new_post)
    # committing the db changes
    db.commit()
    # this works like returning in sql statement and gets the post that just got added and stores in new_post
    db.refresh(new_post)
    return new_post

# passing path parameter id. This path parameter is accessible by the function
# specifying datatype in fastapi function automatically converts it to int
@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id:int, db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):
    # we are validating the post id as int but have to convert it into str
    # cursor.execute(""" SELECT * from posts WHERE id = %s""", (str(id),))
    # post = cursor.fetchone()

    # Using query and fitlering the id and returning the first match
    # old query without the votes
    # post = db.query(models.Post).filter(models.Post.id == id).first()

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter = True).group_by(models.Post.id).filter(models.Post.id == id).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail = f"post with id:{id} was not found")

    
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'message': f"post with id: {id} was not found"}
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: dict= Depends(oauth2.get_current_user)):
    
    # cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    
    # deleted_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You are not authorized to perform requested action")
    
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):

    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id,)))
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)

  

    post_to_update = post_query.first()

    if post_to_update == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")

    if post_to_update.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You are not authorized to perform requested action")
    # using update method to update the post retreived above from the data received from api
    post_query.update(post.dict(), synchronize_session=False)

    db.commit()
   
    return post_query.first()