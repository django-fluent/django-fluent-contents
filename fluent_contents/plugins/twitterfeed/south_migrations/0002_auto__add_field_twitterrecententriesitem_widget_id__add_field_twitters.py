# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'TwitterRecentEntriesItem.widget_id'
        db.add_column(u'contentitem_twitterfeed_twitterrecententriesitem', 'widget_id',
                      self.gf('django.db.models.fields.CharField')(default=12345, max_length=75),
                      keep_default=False)

        # Adding field 'TwitterSearchItem.widget_id'
        db.add_column(u'contentitem_twitterfeed_twittersearchitem', 'widget_id',
                      self.gf('django.db.models.fields.CharField')(default=12345, max_length=75),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'TwitterRecentEntriesItem.widget_id'
        db.delete_column(u'contentitem_twitterfeed_twitterrecententriesitem', 'widget_id')

        # Deleting field 'TwitterSearchItem.widget_id'
        db.delete_column(u'contentitem_twitterfeed_twittersearchitem', 'widget_id')


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
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_fluent_contents.contentitem_set+'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
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
        u'twitterfeed.twitterrecententriesitem': {
            'Meta': {'ordering': "('placeholder', 'sort_order')", 'object_name': 'TwitterRecentEntriesItem', 'db_table': "u'contentitem_twitterfeed_twitterrecententriesitem'", '_ormbases': ['fluent_contents.ContentItem']},
            'amount': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '5'}),
            u'contentitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['fluent_contents.ContentItem']", 'unique': 'True', 'primary_key': 'True'}),
            'footer_text': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'include_replies': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'include_retweets': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'twitter_user': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'widget_id': ('django.db.models.fields.CharField', [], {'max_length': '75'})
        },
        u'twitterfeed.twittersearchitem': {
            'Meta': {'ordering': "('placeholder', 'sort_order')", 'object_name': 'TwitterSearchItem', 'db_table': "u'contentitem_twitterfeed_twittersearchitem'", '_ormbases': ['fluent_contents.ContentItem']},
            'amount': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '5'}),
            u'contentitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['fluent_contents.ContentItem']", 'unique': 'True', 'primary_key': 'True'}),
            'footer_text': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'include_replies': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'include_retweets': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'query': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'widget_id': ('django.db.models.fields.CharField', [], {'max_length': '75'})
        }
    }

    complete_apps = ['twitterfeed']