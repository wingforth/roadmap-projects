from enum import StrEnum
from datetime import datetime, timedelta, UTC

from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator


class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"


class SortBy(StrEnum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    STATUS = "status"


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserRegisterSchema(UserLoginSchema):
    name: str = Field(min_length=1)

    @field_validator("name", mode="after")
    @classmethod
    def strip(cls, val: str) -> str:
        return val.strip()


class TaskCreateSchema(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)

    model_config = ConfigDict(str_strip_whitespace=True)


class TaskUpdateSchema(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    description: str | None = Field(default=None, min_length=1)
    status: TaskStatus | None = None

    model_config = ConfigDict(str_strip_whitespace=True, use_enum_values=True)


class QueryParametersSchema(BaseModel):
    page_num: int = Field(default=1, gt=0, alias="page")
    page_size: int = Field(gt=0, alias="limit")
    dates: tuple[datetime, datetime] | None = None
    search: str | None = None
    sort_by: SortBy | None = Field(default=None, alias="sortBy")
    sort_order: SortOrder | None = Field(default=None, alias="sortOrder")

    model_config = ConfigDict(str_strip_whitespace=True, use_enum_values=True)

    @field_validator("sort_by", mode="before")
    @classmethod
    def _normalize_sort_by(cls, val) -> str | None:
        if not val:
            return None
        if isinstance(val, SortBy):
            return val
        s = str(val)
        mapping = {"createdAt": "created_at", "updatedAt": "updated_at"}
        return mapping.get(s, s)

    @field_validator("dates", mode="before")
    @classmethod
    def _parse_date_range(cls, val) -> tuple[datetime, datetime] | None:
        """
        Inclusive date range in ISO format (`YYYY-MM-DD`) separated by comma, for example '2000-08-04,2000-11-12'.
        If only a date provided, it indicates that single day, for example '2000-08-21'.
        """
        if not val:
            return None
        parts = [s.strip() for s in val.split(",")]
        if len(parts) == 1:
            start = datetime.fromisoformat(parts[0]).astimezone(UTC)
            end = start + timedelta(days=1)
        elif len(parts) == 2:
            start, end = (
                datetime.fromisoformat(parts[0]).astimezone(UTC),
                datetime.fromisoformat(parts[1]).astimezone(UTC) + timedelta(days=1),
            )
        else:
            raise ValueError("`date` field must be an ISO format date or two ISO format dates separated by a comma.")
        return start, end
