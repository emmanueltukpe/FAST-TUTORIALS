from fastapi import Response, HTTPException, status, Depends, APIRouter
from typing import List
from sqlalchemy.orm import Session
import app.models as models
from app.db import get_db
from app.schemas import User, ResponseUser

router = APIRouter(prefix="/users", tags=['Users'])

@router.get("/", response_model=List[ResponseUser])
def get_all(db: Session = Depends(get_db)):
    # cursor.execute(""" SELECT * FROM users""")
    # user = cursor.fetchall()
    users = db.query(models.User).all()
    return users


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ResponseUser)
def create_post(user: User, db: Session = Depends(get_db)):
    # cursor.execute(""" INSERT INTO users (name, price, is_loved) VALUES (%s, %s, %s) RETURNING * """,
    #                (user.name, user.price, user.is_loved))
    # users = cursor.fetchone()
    # conn.commit()
    users = models.User(**user.dict())
    db.add(users)
    db.commit()
    db.refresh(users)
    return users


@router.get("/{id}", response_model=ResponseUser)
def get_user(id: int, db: Session = Depends(get_db)):
    # cursor.execute(""" SELECT * FROM users WHERE id = %s""", (str(id)))
    # user = cursor.fetchone()
    user = db.query(models.User).filter(models.User.id == id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db)):
    # cursor.execute(
    #     """ DELETE FROM users WHERE id = %s returning *""", (str(id)))
    # user = cursor.fetchone()
    # conn.commit()
    user = db.query(models.User).filter(models.User.id == id)
    if user.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{user_id}", status_code=status.HTTP_202_ACCEPTED, response_model=ResponseUser)
def update_user(user_id: int, request: User, db: Session = Depends(get_db)):
    # cursor.execute(""" UPDATE users SET name = %s, price = %s, is_loved = %s WHERE id = %s RETURNING * """,
    #                (request.name, request.price, request.is_loved, str(user_id)))
    # user = cursor.fetchone()
    # conn.commit()
    user = db.query(models.User).filter(models.User.id == user_id)
    if user.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.update(request.dict(), synchronize_session=False)
    db.commit()
    return user.first()