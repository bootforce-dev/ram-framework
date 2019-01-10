
Getting the `ram` framework
---------------------------

There are several options to install `the ram framework` on the machine. At the moment `the ram framework`
has been tested on RHEL 6 / CentOS 6 operating systems. The instructions below assume that these operating
systems will be used.


Installing from ``rpm`` package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 * Get the latest built rpm package from Automake at::

     ...

 * Use ``yum`` to install the package, dependencies will be installed automatically:

   .. sourcecode:: console

       # yum install ram-*.noarch.rpm


Installing from source using ``pip``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 * Get the latest version of the of the `ram` source code from github:

   .. sourcecode:: console

       $ git clone https://github.com/bootforce-dev/ram-framework.git

 * Use ``pip`` to install `the ram framework` to the system:

   .. sourcecode:: console

       $ cd /path/to/ram-framework/src
       # pip install .

 * Use standard library from cloned repository:

   .. sourcecode:: console

       # ram paths append /path/to/ram-framework/lib

 * It's still required to use yum to install `ram` dependencies:

   .. sourcecode:: console

       # yum install newt-python python-iniparse python-inotify

 * Several units from standard library have additional dependencies. Use yum to install them:

   .. sourcecode:: console

       # yum install libuser-python cracklib-python python-dateutil parted


