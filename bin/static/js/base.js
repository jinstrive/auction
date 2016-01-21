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