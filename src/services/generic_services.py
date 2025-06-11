# src/services/generic_service.py
"""
Generic service to fetch paginated, filtered, sorted data for any SQLAlchemy model.
Supports optional joins with custom response fields.
"""
import json
from typing import Any, Dict, List, Optional, Type, Union

from sqlalchemy import select, or_, and_, String, Text
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from src.schema.queries_params_schema import QueryParams


async def get_all(
    db: AsyncSession,
    model: Type[Any],
    params: QueryParams,
    joins: Optional[List[Dict[str, Union[str, List[str]]]]] = None
) -> Dict[str, Any]:
    """
    Fetch items of `model` with dynamic filtering, search, sorting, pagination.
    Optionally join related lists and include selected fields in response.

    :param db: AsyncSession
    :param model: SQLAlchemy ORM class
    :param params: QueryParams instance
    :param joins: list of dicts {"model": relation_name, "response": field or list of fields}
    :return: dict with keys data, total, page, limit
    """
    # Base query
    stmt: Select = select(model)

    # --- Apply joins ---
    if joins:
        for join_cfg in joins:
            rel_name = join_cfg.get("model")  # e.g. "Roles" -> attribute "roles"
            # normalize to attribute name
            attr = rel_name[0].lower() + rel_name[1:]
            if not hasattr(model, attr):
                raise ValueError(f"Unknown relation '{rel_name}' for {model.__name__}")
            stmt = stmt.join(getattr(model, attr))

    # --- Filtering ---
    if params.filter:
        try:
            flt: Dict[str, Any] = json.loads(params.filter)
        except ValueError:
            raise ValueError("`filter` must be valid JSON string.")
        for key, val in flt.items():
            parts = key.split('.')
            if len(parts) == 1:
                col = getattr(model, parts[0], None)
            else:
                rel_attr = getattr(model, parts[0], None)
                col = getattr(rel_attr.property.mapper.class_, parts[1], None)
            if col is None:
                raise ValueError(f"Invalid filter field '{key}'")
            if params.strict or not isinstance(val, str):
                stmt = stmt.where(col == val)
            else:
                stmt = stmt.where(col.ilike(f"%{val}%"))

    # --- Global search ---
    if params.query:
        tokens = [t.strip() for t in params.query.split(',') if t.strip()]
        and_conds = []
        for token in tokens:
            or_conds = []
            for col in model.__table__.columns:
                if isinstance(col.type, (String, Text)):
                    if params.strict:
                        or_conds.append(col == token)
                    else:
                        or_conds.append(col.ilike(f"%{token}%"))
            if or_conds:
                and_conds.append(or_(*or_conds))
        if and_conds:
            stmt = stmt.where(and_(*and_conds))

    # --- Sorting ---
    if params.order_by:
        raw = params.order_by
        direction = 'asc'
        if raw.startswith('-'):
            direction = 'desc'
            fld = raw[1:]
        elif raw.startswith('+'):
            fld = raw[1:]
        else:
            fld = raw
        # validate
        try:
            valid_cols = set(model.__table__.columns.keys())
        except (AttributeError, NoInspectionAvailable):
            valid_cols = set()
        if fld not in valid_cols:
            if params.strict:
                raise ValueError(f"Unknown order_by field '{fld}'")
            else:
                fld = None
        if fld:
            col = getattr(model, fld)
            stmt = stmt.order_by(col.desc() if direction == 'desc' else col.asc())

    # --- Pagination ---
    offset = (params.page - 1) * params.limit
    stmt = stmt.offset(offset).limit(params.limit)

    # Execute main query
    res = await db.execute(stmt)
    items = res.scalars().all()

    # Build response dicts
    data_list: List[Dict[str, Any]] = []
    for obj in items:
        # Convert ORM to dict
        data = {c.key: getattr(obj, c.key) for c in model.__table__.columns}
        # Add joins if requested
        if joins:
            for join_cfg in joins:
                rel_name = join_cfg['model']
                attr = rel_name[0].lower() + rel_name[1:]
                response_fields = join_cfg.get('response')
                rel_objs = getattr(obj, attr, []) or []
                # single field string
                if isinstance(response_fields, str):
                    data[attr] = [getattr(o, response_fields) for o in rel_objs]
                # list of fields
                elif isinstance(response_fields, list):
                    data[attr] = [
                        {f: getattr(o, f) for f in response_fields} for o in rel_objs
                    ]
        data_list.append(data)

    total = len(data_list)
    return {"data": data_list, "total": total, "page": params.page, "limit": params.limit}
