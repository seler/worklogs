# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'WorkLog.worklog'
        db.rename_column('worklogs_worklog', 'worklog_id', 'task_id')

    def backwards(self, orm):

        db.rename_column('worklogs_worklog', 'task_id', 'worklog_id')
