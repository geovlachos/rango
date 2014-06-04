$(document).ready(function() {

    $('#likes').click(function(){
        var catid;
        catid = $(this).attr("data-catid");
    
        $.get('/rango/like_category/', {category_id: catid}, function(data){
            $('#like_count').html(data);
            $('#likes').hide();
        });

    });

    $('#suggestion').keyup(function(){
        var query;
        query = $(this).val();
        $.get('/rango/suggest_category/', {suggestion: query}, function(data){
            $('#cats').html(data);
        });
    });

    $('#user_form #id_username').keyup(function(){
        var username;
        username = $(this).val();
        $.get('/rango/check_new_username/', {new_username: username}, function(data){
            $('#errorlist_username').html(data);
        });
    });
    
    $('#dialog-confirm').on('show', function(){
        var name = $(this).data('args').name;
        var ref = $(this).data('args').ref;
        removeBtn = $(this).find('#confirm-yes');

        removeBtn.attr('href', removeBtn.attr('href').replace(/.*/, ref));
    
        $('#url-name').html('<strong>' + name + '</strong>');
    });

    $('.delete-item').on('click', function(e) {
        e.preventDefault();

        var name = $(this).data('name');
        var ref = $(this).attr('href');
        $('#dialog-confirm').data('args', {'name': name, 'ref': ref}).modal('show');
    });
});
