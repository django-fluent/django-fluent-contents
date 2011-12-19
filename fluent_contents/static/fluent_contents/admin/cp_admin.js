/**
 * Main setup for the content placeholder admin interface.
 */

var cp_admin = {};

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


})(window.jQuery || django.jQuery);
