$(document).ready(function(){
    $('#search_str').autocomplete({
        source: function(request, response){
            var search_str = request.term;

            $.ajax({
                type: 'POST',
                url: '/search_suggestions',
                data: {
                    search_str: search_str
                },
                dataType: 'json',
                success: function (data) {
                    response(data.streams);
                }
            });
        },
        minLength: 1
    });
});