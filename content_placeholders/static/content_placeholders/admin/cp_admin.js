/**
 * Main setup for the content placeholder admin interface.
 */


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
    cp_plugins.move_items_to_placeholders();

    // Starting editor
    console.log("Initialized editor, placeholders=", cp_data.placeholders, " itemtypes=", cp_data.itemtypes);
  }


  /**
   * jQuery debug plugin.
   */
  if( !$.fn.debug )
  {
    $.fn.debug = function() { window.console && console.log( (arguments[0] || '') + this.selector, this ); return this; };
  }


})(window.jQuery || django.jQuery);
