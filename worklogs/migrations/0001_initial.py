# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'WorkLog'
        db.create_table('worklogs_worklog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False, unique=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='worklogs', to=orm['auth.User'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='worklogs', to=orm['worklogs.Project'])),
            ('bugtracker', self.gf('django.db.models.fields.related.ForeignKey')(related_name='worklogs', to=orm['worklogs.BugTracker'])),
            ('bugtracker_object_id', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('duration', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('add_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mod_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('worklogs', ['WorkLog'])

        # Adding model 'WorkLogEntry'
        db.create_table('worklogs_worklogentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False, unique=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='work_logs', to=orm['auth.User'])),
            ('worklog', self.gf('django.db.models.fields.related.ForeignKey')(related_name='worklog_entries', to=orm['worklogs.WorkLog'])),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('end', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('worklogs', ['WorkLogEntry'])

        # Adding model 'Project'
        db.create_table('worklogs_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False, unique=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('worklogs', ['Project'])

        # Adding model 'BugTracker'
        db.create_table('worklogs_bugtracker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False, unique=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('url_pattern', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('worklogs', ['BugTracker'])

    def backwards(self, orm):
        # Deleting model 'WorkLog'
        db.delete_table('worklogs_worklog')

        # Deleting model 'WorkLogEntry'
        db.delete_table('worklogs_worklogentry')

        # Deleting model 'Project'
        db.delete_table('worklogs_project')

        # Deleting model 'BugTracker'
        db.delete_table('worklogs_bugtracker')

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
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'url_pattern': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'worklogs.project': {
            'Meta': {'object_name': 'Project'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'worklogs.worklog': {
            'Meta': {'ordering': "('-add_date',)", 'object_name': 'WorkLog'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'unique': 'True'}),
            'add_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'bugtracker': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'worklogs'", 'to': "orm['worklogs.BugTracker']"}),
            'bugtracker_object_id': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'duration': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mod_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'worklogs'", 'to': "orm['worklogs.Project']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'worklogs'", 'to': "orm['auth.User']"})
        },
        'worklogs.worklogentry': {
            'Meta': {'ordering': "('-start',)", 'object_name': 'WorkLogEntry'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'unique': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'work_logs'", 'to': "orm['auth.User']"}),
            'worklog': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'worklog_entries'", 'to': "orm['worklogs.WorkLog']"})
        }
    }

    complete_apps = ['worklogs']