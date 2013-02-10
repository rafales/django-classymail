from setuptools import setup


setup(
    name="django-classymail",
    version="0.1dev",
    description='E-mails in Django. Classy.',
    author='Rafal Stozek',
    license='BSD',

    packages=['classymail'],

    install_requires=[
        'premailer',
        'cssselect',
    ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ]
)