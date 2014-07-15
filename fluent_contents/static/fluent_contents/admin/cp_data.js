/**
 * This file deals with the lowest data layer / data administration of the backend editor.
 *
 * It tracks the 'ContentItem' metadata of the plugins.
 */
var cp_data = {};


(function($)
{
  // Stored data
  // FIXME: make dom_placeholders private.
  cp_data.dom_placeholders = {};  // the formset items by placeholder; { 'placeholder_slot': { id: 8, slot: 'main, items: [ item1, item2 ], role: 'm', domnode: 'someid' }, ... }

  // Public data (also for debugging)
  cp_data.placeholders = null;  // [ { slot: 'main', title: 'Main', role: 'm', domnode: 'someid' }, { slot: 'sidebar', ...} ]
  cp_data.initial_placeholders = null;
  cp_data.contentitem_metadata = null;  // { 'ModelName': { type: "ModelName", name: "Text item", prefix: "modelname", rel_name: "TypeName_set", auto_id: "id_%s" }, ... }


  // Public initialisation functions
  cp_data.set_placeholders = function(data)
  {
    cp_data.placeholders = data;
    if( ! cp_data.initial_placeholders )
    {
      cp_data.initial_placeholders = data;
    }
    else
    {
      // Allow move icon to be shown/hidden.
      if( cp_data.placeholders.length == 1 )
        $("body").addClass('cp-single-placeholder');
      else
        $("body").removeClass('cp-single-placeholder');
    }
  };

  cp_data.set_contentitem_metadata = function(data) { cp_data.contentitem_metadata = data; };
  cp_data.get_placeholders = function() { return cp_data.placeholders; };
  cp_data.get_initial_placeholders = function() { return cp_data.initial_placeholders; };


  /**
   * Object to describe the metadata of a ContentItem in the formset.
   */
  function ContentItemInfo($fs_item)
  {
    // NOTE: assumes the ContentItem was already moved outside it's inline-group.
    // The parsing only happens with the
    var id = $fs_item.attr("id");
    var pos = id.lastIndexOf('-');      // have to split at last '-' for generic inlines (inlinetype-id / app-model-ctfield-ctfkfield-id)

    this.fs_item = $fs_item;
    this.prefix = id.substring(0, pos);
    this.index = parseInt(id.substring(pos + 1));

    // Global metadata
    this.type = null;
    this.name = null;
    this.plugin = null;
    this.rel_name = null;
    this.auto_id = null;
    this.item_template = null;

    // Overwrite properties with global metadata about the ContentItem
    var contentitem_metadata = cp_data._get_contentitem_metadata_by_prefix(this.prefix);
    if( contentitem_metadata )
      $.extend(this, contentitem_metadata);
  }

  function PlaceholderPane($pane, placeholder)
  {
    this.root = $pane;  // mainly for debugging
    this.content = $pane.children(".cp-content");
    this.empty_message = $pane.children('.cp-empty');
    this.placeholder = placeholder;
    this.is_orphaned = $pane.attr('data-tab-region') == '__orphaned__';
  }

  function DomPlaceholder(placeholder, is_fallback)
  {
    this.slot = placeholder.slot;
    this.role = placeholder.role;
    this.items = [];
    this.is_fallback = is_fallback;
  }


  /**
   * Initialize the data collection by reading the DOM.
   *
   * Read all the DOM formsets into the "dom_placeholders" variable.
   * This information is used in this library to lookup formsets.
   */
  cp_data.init = function()
  {
    // Find all formset items.
    var $all_items   = $(".inline-contentitem-group > .inline-related");
    var $empty_items = $all_items.filter(".empty-form");
    var $fs_items    = $all_items.filter(":not(.empty-form)");

    // Group all formset items by the placeholder they belong to.
    // This administration is used as quick lookup, to avoid unneeded DOM querying.
    if( cp_data.placeholders )
    {
      for(var i = 0; i < $fs_items.length; i++)
      {
        // Get formset DOM elements
        var $fs_item           = $fs_items.eq(i);
        var $placeholder_input = $fs_item.find("input[name$=-placeholder], select[name$=-placeholder]");  // allow <select> for debugging.
        var $placeholder_slot_input = $fs_item.find('input[name$=-placeholder_slot]');

        // placeholder_slot may be __main__, placeholder.slot will be the real one.
        var placeholder_id = $placeholder_input.val();
        var placeholder_slot = $placeholder_slot_input.val();

        // Append item to administration
        var placeholder;
        if(placeholder_id)  // can be empty for add page with form errors
        {
          placeholder = cp_data.get_placeholder_by_id(placeholder_id);   // can be null if item became orphaned.
        }
        else if(placeholder_slot)
        {
          placeholder = cp_data.get_placeholder_by_slot(placeholder_slot)
        }
        var dom_placeholder = cp_data.get_or_create_dom_placeholder(placeholder, placeholder_id, placeholder_slot);
        dom_placeholder.items.push($fs_item);

        // Reset placeholder ID field if the item already
        // doesn't fit in any placeholder.
        if( dom_placeholder.is_fallback )
          $placeholder_input.val('');
      }

      if( cp_data.placeholders.length == 1 )
        $("body").addClass('cp-single-placeholder');
    }

    // Amend the contentitem metadata with the empty-form template
    for(var model_name in cp_data.contentitem_metadata)
    {
      var item_meta = cp_data.contentitem_metadata[model_name];
      item_meta.item_template = $("#" + item_meta.prefix + "-empty");
    }
  }


  cp_data.get_or_create_dom_placeholder = function(placeholder, fallback_id, fallback_slot)
  {
    // If the ID references to a placeholder which was removed from the template,
    // make sure the item is indexed somehow.
    var is_fallback = false;
    if( ! placeholder )
    {
      var slot = fallback_slot || (!fallback_id ? "__orphaned__" : "__orphaned__@" + fallback_id);  // distinguish clearly, easier debugging.
      placeholder = {'slot': slot, 'role': null};
      is_fallback = !fallback_slot;  // slot == __orphaned__
    }

    var dom_placeholder = cp_data.dom_placeholders[placeholder.slot];
    if( ! dom_placeholder )
    {
      // Create the structure for the placeholder.
      dom_placeholder = new DomPlaceholder(placeholder, is_fallback);
      cp_data.dom_placeholders[placeholder.slot] = dom_placeholder;
    }

    return dom_placeholder;
  }


  cp_data.get_dom_placeholders = function()
  {
    return cp_data.dom_placeholders;
  }


  /**
   * Find the desired placeholder, including the preferred occurrence of it.
   */
  cp_data.get_placeholder_for_role = function(role, preferredNr)
  {
    if( cp_data.placeholders == null )
      throw new Error("cp_data.set_placeholders() was never called");

    var candidate = null;
    var itemNr = 0;
    for(var i = 0; i < cp_data.placeholders.length; i++)
    {
      var placeholder = cp_data.placeholders[i];
      if(placeholder.role == role)
      {
        candidate = placeholder;
        itemNr++;

        if( itemNr == preferredNr || !preferredNr )
          return candidate;
      }
    }

    return candidate;
  }


  /**
   * See if there is only one placeholder at the page.
   */
  cp_data.get_single_placeholder = function()
  {
    if( cp_data.placeholders == null )
      throw new Error("cp_data.set_placeholders() was never called");

    if( cp_data.placeholders.length == 1 ) {
      return cp_data.placeholders[0];
    }

    return null;
  }


  /**
   * Find the placeholder corresponding with a given ID.
   */
  cp_data.get_placeholder_by_id = function(id)
  {
    if( id == "" )
      return null;
    return _get_placeholder_by_property('id', id);
  }


  /**
   * Find the placeholder corresponding with a given slot.
   */
  cp_data.get_placeholder_by_slot = function(slot)
  {
    if( slot == "" )
      throw new Error("cp_data.get_placeholder_by_slot() received empty value.");
    return _get_placeholder_by_property('slot', slot);
  }


  function _get_placeholder_by_property(prop, value)
  {
    if( cp_data.placeholders == null )
      throw new Error("cp_data.set_placeholders() was never called");

    // Special case: if there is only a single placeholder,
    // skip the whole support for multiple placeholders per page.
    if( cp_data.placeholders.length == 1 && cp_data.placeholders[0].id == -1 )
      return cp_data.placeholders[0];

    // Find the item based on the property.
    // The placeholders are not a loopup object, but array to keep sort_order correct.
    for(var i = 0; i < cp_data.placeholders.length; i++)
      if( cp_data.placeholders[i][prop] == value )
        return cp_data.placeholders[i];

    if( window.console )
      window.console.warn("cp_data.get_placeholder_by_" + prop + ": no object for '" + value + "'");
    return null;
  }


  /**
   * Return the DOM elements where the placeholder adds it's contents.
   */
  cp_data.get_placeholder_pane = function(placeholder)
  {
    return cp_data.get_object_for_pane($("#" + placeholder.domnode), placeholder);
  }


  /**
   * Return the placeholder pane for a given FormSet item.
   */
  cp_data.get_placeholder_pane_for_item = function($fs_item)
  {
    var pane = $fs_item.closest(".cp-content").parent();
    return cp_data.get_object_for_pane(pane, undefined);
  }


  /**
   * Return an array of all placeholder pane objects.
   */
  cp_data.get_placeholder_panes = function()
  {
    // Wrap in objects too, for consistent API usage.
    var pane_objects = [];
    for(var i = 0; i < cp_data.placeholders.length; i++)
    {
      var placeholder = cp_data.placeholders[i];
      pane_objects.push(cp_data.get_placeholder_pane(placeholder));
    }

    return pane_objects;
  }


  cp_data.get_object_for_pane = function($pane, placeholder)
  {
    if( $pane.length == 0 )
    {
      if( window.console )
        window.console.warn("Pane not found: " + $pane.selector);
      return null;
    }

    return new PlaceholderPane($pane, placeholder);
  }


  cp_data.get_formset_dom_info = function(child_node)
  {
    var current_item = cp_data.get_inline_formset_item_info(child_node);
    var group_prefix = current_item.auto_id.replace(/%s/, current_item.prefix);
    var field_prefix = group_prefix + "-" + current_item.index;

    var placeholder_id = $("#" + field_prefix + "-placeholder").val();  // .val allows <select> for debugging.
    var placeholder_slot = $("#" + field_prefix + "-placeholder_slot")[0].value;

    // Placeholder slot may only filled in when creating items,
    // so restore that info from the existing database.
    if( placeholder_id && !placeholder_slot )
      placeholder_slot = cp_data.get_placeholder_by_id(placeholder_id).slot;

    return {
      // for debugging
      root: current_item.fs_item,

      // management form item
      total_forms: $("#" + group_prefix + "-TOTAL_FORMS")[0],

      // Item fields
      id_field: $("#" + field_prefix + "-contentitem_ptr"),
      delete_checkbox: $("#" + field_prefix + "-DELETE"),
      placeholder_id: placeholder_id,  // .val allows <select> for debugging.
      placeholder_slot: placeholder_slot
    };
  }


  /**
   * Given a random child node, return the formset data that the node belongs to.
   * The formset item itself may be moved outside of the original inline group.
   */
  cp_data.get_inline_formset_item_info = function(child_node)
  {
    if( cp_data.contentitem_metadata == null )
      throw new Error("cp_data.set_contentitem_metadata() was never called. Does the ModelAdmin inherit from the correct base class?");
    if( child_node.fs_item )
      return child_node;   // already parsed

    var fs_item = $(child_node).closest(".inline-related");
    return new ContentItemInfo(fs_item);
  }


  cp_data._get_contentitem_metadata_by_prefix = function(prefix)
  {
    return _get_contentitem_metadata_by_prop('prefix', prefix);
  }


  function _get_contentitem_metadata_by_prop(prop, value)
  {
    if( cp_data.contentitem_metadata == null )
      throw new Error("cp_data.set_contentitem_metadata() was never called");

    for(var model_name in cp_data.contentitem_metadata)
    {
      if(! cp_data.contentitem_metadata.hasOwnProperty(model_name))
        continue;

      var candidate = cp_data.contentitem_metadata[model_name];
      if( candidate[prop] == value )
        return candidate;
    }
    return null;
  }


  /**
   * Verify that a given item type exists.
   */
  cp_data.get_contentitem_metadata_by_type = function(model_name)
  {
    if( cp_data.contentitem_metadata == null )
      throw new Error("cp_data.set_contentitem_metadata() was never called. Does the ModelAdmin inherit from the correct base class?");

    return cp_data.contentitem_metadata[model_name];
  }


  /**
   * Return the contentitem metadata for a plugin name.
   */
  cp_data.get_contentitem_metadata_by_plugin = function(plugin)
  {
    return _get_contentitem_metadata_by_prop('plugin', plugin);
  }


  cp_data.cleanup_empty_placeholders = function()
  {
    for(var i = 0; i < cp_data.dom_placeholders.length; i++)
      if(cp_data.dom_placeholders[i].items.length == 0)
        delete cp_data.dom_placeholders[i];
  }


  cp_data.remove_dom_item = function(placeholder_slot, item_data)
  {
    var dom_placeholder = cp_data.dom_placeholders[placeholder_slot];
    var raw_node        = item_data.fs_item[0];
    for( i = 0; i < dom_placeholder.items.length; i++ )
    {
      if( dom_placeholder.items[i][0] == raw_node)
      {
        dom_placeholder.items.splice(i, 1);
        break;
      }
    }

    return dom_placeholder.items.length == 0;
  }

})(window.jQuery || django.jQuery);
