# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    depends_on = (
        ("fluent_contents", "0001_initial"),
    )

    def forwards(self, orm):
        
        # Adding model 'TwitterRecentEntriesItem'
        db.create_table('contentitem_twitterfeed_twitterrecententriesitem', (
            ('contentitem_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['fluent_contents.ContentItem'], unique=True, primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('twitter_user', self.gf('django.db.models.fields.CharField')(max_length=75)),
            ('amount', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=5)),
            ('footer_text', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('include_retweets', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('include_replies', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('twitterfeed', ['TwitterRecentEntriesItem'])

        # Adding model 'TwitterSearchItem'
        db.create_table('contentitem_twitterfeed_twittersearchitem', (
            ('contentitem_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['fluent_contents.ContentItem'], unique=True, primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('query', self.gf('django.db.models.fields.CharField')(default='', max_length=200)),
            ('amount', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=5)),
            ('footer_text', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('include_retweets', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('include_replies', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('twitterfeed', ['TwitterSearchItem'])


    def backwards(self, orm):
        
        # Deleting model 'TwitterRecentEntriesItem'
        db.delete_table('contentitem_twitterfeed_twitterrecententriesitem')

        # Deleting model 'TwitterSearchItem'
        db.delete_table('contentitem_twitterfeed_twittersearchitem')


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
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'})
        },
        'fluent_contents.placeholder': {
            'Meta': {'unique_together': "(('parent_type', 'parent_id', 'slot'),)", 'object_name': 'Placeholder'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'parent_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'default': "'m'", 'max_length': '1'}),
            'slot': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'twitterfeed.twitterrecententriesitem': {
            'Meta': {'ordering': "('placeholder', 'sort_order')", 'object_name': 'TwitterRecentEntriesItem', 'db_table': "'contentitem_twitterfeed_twitterrecententriesitem'", '_ormbases': ['fluent_contents.ContentItem']},
            'amount': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '5'}),
            'contentitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['fluent_contents.ContentItem']", 'unique': 'True', 'primary_key': 'True'}),
            'footer_text': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'include_replies': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'include_retweets': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'twitter_user': ('django.db.models.fields.CharField', [], {'max_length': '75'})
        },
        'twitterfeed.twittersearchitem': {
            'Meta': {'ordering': "('placeholder', 'sort_order')", 'object_name': 'TwitterSearchItem', 'db_table': "'contentitem_twitterfeed_twittersearchitem'", '_ormbases': ['fluent_contents.ContentItem']},
            'amount': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '5'}),
            'contentitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['fluent_contents.ContentItem']", 'unique': 'True', 'primary_key': 'True'}),
            'footer_text': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'include_replies': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'include_retweets': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'query': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['twitterfeed']
