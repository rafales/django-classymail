"""
classymail.base
~~~~~~~~~~~~~~~

Module which defines `EmailBuilder` class - a base class for building e-mail
messages.
"""
from django.core import mail
from django.utils import encoding


class EmailBuilder(object):
    """
    Main purpose of this class is to build an EmailMessage instance.

    This class can be instantiated with kwargs which will be stored as
    attributes on new builder instance (similar to django class based views).
    This allows for nice parametrization::

        MyMail(to=[user.email]).build().send()

    You can override a lot of hook-methods to change message that is being
    built - all of them start with 'get_'.

    If you wish to customize e-mail instance even further then you can override
    `get_message()` method. You shouldn't override `build()` method unless you
    want to do some kind of isolation (like changing timezone or language for
    the time of building e-mail message).
    """
    to = None
    cc = None
    bcc = None
    subject = ''
    connection = None
    from_email = None
    headers = None
    body = ''
    attachments = None
    mail_class = mail.EmailMessage

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if not hasattr(self.__class__, key):
                raise TypeError("%s received an invalid keyword %r."
                                "Only arguments that are already attributes"
                                "of this class are accepted." %
                                (self.__class__.__name__, key))
            setattr(self, key, value)

    def build(self):
        """
        Builds an e-mail message instance.

        Don't override this method unless you want to do some kind of isolation,
        like changing timezone or language for the time of building a message.
        """
        return self.get_message()

    @classmethod
    def send(cls, **kwargs):
        """
        A shortcut which builds and sends message.
        """
        builder = cls(**kwargs)
        builder.build().send()

    # Methods meant to be overridden by subclasses

    def get_to(self):
        """
        Returns list of recipients for "To" header.
        """
        return self.to

    def get_cc(self):
        """
        Returns list of recipients for "Cc" header.
        """
        return self.cc

    def get_bcc(self):
        """
        Returns list of recipients for "Bcc" header.
        """
        return self.bcc

    def get_subject(self):
        """
        Returns subject of an e-mail message.
        """
        return self.subject

    def get_connection(self):
        """
        Returns connection for message or None to use default backend.
        """
        return self.connection

    def get_from_email(self):
        """
        Returns e-mail from which this message will be sent or None to use
        default value from settings.
        """
        return self.from_email

    def get_headers(self):
        """
        Returns a dictionary of extra e-mail headers.
        """
        return self.headers

    def get_body(self):
        """
        Returns plain text to be used as message body.
        """
        return self.body

    def get_attachments(self):
        """
        Returns list of attachments or None.
        """
        return self.attachments

    def get_message(self):
        """
        Returns the e-mail message.
        """
        kwargs = self.get_message_kwargs()
        return self.mail_class(**kwargs)

    def get_message_kwargs(self):
        """
        Returns arguments for message class.
        """
        return {
            'to': self.get_to(),
            'cc': self.get_cc(),
            'bcc': self.get_bcc(),
            'subject': encoding.force_text(self.get_subject()),
            'connection': self.get_connection(),
            'from_email': self.get_from_email(),
            'headers': self.get_headers(),
            'attachments': self.get_attachments(),
            'body': self.get_body()
        }
