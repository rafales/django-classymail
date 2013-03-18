Django-ClassyMail
=================

.. image:: https://secure.travis-ci.org/rafales/django-classymail.png?branch=master
   :target: http://travis-ci.org/rafales/django-classymail

Django makes it really easy to send simple e-mail messages. But e-mails
sometimes gets really complicated and un-DRY. That's where ClassyMail
steps in.

Django-ClassyMail is a library for building e-mail messages in a fashion
similar to django's class based views.

You can create mixins, override attributes with keyword arguments and
there's a lot of builtin functionality. Just like class based views.

Django-ClassyMail will handle css inlining, timezone, language and urls
for you.

Read the docs for more info:

https://django-classymail.readthedocs.org/en/latest/

And here's an example::

    class UserEmail(ClassyMail):
        """
        Sets language and timezone according to user preferences, adds "user" to
        template context and sets recipient to user's email address.
        """
        user = None

        def get_timezone(self):
            return self.user.get_profile().timezone

        def get_language(self):
            return self.user.get_profile().language

        def get_to(self):
            return [self.user.email]

        def get_context_data(self):
            data = super(UserMixin, self).get_context_data()
            data['user'] = self.user
            return data

    class WelcomeEmail(UserEmail):
        html_template_name = 'emails/welcome.html'
        text_template_name = 'emails/welcome.txt'

        def get_subject(self):
            return _("Welcome %s! Thanks for joining us!") % self.user.first_name

