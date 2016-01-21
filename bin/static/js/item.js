function auction(add_price) {
    var item_id = $("#item-id").val();
    var post_data = {
    	'item_id': item_id,
    	'add_price': add_price,
    }
    console.log(post_data);
    $.ajax({ 
        type: 'POST',
        url: "/auction/auction",
        data: post_data,
        success: function(ret){
            console.log(ret);
            if (ret.respcd == '0000') {
            	$("#now_price").text(ret.data.price);
            } else {
            	if (ret.respcd == '2002') {
            		setCookie("current_page", window.location.href, 10);
            		window.location.href="/auction/login";
            	};
                utils.tips(ret.respmsg);
            }
        }
    });
}

$(function(){
    $("#add10").click(function(e) {
    	e.preventDefault();
    	auction(10);
    });
    $("#add100").click(function(e) {
    	e.preventDefault();
    	auction(100);
    });
});