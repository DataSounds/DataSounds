============
Installation
============

At the command line:

.. code-block:: bash

    $ git clone http://github.com/DataSounds/DataSounds.git
    $ cd DataSounds
    $ python setup.py install

Or using [pip](https://pypi.python.org/pypi/pip/) (program to easily install python packages), which dinamicaly access the *Python Package Index* [PyPI](https://pypi.python.org/pypi/DataSounds/1.2.0)

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
`numpy <http://www.numpy.org/>`_ and `sebastian
<https://github.com/jtauber/sebastian>`_ are necessary packages to 
use `DataSounds. <datasouds.org>`_

Both of them can be installed using **pip**. If you use virtualenvwrapper this
could be done inside your virtual environment and should be already installed if DataSounds was compiled with success.

