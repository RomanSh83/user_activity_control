from pydantic import BaseModel, RootModel


class CategoryParamsSchema(BaseModel):
    name: str


class CategorySchema(CategoryParamsSchema):
    category_id: str


class CategoryParamsUpdateSchema(BaseModel):
    name: str | None = None


class CategoriesSchema(RootModel):
    root: dict[str, CategoryParamsSchema]
