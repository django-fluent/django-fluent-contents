# -*- coding: utf-8 -*-
import datetime
from django.conf import settings
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'SharedContent', fields ['slug']
        db.delete_unique(u'sharedcontent_sharedcontent', ['slug'])

        # Adding field 'SharedContent.parent_site'
        db.add_column(u'sharedcontent_sharedcontent', 'parent_site',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'], default=settings.SITE_ID),
                      keep_default=False)

        # Adding unique constraint on 'SharedContent', fields ['site', 'slug']
        db.create_unique(u'sharedcontent_sharedcontent', ['parent_site_id', 'slug'])


    def backwards(self, orm):
        # Removing unique constraint on 'SharedContent', fields ['parent_site', 'slug']
        db.delete_unique(u'sharedcontent_sharedcontent', ['parent_site_id', 'slug'])

        # Deleting field 'SharedContent.parent_site'
        db.delete_column(u'sharedcontent_sharedcontent', 'parent_site_id')

        # Adding unique constraint on 'SharedContent', fields ['slug']
        db.create_unique(u'sharedcontent_sharedcontent', ['slug'])


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'fluent_contents.contentitem': {
            'Meta': {'ordering': "('placeholder', 'sort_order')", 'object_name': 'ContentItem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '15', 'db_index': 'True'}),
            'parent_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'parent_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contentitems'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['fluent_contents.Placeholder']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_fluent_contents.contentitem_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'})
        },
        'fluent_contents.placeholder': {
            'Meta': {'unique_together': "(('parent_type', 'parent_id', 'slot'),)", 'object_name': 'Placeholder'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'parent_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'default': "'m'", 'max_length': '1'}),
            'slot': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'sharedcontent.sharedcontent': {
            'Meta': {'unique_together': "(('parent_site', 'slug'),)", 'object_name': 'SharedContent'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'sharedcontent.sharedcontentitem': {
            'Meta': {'ordering': "('placeholder', 'sort_order')", 'object_name': 'SharedContentItem', 'db_table': "u'contentitem_sharedcontent_sharedcontentitem'", '_ormbases': ['fluent_contents.ContentItem']},
            u'contentitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['fluent_contents.ContentItem']", 'unique': 'True', 'primary_key': 'True'}),
            'shared_content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shared_content_items'", 'to': u"orm['sharedcontent.SharedContent']"})
        },
        u'sharedcontent.sharedcontenttranslation': {
            'Meta': {'unique_together': "[(u'language_code', u'master')]", 'object_name': 'SharedContentTranslation', 'db_table': "u'sharedcontent_sharedcontent_translation'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            u'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['sharedcontent.SharedContent']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['sharedcontent']
