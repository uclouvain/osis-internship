# OSIS Internship

OSIS Internship is an application that is part of [OSIS].

## Documentation

Visit the project website for the latest news, to read the documentation, to
meet the community and to learn how to contribute: http://uclouvain.github.io/osis.
You can find the technical documentation in the
[`doc` folder](https://github.com/uclouvain/osis/tree/dev/doc) of the source code.
There you learn:
- how to prepare your develop environment (technical-manual.adoc)
- how to install and configure OSIS (technical-manual.adoc)
- how the data is organized and (data-manual.adoc)
- how to use the application (user-manual.adoc)

## Project

OSIS is not a final product yet. It is still an on going project with ambitious
goals and deadlines. The good news is that we are already using it in production
because what is available complements or replaces existing business applications.

## Test

To test the entire project before submitting pull request:

    $ python manage.py test

To test the application when an issue is solved:

    $ python manage.py test internship

To test faster when a problem is identified by the tests.

    $ python manage.py test --keepdb internship

To execute a specific test that is under development:

    $ python manage.py test internship.tests.utils.test_integer.IntegerTestCase.test_to_int

[OSIS](https://www.github.com/uclouvain/osis)
[Python](https://www.python.org/) 3.4,
[HTML5](https://www.w3.org/TR/html5/) and uses
[DJango](https://www.djangoproject.com/) 1.11 as web framework.
To know more about the code and the collaboration of the community, please visit
our [OpenHub](https://www.openhub.net/p/osis-louvain) page.

