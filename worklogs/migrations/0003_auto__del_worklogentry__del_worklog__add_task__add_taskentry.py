# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'WorkLogEntry'
        db.delete_table('worklogs_worklogentry')

        # Deleting model 'WorkLog'
        db.delete_table('worklogs_worklog')

        # Adding model 'Task'
        db.create_table('worklogs_task', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='worklogs', to=orm['auth.User'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='worklogs', to=orm['worklogs.Project'])),
            ('bugtracker', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='worklogs', null=True, to=orm['worklogs.BugTracker'])),
            ('bugtracker_object_id', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('duration', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('add_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mod_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('state', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('eta', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=4, blank=True)),
        ))
        db.send_create_signal('worklogs', ['Task'])

        # Adding model 'TaskEntry'
        db.create_table('worklogs_taskentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('worklog', self.gf('django.db.models.fields.related.ForeignKey')(related_name='worklog_entries', to=orm['worklogs.Task'])),
            ('start', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('worklogs', ['TaskEntry'])

    def backwards(self, orm):
        # Adding model 'WorkLogEntry'
        db.create_table('worklogs_worklogentry', (
            ('end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('worklog', self.gf('django.db.models.fields.related.ForeignKey')(related_name='worklog_entries', to=orm['worklogs.WorkLog'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('worklogs', ['WorkLogEntry'])

        # Adding model 'WorkLog'
        db.create_table('worklogs_worklog', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('duration', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='worklogs', to=orm['auth.User'])),
            ('mod_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('eta', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=4, blank=True)),
            ('add_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='worklogs', to=orm['worklogs.Project'])),
            ('state', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('bugtracker_object_id', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('bugtracker', self.gf('django.db.models.fields.related.ForeignKey')(related_name='worklogs', null=True, to=orm['worklogs.BugTracker'], blank=True)),
        ))
        db.send_create_signal('worklogs', ['WorkLog'])

        # Deleting model 'Task'
        db.delete_table('worklogs_task')

        # Deleting model 'TaskEntry'
        db.delete_table('worklogs_taskentry')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'worklogs.bugtracker': {
            'Meta': {'object_name': 'BugTracker'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'url_pattern': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'worklogs.project': {
            'Meta': {'object_name': 'Project'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'worklogs.task': {
            'Meta': {'ordering': "('-add_date',)", 'object_name': 'Task'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'add_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'bugtracker': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'worklogs'", 'null': 'True', 'to': "orm['worklogs.BugTracker']"}),
            'bugtracker_object_id': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'duration': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'eta': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '4', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mod_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'worklogs'", 'to': "orm['worklogs.Project']"}),
            'state': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'worklogs'", 'to': "orm['auth.User']"})
        },
        'worklogs.taskentry': {
            'Meta': {'ordering': "('-start',)", 'object_name': 'TaskEntry'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'worklog': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'worklog_entries'", 'to': "orm['worklogs.Task']"})
        }
    }

    complete_apps = ['worklogs']