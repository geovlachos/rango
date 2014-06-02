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

});
