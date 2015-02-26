/**
 * This file deals with the internal DOM manipulations within a content placeholder.
 * namely the plugin ("content item types") which are added, reordered, and removed there.
 */
var cp_plugins = {};

(function($){

  // Global state
  var has_load_error = false;
  var restore_timer = null;

  // Allow debugging
  var stub = function() {};
  var console = window.console || {'log': stub, 'error': stub};

  // Settings
  var plugin_handlers = {};
  var on_init_callbacks = [];
  var before_layout_callbacks = [];
  var is_first_layout = true;


  /**
   * Bind an event handler before the plugins are initialized.
   */
  cp_plugins.on_init = function(callback)
  {
    on_init_callbacks.push(callback);
  }


  /**
   * Bind an event before the final layout is organized.
   * The callback can return true to stop the initialisation of the plugin.
   *
   * At some point, `move_items_to_placeholders()` needs to be called.
   * Either manually, or through some `load_layout()` function.
   */
  cp_plugins.on_init_layout = function(callback)
  {
    before_layout_callbacks.push(callback);
  }


  cp_plugins.init = function()
  {
    $("#content-main > form").submit( cp_plugins.onFormSubmit );

    if($.fn.on) {
      // jQuery 1.7+
      $("#content-main")
        .on('click', ".cp-plugin-add-button", cp_plugins.onAddButtonClick )
        .on('click', ".cp-copy-language-controls .cp-copy-button", cp_plugins.onCopyLanguageButtonClick )
        .on('click', ".cp-item-controls .cp-item-up", cp_plugins.onItemUpClick )
        .on('click', ".cp-item-controls .cp-item-down", cp_plugins.onItemDownClick )
        .on('click', ".cp-item-controls .cp-item-move", cp_plugins.onItemMoveClick )
        .on('click', ".cp-item-controls .cp-item-delete a", cp_plugins.onDeleteClick );
    }
    else {
      $(".cp-plugin-add-button").live( 'click', cp_plugins.onAddButtonClick );
      $(".cp-copy-language-controls .cp-copy-button").live( 'click', cp_plugins.onCopyLanguageButtonClick );
      $(".cp-item-controls .cp-item-up").live( 'click', cp_plugins.onItemUpClick );
      $(".cp-item-controls .cp-item-down").live( 'click', cp_plugins.onItemDownClick );
      $(".cp-item-controls .cp-item-move").live( 'click', cp_plugins.onItemMoveClick );
      $(".cp-item-controls .cp-item-delete a").live( 'click', cp_plugins.onDeleteClick );
    }

    // Allow plugins to initialize
    cp_plugins._init_view_handlers();
  }


  cp_plugins.post_init = function()
  {
    // Allow external code to change the layout tabs
    // hence delaying the initialisation.
    for( var i = 0; i < before_layout_callbacks.length; i++ )
    {
      if( before_layout_callbacks[i]() )
      {
        console.log('cp_plugins.post_init() - skipped, waiting for layout.');
        return;
      }
    }

    // Do normal initialisation
    cp_plugins.move_items_to_placeholders();
  }


  /**
   * Move all formset items to their appropriate tabs.
   * The tab is selected based on template key, and role.
   */
  cp_plugins.move_items_to_placeholders = function()
  {
    // Count number of seen tabs per role.
    var roles_seen = {};
    var placeholders = cp_data.get_placeholders();
    if(placeholders == null) {
      console.error("Placeholders are not defined. Is the proper PlaceholderFieldAdmin/PlaceholderEditorAdmin class used?")
      return;
    }
    for(var i = 0; i < placeholders.length; i++)
      roles_seen[placeholders[i].role] = 0;

    // Move all items to the tabs.
    // TODO: direct access to dom_placeholder data, should be cleaned up.
    // The DOM placeholders holds the desired layout of all items.
    // Depending on the current layout, it placeholder pane can be found, or needs to be migrated.
    for(var placeholder_slot in cp_data.dom_placeholders)
    {
      if(! cp_data.dom_placeholders.hasOwnProperty(placeholder_slot))
        continue;

      var dom_placeholder = cp_data.dom_placeholders[placeholder_slot];
      var last_role_occurance =  ++roles_seen[dom_placeholder.role];
      if( dom_placeholder.items.length == 0)
        continue;

      // Fill the tab
      var pane = cp_plugins.get_new_placeholder_pane(dom_placeholder, last_role_occurance);
      cp_plugins.move_items_to_pane(dom_placeholder, pane);
    }

    // Initialisation completed!
    if( is_first_layout )
    {
      console.log("Initialized editor, placeholders=", cp_data.get_placeholders(), " contentitems=", cp_data.contentitem_metadata);
      is_first_layout = false;
    }
  }


  /**
   * Find the new placeholder where the contents can be displayed.
   */
  cp_plugins.get_new_placeholder_pane = function(dom_placeholder, last_known_nr)
  {
    var pane;
    var isExpiredTab = window.cp_tabs ? cp_tabs.is_expired_tab : function(node) { return false; };

    // Option 1. Find identical placeholder by slot name.
    var placeholder = cp_data.get_placeholder_by_slot(dom_placeholder.slot);
    if( placeholder )
    {
      // Option 1. Find by slot name,
      pane = cp_data.get_placeholder_pane(placeholder);
      if( pane && ! isExpiredTab(pane.root) )
        return pane;
    }

    // Option 2. Find a good substitude candidate, the last placeholder which was used for the same role.
    var altplaceholder = cp_data.get_placeholder_for_role(dom_placeholder.role, last_known_nr);
    if( altplaceholder )
    {
      pane = cp_data.get_placeholder_pane(altplaceholder);
      if( pane && ! isExpiredTab(pane.root) )
      {
        console.log("Using placeholder '" + altplaceholder.slot + "' as fallback for item from placeholder '" + dom_placeholder.slot + "'.");
        return pane;
      }
    }

    // Option 3: If there is only one placeholder, that can be used.
    // This is typically the case for the PlaceholderField() object at the page.
    var single_placeholder = cp_data.get_single_placeholder();
    if( single_placeholder )
    {
      pane = cp_data.get_placeholder_pane(single_placeholder);
      if( pane && ! isExpiredTab(pane.root) )
      {
        console.log("Using single placeholder '" + single_placeholder.slot + "' as fallback for item from placeholder '" + dom_placeholder.slot + "'.");
        return pane;
      }
    }

    // Option 4. Open a "lost+found" tab.
    // NOTE: not really a clean solution, needs a better (public) API for this (cp_tabs is optional).
    if( window.cp_tabs )
    {
      pane = cp_tabs.get_fallback_pane();
      if( pane )
      {
        console.log("Using orphaned tab as fallback for item from placeholder '" + dom_placeholder.slot + "'.");
        return pane;
      }
    }

    throw new Error("No placeholder pane for placeholder: " + dom_placeholder.slot + " (role: " + dom_placeholder.role + ")");
  }


  /**
   * Move the items of one placeholder to the given tab.
   */
  cp_plugins.move_items_to_pane = function(dom_placeholder, pane)
  {
    if( !pane || pane.content.length == 0)
    {
      if( window.console )
        window.console.error("Invalid tab, missing tab-content: ", pane);
      return;
    }

    console.log("move_items_to_pane:", dom_placeholder, pane);

    // Reorder in accordance to the sorting order.
    cp_plugins._sort_items( dom_placeholder.items );

    // Move all items to that tab.
    // Restore item values upon restoring fields.
    for(var i = 0; i < dom_placeholder.items.length; i++)
    {
      var $fs_item = dom_placeholder.items[i];
      dom_placeholder.items[i] = cp_plugins._move_item_to( $fs_item, function _move_to_pane($fs_item)
      {
        pane.content.append($fs_item);

        // Update the placeholder-id.
        // Note this will not update the dom_placeholders,
        // hence the item will move back when the original layout is restored.
        if( pane.placeholder )
          cp_plugins._set_pageitem_data($fs_item, pane.placeholder, i);
      });
    }

    if( dom_placeholder.items.length )
      pane.empty_message.hide();
  }


  /**
   * Move an item to a new place.
   */
  cp_plugins._move_item_to = function( $fs_item, add_action )
  {
    var itemId = $fs_item.attr("id");

    // Don't restore the special fields,
    // The add_action could move the formset item, and this update it.
    var ignoreFields = ['placeholder', 'placeholder_slot', 'sort_order', 'DELETE'];
    var ignoreTest = function(name) { return $.inArray(name.substring(name.lastIndexOf('-')+1), ignoreFields) != -1; };

    // Remove the item.
    cp_plugins.disable_pageitem($fs_item);   // needed for WYSIWYG editors!
    var values = cp_plugins._get_input_values($fs_item, ignoreTest);
    add_action( $fs_item );

    // Fetch the node reference as it was added to the DOM.
    $fs_item = $("#" + itemId);

    // Re-enable the item
    cp_plugins._set_input_values($fs_item, values, ignoreTest);
    cp_plugins.enable_pageitem($fs_item);

    // Return to allow updating the administration
    return $fs_item;
  }


  cp_plugins._get_input_values = function($root, ignoreTestFunc)
  {
    var $inputs = $root.find(":input");
    var values = {};
    for(var i = 0; i < $inputs.length; i++)
    {
      var $input = $inputs.eq(i)
        , id = $input.attr("id") || $input.attr("name")  // multiple input checkbox has one name, but different IDs
        , input_type = $input[0].type;
      if((input_type == 'radio' || input_type == 'checkbox') && !$input[0].checked)
        continue;

      if( !ignoreTestFunc || !ignoreTestFunc(name) )
        values[id] = $input.val();
    }

    return values;
  }


  cp_plugins._set_input_values = function($root, values, ignoreTestFunc)
  {
    var $inputs = $root.find(":input");
    for(var i = 0; i < $inputs.length; i++)
    {
      var $input = $inputs.eq(i)
        , id = $input.attr("id") || $input.attr("name");

      if( values.hasOwnProperty(id)
       && (!ignoreTestFunc || !ignoreTestFunc(id)) )
      {
        var value = values[id];
        cp_plugins._set_input_value($input, value);
      }
    }
  }


  cp_plugins._set_input_value = function($input, value)
  {
    var input_type = $input[0].type;
    if( input_type == 'radio' || input_type == 'checkbox' )
    {
      $input[0].checked = ($input[0].value == value);
    }
    else
    {
      if(value == null)
        $input.removeAttr('value');
      else
        $input.val(value);
    }
  }


  // -------- Add plugin feature ------

  /**
   * Add plugin click
   */
  cp_plugins.onAddButtonClick = function(event)
  {
    var $add_button = $(event.target);
    var placeholder_key = $add_button.attr("data-placeholder-slot");  // TODO: use ID?
    var model_name = $add_button.siblings("select").val();
    cp_plugins.add_formset_item( placeholder_key, model_name );
  }


  /**
   * Add an item to a tab.
   */
  cp_plugins.add_formset_item = function( placeholder_slot, model_name, options )
  {
    options = options || {};

    // The Django admin/media/js/inlines.js API is not public, or easy to use.
    // Recoded the inline model dynamics.

    // Get objects
    var inline_meta = cp_data.get_contentitem_metadata_by_type(model_name);
    var group_prefix = inline_meta.auto_id.replace(/%s/, inline_meta.prefix);
    var placeholder = cp_data.get_placeholder_by_slot(placeholder_slot);
    var dom_placeholder = cp_data.get_or_create_dom_placeholder(placeholder);

    // Get DOM items
    var pane  = cp_data.get_placeholder_pane(placeholder);
    var total = $("#" + group_prefix + "-TOTAL_FORMS")[0];

    // Clone the item.
    var new_index = total.value;
    var item_id   = inline_meta.prefix + "-" + new_index;
    var newhtml   = options.get_html
                  ? options.get_html(inline_meta, new_index)   // hook
                  : inline_meta.item_template.get_outerHtml().replace(/__prefix__/g, new_index);
    var $newitem  = $(newhtml).removeClass("empty-form").attr("id", item_id);

    // Add it
    pane.content.append($newitem);
    pane.empty_message.hide();

    var $fs_item = $("#" + item_id);
    if( $fs_item.length == 0 )
      throw new Error("New FormSetItem not found: #" + item_id);

    // Update administration
    dom_placeholder.items.push($fs_item);
    total.value++;

    // Configure it
    cp_plugins._set_pageitem_data($fs_item, placeholder, new_index);
    cp_plugins.enable_pageitem($fs_item);
    cp_plugins.update_sort_order(pane);  // Not required, but keep the form state consistent all the time.
    if(options.on_post_add) options.on_post_add($fs_item);
  }


  cp_plugins._set_pageitem_data = function($fs_item, placeholder, new_sort_index)
  {
    var field_prefix = cp_plugins._get_field_prefix($fs_item);
    $("#" + field_prefix + "-placeholder").val(placeholder.id);
    $("#" + field_prefix + "-placeholder_slot").val(placeholder.slot);
    $("#" + field_prefix + "-sort_order").val(new_sort_index);
  }


  cp_plugins._get_field_prefix = function($fs_item)
  {
    // Currently redetermining group_prefix, avoid letting fs_item to go out of sync with different call paths.
    var current_item = cp_data.get_inline_formset_item_info($fs_item);
    var group_prefix = current_item.auto_id.replace(/%s/, current_item.prefix);
    return group_prefix + "-" + current_item.index;
  }


  // -------- Moving and sorting plugins ------


  cp_plugins.onItemUpClick = function(event)
  {
    event.preventDefault();
    cp_plugins.swap_formset_item(event.target, true);
  }


  cp_plugins.onItemMoveClick = function(event)
  {
    event.preventDefault();
    event.stopPropagation();
    cp_plugins._show_move_popup(event.target);
  }


  cp_plugins.onItemDownClick = function(event)
  {
    event.preventDefault();
    cp_plugins.swap_formset_item(event.target, false);
  }


  cp_plugins.swap_formset_item = function(child_node, isUp)
  {
    var current_item = cp_data.get_inline_formset_item_info(child_node);
    var $fs_item = current_item.fs_item;
    var pane = cp_data.get_placeholder_pane_for_item($fs_item);

    // Get next/previous item
    var relative = $fs_item[isUp ? 'prev' : 'next']("div");
    if(!relative.length) return;

    cp_plugins._fixate_item_height($fs_item);
    $fs_item = cp_plugins._move_item_to( $fs_item, function _moveUpDown(fs_item) { fs_item[isUp ? 'insertBefore' : 'insertAfter'](relative); } );
    cp_plugins._restore_item_height($fs_item);
    cp_plugins.update_sort_order(pane);
  }


  cp_plugins.move_item_to_placeholder = function(child_node, slot)
  {
    var dominfo = cp_data.get_formset_dom_info(child_node);
    var current_item = cp_data.get_inline_formset_item_info(child_node);  // childnode is likely already a current_item object.
    var $fs_item = current_item.fs_item;

    var old_pane = cp_data.get_placeholder_pane_for_item($fs_item);
    var old_slot = old_pane.is_orphaned ? '__orphaned__' : dominfo.placeholder_slot;
    var old_placeholder = cp_data.get_placeholder_by_slot(old_slot);
    var new_placeholder = cp_data.get_placeholder_by_slot(slot);
    var dom_placeholder = cp_data.get_or_create_dom_placeholder(new_placeholder);
    var new_pane = cp_data.get_placeholder_pane(new_placeholder);

    // Move formset item
    $fs_item = cp_plugins._move_item_to( $fs_item, function(fs_item) { new_pane.content.append(fs_item); } );
    var last_index = cp_plugins.update_sort_order(new_pane);
    cp_plugins._set_pageitem_data($fs_item, new_placeholder, last_index);

    // Move to proper dom placeholder list.
    // dom_placeholder is currently not accurate, behaves more like "desired placeholder".
    if( old_placeholder ) cp_data.remove_dom_item(old_placeholder.slot, current_item);
    dom_placeholder.items.push($fs_item);

    // Update placeholders + hide popup
    new_pane.empty_message.hide();
    cp_plugins._check_empty_pane(old_pane);
    cp_plugins._hide_move_popup(null);
  }


  cp_plugins._show_move_popup = function(child_node)
  {
    var current_item = cp_data.get_inline_formset_item_info(child_node);
    var dominfo      = cp_data.get_formset_dom_info(current_item);
    var placeholders = cp_data.get_placeholders();

    // Build popup HTML
    var html = '<p>Move to</p><ul>';
    for( var i = 0; i < placeholders.length; i++ )
    {
      var placeholder = placeholders[i];
      if( (placeholder.id && placeholder.id == dominfo.placeholder_id)
       || (placeholder.slot && placeholder.slot == dominfo.placeholder_slot) )
        continue;

      html += '<li><a href="#' + placeholder.slot + '">' + placeholder.title + '</a></li>';
    }
    html += '</ul>';
    $("body").append('<div id="cp-move-popup">' + html + '</div>');

    // Set position
    var $window = $(window);
    var $child_node = $(child_node);
    var pos = $child_node.offset();
    var $popup = $("#cp-move-popup");
    var oldJquery = !$.fn.on;  // assume that 1.7 has the bug fixed.
    $popup.offset({
      left: parseInt(pos.left) - $popup.width() + 18 + (oldJquery ? $window.scrollLeft() : 0),
      top: parseInt(pos.top) + $child_node.height() + 2 + (oldJquery ? $window.scrollTop() : 0)
    });

    // Configure clicks
    $popup.find('a').click(function(event){
      event.preventDefault();
      var slot = event.target.href;
      slot = slot.substring(slot.indexOf('#') + 1);
      cp_plugins.move_item_to_placeholder(current_item, slot);
    });

    $(document).click(cp_plugins._hide_move_popup);

    // Show!
    $popup.fadeIn(150);
  }

  cp_plugins._hide_move_popup = function(event)
  {
    if( event && $(event.target).closest('#cp-move-popup').length ) return;
    $("#cp-move-popup").remove();
    $(document).unbind('click', cp_plugins._hide_move_popup);
  }


  cp_plugins._fixate_item_height = function($fs_item)
  {
    // Avoid height flashes by fixating height
    clearTimeout( restore_timer );
    var $tabmain = $("#cp-tabmain");   // FIXME: this breaks encapsulation of the tabbar control. Yet it is pretty easy this way.
    $tabmain.css("height", $tabmain.height() + "px");
    $fs_item.css("height", $fs_item.height() + "px");
  }


  cp_plugins._restore_item_height = function($fs_item)
  {
    // Give more then enough time for the YUI editor to restore.
    // The height won't be changed within 2 seconds at all.
    var $tabmain = $("#cp-tabmain");   // FIXME: this breaks encapsulation of the tabbar control. Yet it is pretty easy this way.
    restore_timer = setTimeout(function() {
      $fs_item.css("height", '');
      $tabmain.css("height", '');
    }, 500);
  }


  cp_plugins.onFormSubmit = function(event)
  {
    // The form state should be consistent all the time,
    // but to be sure, update the sort ordering.
    var panes = cp_data.get_placeholder_panes();
    for(var i = 0; i < panes.length; i++)
    {
      cp_plugins.update_sort_order(panes[i]);
    }

    // Validate
    for(var i = 0; i < panes.length; i++)
    {
      if( ! cp_plugins.validate_placeholder_forms(panes[i]) )
      {
        alert("Internal CMS error: error in placeholder data found. Not saving results");
        event.preventDefault();
        return false;
      }
    }
  }


  cp_plugins.update_sort_order = function(tab)
  {
    // Can just assign the order in which it exists in the DOM.
    var sort_order = tab.content.find("input[id$=-sort_order]");
    for(var i = 0; i < sort_order.length; i++)
    {
      sort_order[i].value = i;
    }
    return i - 1;
  }


  cp_plugins.validate_placeholder_forms = function(tab)
  {
    var desired_id = tab.placeholder.id;
    var desired_slot = tab.placeholder.slot;
    var $inputs = tab.content.find('input[type=hidden]');
    var $ids = $inputs.filter('[id$=-placeholder]');
    var $slots = $inputs.filter('[id$=-placeholder_slot]');
    if( $ids.length != $slots.length )
      return false;

    for( var i = 0; i < $ids.length; i++ )
    {
      var id = $ids[i].value, slot = $slots[i].value;
      if( id != desired_id || (slot != desired_slot && !(slot == '' && id)) )
        return false;
    }
    return true;
  }


  cp_plugins._sort_items = function($items)
  {
    // The sort_order field is likely top-level, but the fieldset html can place it anywhere.
    for( var i = 0; i < $items.length; i++ )
    {
      var $fs_item = $items[i];
      $fs_item._sort_order = parseInt($fs_item.find("input[id$=-sort_order]:first").val());
    }

    $items.sort(function(a, b) { return a._sort_order - b._sort_order; });
  }



  // -------- Copy languages ------

  cp_plugins.onCopyLanguageButtonClick = function(event)
  {
    var $button = $(event.target);
    var language_code = $button.siblings('select').val();
    var placeholder_slot = $button.attr('data-placeholder-slot');
    var url = $('.inline-placeholder-group').attr('data-get-placeholder-data-url');
    $.ajax({
      url: url,
      dataType: 'json',
      data: 'language=' + language_code,
      success: function(data, textStatus, xhr)
      {
        // Ask to update the tabs!
        if(data.success)
          cp_plugins.load_formset_data(data, placeholder_slot);
        else
          alert("Internal CMS error: failed to fetch site data!");
      },
      error: function(xhr, textStatus, ex)
      {
        alert("Internal CMS error: failed to fetch site data!");    // can't yet rely on $.ajaxError
      }
    });
  }


  cp_plugins.load_formset_data = function(data, match_placeholder_slot)
  {
    for (var i = 0; i < data.formset_forms.length; i++) {
      // Each item is stored as basic formdata
      // and generated HTML.
      var itemdata = data.formset_forms[i];
      if(match_placeholder_slot && itemdata.placeholder_slot != match_placeholder_slot)
        continue;

      // Replace the server-side generated prefix,
      // as this clearly won't be the same as what we'll generate client-side.
      var re_old_prefix = new RegExp(itemdata.prefix + '-', 'g');

      cp_plugins.add_formset_item(itemdata.placeholder_slot, itemdata.model, {
        'get_html': function(inline_meta, new_index) {
          // Use the server-side provided HTML, which has fields filled in
          // with all template-styling handled. It's a literal copy of the edit page.
          var new_prefix = inline_meta.prefix + "-" + new_index + "-";
          var new_formfields = itemdata.html.replace(re_old_prefix, new_prefix);

          // Take the original template, replace the contents of the 'cp-formset-item-fields' block.
          var orig_html = inline_meta.item_template.get_outerHtml().replace(/__prefix__/g, new_index);
          var $orig_html = $(orig_html);
          $orig_html.find('.cp-formset-item-fields').empty().html(new_formfields);
          return $orig_html;
        },
        'on_post_add': function($fs_item) {
          // Trigger a change() event for radio fields.
          // This fixes the django-any-urlfield display.
          $fs_item.find('input[type=radio]:checked').change();
        }
      });
    }
  }



  // -------- Delete plugin ------


  /**
   * Delete item click
   */
  cp_plugins.onDeleteClick = function(event)
  {
    event.preventDefault();
    cp_plugins.remove_formset_item(event.target);
  }


  cp_plugins.remove_formset_item = function(child_node)
  {
    // Get dom info
    var current_item = cp_data.get_inline_formset_item_info(child_node);
    var dominfo      = cp_data.get_formset_dom_info(current_item);
    var pane         = cp_data.get_placeholder_pane_for_item(current_item.fs_item);

    // Get administration
    // dominfo slot is always filled in, id may be unknown yet.
    var placeholder  = null;
    var total_count  = parseInt(dominfo.total_forms.value);
    if( dominfo.placeholder_slot )   // could be orphaned tab
      placeholder = cp_data.get_placeholder_by_slot( dominfo.placeholder_slot );

    // Final check
    if( dominfo.id_field.length == 0 )
      throw new Error("ID field not found for deleting objects!");

    // Disable item, wysiwyg, etc..
    current_item.fs_item.css("height", current_item.fs_item.height() + "px");  // Fixate height, less redrawing.
    cp_plugins.disable_pageitem(current_item.fs_item);

    // In case there is a delete checkbox, save it.
    if( dominfo.delete_checkbox.length )
    {
      var id_field = dominfo.id_field.remove().insertAfter(dominfo.total_forms);
      dominfo.delete_checkbox.attr('checked', true).remove().insertAfter(dominfo.total_forms);
    }
    else
    {
      // Newly added item, renumber in reverse order
      for( var i = current_item.index + 1; i < total_count; i++ )
      {
        var $fs_item = $("#" + current_item.prefix + "-" + i);
        cp_admin.renumber_formset_item($fs_item, current_item.prefix, i - 1);
      }

      dominfo.total_forms.value--;
    }

    // And remove item
    current_item.fs_item.remove();

    // Remove from node list, if all removed
    if( placeholder )
    {
      // TODO: currently ignoring return value. dom_placeholder is currently not accurate, behaves more like "desired placeholder".
      // TODO: deal with orphaned items, might exist somewhere in the dom_placeholder administration.
      cp_data.remove_dom_item(placeholder.slot, current_item);
    }

    // Show empty tab message
    cp_plugins._check_empty_pane(pane);
    if( window.cp_tabs )
      cp_tabs.update_empty_message();
  }


  cp_plugins._check_empty_pane = function(pane)
  {
    if( pane.content.children('.inline-related').length == 0 )
    {
      pane.empty_message.show();

      // Orphaned tab?
      if( pane.placeholder == null && window.cp_tabs )
      {
        cp_tabs.hide_fallback_pane();
      }
    }
  }


  // -------- Page item scripts ------

  /**
   * Register a class which can update the appearance of a plugin
   * when it is loaded in the DOM tree.
   */
  cp_plugins.register_view_handler = function(model_typename, view_handler)
  {
    var typename = model_typename;
    if( plugin_handlers[ typename ] )
      throw new Error("Plugin already registered: " + typename);
    //if( cp_data.get_formset_itemtype( typename ) == null )
    //  throw new Error("Plugin Model type unknown: " + typename);

    plugin_handlers[ typename ] = view_handler;
  }

  cp_plugins._init_view_handlers = function()
  {
    // Allow a global initialization (e.g. have a script that handles things for multiple plugins)
    for( var i = 0; i < on_init_callbacks.length; i++ )
    {
      on_init_callbacks[i]();
    }

    // Offer plugin view handlers a change to initialize after the placeholder editor is loaded, but before the items are moved.
    for( var model_name in plugin_handlers )
    {
      if( plugin_handlers.hasOwnProperty(model_name) && plugin_handlers[model_name].initialize )
      {
        var item_meta = cp_data.get_contentitem_metadata_by_type(model_name);
        var $formset_group = $("#" + item_meta.prefix + "-group");
        plugin_handlers[model_name].initialize($formset_group);
      }
    }
  }


  cp_plugins.get_view_handler = function($fs_item)
  {
    var itemdata = cp_data.get_inline_formset_item_info($fs_item);
    return plugin_handlers[ itemdata.type ];
  }


  cp_plugins.enable_pageitem = function($fs_item)
  {
    // Default actions:
    cp_widgets.enable_wysiwyg($fs_item);

    // Custom view handler
    var view_handler = cp_plugins.get_view_handler($fs_item);
    if( view_handler ) view_handler.enable($fs_item);
  }


  cp_plugins.disable_pageitem = function($fs_item)
  {
    // Default actions:
    cp_widgets.disable_wysiwyg($fs_item);

    // Custom code
    var view_handler = cp_plugins.get_view_handler($fs_item);
    if( view_handler ) view_handler.disable($fs_item);
  }

})(window.jQuery || django.jQuery);
