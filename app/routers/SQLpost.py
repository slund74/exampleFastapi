from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. database import get_db
from sqlalchemy.orm import Session
from typing import Optional, List
from .. import models, schemas
import psycopg2
from psycopg2.extras import RealDictCursor
import time

router = APIRouter(
    prefix="/posts",
    tags=["SQL Posts"]
)

while True:

    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', 
                            password='Pa$$word', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("DB connection was succesfull")
        break
    except Exception as error:
        print("Connectingto DB failed")
        print("Error: ",  error)
        time.sleep(2)  

@router.get("/", response_model=List[schemas.Post])
def get_posts():
    cursor.execute("""SELECT * FROM posts """)
    posts = cursor.fetchall()
    return posts

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate):
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, 
                  (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return new_post

@router.get("/{id}", response_model=schemas.Post)
def get_post(id: int, response: Response):
    cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id),))
    post = cursor.fetchone()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found")
    
    return post

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found") 
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put('/{id}', response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %sRETURNING *""",
                   (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found") 
   
    return updated_post