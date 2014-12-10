# -*- coding: utf-8 -*-

import time
from funkload.Lipsum import Lipsum
from anybox.funkload.openerp import OpenERPTestCase

lipsum = Lipsum()


class CronWorkerTestCase(OpenERPTestCase):
    """Test that the cron worker is working by XML-RPC calls only."""

    has_nomenclature_data = False

    def setUp(self):
        super(CronWorkerTestCase, self).setUp()
        self.cron = self.model('ir.cron')
        self.user = self.model('res.users')
        self.login('admin', 'admin')

    def test_dummy(self):
        """Check test setup & infrastructure"""
        self.assertEqual(self.user.read(self.uid, ('login', ))['login'],
                         'admin')

    def test_cron(self):
        """Create a cron and watch it being executed."""
        self.assertFalse(self.user.search([('login', '=', 'testcron')]),
                         msg="Remnants of previous test runs detected, "
                         "please cleanup db")

        self.cron.create(dict(name="Create user by cron",
                              model='res.users',
                              function='create',
                              args=repr([dict(login='testcron',
                                              name="Test Cron")]),
                              user_id=self.uid,
                              priority=100,
                              numbercall=1,
                              doall=True))

        time.sleep(90)  # wait for cron engine to wake up and run the job

        created_ids = self.user.search([('login', '=', 'testcron')])
        self.assertEqual(len(created_ids), 1)
        self.user.unlink(created_ids)
