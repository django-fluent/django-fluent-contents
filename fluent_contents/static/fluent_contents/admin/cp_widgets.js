/**
 * Code to initialize custom widgets.
 */

var cp_widgets = {};

(function($){

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
