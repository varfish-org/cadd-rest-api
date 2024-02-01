.. image:: https://app.codacy.com/project/badge/Grade/f47216cf5a4349acbb9baf5ca1c91329
    :target: https://www.codacy.com/gh/bihealth/cadd-rest-api/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bihealth/cadd-rest-api&amp;utm_campaign=Badge_Grade
.. image:: https://app.codacy.com/project/badge/Coverage/f47216cf5a4349acbb9baf5ca1c91329
    :target: https://www.codacy.com/gh/bihealth/cadd-rest-api/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bihealth/cadd-rest-api&amp;utm_campaign=Badge_Coverage
.. image:: https://img.shields.io/badge/License-MIT-green.svg
    :target: https://opensource.org/licenses/MIT

=============
CADD REST API
=============

This package implements a simple CADD Server.

``cadd-rest-api`` is used in your Docker Compose--based installation of VarFish.
You can find out more here:

- https://github.com/bihealth/varfish-docker-compose

----------
Quick Info
----------

- Language: Python
- License: MIT License
    - Important: the dependency CADD-scripts is not MIT licensed but "free for non-commercial" only!
- Dependencies:
    - `CADD-scripts <https://github.com/kircherlab/CADD-scripts>`__
    - Celery for Queuing

---------------------
Building Docker Image
---------------------

Use the ``docker/build-docker`` if you are at a given tag.
Or:

.. code-block:: bash

    $ docker build . --build-arg app_git_tag=v0.3.2 -t varfish-org/cadd-rest-api:0.3.2-0
