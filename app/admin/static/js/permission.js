let select_permission_id = 0;
$(document).ready(function() {
    $('.btn-edit').click(function(e){
        select_permission_id = $(this).data('id');
        $('#pname').val($(this).data('name'));
        $('#pmethod').val($(this).data('method'));
        $('#puri').val($(this).data('uri'));
    })  

    $('.btn-del').click(function(e){
        save_permission({'id': $(this).data('id'), '_method': "delete"});
    })  

    $('#btn_save').click(function(e){
        var params = { 
            "id": select_permission_id,
            "name": $('#pname').val(),
            "method": $('#pmethod').val(),
            "uri": $('#puri').val(),
        }   
        save_permission(params);
    })  

    $('#btn_create').click(function(e){
        select_permission_id = 0;
        $('#pname').val('');
        $('#pmethod').val('');
        $('#puri').val('');
    })
});

function save_permission(params){
    $.post("/admin/permission", params, function(data){
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
