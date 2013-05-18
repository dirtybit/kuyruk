import imp
import logging

logger = logging.getLogger(__name__)


class Config(object):
    """Kuyruk configuration object. Default values are defined as
    class attributes.

    """
    def __init__(self):
        self.filename = None

    # Worker options

    IMPORT_PATH = None
    """Worker imports tasks from this directory."""

    IMPORTS = []
    """By default worker imports the task modules lazily when it receive a
    task from the queue. If you specify the modules here they will be
    imported when the worker is started."""

    EAGER = False
    """Run tasks in the process without sending to queue. Useful in tests."""

    MAX_LOAD = None
    """Stop consuming queue when the load goes above this level."""

    MAX_RUN_TIME = None
    """Gracefully shutdown worker after running this seconds.
    Master will detect that the worker is exited and will spawn a new
    worker with identical config.
    Can be used to force loading of new application code."""

    SAVE_FAILED_TASKS = False
    """Save failed tasks to a queue (named kuyruk_failed) for inspecting and
    requeueing later."""

    WORKERS = {}
    """You can specify the hostnames and correspondant queues here.
    By default all workers starts a single process to run tasks from
    the default queue (named kuyruk).

    Keys are hostnames (socket.gethostname()), values are comma seperated
    list of queue names.

    Example::

        {'host1.example.com': 'a, 2*b'}

    host1 will run 3 worker processes; 1 for "a" and 2 for "b" queue."""

    LOGGING_LEVEL = 'INFO'
    """Logging level of root logger."""

    LOGGING_CONFIG = None
    """INI style logging configuration file.
    This has pecedence over ``LOGGING_LEVEL``."""

    # Connection options

    RABBIT_HOST = 'localhost'
    RABBIT_PORT = 5672
    RABBIT_USER = 'guest'
    RABBIT_PASSWORD = 'guest'

    # Manager options

    MANAGER_HOST = None
    """Manager host that the workers will connect and send stats."""

    MANAGER_PORT = 16501
    """Manager port that the workers will connect and send stats."""

    MANAGER_HTTP_PORT = 16500
    """Manager HTTP port that the Flask application will run on."""

    def from_object(self, obj):
        """Populate Config from an object."""
        for key in dir(obj):
            if key.isupper():
                value = getattr(obj, key)
                setattr(self, key, value)
        logger.info("Config is loaded from %r", obj)

    def from_pyfile(self, filename):
        self.filename = filename
        d = imp.new_module('kuyruk_config')
        d.__file__ = filename
        try:
            execfile(filename, d.__dict__)
        except IOError as e:
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise
        self.from_object(d)

    def export(self, path):
        with open(path, 'w') as f:
            for attr in dir(self):
                if attr.isupper() and not attr.startswith('_'):
                    value = getattr(self, attr)
                    f.write("%s = %r\n" % (attr, value))
