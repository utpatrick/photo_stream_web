$(function() {
        $("#search_str").autocomplete({
            source: stream_names,
            var stream_names = {{stream_names | safe}};
            select: function(event,ui) {
                $('#search_str').val($("autocomplete").val());
                }
            });
        });