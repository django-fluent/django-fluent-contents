(function($){
	$(window).load(function() {
		var sort_sections = $('.cp-content');
		sort_sections.sortable({
			handle: '.cp-item-drag',
			axis: 'y',
			activate: function(event, ui) {
				cp_plugins.disable_pageitem(ui.item);
			},
			deactivate: function(event, ui) {
				cp_plugins.enable_pageitem(ui.item);
			}
		});
		sort_sections.disableSelection();
	});
})(window.jQuery || django.jQuery);
