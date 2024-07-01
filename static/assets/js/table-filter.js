$(function () {
    var cur = "今天";   // 全局，日期过滤开关
    var pdo = "今天";  // 前一个日期过滤选项
    var cur_page;
    var optionlist = ['今天', '本周', '本月', '今年', '全部']
    var ENTER_KEY = 13;
    var update_pages = block_pages;  // 总页数

    var $tf = $('#tf-button');  // tf：table filter
    // var cur = "all"; // table-filter.js内定义
    // var optionlist = ['all', '今天', '本周', '本月', '今年']

    // pagination function
    $('.M-box4').pagination({  // 总页数改变后， at  147
        pageCount: block_pages,
        // jump: true, // 有bug
        callback: function (api) {
            var data = {
                page: api.getCurrent(),
                name: 'mss',
                say: 'oh'
            };
            //  可在此处发送ajax请求
            // api.setPageCount(10); // 生效，但有bug
            $('.bee-pagination .jump-ipt').val(api.getCurrent())
            update_bt();
        }
    }, function (api) {
        // api.setPageCount(update_pages); // test
    });

    // 日期筛选，需处理两个点击事件
    $tf.next().children('.dropdown-item').on('click', function () {
        update_dropmenu($(this));
        update_bt();
        // console.log(api.getPageCount());
        pdo = cur;
    });

    $tf.next().on('click', '.dropdown-item', function () {
        update_dropmenu($(this));
        // 参数 $(this).text()
        update_bt();
        pdo = cur; // 解决 周->天 bug
    });


    function update_dropmenu(e) {
        var cid = optionlist.indexOf(cur);
        var item = '<a class="dropdown-item">' + cur + '</a>';
        if (cid === 0) {
            $tf.next().children(':first').before(item);
        } else {
            cid = cid - 1;
            $tf.next().children('.dropdown-item:eq(' + cid + ') ').after(item);
        }

        $tf.html("按" + e.text() + "筛选 <span class='oi oi-elevator'></span>");
        cur = e.text();
        e.remove();
    }

    function update_block_table(json_data) {
        var blocks = json_data.blocks;
        // var columns = ['height', 'hash', 'miner', 'time', 'trans_num', 'size', 'uncles', ['cost','block_reward'], ['cost','total_value']]
        var columns = json_data.key_list;
        $("#block_table tbody tr").remove();
        for (var i = 0; i < blocks.length; i++) {
            var row = "<tr>";
            for (var j = 0; j < columns.length; j++) {

                // var tdv = blocks[i][columns[j]].length>23?blocks[i][columns[j]].substr(0,20)+'...':blocks[i][columns[j]];
                // var tdv = cutstr(blocks[i][columns[j]], 23);
                var tdv = truncate_str(get_dict_key_value(blocks[i],columns[j]), 23);

                row += "<td>" + tdv + "</td>";
            }
            row += "</tr>"

            $("#block_table tbody:last").append(row);
        }


        // 隐藏行字段
        // var $table = $('#block_table')
        var $table = $("#block_table")
        var tharr = $table.find('th');
        for (var i=0;i<tharr.length;i++){
            if (tharr[i].hasAttribute('hidden')){
                $table.find('tr').find('td:eq(' + i + ')').attr({"hidden":"hidden"});
            }
        }

        // 处理第0列，添加超链接
        for (var i = 0; i < blocks.length; i++) {
            var tdv = cutstr(blocks[i][columns[0]], 18);
            var td = "<a href='/eth/block_detail/" + blocks[i][columns[0]] + "'>" + tdv + "</a>"
            // console.log($('#block_table tr:eq(i)').children('td').eq(0).val()) ;
            // $('#block_table').find('tr').eq(i).find('td').eq(0).html(td)  // 有问题
            $('#block_table tbody tr:eq(' + i + ') td:eq(0)').html(td)
        }

        // 处理第1列，添加超链接
        for (var i = 0; i < blocks.length; i++) {
            var tdv = cutstr(blocks[i][columns[1]], 18);
            var td = "<a href='/eth/block_detail/" + blocks[i][columns[0]] + "'>" + tdv + "</a>"
            $('#block_table tbody tr:eq(' + i + ') td:eq(1)').html(td)
        }

        // 处理第2列，添加超链接
        for (var i = 0; i < blocks.length; i++) {
            var tdv = cutstr(blocks[i][columns[2]], 18);
            var td = "<a href='/eth/address/detail/" + blocks[i][columns[2]] + "'>" + tdv + "</a>"
            // console.log($('#block_table tr:eq(i)').children('td').eq(0).val()) ;
            // $('#block_table').find('tr').eq(i).find('td').eq(0).html(td)  // 有问题
            // if transes[i][columns[4]]!=None
            $('#block_table tbody tr:eq(' + i + ') td:eq(2)').html(td)
        }
    }


    function renderColumn(col, href) { // 备用

    }


    function get_filter_args() {
        // order
        var order = '';
        if ($("#switch").hasClass("switched")) {
            order = 'asc';
        } else {
            order = 'desc';
        }
        var page;
        if (optionlist.indexOf(cur) < optionlist.indexOf(pdo)) {
            page = 1
            $('.bee-pagination .jump-ipt').val(1);
        } else {
            // page = $('.M-box4 .active').text();  // 废弃
            page = $('.bee-pagination .jump-ipt').val();

        }

        // if (page>update_pages) page = update_pages;  // 没能解决问题

        var $input = $('#block-search');
        // var value = $input.val().trim();
        // 需处理搜索字段为空(非)，但是过滤由其他条件触发的情况

        return {"order": order, "page": page, "time": optionlist.indexOf(cur), "search_text": ''}; // $input.val().trim()

    }


// update block table
    function update_bt() {
        filter_args = get_filter_args();
        // $.ajax({    // 废弃
        //     type: 'POST',
        //     // url: '/ajax/block/order',
        //     url: '/ajax/block/filter',
        //     data: filter_args,
        //     success: function (data) {
        //         update_block_table(data);
        //     }
        // });

        if (filter_args != null) {
            $.ajax({
                type: 'POST',
                url: '/ajax/block/filter',
                data: JSON.stringify(filter_args),
                contentType: 'application/json;charset=UTF-8',
                success: function (data) {
                    json_data = jQuery.parseJSON(data);
                    $('#block_pages').text(json_data.pages);
                    $('#block_total').text(json_data.total);
                    update_block_table(json_data);
                    // if (json_data.pages != update_pages) {
                    update_pages = json_data.pages;
                    cur_page = json_data.page;
                    // if (cur_page > update_pages) {  // 废弃，不合理，可能发送了一个错误值
                    //     cur_page = update_pages;
                    //     $('.bee-pagination .jump-ipt').val(cur_page);
                    // }
                    // console.log(cur_page)
                    // 需要设置pagination的cur_page

                    $('.M-box4').empty();
                    $('.M-box4').pagination({ // 曲线救国，待优化
                        pageCount: update_pages,
                        current: cur_page,
                        // jump: true,
                        callback: function (api) {
                            var data = {
                                page: api.getCurrent(),
                                name: 'mss',
                                say: 'oh'
                            };
                            //  可在此处发送ajax请求
                            // api.setPageCount(update_pages);
                            // console.log('d')
                            $('.bee-pagination .jump-ipt').val(api.getCurrent);

                            update_bt();
                            // console.log('e')
                        }
                    }, function (api) {
                        // api.setPageCount(update_pages); // test
                    });


                    // }
                    if (json_data.message !== '')
                        alert(json_data.message);
                    // alert(jQuery.parseJSON(data).message);
                }
            });
        }
    }


    $("#block-order-switch").on('click', function () {  // 废弃
        if ($("#block-order-switch").is(':checked')) {
            console.log("c")
        } else {
            console.log("un")
        }

    });

    function search_block(e) {   // 过滤条件冲突，需单独处理
        var $input = $('#block-search');
        var value = $input.val().trim();
        if (e.which !== ENTER_KEY || !value) {
            return;
        }

        filter_args = get_filter_args();
        update_bt();
        // $input.focus().val('');

    }


    $(document).on('keyup', '#block-search', search_block.bind(this));


    $('#choose-field').next().children('.dropdown-item').on('click', function (e) {
        // console.log($(this).index());
        if ($(this).hasClass('item-checked')) {
            $(this).removeClass('item-checked');
            $(this).find('i').removeClass('fa-check-square-o');
            $(this).find('i').addClass('fa-square-o');

            $('#block_table tr').find('td:eq(' + $(this).index() + ')').removeAttr("hidden");
            $('#block_table tr').find('th:eq(' + $(this).index() + ')').removeAttr("hidden");

            // $('#block_table tr').find('td:eq(' + $(this).index() + ')').show();
            // $('#block_table tr').find('th:eq(' + $(this).index() + ')').show();
        } else {
            $(this).addClass('item-checked');
            $(this).find('i').removeClass('fa-square-o');
            $(this).find('i').addClass('fa-check-square-o');
            $('#block_table tr').find('td:eq(' + $(this).index() + ')').attr({"hidden":"hidden"});
            $('#block_table tr').find('th:eq(' + $(this).index() + ')').attr({"hidden":"hidden"});

            // $('#block_table tr').find('td:eq(' + $(this).index() + ')').hide();
            // $('#block_table tr').find('th:eq(' + $(this).index() + ')').hide();
        }
        e.stopPropagation();


        // $(this).index()
        // var column = $('#block_table').column();
        // column.visible(!column.visible());
    });

    //  bee-pagination
    $('.bee-pagination .prev').on('click', function () {
        $('.M-box4 .prev').click();
        update_bt;
        //$('.bee-pagination .jump-ipt').val($('.M-box4').find('span').text())
    });

    $('.bee-pagination .next').on('click', function () {
        $('.M-box4 .next').click();
        //$('.bee-pagination .jump-ipt').val($('.M-box4').find('span').text())
        update_bt();
    });


    $('.bee-pagination .jump-ipt').keypress(function (e) { // 跳转

        // alert($(this).val());
        if (e.which == 13) {

            update_bt();
        }

    });

    // order checkbox//排序
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

