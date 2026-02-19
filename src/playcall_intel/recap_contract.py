from pydantic import BaseModel, Field


class GameRecapV1(BaseModel):
    paragraph_1: str = Field(..., description="2–4 sentences, grounded in provided stats.")
    paragraph_2: str = Field(..., description="2–4 sentences, grounded in provided stats.")
