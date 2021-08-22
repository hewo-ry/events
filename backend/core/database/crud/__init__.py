import uuid
import json

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, Tuple
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from pydantic import BaseModel
from core.database import models

ModelType = TypeVar("ModelType", bound=models.Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

FilterParseException = HTTPException(
    status_code=400, detail="Filter parsing failed. Invalid attributes present."
)

OrderParseException = HTTPException(
    status_code=400, detail="Order parsing failed. Invalid attributes present."
)


def parse_filter(filters: dict, parent: Any) -> Tuple[List[Any], list]:
    """
    Convert filter dict into filter list

    :param filters: Dict to be converted
    :param parent: Parent object
    :return: Filter list
    """
    new_filters = []
    joins = []

    for k, v in filters.items():

        # Detect comparison
        gt = "__gt" in k
        ge = "__ge" in k
        lt = "__lt" in k
        le = "__le" in k

        # Remove suffixes
        if gt or ge or lt or le:
            k = k[:-4]

        try:
            attr = getattr(parent, k)

            # Construct filter expressions
            if isinstance(v, dict):
                joins.append(attr.property.mapper.class_)
                joins.append(attr)
                fs, js = parse_filter(v, attr.property.mapper.class_)
                new_filters += fs
                joins += js
            elif gt:
                new_filters.append(attr > v)
            elif ge:
                new_filters.append(attr >= v)
            elif lt:
                new_filters.append(attr < v)
            elif le:
                new_filters.append(attr <= v)
            else:
                new_filters.append(attr == v)
        except AttributeError as e:
            raise FilterParseException from e

    return new_filters, joins


def parse_order(order: List[str], parent) -> List[str]:
    """
    Convert order list into usable version in SQLAlchemy
    :param order: Order list
    :param parent: Parent object
    :return: New order list
    """
    for i, v in enumerate(order):
        a = "__a" in v
        d = "__d" in v

        if a or d:
            v = v[:-3]

        if not hasattr(parent, v):
            raise OrderParseException

        order[i] = asc(v) if a and not d else desc(v) if not a and d else v
    return order


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """CRUD Base for other Models and Schemas"""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_count(self, db: Session) -> int:
        """
        Get total number of objects in database.
        :param db: Databse Session to be used
        """
        return db.query(self.model).count()

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Get Object by ID.
        :param db: Database Session to be used
        :param id: ID to be fetched with
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        all: bool = False,
        filters: Optional[Union[Dict, str]] = None,
        group: Optional[Union[List[str], str]] = None,
        order: Optional[Union[List[str], str]] = None
    ) -> Tuple[List[ModelType], int]:
        """
        Get multiple objects.
        :param db: Database Session to be used
        :param skip: How many objects to skip
        :param limit: How many objects will be returned
        :param all: Ignore skip and limit, return all
        :param filters: Filter objects by given values
        :param group: List of attributes to group by
        :param order: List of orders for attributes
        """
        q = db.query(self.model)

        if filters is not None:
            if isinstance(filters, str):
                filters = json.loads(filters)

            fs, joins = parse_filter(filters, self.model)

            if len(joins) > 0:
                q = q.join(*joins)

            q = q.filter(*fs)

        # Add grouping to query
        if group is not None:
            if isinstance(group, str):
                group = json.loads(group)

            q = q.group_by(*group)

        # Add ordering to query
        if order is not None:
            if isinstance(order, str):
                order = json.loads(order)

            q = q.order_by(*parse_order(order, self.model))

        if not all:
            final = q.offset(skip).limit(limit)
        else:
            final = q

        # Return partial list, and total count
        return final.all(), q.count()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new object
        :param db: Database Session to be used
        :param obj_in: Object to be created
        """
        obj_in_data = jsonable_encoder(obj_in)

        # New object
        db_obj = self.model(**obj_in_data)

        # Update database
        db.add(db_obj)
        db.commit()

        # Update object
        db.refresh(db_obj)

        return db_obj

    @classmethod
    def update(
        cls,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update existing object
        :param db: Database Session to be used
        :param db_obj: Object to be updated
        :param obj_in: Update data
        """
        obj_data = jsonable_encoder(db_obj)

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        # Combine new data with the existing object
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        # Update database
        db.add(db_obj)
        db.commit()

        # Update object
        db.refresh(db_obj)

        return db_obj

    def remove(self, db: Session, *, id: uuid.UUID) -> ModelType:
        """
        Remove existing object
        :param db: Database Session to be used
        :param id: UUID of the object
        """
        obj = db.query(self.model).get(id)

        # Delete from database
        db.delete(obj)
        db.commit()

        return obj
