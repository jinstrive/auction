function auction(add_price) {
    item_id = $("#item-id").value;
    $.ajax({ 
        type: 'POST',
        url: "/auction",
        data: {'item_id': item_id, 'add_price': add_price},
        success: function(ret){
            console.log(ret);
            if (ret.respcd == '0000') {
            	$("#now_price").text(ret.data.price);
            } else {
            	if (ret.respcd == '2002') {
            		window.location.href="/login";
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