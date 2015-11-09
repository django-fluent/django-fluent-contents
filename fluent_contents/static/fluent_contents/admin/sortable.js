(function($){
	$(window).load(function() {
		var sort_sections = $('.cp-content');
		sort_sections.sortable({
			handle: '.cp-item-drag',
			axis: 'y'
		});
		sort_sections.disableSelection();
	});
})(window.jQuery || django.jQuery);
