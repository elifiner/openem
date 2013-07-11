# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table('users', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('password_hash', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
        ))
        db.send_create_signal(u'openem', ['User'])

        # Adding model 'Conversation'
        db.create_table('conversations', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('update_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='conversations', to=orm['openem.User'])),
        ))
        db.send_create_signal(u'openem', ['Conversation'])

        # Adding model 'Message'
        db.create_table('messages', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('post_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('conversation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='messages', to=orm['openem.Conversation'])),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['openem.User'])),
        ))
        db.send_create_signal(u'openem', ['Message'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table('users')

        # Deleting model 'Conversation'
        db.delete_table('conversations')

        # Deleting model 'Message'
        db.delete_table('messages')


    models = {
        u'openem.conversation': {
            'Meta': {'object_name': 'Conversation', 'db_table': "'conversations'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'conversations'", 'to': u"orm['openem.User']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        },
        u'openem.message': {
            'Meta': {'object_name': 'Message', 'db_table': "'messages'"},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['openem.User']"}),
            'conversation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': u"orm['openem.Conversation']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'openem.user': {
            'Meta': {'object_name': 'User', 'db_table': "'users'"},
            'create_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'password_hash': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['openem']