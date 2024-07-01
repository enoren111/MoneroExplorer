$(function () {
    $("#switch").on('click', function () {
        if ($("#switch").hasClass("switched")) {
            $("#switch").removeClass("switched");
            // console.log("adds")
            //
            update_bt();

        }
        else {
            $("#switch").addClass("switched");
            // console.log("adda")
            //  升序
            update_bt();
        }
    });
    



});





