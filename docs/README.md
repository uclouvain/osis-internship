# Documentation

To build the documentation:

    $ python3 build.py

To know more about what the build can do for you:

    $ python3 build.py -h

While maintaining `build.py`, you can run its specific tests this way:

    $ cd ~/python/projects/osis/osis
    $ source venv/bin/activate
    (venv) $ python -m unittest internship/tests/docs/test_build.py