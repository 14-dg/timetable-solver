from pydantic import BaseModel, Field, HttpUrl


class TimetableTaskRequest(BaseModel):
    webhook_url: HttpUrl | None = Field(default=None, description="The URL to call once the computation is complete.")