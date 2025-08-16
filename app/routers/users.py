from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core import schemas
from ..core.db import get_db
from ..core.security import get_current_user
from ..core.models import User

router = APIRouter()

@router.get("/me", response_model=schemas.UserOut)
def read_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return current_user
