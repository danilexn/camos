from datetime import datetime
from typing import Callable, Sequence, Tuple
from enum import auto, Enum, EnumMeta

name2num = {
    "error": 40,
    "warning": 30,
    "info": 20,
    "debug": 10,
    "none": 0,
}

ActionSequence = Sequence[Tuple[str, Callable[[], None]]]


class StringEnumMeta(EnumMeta):
    def __getitem__(self, item):
        """set the item name case to uppercase for name lookup"""
        if isinstance(item, str):
            item = item.upper()

        return super().__getitem__(item)

    def __call__(
        cls, value, names=None, *, module=None, qualname=None, type=None, start=1,
    ):
        """set the item value case to lowercase for value lookup"""
        # simple value lookup
        if names is None:
            if isinstance(value, str):
                return super().__call__(value.lower())
            elif isinstance(value, cls):
                return value
            else:
                pass

        # otherwise create new Enum class
        return cls._create_(
            value, names, module=module, qualname=qualname, type=type, start=start,
        )

    def keys(self):
        return list(map(str, self))


class StringEnum(Enum, metaclass=StringEnumMeta):
    def _generate_next_value_(name, start, count, last_values):
        """autonaming function assigns each value its own name as a value"""
        return name.lower()

    def __str__(self):
        """String representation: The string method returns the lowercase
        string of the Enum name
        """
        return self.value


class NotificationSeverity(StringEnum):
    """Severity levels for the notification dialog.  Along with icons for each."""

    ERROR = auto()
    WARNING = auto()
    INFO = auto()
    DEBUG = auto()
    NONE = auto()

    def as_icon(self):
        return {
            self.ERROR: "ⓧ",
            self.WARNING: "⚠️",
            self.INFO: "ⓘ",
            self.DEBUG: "🐛",
            self.NONE: "",
        }[self]

    def __lt__(self, other):
        return name2num[str(self)] < name2num[str(other)]

    def __le__(self, other):
        return name2num[str(self)] <= name2num[str(other)]

    def __gt__(self, other):
        return name2num[str(self)] > name2num[str(other)]

    def __ge__(self, other):
        return name2num[str(self)] >= name2num[str(other)]


class Notification:
    """A Notifcation event.  Usually created by :class:`NotificationManager`.
    Parameters
    ----------
    message : str
        The main message/payload of the notification.
    severity : str or NotificationSeverity, optional
        The severity of the notification, by default
        `NotificationSeverity.WARNING`.
    actions : sequence of tuple, optional
        Where each tuple is a `(str, callable)` 2-tuple where the first item
        is a name for the action (which may, for example, be put on a button),
        and the callable is a callback to perform when the action is triggered.
        (for example, one might show a traceback dialog). by default ()
    """

    def __init__(
        self, message: str, severity: str, actions: ActionSequence = (), **kwargs,
    ):
        self.severity = NotificationSeverity(severity)
        self.message = message
        self.actions = actions
        self.source = "CaMOS"

        # let's store when the object was created;
        self.date = datetime.now()
