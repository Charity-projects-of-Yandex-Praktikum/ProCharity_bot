from pydantic import Field, StrictStr

from app.request_models.request_base import RequestBase
from core.services.mailing_type import MailingType, MailingNumber


class TelegramNotificationRequest(RequestBase):
    message: StrictStr = Field()
    mailing_type: MailingType = MailingType.subscribed
    mailing_number: MailingNumber = MailingNumber.subscribed

    class Config:
        use_enum_values = True
