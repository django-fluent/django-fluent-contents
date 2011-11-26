/**
 * A Tab interface to organize Placeholder panes.
 */
var cp_tabs = {};

(function($)
{

  // Cached DOM objects
  var empty_tab_title = null;
  var empty_tab = null;

  // Allow debugging
  var stub = function() {};
  var console = window.console || {'log': stub, 'error': stub};


  cp_tabs.init = function()
  {
    // Get the tab templates
    empty_tab_title = $("#cp-tabnav-template");
    empty_tab       = $("#tab-template");

    // Bind events
    $("#cp-tabnav a").mousedown( cp_tabs.onTabMouseDown ).click( cp_tabs.onTabClick );
  }


  /**
   * Get a fallback tab to store an orphaned item.
   */
  cp_tabs._get_fallback_tab = function(role, last_known_nr)
  {
    // Find the last region which was also the same role.
    var tab = [];
    var fallback_region = cp_data.get_placeholder_for_role(role || cp_data.REGION_ROLE_MAIN, last_known_nr);
    if( fallback_region )
    {
      tab = $("#tab-region-" + fallback_region.key);
    }

    // If none exists, reveal the tab for orphaned items.
    if( tab.length == 0 )
    {
      $("#cp-tabnav-orphaned").css("display", "inline");
      tab = $("#tab-orphaned");
    }

    return tab;
  }


  /**
   * Rearrange all tabs due to the newly loaded layout.
   *
   * layout = {id, key, title, regions: [{key, title}, ..]}
   */
  cp_tabs.load_layout = function(layout)
  {
    // Hide loading
    var loading_tab = $("#cp-tabnav-loading").hide();
    var tabnav  = $("#cp-tabnav");
    var tabmain = $("#cp-tabmain");

    // Deal with invalid layouts
    if( layout == null )
    {
      alert("Error: no layout information available!");
      return;
    }

    // Cache globally
    console.log("Received regions: ", layout.regions, "dom_regions=", dom_regions )
    regions = layout.regions;

    // Create the appropriate tabs for the regions.
    for( var i = 0, len = regions.length; i < len; i++ )
    {
      var region = regions[i];
      loading_tab.before( cp_tabs._create_tab_title(region) );
      tabmain.append( cp_tabs._create_tab_content(region) );
    }

    // Rebind event
    var tab_links = $("#cp-tabnav > li.cp-region > a");
    tab_links.mousedown( cp_tabs.onTabMouseDown ).click( cp_tabs.onTabClick );

    // Migrate formset items.
    // The previous old tabs can be removed afterwards.
    cp_plugins.move_items_to_placeholders();
    cp_tabs._remove_old_tabs();
    cp_tabs._ensure_active_tab(tab_links.eq(0));
    cp_tabs.show(); // Show tabbar if still hidden (at first load)
  }


  cp_tabs._create_tab_title = function(region)
  {
    // The 'cp-region' class is not part of the template, to avoid matching the actual tabs.
    var tabtitle = empty_tab_title.clone().removeAttr("id").addClass("cp-region").show();
    tabtitle.find("a").attr("href", '#tab-region-' + region.key).text(region.title);
    return tabtitle;
  }


  cp_tabs._create_tab_content = function(region)
  {
    // The 'cp-region-tab' class is not part of the template, to avoid matching the actual tabs.
    var tab = empty_tab.clone().attr("id", 'tab-region-' + region.key).addClass("cp-region-tab");
    tab.find(".cp-plugin-add-button").attr('data-region', region.key);
    return tab;
  }


  cp_tabs.show = function(slow)
  {
    if( slow )
      $("#cp-tabbar").slideDown();
    else
      $("#cp-tabbar").show();
  }


  cp_tabs.hide = function(slow)
  {
    if( slow )
      $("#cp-tabbar").slideUp();
    else
      $("#cp-tabbar").hide();
  }


  cp_tabs.hide_all_tabs = function()
  {
    // Replace tab titles with loading sign.
    // Must avoid copying the template tab too (this is another guard against it).
    $("#cp-tabnav-loading").show();
    $("#cp-tabnav-orphaned").hide();
    $("#cp-tabnav > li.cp-region:not(#cp-tabnav-template)").remove();

    // set fixed height to avoid scrollbar/footer flashing.
    var tabmain = $("#cp-tabmain");
    var height = tabmain.height();
    if( height )
    {
      tabmain.css("height", height + "px");
    }

    // Hide and mark as old.
    var all_tabs = tabmain.children(".cp-region-tab:not(#tab-template)");
    all_tabs.removeClass("cp-region-tab").addClass("cp-oldtab").removeAttr("id").hide();
  }


  cp_tabs._ensure_active_tab = function(fallback_tab_link)
  {
    // Activate the fallback item (first) if none active.
    // This needs to happen after organize, so orphans tab might be visible
    if( $("#cp-tabnav > li.active:visible").length == 0 )
      fallback_tab_link.mousedown().mouseup().click();
  }


  cp_tabs._remove_old_tabs = function()
  {
    var tabmain = $("#cp-tabmain");
    tabmain.children(".cp-oldtab").remove();

    // Remove empty/obsolete dom regions
    cp_data.cleanup_empty_placeholders();

    // After children height recalculations / wysiwyg initialisation, restore auto height.
    setTimeout( function() { tabmain.css("height", ''); }, 100 );
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


  cp_tabs.enable_tab = function(thisnav)
  {
    var nav   = $("#cp-tabnav li");
    var panes = $("#cp-tabmain .cp-tab");

    // Find new pane to activate
    var href  = thisnav.find("a").attr('href');
    var active = href.substring( href.indexOf("#") );
    var activePane = panes.filter("#" + active);

    // And switch
    panes.hide();
    activePane.show();
    nav.removeClass("active");
    thisnav.addClass("active");

    cp_tabs._focus_first_input(activePane);
  }


  cp_tabs._focus_first_input = function(root)
  {
    // Auto focus on first editor.
    // This can either be an iframe (WYSIWYG editor), or normal input field.
    var firstField = root.find(".yui-editor-editable-container:first > iframe, .form-row :input:first").eq(0);
    firstField.focus();
  }


})(window.jQuery || django.jQuery);
