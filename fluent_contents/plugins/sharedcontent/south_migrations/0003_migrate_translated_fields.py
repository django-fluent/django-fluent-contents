# -*- coding: utf-8 -*-
import datetime
from django.core.exceptions import ObjectDoesNotExist
from south.db import db
from south.v2 import DataMigration
from django.db import models
from fluent_contents import appsettings


class Migration(DataMigration):

    def forwards(self, orm):
        db.execute(
            'INSERT INTO sharedcontent_sharedcontent_translation(title, language_code, master_id)'
            ' SELECT title, %s, id FROM sharedcontent_sharedcontent',
            [appsettings.FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE]
        )

    def backwards(self, orm):
        # Convert all fields back to the single-language table.
        for sharedcontent in orm['sharedcontent.SharedContent'].objects.all():
            translations = orm['sharedcontent.SharedContent_Translation'].objects.filter(master_id=sharedcontent.id)
            try:
                # Try default translation
                translation = translations.get(language_code=appsettings.FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE)
            except ObjectDoesNotExist:
                try:
                    # Try internal fallback
                    translation = translations.get(language_code__in=('en-us', 'en'))
                except ObjectDoesNotExist:
                    # Hope there is a single translation
                    translation = translations.get()

            sharedcontent.title = translation.title
            sharedcontent.save()

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
            'Meta': {'object_name': 'SharedContent'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'sharedcontent.sharedcontent_translation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'SharedContent_Translation'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['sharedcontent.SharedContent']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'sharedcontent.sharedcontentitem': {
            'Meta': {'ordering': "('placeholder', 'sort_order')", 'object_name': 'SharedContentItem', 'db_table': "u'contentitem_sharedcontent_sharedcontentitem'", '_ormbases': ['fluent_contents.ContentItem']},
            u'contentitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['fluent_contents.ContentItem']", 'unique': 'True', 'primary_key': 'True'}),
            'shared_content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shared_content_items'", 'to': u"orm['sharedcontent.SharedContent']"})
        }
    }

    complete_apps = ['sharedcontent']
    symmetrical = True
