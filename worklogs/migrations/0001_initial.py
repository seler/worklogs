# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Task'
        db.create_table('worklogs_task', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tasks', to=orm['auth.User'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='tasks', null=True, to=orm['worklogs.Project'])),
            ('bugtracker', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='tasks', null=True, to=orm['worklogs.BugTracker'])),
            ('bugtracker_object_id', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('duration', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('add_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mod_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('state', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('eta', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=4, blank=True)),
        ))
        db.send_create_signal('worklogs', ['Task'])

        # Adding model 'WorkLog'
        db.create_table('worklogs_worklog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(related_name='worklogs', to=orm['worklogs.Task'])),
            ('start', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('accounted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('worklogs', ['WorkLog'])

        # Adding model 'Project'
        db.create_table('worklogs_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('worklogs', ['Project'])

        # Adding model 'BugTracker'
        db.create_table('worklogs_bugtracker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('url_pattern', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('worklogs', ['BugTracker'])

        # Adding model 'Note'
        db.create_table('worklogs_note', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(related_name='notes', to=orm['worklogs.Task'])),
            ('note', self.gf('django.db.models.fields.TextField')()),
            ('add_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mod_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('worklogs', ['Note'])


    def backwards(self, orm):
        # Deleting model 'Task'
        db.delete_table('worklogs_task')

        # Deleting model 'WorkLog'
        db.delete_table('worklogs_worklog')

        # Deleting model 'Project'
        db.delete_table('worklogs_project')

        # Deleting model 'BugTracker'
        db.delete_table('worklogs_bugtracker')

        # Deleting model 'Note'
        db.delete_table('worklogs_note')


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
        'worklogs.note': {
            'Meta': {'object_name': 'Note'},
            'add_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mod_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notes'", 'to': "orm['worklogs.Task']"})
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
            'bugtracker': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tasks'", 'null': 'True', 'to': "orm['worklogs.BugTracker']"}),
            'bugtracker_object_id': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'duration': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'eta': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '4', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mod_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tasks'", 'null': 'True', 'to': "orm['worklogs.Project']"}),
            'state': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasks'", 'to': "orm['auth.User']"})
        },
        'worklogs.worklog': {
            'Meta': {'ordering': "('-start',)", 'object_name': 'WorkLog'},
            'accounted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'worklogs'", 'to': "orm['worklogs.Task']"})
        }
    }

    complete_apps = ['worklogs']