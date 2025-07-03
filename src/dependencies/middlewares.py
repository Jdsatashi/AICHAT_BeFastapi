import re
import time

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.status import HTTP_403_FORBIDDEN

from src.db.database import get_db_instance
from src.handlers.perm import get_perm_name
from src.models import Users, Permission, Role
from src.services.auth_services import check_access_token
from src.utils.api_path import RoutePaths, route_model_map, route_model_pk_map
from src.utils.logs import debug_log
from src.utils.perm_actions import method_map, actions


class PermissionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        debug_log(" -- Middleware function -- ")
        start_time = time.time()

        route_path = request.url.path
        debug_log(f"Request path: {route_path}")

        path_params = request.scope.get("path_params", {})

        debug_log(f"Path parameters: {path_params}")

        if (route_path.startswith("/docs")
                or route_path.startswith("/openapi.json")
                or route_path == RoutePaths.API_PREFIX
                or route_path.startswith(RoutePaths.API_PREFIX + RoutePaths.Auth.init)
                or not route_path.startswith(RoutePaths.API_PREFIX)
        ):
            # Skip permission check for documentation and API prefix
            debug_log(f"Time validation: {time.time() - start_time}")
            debug_log("Skipping permission for API prefix")
            return await call_next(request)

        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            debug_log(f"Time validation: {time.time() - start_time}")
            debug_log("Missing or invalid Authorization header")
            return JSONResponse(
                status_code=HTTP_403_FORBIDDEN,
                content={"detail": "Missing or invalid Authorization header"}
            )

        # Extract token from Authorization header
        token = auth_header.split(" ")[1]

        db = await get_db_instance()
        try:
            # Check access token and decode to get payload
            payload = await check_access_token(token, db)
            if isinstance(payload, str):
                debug_log(f"Time validation: {time.time() - start_time}")
                debug_log(f"Invalid access token in payload")
                return JSONResponse(
                    status_code=HTTP_403_FORBIDDEN,
                    content={"detail": f"Access token {payload}"}
                )

            # Extract user ID from payload
            user_id = payload.user_id

            # If user_id is not present in the payload, raise an error
            if not user_id:
                debug_log(f"Time validation: {time.time() - start_time}")
                debug_log("User ID not found in token payload")
                return JSONResponse(
                    status_code=HTTP_403_FORBIDDEN,
                    content={"detail": "Invalid data payload"}
                )

            get_user = await db.execute(
                select(Users)
                .options(
                    selectinload(Users.roles).selectinload(Role.permissions)
                )
                .where(Users.id == user_id)
            )
            user = get_user.scalar_one_or_none()
            if not user:
                debug_log(f"Time validation: {time.time() - start_time}")
                debug_log("User not found in database")
                return JSONResponse(
                    status_code=HTTP_403_FORBIDDEN,
                    content={"detail": "User not found"}
                )

            if user.is_active is False:
                debug_log(f"Time validation: {time.time() - start_time}")
                debug_log("User is inactive")
                return JSONResponse(
                    status_code=HTTP_403_FORBIDDEN,
                    content={"detail": "User is inactive"}
                )
            debug_log(f"User: {user.roles}")
            permissions = set()
            for role in user.roles:
                for perm in role.permissions:
                    permissions.add(perm.name)
        finally:
            await db.close()

        method = request.method

        clean_path = clean_route_path(route_path)

        model_name, object_id = extract_model_and_object_id(clean_path)
        debug_log(object_id)
        if not model_name:
            debug_log(f"Time validation: {time.time() - start_time}")
            return await call_next(request)

        action = method_map[method]
        debug_log(permissions)
        if check_all_perm(model_name, action, permissions):
            return await call_next(request)
        permission_needed = get_perm_name(model_name, action, object_id)
        debug_log(f"Permission needed: {permission_needed}")
        if permission_needed in permissions:
            depend_on = await get_permission_depend_on(db, permission_needed)
            debug_log(f"Depend on permission: {depend_on}")
            if depend_on:
                if depend_on not in permissions:
                    debug_log(f"Permission depend: {depend_on}")
                    debug_log(f"Time validation: {time.time() - start_time}")
                    return JSONResponse(
                        status_code=HTTP_403_FORBIDDEN,
                        content={"detail": f"Permission {depend_on} is required"}
                    )
            debug_log(f"Time validation: {time.time() - start_time}")
            return await call_next(request)

        debug_log(f"Time validation: {time.time() - start_time}")
        return JSONResponse(
            status_code=HTTP_403_FORBIDDEN,
            content={"detail": f"Permission {method_map[method]} on {model_name} is required"}
        )


def extract_model_and_object_id(route_path: str) -> tuple[str | None, int | None]:
    for pattern, model_name, param_key in route_model_pk_map:
        match = re.match(f"^{pattern}", route_path)
        if match:
            object_id = None
            if param_key and param_key in match.groupdict():
                object_id = int(match.group(param_key))
            return model_name, object_id
    return None, None


def clean_route_path(route_path: str) -> str:
    if route_path.startswith(RoutePaths.API_PREFIX):
        return route_path[len(RoutePaths.API_PREFIX):] or "/"
    return route_path


def get_model_name_from_path(route_path: str) -> str | None:
    for pattern, model in route_model_map.items():
        if re.match(f"^{pattern}", route_path):
            return model
    return None


def check_all_perm(model_name: str, action: str, permissions) -> bool:
    permission_all = get_perm_name(model_name, actions.all)
    permission_group = get_perm_name(model_name, action)

    if permission_all in permissions or permission_group in permissions:
        return True

    return False


async def get_permission_depend_on(db, permission_name: str) -> str | None:
    result = await db.execute(
        select(Permission).where(Permission.name == permission_name)
    )
    perm = result.scalar_one_or_none()
    if perm and perm.depend_on:
        return perm.depend_on
    return None
