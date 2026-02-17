from pydantic import BaseModel


class CategorySchema(BaseModel):
    slug: str
    name: str
