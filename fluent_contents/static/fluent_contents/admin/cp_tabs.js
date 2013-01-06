/**
 * A Tab interface to organize Placeholder panes.
 */
var cp_tabs = {};

(function($)
{

  // Cached DOM objects
  var $empty_tabnav = null;
  var $empty_tab = null;
  var $placeholder_inline;
  var $loading_tabnav;
  var $orphaned_tabnav;
  var $orphaned_tab;
  var $tabnav_root;
  var $tabs_root;

  var placeholder_group_prefix = null;
  var placeholder_id_prefix = null;

  // Allow debugging
  var stub = function() {};
  var console = window.console || {'log': stub, 'error': stub, 'warn': stub};


  cp_tabs.init = function()
  {
    // Get the tab templates
    $empty_tabnav = $("#cp-tabnav-template");
    $empty_tab = $("#tab-template");
    $loading_tabnav = $("#cp-tabnav-loading");
    $orphaned_tabnav = $("#cp-tabnav-orphaned");
    $orphaned_tab = $("#tab-orphaned");
    $tabnav_root = $("#cp-tabnav");
    $tabs_root = $("#cp-tabmain");

    // Bind events
    $tabnav_root.find("a").mousedown( cp_tabs.onTabMouseDown ).click( cp_tabs.onTabClick );

    $placeholder_inline = $(".inline-placeholder-group");
    placeholder_group_prefix = $placeholder_inline.attr('id').replace(/-group$/, '');
    placeholder_id_prefix = 'id_' + placeholder_group_prefix;   // HACK: assume id_%s as auto_id.

    // Improve quick editing a lot:
    cp_tabs._select_previous_or_first_tab();

    // Hide empty message
    if( cp_data.get_placeholders().length )
      $("#cp-tabs-empty").hide();
  }


  /**
   * Get a fallback tab to store an orphaned item.
   */
  cp_tabs.get_fallback_pane = function(role, last_known_nr)
  {
    $orphaned_tabnav.css("display", "inline");
    return cp_data.get_object_for_pane($("#tab-orphaned"));
  }


  /**
   * Hide the tab to display an orphaned item.
   */
  cp_tabs.hide_fallback_pane = function()
  {
    $orphaned_tabnav.hide();
    $orphaned_tab.hide();
    cp_tabs._ensure_active_tab();
  }


  /**
   * Rearrange all tabs due to the newly loaded layout.
   *
   * layout = {placeholders: [{key, title}, ..]}
   */
  cp_tabs.load_layout = function(layout)
  {
    $loading_tabnav.hide();

    // Deal with invalid layouts
    if( layout == null )
    {
      alert("Error: no layout information available!");
      return;
    }

    // Cache globally
    console.log("Received placeholders: ", layout.placeholders, "dom_regions=", cp_data.dom_placeholders );
    var dbplaceholders = cp_data.get_initial_placeholders();
    var newplaceholders = layout.placeholders;
    var placeholders = [];

    // Create map of old IDs
    var dbplaceholderids = {};
    for( var i = 0, len = dbplaceholders.length; i < len; i++ )
      dbplaceholderids[dbplaceholders[i].slot] = dbplaceholders[i].id;

    // Amend the placeholder data with old ID's and dommnode info.
    var reused_ids = {};
    for( i = 0, len = newplaceholders.length; i < len; i++ )
    {
      var placeholder = newplaceholders[i];
      var placeholder_id = dbplaceholderids[placeholder.slot] || '';

      // Prepare data for administration
      // Reuse old ID's when possible.
      placeholder.domnode = "tab-region-" + placeholder.slot;
      placeholder.role = placeholder.role || 'm';
      placeholder.id = placeholder_id;
      placeholders.push(placeholder);

      if( newplaceholders[i].id )
        reused_ids[newplaceholders[i].id] = true;
    }

    // Find out how many items are deleted
    // Remove the ones which are no longer available.
    var id_index = 0;
    $tabs_root.children('.cp-placeholder-delete, .cp-placeholder-delete').remove();
    for( var i = 0; i < dbplaceholders.length; i++ )
    {
      var id = dbplaceholders[i].id;
      if( !reused_ids[id] )
      {
        var name = placeholder_group_prefix + '-' + id_index++;
        $tabs_root.prepend(
          '<input type="checkbox" class="cp-placeholder-delete" name="' + name + '-DELETE" checked="checked" />' +
            '<input type="hidden" class="cp-placeholder-delete" name="' + name + '-id" value="' + id + '" />'
        );
      }
    }

    // Create tabs for the new placeholders
    var new_index = dbplaceholders.length;  // Start after ID's that exist or are removed.
    for( i = 0, len = newplaceholders.length; i < len; i++ )
    {
      // Create DOM nodes
      placeholder = newplaceholders[i];
      $loading_tabnav.before( cp_tabs._create_tab_title(placeholder) );
      $tabs_root.append( cp_tabs._create_tab_content(placeholder, ( placeholder.id ? id_index : new_index )) );

      if( placeholder.id )
        id_index++;
      else
        new_index++;
    }

    // Total forms should also incorporate deleted records, so always be >= dbamount
    $("#" + placeholder_id_prefix + "-TOTAL_FORMS").val(new_index);

    // Rebind event
    var $tab_links = $tabnav_root.children("li.cp-region").children("a");
    $tab_links.mousedown( cp_tabs.onTabMouseDown ).click( cp_tabs.onTabClick );

    // Migrate formset items.
    cp_data.set_placeholders( placeholders );
    cp_plugins.move_items_to_placeholders();

    // Cleanup. The previous old tabs can be removed now.
    cp_tabs._remove_old_tabs();
    cp_tabs._ensure_active_tab();
    cp_tabs.update_empty_message();
    cp_tabs._restore_tabmain_height();

    // Show tabbar if still hidden (at first load)
    cp_tabs.show();
  }


  cp_tabs._create_tab_title = function(placeholder)
  {
    // The 'cp-region' class is not part of the template, to avoid matching the actual tabs.
    var $tabtitle = $empty_tabnav.clone().removeAttr("id").addClass("cp-region").show();
    $tabtitle.find("a").attr("href", '#' + placeholder.domnode).text(placeholder.title);
    return $tabtitle;
  }


  cp_tabs._create_tab_content = function(placeholder, new_index)
  {
    // The 'cp-region-tab' class is not part of the template, but added here to avoid matching the actual tabs earlier on.
    var $tab = $empty_tab.clone().attr("id", placeholder.domnode).addClass("cp-region-tab");
    $tab.find(".cp-plugin-add-button").attr({
        'data-placeholder-id': placeholder.id,
        'data-placeholder-slot': placeholder.slot
    });

    // Set placeholder form fields (id, slot, name, title) from placeholder object.
    var $inputs = $tab.children('input[name*=__prefix__]');
    for( var i = 0; i < $inputs.length; i++ )
    {
      var name = $inputs[i].name;
      var fieldname = name.substring(name.lastIndexOf('-') + 1);

      if( fieldname == 'id' && ! placeholder.id)
        $inputs.eq(i).removeAttr('value');
      else
        $inputs[i].value = placeholder[fieldname];
    }

    // TODO: this is tricky, temporary there will be two elements with the same ID.
    var name_prefix = $inputs.filter('[name$=-__prefix__-id]').attr('name').replace(/-__prefix__-id/, '');
    cp_admin.renumber_formset_item($tab, name_prefix, new_index);
    return $tab;
  }


  cp_tabs.get_container = function()
  {
    return $placeholder_inline;
  }


  cp_tabs.show = function(slow)
  {
    if( slow )
      $placeholder_inline.slideDown();
    else
      $placeholder_inline.show();
  }


  cp_tabs.hide = function(slow)
  {
    if( slow )
      $placeholder_inline.slideUp();
    else
      $placeholder_inline.hide();
  }


  cp_tabs.expire_all_tabs = function()
  {
    // Replace tab titles with loading sign.
    // Must avoid copying the template tab too (this is another guard against it).
    $loading_tabnav.show();
    $orphaned_tabnav.hide();
    $tabnav_root.children("li.cp-region:not(#cp-tabnav-template)").remove();

    // set fixed height to avoid scrollbar/footer flashing.
    var height = $tabs_root.height();
    if( height )
    {
      $tabs_root.css("height", height + "px");
    }

    // Hide and mark as old.
    var all_tabs = $tabs_root.children(".cp-region-tab:not(#tab-template)");
    all_tabs.removeClass("cp-region-tab").addClass("cp-oldtab").removeAttr("id").hide();
  }


  cp_tabs.is_expired_tab = function($node)
  {
    return $node.closest('.cp-tab').hasClass('cp-oldtab');
  }


  cp_tabs._ensure_active_tab = function()
  {
    // Activate the fallback item (first) if none active.
    // This needs to happen after organize, so orphans tab might be visible
    if( $tabnav_root.children("li.active:visible").length == 0 )
    {
      cp_tabs._select_previous_or_first_tab();  // TODO: check orphaned tab
    }
  }


  cp_tabs.update_empty_message = function()
  {
    var no_tabs = cp_data.get_placeholders().length == 0 && $tabs_root.find(".inline-related").length == 0;
    $("#cp-tabs-empty")[no_tabs ? "show" : "hide"]();
  }


  cp_tabs._select_previous_or_first_tab = function()
  {
    // See if there is an old selected tab that can be reselected
    var $tab;
    var oldtab = ($.cookie ? $.cookie('cp-last-tab') : null);
    if( oldtab )
      $tab = $tabnav_root.find('li.cp-region > a[href$=#' + oldtab + ']');  // .children() gave no results (note Django 1.3 ships jQuery v1.4.2)

    if( ! $tab || $tab.length == 0 )
    {
      // Get the first tab
      $tab = $tabnav_root.children("li.cp-region > a:first");
      if( $tab.length == 0 )
      {
        // Only fallback tab visible?
        $tab = $orphaned_tabnav.children("a:first");
      }
    }

    if( $tab.length )
      $tab.mousedown().mouseup().click();
    return $tab.length > 0;
  }


  cp_tabs._remove_old_tabs = function()
  {
    $tabs_root.children(".cp-oldtab").remove();

    // Remove empty/obsolete dom regions
    cp_data.cleanup_empty_placeholders();
  }


  cp_tabs._restore_tabmain_height = function()
  {
    // When the tab height is fixated (during hiding), restore that
    // after children height recalculations / wysiwyg initialisation have happened.
    setTimeout( function() { $tabs_root.css("height", ''); }, 100 );
  }


  // -------- Basic tab events ------

  /**
   * Tab button click
   */
  cp_tabs.onTabMouseDown = function(event)
  {
    var thisnav = $(event.target).parent("li");
    cp_tabs.enable_tab(thisnav);
  }


  cp_tabs.onTabClick = function(event)
  {
    // Prevent navigating to the href.
    event.preventDefault();
  }


  cp_tabs.enable_tab = function($thisnav)
  {
    // Find new pane to activate
    var href  = $thisnav.find("a").attr('href');
    var active = href.substring( href.indexOf("#") + 1 );
    var $panes = $tabs_root.children('.cp-tab');
    var $activePane = $panes.filter("#" + active);

    // And switch
    $panes.hide();
    $activePane.show();
    $tabnav_root.find('li').removeClass("active");
    $thisnav.addClass("active");

    cp_tabs._focus_first_input($activePane);

    // Store as current tab
    if( $.cookie )
    {
      $.cookie('cp-last-tab', active);
    }
  }


  cp_tabs._focus_first_input = function(root)
  {
    // Auto focus on first editor.
    // This can either be an iframe (WYSIWYG editor), or normal input field.
    var $firstField = root.find(".yui-editor-editable-container:first > iframe, .mceEditor:first iframe, .form-row :input:first").eq(0);
    $firstField.focus();
  }


})(window.jQuery || django.jQuery);
