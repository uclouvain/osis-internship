# OSIS-Louvain

OSIS stands for **Open Student Information System**. It's an application designed to manage the core business of higher education institutions, such as universities, faculties, institutes and professional schools. The core business involves the administration of students, teachers, courses, programs and so on.

This application is designed as a module of [Odoo](https://www.odoo.com), a modular ERP framework written in Python.

[![Join the chat at https://gitter.im/uclouvain/OSIS-Louvain](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/uclouvain/OSIS-Louvain?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

## Contributing to the Project

If you wish to point out an issue in the application or propose a new feature, you can do so by filing a GitHub issue at https://github.com/uclouvain/osis-louvain/issues.

### 

### Updating your Fork

It's a good practice to update your fork before submiting a new pull request. It helps the project manager on his demanding job of merging and solving conflits on the code. To update your fork, add a new remote link pointing to the original repository:

    $ git remote add upstream https://github.com/uclouvain/osis-louvain.git

This step is performed only once because Git preserves a list of remote links locally. Fetch the content of upstream in order to perform a merge with your local `master` branch:

    $ git fetch upstream

Then, go to the local `master` branch (if you are not already there) and merge it with upstream's `master` branch:

    $ git checkout master
    $ git merge upstream/master

Finally, push your master branch to your own repository:

    $ git push origin master

Now, you are ready to write your contributions.
