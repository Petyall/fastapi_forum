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
async def get_user_by_email(email: str, db: Session):
    """Асинхронная функция, для поиска пользователя среди БД по атрибуту email"""
    return db.query(models.User).filter(models.User.email == email).first()

async def create_user(user: schemas.UserCreate, db: Session):
    """Асинхронная функция, для создания и сохранения в БД пользователя"""
    user_obj = models.User(
        email=user.email, first_name=user.first_name, last_name=user.last_name,hashed_password=hash.bcrypt.hash(user.hashed_password))
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

async def authenticate_user(email: str, password: str, db: Session):
    """Асинхронная функция, аутентификации пользователя с обработкой ошибок"""
    user = await get_user_by_email(db=db, email=email)
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user

async def create_token(user: models.User):
    """Асинхронная функция, генерирующая JWT токен"""
    user_obj = schemas.User.from_orm(user)
    token = jwt.encode(user_obj.dict(), JWT_SECRET)
    return dict(access_token=token, token_type="bearer")

async def get_current_user(db: Session = fastapi.Depends(get_db), token: str = fastapi.Depends(oauth2schema)):
    """Асинхронная функция, возвращающая информацию о пользователе"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(models.User).get(payload["id"])
    except:
        raise fastapi.HTTPException(
            status_code=401, detail="Неправильный пароль или почта")
    return schemas.User.from_orm(user)


"""РАБОТА С ПОСТАМИ"""
async def create_post(db: Session, post: schemas.PostCreate, user: schemas.User):
    """Асинхронная функция, сохраняющая пост в БД"""
    post = models.Post(**post.dict(), owner_id=user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

async def update_post(post_id: int, post: schemas.PostCreate, user: schemas.User, db: Session):
    """Асинхронная функция, изменяющая существующий пост"""
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise fastapi.HTTPException(status_code=404, detail="Пост не найден")
    if db_post.owner_id == user.id:
        db_post.title = post.title
        db_post.description = post.description
        db.commit()
        return {"message": "Пост успешно изменен"}
    else:
        raise fastapi.HTTPException(status_code=403, detail="Отказано в доступе")

async def get_posts(db:Session, skip: int = 0, limit: int = 100):
    """Асинхронная функция, возвращающая все посты"""
    return db.query(models.Post).offset(skip).limit(limit).all()

async def get_post(db: Session, post_id: int):
    """Асинхронная функция, возвращающая пост по post_id"""
    return db.query(models.Post).filter(models.Post.id == post_id).first()

async def delete_post(post_id: int, user: schemas.User, db: Session):
    """Асинхронная функция, удаляющая пост вместе с комментариями"""
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise fastapi.HTTPException(status_code=404, detail="Пост не найден")
    if db_post.owner_id == user.id:
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
async def create_comment(db:Session, post_id: int, user: schemas.User, comment: schemas.CommentCreate):
    """Асинхронная функция, сохраняющая комментарий в БД"""
    db_comment = models.Comment(text=comment.text, post_id=post_id, owner_id=user.id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

async def get_comments(db: Session, post_id: int):
    """Асинхронная функция, возвращающая все комментарии к конкретному посту"""
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).all()

async def update_comment(comment_id: int, comment: schemas.CommentCreate, user: schemas.User, db: Session):
    """Асинхронная функция, изменяющая существующий комментарий"""
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not db_comment:
        raise fastapi.HTTPException(status_code=404, detail="Комментарий не найден")
    if db_comment.owner_id == user.id:
        db_comment.text = comment.text
        db.commit()
        return {"message": "Комментарий успешно изменен"}
    else:
        raise fastapi.HTTPException(status_code=403, detail="Отказано в доступе")

async def delete_comment(comment_id: int, user: schemas.User, db: Session):
    """Асинхронная функция, удаляющая комментарий пользователем"""
    db_comment = db.query(models.Comment).filter_by(owner_id = user.id).filter(models.Comment.id == comment_id).first()
    if not db_comment:
        raise fastapi.HTTPException(status_code=404, detail="Комментарий не найден")
    db.delete(db_comment)
    db.commit()   
    return {"message", "Успешно удалено"}
