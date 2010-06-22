
from dbus.exceptions import DBusException


def retry(connect, func):
    """
    Call a function, and re-try if there was a DBus connection issue.
    """
    try:
        return func()
    except DBusException, e:
        # only handle connection errors
        if 'org.freedesktop.DBus.Error' not in e._dbus_error_name:
            raise
        connect()
        return func()
