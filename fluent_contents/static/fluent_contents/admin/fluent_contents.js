/**
 * Public API for django-fluent-contents
 *
 * This public API has a backwards compatibility policy.
 * The internal API does not offer these guarantees.
 */
var fluent_contents = {
    plugins: {
        /**
         * Register a function to call before initialization of all plugins scripts.
         * This handler may still register new view handlers.
         *
         * @param handler  The event handler callback/
         */
        onInitialize: function(handler) {
          cp_plugins.on_init(handler);
        },

        /**
         * Register a handler to capture events
         *
         * @param model_typename The classname of the model.
         * @param view_handler   A object with 'enable', 'disable' and optional 'initialize' function.
         */
        registerViewHandler: function(model_typename, view_handler) {
            cp_plugins.register_view_handler(model_typename, view_handler);
        }
    },


    layout: {
        /**
         * Bind an event handler before the final layout is organized.
         * The callback can return true to stop the initialisation of the plugin.
         * When the layout is blocked, call `loadLayout()` manually.
         */
        onInitialize: function(handler) {
          cp_plugins.on_init_layout(handler);
        },


        /**
         * Load the new layout for the tabs.
         * The layout structure looks like:
         *
         * var laout = {
         *   'placeholders': [
         *     {'title': "Main content", 'slot': "main", 'role': "m"},
         *     {'title': "Sidebar", 'slot': "sidebar", 'role': "s"},
         *   ]
         * };
         *
         * @param layout An object with 'placeholders' array.
         */
        load: function(layout) { cp_tabs.load_layout(layout); },


        /**
         * Hide the tabs, but don’t remove them yet. This can be used when the new layout is being fetched;
         * the old content will be hidden and is ready to move.
         */
        expire: function() { cp_tabs.expire_all_tabs(); }
    },


    tabs: {
      /**
       * Show the tabs
       *
       * @param animate  Whether to use animation, default false.
       */
      show: function(animate) { cp_tabs.show(animate); },

      /**
       * Hide the tabs.
       *
       * @param animate  Whether to use animation, default false.
       */
      hide: function(animate) { cp_tabs.hide(animate); },
    },


    widgets: {
      /**
       * Enable the WYSIWYG editor for a root.
       * @param root The inline formset item
       * @param selector Optional CSS selector for the elements.
       */
      enable_wysiwyg: function(root, selector) { cp_widgets.enable_wysiwyg(root, selector); },

      /**
       * Disable the WYSIWYG editor for a root.
       * @param root The inline formset item
       * @param selector Optional CSS selector for the elements.
       */
      disable_wysiwyg: function(root, selector) { cp_widgets.disable_wysiwyg(root, selector); },
    }
};

// Backwards compatibility:
// Renamed the onInit function because it's inconsistently abbreviated
// when taking the view handler's initialize() callback into consideration.
fluent_contents.layout.onInit = fluent_contents.layout.onInitialize;
