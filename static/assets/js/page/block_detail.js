$(document).ready(function () {


    var table = $('#trans-in-block1').DataTable({
        "dom": "<'#toolbar1'<l><f>>rtip",
        // "dom": "l<'#toolbar'>frtip",
        // "order": [[2, 'desc']], //asc desc
        "order":[],   // 不设置排序
        "language":{
            "url":"/static/data/chinese.txt"
        },
        "serverSide": true,
        "ajax": {
            url: "/data/translist",
            data: {bnum: bid},
        },
        columns: [
            {data: "hash", "orderable": false},
            {data: "blockNumber", "orderable": false},
            {data: "time","orderable": false},
            {data: "from", "orderable": false,},
            {data: "to", "orderable": false,},
            {data: "trans_type", "orderable": false,},  // no data
            {data: "trans_fee", "orderable": false,},   //  no data
            {data: "value", "orderable": false,}

        ],
        "columnDefs": [{
            "targets": 0,
            "render": function (data, type, full, meta) {
                // return type === 'display' && data.length > 23 ?
                //     '<a href="#">' + data.substr(0, 20) + '...</a>' :
                //     data;
                var tdv = cutstr(data, 18)
                return '<a href="/eth/tsc_detail?hash=' + data + '">' + tdv + '</a>'

            }
        }, {
            "targets": 1,
            "render": function (data, type, full, meta) {
                // return type === 'display' && data.length > 23 ?
                //     '<a href="#">' + data.substr(0, 20) + '...</a>' :
                //     data;
                return '<a href="/eth/block_detail/' + data + '">' + data + '</a>'

            }
        },
            {
                "targets": 2,
                "render": function (data, type, full, meta) {
                    // return crtTimeFtt(data);
                    return data;
                }
            },
            {
                "targets": 3,
                "render": function (data, type, full, meta) {
                    var tdv = cutstr(data, 18)
                    return '<a href="/eth/address/detail/' + data + '">' + tdv + '</a>'

                }
            },
            {
                "targets": 4,
                "render": function (data, type, full, meta) {
                    if (data) {
                        var tdv = cutstr(data, 18)  // 注意data为空的情况
                        return '<a href="/eth/address/detail/' + data + '">' + tdv + '</a>'
                    }else{
                        return ''
                    }


                }
            }
        ],
        initComplete: function () {
            var tb = $("#toolbar1");
            tb.addClass('bee-row');
            tb.find('label').css({"margin-bottom": 0});
            // $("#toolbar").css("width", "100px").css("display", "inline").css("margin-left", "10px");
            tb.append("<div><a  " +
                "class='btn btn-primary btn-sm' type='button' aria-haspopup=\"true\" aria-expanded=\"false\" id='hs-fields' data-toggle='dropdown'>选择字段</a><div>");

            // $("#toolbar1").children().css({'display': 'inline-block'});

            // 选择字段
            $('#hs-fields').after('<div class="dropdown-menu" aria-labelledby="hs-fields">');  // hide or show
            for (var i = 0; i < col_names.length; i++) {

                $('#hs-fields').next().append('<a class="dropdown-item" data-stopPropagation="true"><i class="fa fa-square-o fa-fw"></i> ' + col_names[i] + '</a>');
            }

            $('#hs-fields').next().children('.dropdown-item').on('click', function (e) {
                var column = table.column($(this).index());
                column.visible(!column.visible());
                if ($(this).hasClass('item-checked')) {
                    $(this).removeClass('item-checked');
                    $(this).find('i').removeClass('fa-check-square-o');
                    $(this).find('i').addClass('fa-square-o');
                } else {
                    $(this).addClass('item-checked');
                    $(this).find('i').removeClass('fa-square-o');
                    $(this).find('i').addClass('fa-check-square-o');
                }
                e.stopPropagation();
            });


        }
    });


    function gather_rargs() { // 统计请求参数

    }


});
