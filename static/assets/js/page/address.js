$(function () {

     // pagination.js  翻页
    $('.pagination').pagination({  // 总页数改变后， at  147
        pageCount: pages,
        callback: function (api) {
            var data = {
                page: api.getCurrent()
            };
            //  可在此处发送ajax请求
            $('.bee-pagination .jump-ipt').val(api.getCurrent())
            ru_table();
        }
    }, function (api) {
        // api.setPageCount(update_pages); // test
    });


    function ru_table() {

    }

});