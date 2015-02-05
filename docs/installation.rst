============
Installation
============

At the command line:

.. code-block:: bash

    $ git clone http://github.com/DataSounds/DataSounds.git
    $ cd DataSounds
    $ python setup.py install

Or using pip_ (program to easily install Python packages), which dinamicaly access the *Python Package Index* PyPI_.

.. _pip: https://pypi.python.org/pypi/pip/
.. _PyPI: https://pypi.python.org/pypi/DataSounds/1.2.0

.. code-block:: bash

    $ pip install DataSounds

Or, with the controled python ecosystem virtualenvwrapper_.
After install virtualenvwrapper, follow the instructions below:

.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.org/en/latest/#

.. code-block:: bash

    $ mkvirtualenv DataSounds
    $ workon DataSounds
    (DataSounds) $ git clone http://github.com/DataSounds/DataSounds.git
    (DataSounds) $ cd DataSounds
    (DataSounds) $ python setup.py install


Dependencies
************
`Numpy <http://www.numpy.org/>`_ is a necessary packages to
use DataSounds_.


..
    and `sebastian <https://github.com/jtauber/sebastian>`_ are
    Both of them can be installed using **pip**. If you use virtualenvwrapper this
Numpy can be installed using **pip**. If you use virtualenvwrapper, this
could be done inside your virtual environment. Normally, **Numpy** is installed as a dependency of DataSounds_ and should work if it was sucessfully compiled.

.. _DataSounds: www.datasounds.org
