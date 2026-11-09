from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.crud.users import get_user_roles


def require_role(required_role: str):

    def role_checker(
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        roles = get_user_roles(db, current_user.user_id)

        role_names = [role.role_name for role in roles]

        if required_role not in role_names:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )

        return current_user

    return role_checker