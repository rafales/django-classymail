from django.utils import timezone, translation


class isolate_timezone(object):
    """
    This context manager makes sure that any change to an active timezone
    will be reverted.
    """
    def __enter__(self):
        self.timezone = getattr(timezone._active, 'value', None)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.timezone is None:
            timezone.deactivate()
        else:
            timezone.activate(self.timezone)


class isolate_language(object):
    """
    This context manager makes sure that any change to an active timezone
    will be reverted.
    """
    def __enter__(self):
        self.language = translation.get_language()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.language:
            translation.deactivate()
        else:
            translation.activate(self.language)
