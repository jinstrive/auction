var utils = {
    tips: function (msg, delay) {
        var html = '<div class="alert alert-danger alert-dismissable">'
            + '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>'
            + '<strong>' + msg + '</strong>'
            + '</div>';
        $("#tips").html(html);
        $("#tips").css('display', 'block');

        //重新设置关闭按钮的事件
        $("#tips").find(".close").click(function () {
            $("#tips").hide("slow").empty();
        });

        var timeout = 3000;
        if (typeof(delay) == 'undefined') {
            setTimeout(function () {
                $("#tips").hide("slow").empty();
            }, timeout);
            return;
        }
        if (delay > 0) {
            setTimeout(function () {
                $("#tips").hide("slow").empty();
            }, delay);
        }
    }
}

function goBack() {
    window.history.back();
}

function go_iwant() {
	window.location.href="/auction/iwant";
}

function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + "; " + expires + "; path=/;";
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1);
        if (c.indexOf(name) == 0) return c.substring(name.length,c.length);
    }
    return "";
}

function statistics(pname) {
    var post_data = {"pname": pname}
    $.ajax({ 
        type: 'POST',
        url: "/auction/statistics",
        data: post_data,
        success: function(ret){
            console.log(ret);
        }
    });
}