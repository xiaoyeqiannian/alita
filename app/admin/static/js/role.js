let select_role_id = 0;
$(document).ready(function() {
   
    //$.fn.modal.Constructor.prototype.enforceFocus = function() {}; 
    $('#permission').select2({dropdownParent: $('#role_info')});
    init_permission_option();

    $('.btn-edit').click(function(e){
        select_role_id = $(this).data('id');
        parse_permission_info(
            $(this).data('en_name'),
            $(this).data('name'),
            $(this).data('description'),
            $(this).data('routes'),
        );
    })
    
    $('.btn-del').click(function(e){
        save_role({'id': $(this).data('id'), '_method': "delete"});
    })

    $('#btn_save').click(function(e){
        var params = {
            "id": select_role_id,
            "en_name": $('#enname').val(),
            "name": $('#name').val(),
            "description": $('#description').val(),
            "routes": $('#routes').val(),
            "permissions": $('#permission').val(),
        }
        save_role(params);
    })

    $('#btn_create').click(function(e){
        select_role_id = 0;
        parse_permission_info('', '', '', '')
    })
});


function save_role(params){
    $.post("/admin/role", params, function(data){
        if (typeof data === 'string') {
            data = JSON.parse(data);
        }
        if (data.code == '0000') {
            alert("操作成功");
            window.location.reload();
        } else {
            alert(data.error);
        }
    });
}
 
async function init_permission_option() {
    try {
        var data = await GET({
                        url: '/admin/permission/list',
                        type: 'get',
                        data: {},
                        })
        $('#permission').select2({
                        data: data,
                        placeholder:'请选择',
                        allowClear:true});
        $('.select2-container').css("width", "100%")
    } catch (e) {
        console.error(e)
    }
}


async function parse_permission_info(enname, name, description, routes) {
    $('#enname').val(enname);
    $('#name').val(name);
    $('#description').val(description);
    $('#routes').val(routes);
    $('#permission').val(null).trigger("change")
    try {
        var data = await GET({
                        url: '/admin/permission/selected',
                        type: 'get',
                        data: {'role_id': select_role_id},
                        })
        $('#permission').val(data).trigger('change');
        $('.select2-container').css("width", "100%");
    } catch (e) {
        console.error(e)
    }
}
