from sqlalchemy.orm import Session
import models, schemas
import database
import fastapi
from fastapi import security
import jwt
from passlib import hash

oauth2schema = security.OAuth2PasswordBearer(tokenUrl="/api/token")
JWT_SECRET = "myjwtsecret"


"""РАБОТА С БД"""
def get_db():
    """Функция, возвращающая БД для работы с ней"""
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_database():
    """Функция, создающая БД, если она не существует 
    (вызывается обычно один раз в самом начале создания проекта)"""
    return database.Base.metadata.create_all(bind=database.engine)


"""РАБОТА С ПОЛЬЗОВАТЕЛЯМИ"""
def get_user(db:Session, user_id:int):
    """Функция, возвращающая пользователя по user_id"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db:Session, email:str):
    """Функция, возвращающая пользователя по email"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db:Session, skip: int = 0, limit: int = 100):
    """Функция, возвращающая всех пользователей"""
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    """Функция, сохраняющая пользователя в БД"""
    hashed_password=hash.bcrypt.hash(user.hashed_password)
    db_user = models.User(email=user.email, 
                        first_name=user.first_name,
                        last_name=user.last_name,
                        hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


"""РАБОТА С ПОСТАМИ"""
def create_post(db: Session, post: schemas.PostCreate, user_id: int):
    """Функция, сохраняющая пост в БД"""
    db_post = models.Post(**post.dict(), owner_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def update_post(post_id: int, post: schemas.PostCreate, owner_id: int, db: Session):
    """Функция, изменяющая существующий пост"""
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise fastapi.HTTPException(status_code=404, detail="Пост не найден")
    if db_post.owner_id == owner_id:
        db_post.title = post.title
        db_post.description = post.description
        db.commit()
        return {"message": "Пост успешно изменен"}
    else:
        raise fastapi.HTTPException(status_code=403, detail="Отказано в доступе")


def get_posts(db:Session, skip: int = 0, limit: int = 100):
    """Функция, возвращающая все посты"""
    return db.query(models.Post).offset(skip).limit(limit).all()


def get_post(db: Session, post_id: int):
    """Функция, возвращающая пост по post_id"""
    return db.query(models.Post).filter(models.Post.id == post_id).first()


def delete_post(post_id: int, owner_id: int, db: Session):
    """Функция, удаляющая пост вместе с комментариями"""
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise fastapi.HTTPException(status_code=404, detail="Пост не найден")
    if db_post.owner_id == owner_id:
        db_comments = db.query(models.Comment).filter_by(post_id=post_id).all()
        if db_comments:
            for db_comment in db_comments:
                db.delete(db_comment)
            db.delete(db_post)
            db.commit()
            return {"message", "Успешно удалено"}
        else:
            db.delete(db_post)
            db.commit()
            return {"message", "Успешно удалено"}
    else:
        raise fastapi.HTTPException(status_code=403, detail="Отказано в доступе")


"""РАБОТА С КОММЕНТАРИЯМИ"""
def create_comment(db:Session, post_id: int, user_id: int, comment: schemas.CommentCreate):
    """Функция, сохраняющая комментарий в БД"""
    db_comment = models.Comment(text=comment.text, post_id=post_id, owner_id=user_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comments(db: Session, post_id: int):
    """Функция, возвращающая все комментарии к конкретному посту"""
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).all()


def update_comment(comment_id: int, comment: schemas.CommentCreate, owner_id: int, db: Session):
    """Функция, изменяющая существующий комментарий"""
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not db_comment:
        raise fastapi.HTTPException(status_code=404, detail="Комментарий не найден")
    if db_comment.owner_id == owner_id:
        db_comment.text = comment.text
        db.commit()
        return {"message": "Комментарий успешно изменен"}
    else:
        raise fastapi.HTTPException(status_code=403, detail="Отказано в доступе")
    

def delete_comment(comment_id: int, owner_id: int, db: Session):
    """Функция, удаляющая комментарий пользователем"""
    db_comment = db.query(models.Comment).filter_by(owner_id = owner_id).filter(models.Comment.id == comment_id).first()
    if not db_comment:
        raise fastapi.HTTPException(status_code=404, detail="Комментарий не найден")
    db.delete(db_comment)
    db.commit()   
    return {"message", "Успешно удалено"}


