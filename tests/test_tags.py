import mock
import pytest
from django.contrib.sites.models import Site
from django.template import Template, Context
from classymail.templatetags.classymail_tags import build_absolute_url


class TestEmailUrlTag(object):
    @mock.patch('classymail.utils.build_absolute_url')
    def test_build_absolute_url_called(self, m):
        """
        Checks if build_absolute_url() is called correctly by
        {% build_absolute_url %} tag.
        """
        m.return_value = 'http://example.com/test/'
        s = Site(domain='spam', name='spam')
        context = {'site': s}

        ret = build_absolute_url(context, path='/test/', foo='bar')

        m.assert_called_once_with(
            path='/test/', object=None, site=s, builder=None,
            foo='bar', context=context, request=None)

        assert ret == m.return_value

    def test_path_and_object_missing(self):
        """
        Checks if TypeError is raised when both path and object params
        are missing.
        """
        with pytest.raises(TypeError):
            build_absolute_url({}, object=None, path=None)

    def test_tag_works_in_template(self):
        """
        Checks if tag works when used in e-mail.
        """
        s = Site(domain='spam', name='spam')
        context = {'site': s}
        tpl = Template(
            """
            {% load classymail_tags %}
            {% build_absolute_url path='/test/' %}
            """
        )

        body = tpl.render(Context(context))
        assert body.strip() == 'http://spam/test/'
