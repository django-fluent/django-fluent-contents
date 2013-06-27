/**
 * Main setup for the content placeholder admin interface.
 */

var cp_admin = {};
var cp_widgets = {};

(function($){

  // Mark the document as JavaScript enabled.
  $(document.documentElement).addClass("cp-jsenabled");

  // Speed up IE 6, fix background image flickering
  try { document.execCommand("BackgroundImageCache", false, true); }
  catch(exception) {}

  // Register main event
  $(document).ready( onReady );


  /**
   * Main init code
   */
  function onReady()
  {
    // Init all parts. Ordering shouldn't matter that much.
    cp_data.init();
    if( window.cp_tabs ) cp_tabs.init();
    cp_plugins.init();
    cp_plugins.post_init();
    cp_widgets.init();
  }


  /**
   * jQuery debug plugin.
   */
  if( !$.fn.debug )
  {
    $.fn.debug = function() { window.console && console.log( (arguments[0] || '') + this.selector, this ); return this; };
  }


  /**
   * jQuery outerHTML plugin
   * Very simple, and incomplete - but sufficient for here.
   */
  $.fn.get_outerHtml = function( html )
  {
    if( this.length )
    {
      if( this[0].outerHTML )
        return this[0].outerHTML;
      else
        return $("<div>").append( this.clone() ).html();
    }
  }


  // Based on django/contrib/admin/media/js/inlines.js
  cp_admin.renumber_formset_item = function(fs_item, prefix, new_index)
  {
    var id_regex = new RegExp("(" + prefix + "-(\\d+|__prefix__))");
    var replacement = prefix + "-" + new_index;

    // Loop through the nodes.
    // Getting them all at once turns out to be more efficient, then looping per level.
    var nodes = fs_item.add( fs_item.find("*") );
    for( var i = 0; i < nodes.length; i++ )
    {
      var node = nodes[i];
      var $node = $(node);

      var for_attr = $node.attr('for');
      if( for_attr && for_attr.match(id_regex) )
        $node.attr("for", for_attr.replace(id_regex, replacement));

      if( node.id && node.id.match(id_regex) )
        node.id = node.id.replace(id_regex, replacement);

      if( node.name && node.name.match(id_regex) )
        node.name = node.name.replace(id_regex, replacement);
    }
  }


  var has_load_error = false;

  cp_widgets.init = function()
  {
    // Extra customizations for the YUI editor
    if( window.django_wysiwyg_editor_config && window.YAHOO )
    {
      window.django_wysiwyg_editor_config.height = "150px";
      window.django_wysiwyg_editor_config.autoHeight = true;
    }
  };


  cp_widgets.disable_wysiwyg = function(root, selector)
  {
    selector = selector || 'textarea.cp-wysiwyg-widget';
    var textareas = root.find(selector + ":not([id~=__prefix__])").toArray();
    for(var i = 0; i < textareas.length; i++)
    {
      var textarea = textareas[i];
      django_wysiwyg.disable("e:" + textarea.name);
    }
  }


  cp_widgets.enable_wysiwyg = function(root, selector)
  {
    selector = selector || 'textarea.cp-wysiwyg-widget';
    var textareas = root.find(selector + ":not([id~=__prefix__])");

    if( ! django_wysiwyg.is_loaded() )
    {
      textareas.show();

      // Show an error message, but just once.
      if( ! has_load_error )
      {
        textareas.before("<p><em style='color:#cc3333'>Unable to load the WYSIWYG editor, is the system connected to the Internet?</em></p>");
        has_load_error = true;
      }

      return;
    }

    textareas = textareas.toArray();
    for(var i = 0; i < textareas.length; i++)
    {
      var textarea = textareas[i];
      django_wysiwyg.enable("e:" + textarea.name, textarea.id);
    }
  };


})(window.jQuery || django.jQuery);
