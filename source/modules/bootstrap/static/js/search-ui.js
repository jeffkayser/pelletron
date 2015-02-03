function update_search_ui(results) {
    if(search_view == null) {
        search_view = $('.searchbox-container');
    }
    if(search_view.data('bs.popover') === undefined) {
        search_view.popover({placement: 'bottom', html: true, trigger: 'focus', title: 'Search results', container: 'body'});
    }
    if(results == null) {
        search_view.popover('destroy');
    } else if(Object.keys(results).length == 0) {
        search_view.data('bs.popover').options.content = '<div class="search-results label label-danger">Nothing found</div>';
        search_view.popover('show');
    } else {
        var result_html = '<div class="search-results"><ul>';
        $.each(results, function(url, title) {
            result_html += '<li><a href="' + url + '">' + title + '</a></li>';
        });
        result_html += '</ul></div>';
        search_view.data('bs.popover').options.content = result_html;
        search_view.popover('show');
    }
}
