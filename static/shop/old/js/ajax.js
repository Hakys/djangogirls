$(document).ready(function(){ 
    $("#txtSearch").autocomplete({
        source: "search",
        minLength: 2,
        open: function(){
            setTimeout(function () {
                $('.ui-autocomplete').css('z-index', 99);
            }, 0);
        }
    });
});
