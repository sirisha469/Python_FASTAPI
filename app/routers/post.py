from fastapi import status, HTTPException, Depends, FastAPI, Response, APIRouter
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from ..database import get_db
from typing import Optional, List

router = APIRouter(
  prefix="/posts",
  tags=['Posts']
)

#read: getting all posts
@router.get("/", response_model=List[schemas.PostRes])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip:int = 0, search: Optional[str] = ""):
  # cursor.execute(""" SELECT * FROM posts  """)
  # post = cursor.fetchall()

  #posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()
  posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
  return posts

#create: creating posts 
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostRes)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db),  current_user: int = Depends(oauth2.get_current_user)):
  
  # cursor.execute(""" INSERT INTO posts(title, content, published) values(%s, %s, %s) returning *""", (post.title, post.content, post.published))

  # new_post = cursor.fetchone()

  # conn.commit()

  # print(**post.dict())

  # new_post = models.Post(title=post.title, content= post.content, published= post.published)

  print(current_user.email)

  new_post = models.Post(owner_id = current_user.id, **post.model_dump())
  
  db.add(new_post)
  db.commit()
  db.refresh(new_post)

  return new_post



#read: getting single post based on id
@router.get("/{id}", response_model=schemas.PostRes)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)): 
  # cursor.execute(""" SELECT * from posts WHERE id = %s """, (id))
  # post = cursor.fetchone()

  # print(post)

  post = db.query(models.Post).filter(models.Post.id == id).first()
  # print(post)

  if not post:
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                        detail=f"post with id: {id} was not found")
  
  return post


#delete: deleting post
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
  # cursor.execute(""" DELETE FROM posts WHERE id = %s returning *""", (id))
  # deleted_post = cursor.fetchone()
  # conn.commit()

  post_query = db.query(models.Post).filter(models.Post.id == id)

  post = post_query.first()

  if post == None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"post with id: {id} does not exist")
  
  if post.owner_id != current_user.id:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
  
  post_query.delete(synchronize_session=False)
  db.commit()

  return Response(status_code=status.HTTP_204_NO_CONTENT)


#update post
@router.put("/{id}", response_model=schemas.PostRes)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

  # cursor.execute(""" UPDATE posts SET title=%s , content=%s, published=%s where id = %s returning *""", (post.title, post.content, post.published, id))

  # updated_post = cursor.fetchone()
  # conn.commit() 

  post_query = db.query(models.Post).filter(models.Post.id == id)

  post = post_query.first()

  if post == None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"post with id: {id} does not exist")
  
  if post.owner_id != current_user.id:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                        detail="Not authorized to perform requested action")
  
  post_query.update(updated_post.dict(), synchronize_session=False)

  db.commit()

  return post_query.first()


