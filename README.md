# OSIS Internship

OSIS Internship is a web application to manage the internships of the 
students of medicine. Its main goal is to optimize the workload of assigning
students to internships available in hospitals throughout 12 distinct periods 
of the year where each period covers a medical specialty.

This application is part of [OSIS](osis), an umbrella project to manage the 
core business of higher education institutions. It is a Django application that
only works when installed together with OSIS. It cannot run separately because
it depends on the applications [base](base), [reference](reference) and 
[osis-common](osis-common).

![GIT submodule](https://uclouvain.github.io/osis-internship/images/github-repo-submodule.png) 

## Documentation

The documentation of the project is available at [https://uclouvain.github.io/osis-internship/]().

## Development

### Testing

To test the entire project before submitting pull request:

    $ python manage.py test

To test the application when an issue is solved:

    $ python manage.py test internship

To test faster when a problem is identified by the tests.

    $ python manage.py test --keepdb internship

To execute a specific test that is under development:

    $ python manage.py test internship.tests.utils.test_integer.IntegerTestCase.test_to_int

[OSIS]: https://www.github.com/uclouvain/osis
[base]: https://github.com/uclouvain/osis/tree/dev/base
[reference]: https://github.com/uclouvain/osis/tree/dev/reference
[osis-common]: https://github.com/uclouvain/osis-common