# src/services/generic_service.py
"""
Generic service to fetch paginated, filtered, sorted data for any SQLAlchemy model.
Supports optional joins with custom response fields.
"""
import json
from typing import Any, Dict, List, Optional, Type, Union

from sqlalchemy import select, or_, and_, String, Text, func
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from src.schema.queries_params_schema import QueryParams


def build_query(
        model, params: QueryParams, joins, external_query=None
) -> Select:
    """ Function combine all query select, filter, and sorting """
    stmt = select(model) if external_query is None else external_query
    stmt = apply_joins(stmt, model, joins)
    stmt = apply_filter(stmt, model, params)
    stmt = apply_search(stmt, model, params)
    stmt = apply_sorting(stmt, model, params)
    return stmt


def object_to_dict(obj_items, model, joins = None):
    """ Convert object model iterable to List[dict] """
    data_list: List[Dict[str, Any]] = []
    for obj in obj_items:
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
    return data_list


async def get_all(db: AsyncSession,
                  model,
                  params: QueryParams,
                  joins: Optional[List[Dict[str, Union[str, List[str]]]]] = None,
                  external_query=None
                  ):
    base_stmt = build_query(model, params, joins, external_query)

    # count total
    total = await count_total(db, base_stmt)

    # apply pagination
    stmt = apply_pagination(base_stmt, params)

    # execute
    res = await db.execute(stmt)
    obj_items = res.scalars().all()

    data_list = object_to_dict(obj_items, model, joins)

    return {
        "data": data_list,
        "total": total,
        "page": params.page,
        "limit": params.limit
    }


def build_base_query(model: Type[Any]) -> Select:
    return select(model)


def apply_joins(stmt: Select, model: Type[Any], joins: List[Dict]) -> Select:
    """ Apply joins models and add foreign items """
    if joins:
        for join_cfg in joins:
            attr = join_cfg["model"][0].lower() + join_cfg["model"][1:]
            stmt = stmt.join(getattr(model, attr))
    return stmt


def apply_filter(stmt: Select, model: Type[Any], params: QueryParams) -> Select:
    """ Filter items by key - value """
    if not params.filter:
        return stmt
    flt = json.loads(params.filter)
    for key, val in flt.items():
        parts = key.split('.')
        if len(parts) == 1:
            col = getattr(model, parts[0], None)
        else:
            rel_attr = getattr(model, parts[0], None)
            col = getattr(rel_attr.property.mapper.class_, parts[1], None)
        if col is not None:
            stmt = stmt.where(col == val)
    return stmt


def apply_search(stmt: Select, model: Type[Any], params: QueryParams) -> Select:
    """ Query find items """
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
    return stmt


def apply_sorting(stmt: Select, model: Type[Any], params: QueryParams) -> Select:
    """ Sorting by order_by """
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
    return stmt


def apply_pagination(stmt: Select, params: QueryParams) -> Select:
    """ Make pagination with offset and limit """
    offset = (params.page - 1) * params.limit
    return stmt.offset(offset).limit(params.limit)


async def count_total(db, stmt):
    """ Counting query total items """
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()
    return total
