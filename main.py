from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import schemas
import crud
from fastapi import security

app = FastAPI()


"""РАБОТА С ПОЛЬЗОВАТЕЛЯМИ"""
@app.post("/users/", response_model=schemas.User)
# СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ
def create_user(user: schemas.UserCreate, db: Session = Depends(crud.get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400, detail="Почта уже была использована")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
# ВОЗВРАТ ПОЛЬЗОВАТЕЛЕЙ
def get_users(db: Session = Depends(crud.get_db), skip: int = 0, limit: int = 100):
    users = crud.get_users(db=db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
# ВОЗВРАТ ПОЛЬЗОВАТЕЛЯ
def get_user(user_id: int, db: Session = Depends(crud.get_db)):
    db_user = crud.get_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return db_user


"""РАБОТА С ПОСТАМИ"""
@app.post("/posts/{user_id}.", response_model=schemas.Post)
# СОЗДАНИЕ ПОСТА
def create_post(user_id: int, post: schemas.PostCreate, db: Session = Depends(crud.get_db)):
    return (crud.create_post(db=db, post=post, user_id=user_id))


@app.put("/posts/update_post/{post_id}", status_code=200)
# РЕДАКТИРОВАНИЕ ПОСТА
def update_post(post_id: int, post: schemas.PostCreate, owner_id: int, db: Session = Depends(crud.get_db)):
    return(crud.update_post(post_id, post, owner_id, db))


@app.get("/posts/", response_model=list[schemas.Post])
# ВОЗВРАТ ПОСТОВ
def get_posts(db: Session = Depends(crud.get_db), skip: int = 0, limit: int = 100):
    users = crud.get_posts(db=db, skip=skip, limit=limit)
    return users


@app.get("/posts/{post_id}", response_model=schemas.PostWithComments)
# ВОЗВРАТ ПОСТА С КОММЕНТАРИЯМИ
def get_post_with_comments(post_id: int, db: Session = Depends(crud.get_db)):
    post = crud.get_post(db, post_id)
    comments = crud.get_comments(db, post_id)
    post_with_comments = schemas.PostWithComments(post=post, comments=comments)
    return post_with_comments


@app.delete("/posts/delete_post/{post_id}", status_code=204)
# УДАЛЕНИЕ КОММЕНТАРИЯ
def delete_post(post_id: int, owner_id: int, db: Session = Depends(crud.get_db)):
    return crud.delete_post(post_id, owner_id, db)


"""РАБОТА С КОММЕНТАРИЯМИ"""
@app.post("/comments/", response_model=schemas.Comment)
# СОЗДАНИЕ КОММЕНТАРИЯ
def create_comment(user_id: int, post_id: int, comment: schemas.CommentCreate, db: Session = Depends(crud.get_db)):
    return (crud.create_comment(db=db, post_id=post_id, user_id=user_id, comment=comment))


@app.put("/comments/update_comment/{comment_id}", status_code=200)
# РЕДАКТИРОВАНИЕ КОММЕНТАРИЯ
def update_comment(comment_id: int, comment: schemas.CommentCreate, owner_id: int, db: Session = Depends(crud.get_db)):
    return(crud.update_comment(comment_id, comment, owner_id, db))


@app.delete("/comments/delete_comment/{comment_id}", status_code=204)
# УДАЛЕНИЕ КОММЕНТАРИЯ
def delete_comment(comment_id: int, owner_id: int, db: Session = Depends(crud.get_db)):
    return crud.delete_comment(comment_id, owner_id, db)








