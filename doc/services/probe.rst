``probe`` service
=================

Synopsis
--------

Проверка наличия функционального домена в системе.
Включение и выключение порций скриптов в составе конфигурационного юнита.


Usage
-----

Вызов сервиса позволяет определить наличие функционального домена в системе.
Нулевой код означет, что домен присутствует.
Ненулевой код возврата означает, что домен отсутствует.

.. sourcecode:: console

    # ram probe proxywiz

При использовании python-интерфейса можно указать название конкретной порции для проверки:

.. sourcecode:: pycon

    >>> import ram
    >>> ram.probe('proxywiz', using='phobos')

Interface
---------

Для поддержки сервиса ``probe`` в юните необходимо добавить одноименный исполняемый скрипт ``probe`` в состав файлов юнита.
Отсутствие скрипта или успешное выполнение скрипта интерпретируются фреймворком как присутствие функционального домена в системе.
Неуспешное выполнение скрипта интерпретируется фреймворком как отсутствие функциональноого домена в системе.

Для каждой порции скриптов в составе конфигурационного юнита может быть определен свой скрипт ``probe``.

Например, в состав конфигурационного юнита ``proxywiz`` добавлена порция скриптов для демона ``phobos``.
Порция состоит из скриптов: ``probe``, ``store``, ``apply``:

.. sourcecode:: console

    # ram which proxywiz
    /opt/my-appliance/lib/ram/proxywiz/apply.phobos
    /opt/my-appliance/lib/ram/proxywiz/about
    /opt/my-appliance/lib/ram/proxywiz/param
    /opt/my-appliance/lib/ram/proxywiz/store.phobos
    /opt/my-appliance/lib/ram/proxywiz/input
    /opt/my-appliance/lib/ram/proxywiz/query
    /opt/my-appliance/lib/ram/proxywiz/store
    /opt/my-appliance/lib/ram/proxywiz/probe.phobos

Так, при вызове сервиса ``store`` фреймворк будет последовательно вызывать скрипты ``store`` и ``store.phobos``.
Однако, последний будет вызван, только если предварительный вызов скрипта ``probe.phobos`` завершится успешно.

.. sourcecode:: console

    # ram tweak trace on
    # ram store proxywiz
    : /opt/my-appliance/lib/ram/proxywiz/store  = 0
    : /opt/my-appliance/lib/ram/proxywiz/probe.phobos  = 0
    : /opt/my-appliance/lib/ram/proxywiz/store.phobos  = 0

В случае неуспешного запуска скрипта ``probe.phobos``, вызова соотвествующего скрипта ``store.phobos`` не произойдет.
При этом вызов команды ``ram store`` завершится успешно:

.. sourcecode:: console

    # ram tweak trace on
    # ram store proxywiz
    : /opt/my-appliance/lib/ram/proxywiz/store  = 0
    : /opt/my-appliance/lib/ram/proxywiz/probe.phobos  = 1


See also
--------

.. toctree::
    :maxdepth: 1

    query
    store
    apply
    which
