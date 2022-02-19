from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models, database, oauth2

router = APIRouter(prefix="/vote", tags=['Vote'])

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote:schemas.Vote, db:Session=Depends(database.get_db), current_user: dict= Depends(oauth2.get_current_user)):

    # check if the user is trying to vote a post that doesn't exist, raise an exception if it deoesn't
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail= f"Post with id: {vote.post_id} does not exist")
    # query to check if the vote from post is existing in the votes table
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()

    # check if vote is given - vote = 1
    if (vote.dir ==1):
        # check if it is existing vote in votes table
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user {current_user.id} has already votes on post {vote.post_id}")

        # if vote is not existing then  add the vote and retun a message
        new_vote = models.Vote(post_id =vote.post_id, user_id= current_user.id)

        db.add(new_vote)
        db.commit()
        return {"message":"successfully added vote"}
    #  if user wants to remove his vote vote = 0
    else:
        # if user is trying to remove vote which is not existing in votes table
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote does not exist")

        vote_query.delete(synchronize_session=False)
        db.commit
 
        return {"message": "successfully deleted vote"}
            

