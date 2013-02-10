import copy
from django.utils import translation, functional
from django.core.mail.backends.dummy import EmailBackend as DummyEmailBackend
from classymail import EmailBuilder


class TestEmailBuilderClass(object):
    default_kwargs = {'to': ['test1@example.com'], 'cc': ['test2@example.com'],
                      'bcc': ['test3@example.com'], 'subject': "Test subject",
                      'connection': DummyEmailBackend(),
                      'from_email': 'admin@example.com',
                      'headers': {'X-Spam': 'Yes'}, 'body': 'Test',
                      'attachments': [('test.txt', 'Test', 'text/plain')]}

    def test_default_kwargs(self):
        """Check default message keyword arguments"""
        builder = EmailBuilder()
        kwargs = builder.get_message_kwargs()
        expected = {'to': None, 'cc': None, 'bcc': None, 'subject': '',
                    'connection': None, 'from_email': None, 'headers': None,
                    'attachments': None, 'body': ''}
        assert kwargs == expected

    def test_get_message_kwargs_method(self):
        """Checks if all kwargs can be changed using attributes"""
        kwargs = copy.deepcopy(self.default_kwargs)
        builder = EmailBuilder(**kwargs)
        assert builder.get_message_kwargs() == kwargs

    def test_subject_can_be_a_promise(self):
        """Subject can be a promise object (lazy translation)"""
        builder = EmailBuilder(subject=translation.ugettext_lazy("test subject"))
        kwargs = builder.get_message_kwargs()
        assert not isinstance(kwargs['subject'], functional.Promise)
        assert kwargs['subject'] == "test subject"

    def test_message_building(self):
        """
        Checks if e-mail class can be customized using mail_class and if it
        will receive all arguments it should
        """
        class Dummy(object):
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        kwargs = copy.deepcopy(self.default_kwargs)
        builder = EmailBuilder(mail_class=Dummy, **kwargs)
        msg = builder.build()
        assert isinstance(msg, Dummy)
        assert msg.kwargs == kwargs
