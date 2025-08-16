from __future__ import annotations
import os
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")


def get_admin(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    is_user = secrets.compare_digest(credentials.username, ADMIN_USER)
    is_pass = secrets.compare_digest(credentials.password, ADMIN_PASS)
    if not (is_user and is_pass):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Basic"})
    return credentials.username
