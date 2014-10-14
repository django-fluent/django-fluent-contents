# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Placeholder'
        db.create_table('fluent_contents_placeholder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slot', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('role', self.gf('django.db.models.fields.CharField')(default='m', max_length=1)),
            ('parent_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('parent_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('fluent_contents', ['Placeholder'])

        # Adding unique constraint on 'Placeholder', fields ['parent_type', 'parent_id', 'slot']
        db.create_unique('fluent_contents_placeholder', ['parent_type_id', 'parent_id', 'slot'])

        # Adding model 'ContentItem'
        db.create_table('fluent_contents_contentitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('polymorphic_ctype', self.gf('django.db.models.fields.related.ForeignKey')(related_name='polymorphic_fluent_contents.contentitem_set', null=True, to=orm['contenttypes.ContentType'])),
            ('parent_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('parent_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('placeholder', self.gf('django.db.models.fields.related.ForeignKey')(related_name='contentitems', null=True, to=orm['fluent_contents.Placeholder'])),
            ('sort_order', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('fluent_contents', ['ContentItem'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Placeholder', fields ['parent_type', 'parent_id', 'slot']
        db.delete_unique('fluent_contents_placeholder', ['parent_type_id', 'parent_id', 'slot'])

        # Deleting model 'Placeholder'
        db.delete_table('fluent_contents_placeholder')

        # Deleting model 'ContentItem'
        db.delete_table('fluent_contents_contentitem')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'fluent_contents.contentitem': {
            'Meta': {'ordering': "('placeholder', 'sort_order')", 'object_name': 'ContentItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'parent_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contentitems'", 'null': 'True', 'to': "orm['fluent_contents.Placeholder']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_fluent_contents.contentitem_set'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'fluent_contents.placeholder': {
            'Meta': {'unique_together': "(('parent_type', 'parent_id', 'slot'),)", 'object_name': 'Placeholder'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'parent_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'default': "'m'", 'max_length': '1'}),
            'slot': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        }
    }

    complete_apps = ['fluent_contents']
