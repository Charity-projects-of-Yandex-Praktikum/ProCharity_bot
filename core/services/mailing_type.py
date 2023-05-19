from enum import Enum, IntEnum


class MailingType(str, Enum):
    """
    This class implements enumeration.
    """
    subscribed = 'subscribed'
    unsubscribed = 'unsubscribed'
    all = 'all'


class MailingNumber(IntEnum):
    subscribed = 1
    unsubscribed = 2
    all = 3
