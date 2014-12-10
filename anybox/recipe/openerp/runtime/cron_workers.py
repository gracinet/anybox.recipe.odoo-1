import os
import logging
import random
import argparse
try:
    from openerp.service.server import WorkerCron
except ImportError:  # OpenERP 7
    from openerp.service.workers import WorkerCron


_logger = logging.getLogger(__name__)


class SingleManager(object):
    """A minimal implementation that cares about one process only.
    """

    timeout = 0

    def __init__(self, limit_request=None):
        self.limit_request = limit_request

    def pipe_new(self):
        pass

    def pipe_ping(self, watchdog_pipe):
        pass


class StandaloneCronWorker(WorkerCron):
    """A simple cron launcher.

    The current process will not spawn any children, it is designed
    to be managed by an external process manager (supervisor, systemd...)
    """

    def __init__(self, db_names, config):
        super(StandaloneCronWorker, self).__init__(
            SingleManager(limit_request=config['limit_request']))
        self.db_names = db_names
        # parent class expect to fork after __init__ and uses therefore
        # getpid() for parent pid in __init__().
        # We need to fix that to avoid immediate suicide in process_limit()
        self.ppid = os.getppid()

    def _db_list(self):
        return (self.db_names if self.db_names is not None
                else super(StandaloneCronWorker, self)._db_list())

    def start(self):
        # base class sets nice, but that's an external manager
        # responsibility
        self.pid = os.getpid()
        self.setproctitle()
        _logger.info("%s (pid=%s) alive", self.__class__.__name__, self.pid)
        # Reseed the random number generator
        random.seed()


def main():
    from openerp.tools import config
    parser = argparse.ArgumentParser()
    parser.add_argument("db", nargs='*')

    arguments = parser.parse_args()
    # for the worker, None has the precise meaning to rely on config file
    # I don't want to tie this to the empty list
    dbs = arguments.db if arguments.db else None
    StandaloneCronWorker(dbs, config).run()
