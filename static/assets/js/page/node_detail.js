$(function () {

    var table = $('#node-kbuckets').DataTable({
        "dom": "t",
        // "dom": "l<'#toolbar'>frtip",
        // "order": [[2, 'desc']], //asc desc
        "order": [],   // 不设置排序
        "language": {
            // "url": "/static/data/chinese.txt"
            "emptyTable": "无K桶数据"
        },
        "serverSide": true,
        "ajax": {
            url: "/data/kbuckets",
            data: {nid: nodeid},
        },
        columns: [
            {data: "rname", "orderable": false},
            {data: "c0", "orderable": false},
            {data: "c1", "orderable": false},
            {data: "c2", "orderable": false},
            {data: "c3", "orderable": false},
            {data: "c4", "orderable": false},
            {data: "c5", "orderable": false},
            {data: "c6", "orderable": false},  // no data
            {data: "c7", "orderable": false},   //  no data
            {data: "c8", "orderable": false},
            {data: "c9", "orderable": false},
            {data: "c10", "orderable": false},
            {data: "c11", "orderable": false},
            {data: "c12", "orderable": false},
            {data: "c13", "orderable": false},
            {data: "c14", "orderable": false},
            {data: "c15", "orderable": false}

        ],
        "columnDefs": [{
            "targets": 1,
            "render": function (data, type, full, meta) {

                return render_kbuckets_cell(data)

            }
        },
        {
            "targets": 2,
            "render": function (data, type, full, meta) {
                return render_kbuckets_cell(data)
            }
        },
        {
            "targets": 3,
            "render": function (data, type, full, meta) {
                return render_kbuckets_cell(data)
            }
        },
        {
            "targets": 4,
            "render": function (data, type, full, meta) {
                return render_kbuckets_cell(data)
            }
        },
        {
            "targets": 5,
            "render": function (data, type, full, meta) {
                return render_kbuckets_cell(data)
            }
        },
        {
            "targets": 6,
            "render": function (data, type, full, meta) {
                return render_kbuckets_cell(data)
            }
        },
        {
            "targets": 7,
            "render": function (data, type, full, meta) {
                return render_kbuckets_cell(data)
            }
        },
        {
            "targets": 8,
            "render": function (data, type, full, meta) {
                return render_kbuckets_cell(data)
            }
        },
        {
            "targets": 9,
            "render": function (data, type, full, meta) {
                return render_kbuckets_cell(data)
            }
        },
        {
            "targets": 10,
            "render": function (data, type, full, meta) {
                return render_kbuckets_cell(data)
            }
        },
        {
            "targets": 11,
            "render": function (data, type, full, meta) {
                return render_kbuckets_cell(data)
            }
        },
        {
            "targets": 12,
            "render": function (data, type, full, meta) {
                return render_kbuckets_cell(data)
            }
        },
        {
            "targets": 13,
            "render": function (data, type, full, meta) {
                return render_kbuckets_cell(data)
            }
        },
        {
            "targets": 14,
            "render": function (data, type, full, meta) {
                return render_kbuckets_cell(data)
            }
        },
        {
            "targets": 15,
            "render": function (data, type, full, meta) {
                return render_kbuckets_cell(data)
            }
        },
        {
            "targets": 16,
            "render": function (data, type, full, meta) {
                return render_kbuckets_cell(data)
            }
        }],
        initComplete: function () {


        }
    });

    function render_kbuckets_cell(data) {
        if (data!='null') {
            if (data['online']=='g')
                return get_kbuckets_cell_content('yellowgreen')
            else if(data['online']=='y')
                return get_kbuckets_cell_content('yellow')
            else if (data['online']=='r')
                return get_kbuckets_cell_content('orangered')
        }else{
            return get_kbuckets_cell_content('black')
        }

    }

    function get_kbuckets_cell_content(color) {
        return '<div style="width: 35px;height:25px;background:' + color + '"></div>'
    }
});