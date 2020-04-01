const USER_STATE_VALIED = 1;
const USER_STATE_DELETED = 2; 
let select_user_id = 0;
$(document).ready(function() {
    $('.btn-edit').click(function(e){
        select_user_id = $(this).data('id');
        $('#user_phone').val($(this).data('phone'));
        $('#user_name').val($(this).data('name'));
        get_roles($(this).data('role_id'));
    })
    
    $('.btn-valied').click(function(e){
        save_user_info({'id': $(this).data('id'), 'state': USER_STATE_VALIED});
    })

    $('.btn-del').click(function(e){
        save_user_info({'id': $(this).data('id'), 'state': USER_STATE_DELETED});
    })

    $('#btn_user_save').click(function(e){
        if($('#new_pwd').val() && $('#new_pwd').val()!=$('#confirm_pwd').val()){
            alert('两次输入密码不同,请确认');
        }
        var params = {
            "id": select_user_id,
            "phone": $('#user_phone').val(),
            "name": $('#user_name').val(),
            "pwd": $('#new_pwd').val(),
            "role_id": $('#user_role').val(),
        }
        save_user_info(params);
    })

    $('#download_user_list').click(function(e){
        download_users_info();
    })
});

function get_roles(role_id){
    // 异步回调方式
    $.get("/admin/role/list", {}, function(data){
        if (typeof data === 'string') {
            data = JSON.parse(data);
        }
        if (data.code == '0000') {
            var roles = data.data;
            var item = '';
            for(var i=0; i<roles.length; i++){
                if(roles[i].role_id == role_id){
                    item += '<option value="'+ roles[i].role_id +'" selected="selected">' +roles[i].role_name +'</option>'
                }else{
                    item += '<option value="'+ roles[i].role_id +'">'+ roles[i].role_name +'</option>'
                }
            }
            $('#user_role').html(item)
        } else {
            alert(data.error);
        }
    });
}

function save_user_info(params){
    $.post("/admin/user", params, function(data){
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

function download_users_info(){
    $.get("/admin/user", {'download': true}, function(data){
        if (typeof data === 'string') {
            data = JSON.parse(data);
        }
        if (data.code == '0000') {
            
        } else {
            alert(data.error);
        }
    });
}
