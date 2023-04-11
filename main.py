from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import schemas
import crud
from fastapi import security

app = FastAPI()


"""РАБОТА С ПОЛЬЗОВАТЕЛЯМИ"""
@app.post("/api/users")
# СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ
async def create_user(user: schemas.UserCreate, db: Session = Depends(crud.get_db)):
    db_user = await crud.get_user_by_email(user.email, db)
    if db_user:
        raise HTTPException(
            status_code=400, detail="Почта уже использована")
    user = await crud.create_user(user, db)

    return await crud.create_token(user)

@app.post("/api/token")
# ГЕНЕРАЦИЯ JWT ТОКЕНА
async def generate_token(form_data: security.OAuth2PasswordRequestForm = Depends(), db: Session = Depends(crud.get_db)):
    user = await crud.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=401, detail="Неправильные данные")

    return await crud.create_token(user)

@app.get("/api/users/me", response_model=schemas.User)
# ВОЗВРАТ ИНФОРМАЦИИ О ПОЛЬЗОВАТЕЛЕ
async def get_user(user: schemas.User = Depends(crud.get_current_user)):
    return user


"""РАБОТА С ПОСТАМИ"""
@app.post("/posts/create_post/", response_model=schemas.Post)
# СОЗДАНИЕ ПОСТА
async def create_post(post: schemas.PostCreate, user: schemas.User = Depends(crud.get_current_user), db: Session = Depends(crud.get_db)):
    return await crud.create_post(db=db, post=post, user=user)



@app.put("/posts/update_post/{post_id}", status_code=200)
# РЕДАКТИРОВАНИЕ ПОСТА
async def update_post(post_id: int, post: schemas.PostCreate, user: schemas.User = Depends(crud.get_current_user), db: Session = Depends(crud.get_db)):
    return await crud.update_post(post_id, post, user, db)


@app.get("/posts/", response_model=list[schemas.Post])
# ВОЗВРАТ ПОСТОВ
async def get_posts(db: Session = Depends(crud.get_db), skip: int = 0, limit: int = 100):
    posts = await crud.get_posts(db=db, skip=skip, limit=limit)
    return posts


@app.get("/posts/{post_id}", response_model=schemas.PostWithComments)
# ВОЗВРАТ ПОСТА С КОММЕНТАРИЯМИ
async def get_post_with_comments(post_id: int, db: Session = Depends(crud.get_db)):
    post = await crud.get_post(db, post_id)
    comments = await crud.get_comments(db, post_id)
    post_with_comments = schemas.PostWithComments(post=post, comments=comments)
    return post_with_comments


@app.delete("/posts/delete_post/{post_id}", status_code=204)
# УДАЛЕНИЕ ПОСТА
async def delete_post(post_id: int, user: schemas.User = Depends(crud.get_current_user), db: Session = Depends(crud.get_db)):
    return await crud.delete_post(post_id, user, db)


"""РАБОТА С КОММЕНТАРИЯМИ"""
@app.post("/comments/", response_model=schemas.Comment)
# СОЗДАНИЕ КОММЕНТАРИЯ
async def create_comment(post_id: int, comment: schemas.CommentCreate, user: schemas.User = Depends(crud.get_current_user), db: Session = Depends(crud.get_db)):
    return await crud.create_comment(db=db, post_id=post_id, user=user, comment=comment)


@app.put("/comments/update_comment/{comment_id}", status_code=200)
# РЕДАКТИРОВАНИЕ КОММЕНТАРИЯ
async def update_comment(comment_id: int, comment: schemas.CommentCreate, user: schemas.User = Depends(crud.get_current_user), db: Session = Depends(crud.get_db)):
    return await crud.update_comment(comment_id, comment, user, db)


@app.delete("/comments/delete_comment/{comment_id}", status_code=204)
# УДАЛЕНИЕ КОММЕНТАРИЯ
async def delete_comment(comment_id: int, user: schemas.User = Depends(crud.get_current_user), db: Session = Depends(crud.get_db)):
    return await crud.delete_comment(comment_id, user, db)
