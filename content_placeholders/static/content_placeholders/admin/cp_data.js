/**
 * This file deals with the lowest data layer / data administration of the backend editor.
 *
 * It tracks the 'itemtypes' of the plugins.
 */
var cp_data = {};


(function($)
{
  // Public functions
  window.cp_admin = {
    'setPlaceholders':     function(data) { cp_data.placeholders = data; },
    'setContentItemTypes': function(data) { cp_data.itemtypes = data; }
  };

  // Stored data
  // FIXME: make dom_placeholders private.
  cp_data.dom_placeholders = {};  // the formset items by placeholder; { 'placeholder_slot': { id: 8, slot: 'main, items: [ item1, item2 ], role: 'm', domnode: 'someid' }, ... }

  // Public data (also for debugging)
  cp_data.placeholders = null;  // [ { slot: 'main', title: 'Main', role: 'm', domnode: 'someid' }, { slot: 'sidebar', ...} ]
  cp_data.itemtypes = null;     // { 'TypeName': { type: "Cms...ItemType", name: "Text item", rel_name: "TypeName_set", auto_id: "id_%s" }, ... }


  /**
   * Initialize the data collection by reading the DOM.
   *
   * Read all the DOM formsets into the "dom_placeholders" variable.
   * This information is used in this library to lookup formsets.
   */
  cp_data.init = function()
  {
    // Find all formset items.
    var all_items   = $(".inline-group > .inline-related");
    var empty_items = all_items.filter(".empty-form");
    var fs_items    = all_items.filter(":not(.empty-form)");

    if( cp_data.placeholders )
    {
      // Split formset items by the placeholder they belong to.
      for(var i = 0; i < fs_items.length; i++)
      {
        // Get formset DOM elements
        var fs_item           = fs_items.eq(i);
        var placeholder_input = fs_item.find("input[name$=-placeholder]");

        // placeholder_slot may be __main__, placeholder.slot will be the real one.
        var placeholder_id = placeholder_input.val();
        var placeholder = cp_data.get_placeholder_by_id(placeholder_id);
// TODO: This was old code when a placeholder was found by name.
//        if( placeholder )
//          placeholder_input.val(placeholder.id);

        // Append item to administration
        var dom_placeholder = cp_data.get_or_create_dom_placeholder(placeholder);
        cp_data.dom_placeholders[placeholder.slot].items.push(fs_item);
      }
    }

    // Add the empty items to the itemtypes dictionary.
    for(i = 0; i < empty_items.length; i++)
    {
      var empty_item = cp_data.get_formset_item_data(empty_items[i]);   // {fs_item, index, itemtype: {..}}
      empty_item.itemtype.item_template = empty_item.fs_item;
    }
  }


  cp_data.get_or_create_dom_placeholder = function(placeholder)
  {
    var dom_placeholder = cp_data.dom_placeholders[placeholder.slot];
    if(!dom_placeholder)
      dom_placeholder = cp_data.dom_placeholders[placeholder.slot] = { slot: placeholder.slot, items: [], role: placeholder.role };

    return dom_placeholder;
  }


  /**
   * Find the desired placeholder, including the preferred occurrence of it.
   */
  cp_data.get_placeholder_for_role = function(role, preferredNr)
  {
    if( cp_data.placeholders == null )
      throw new Error("cp_data.setPlaceholders() was never called");

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
   * Find the placeholder corresponding with a given ID.
   */
  cp_data.get_placeholder_by_id = function(id)
  {
    return _get_placeholder_by_property('id', id);
  }


  /**
   * Find the placeholder corresponding with a given slot.
   */
  cp_data.get_placeholder_by_slot = function(slot)
  {
    return _get_placeholder_by_property('slot', slot);
  }


  function _get_placeholder_by_property(prop, value)
  {
    if( cp_data.placeholders == null )
      throw new Error("cp_data.setPlaceholders() was never called");

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
      window.console.error("ecms_data.get_placeholder_by_" + prop + ": no object for '" + value + "'");
    return null;
  }


  /**
   * Return the DOM elements where the placeholder adds it's contents.
   */
  cp_data.get_placeholder_pane = function(placeholder_slot, last_known_nr)
  {
    var pane_id = cp_data.get_placeholder_by_slot(placeholder_slot).domnode;
    return cp_data._get_object_for_pane($("#" + pane_id));
  }


  /**
   * Return the placeholder pane for a given FormSet item.
   */
  cp_data.get_placeholder_pane_for_item = function(fs_item)
  {
    var pane = fs_item.closest(".cp-content").parent();
    return cp_data._get_object_for_pane(pane);
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
      var pane_id = cp_data.placeholders[i].domnode;
      pane_objects.push(cp_data._get_object_for_pane($("#" + pane_id)));
    }

    return pane_objects;
  }


  cp_data._get_object_for_pane = function(pane)
  {
    if( pane.length == 0 )
      throw new Error("Pane not found: " + pane.selector);
    return {
      root: pane,  // mainly for debugging
      content: pane.children(".cp-content"),
      empty_message: pane.children('.cp-empty')
    };
  }


  /**
   * Get the formset information, by passing a child node.
   */
  cp_data.get_formset_item_data = function(child_node)
  {
    if( cp_data.itemtypes == null )
      throw new Error("cp_data.setContentItemTypes() was never called");

    var fs_item = $(child_node).closest(".inline-related");
    var ids = fs_item.attr("id").split('-');
    var prefix = ids[0];

    // Get itemtype
    var itemtype = null;
    for(var i in cp_data.itemtypes)
    {
      if( cp_data.itemtypes[i].prefix == prefix )
      {
        itemtype = cp_data.itemtypes[i];
        break;
      }
    }

    return {
      fs_item: fs_item,
      itemtype: itemtype,
      index: parseInt(ids[1])
    };
  }


  /**
   * Verify that a given item type exists.
   */
  cp_data.get_formset_itemtype = function(typename)
  {
    if( cp_data.itemtypes == null )
      throw new Error("cp_data.setContentItemTypes() was never called");

    return cp_data.itemtypes[typename];
  }


  cp_data.cleanup_empty_placeholders = function()
  {
    for(var i in dom_placeholders)
      if(dom_placeholders[i].items.length == 0)
        delete dom_placeholders[i];
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
