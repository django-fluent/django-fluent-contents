/**
 * This file deals with the high level layout switching / fetching layout info.
 * When a new layout is fetched, it is passed to the cp_tabs to rebuild the tabs.
 */
var simplecms_layouts = {};

(function($)
{
  var ajax_root = location.href.substring(0, location.href.indexOf('/simplecms/page/') + 16);
  var initial_template_name = null;


  /**
   * Initialize this component,
   * bind events and select the first option if there is only one.
   */
  simplecms_layouts.init = function(real_initial_template_name)
  {
    var layout_selector = $("#id_template_name");
    simplecms_layouts._select_single_option( layout_selector );
    layout_selector.change( simplecms_layouts.onLayoutChange );

    // Firefox will restore form values at refresh.
    // Know what the real initial value was.
    initial_template_name = real_initial_template_name
  }


  simplecms_layouts.fetch_layout_on_refresh = function()
  {
    var layout_selector = $("#id_template_name");

    // Place items in tabs
    var selected_template_name = layout_selector.val() || 0;
    if( selected_template_name != initial_template_name )
    {
      // At Firefox refresh, the form field value was restored,
      // Update the DOM content by fetching the data.
      cp_tabs.hide();
      layout_selector.change();

      console.log("<select> box updated on load, fetching new layout; old=", initial_template_name, "new=", selected_template_name);
      return true;
    }

    return false;
  }


  /**
   * If a selectbox has only one choice, enable it.
   */
  simplecms_layouts._select_single_option = function(selectbox)
  {
    var options = selectbox[0].options;
    if( ( options.length == 1 )
     || ( options.length == 2 && options[0].value == "" ) )
    {
      selectbox.val( options[ options.length - 1 ].value );
    }
  }


  /**
   * The layout has changed.
   */
  simplecms_layouts.onLayoutChange = function(event)
  {
    var template_name = this.value;
    if( ! template_name )
    {
      cp_tabs.hide(true);
      return;
    }

    // Disable content
    cp_tabs.expire_all_tabs();

    if( event.originalEvent )
    {
      // Real change event, no manual invocation made above
      cp_tabs.show(true);
    }

    simplecms_layouts.fetch_layout(template_name);
  }


  simplecms_layouts.fetch_layout = function(template_name)
  {
    // Get layout info.
    $.ajax({
      url: ajax_root + "get_layout/?name=" + encodeURIComponent(template_name),
      success: function(layout, textStatus, xhr)
      {
        // Ask to update the tabs!
        cp_tabs.load_layout(layout);
      },
      dataType: 'json',
      error: function(xhr, textStatus, ex)
      {
        alert("Internal CMS error: failed to fetch layout data!");    // can't yet rely on $.ajaxError
      }
    })
  }

})(window.jQuery || django.jQuery);
