from pydantic import Field, StrictStr

from app.request_models.request_base import RequestBase


class TelegramNotificationRequest(RequestBase):
    message: StrictStr = Field()
    has_mailing: StrictStr = Field()
