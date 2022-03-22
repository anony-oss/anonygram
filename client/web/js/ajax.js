url = 'http://localhost:5000';

/* register */
function register(){
    if($('#password2_1').val() == $('#password2_2').val()){
        if($('#password2_1').val() !== '' && $('#password2_2').val() !== ''){
            $.post(
                url + '/api/register/',
                {username: $('#nickname').val(), email: $('#email2').val(), password: $('#password2_1').val()},
                function(data){
                    console.log(data);
                    switch(data.status){
                        case 'OK':
                            $('#message-popup2').slideDown();
                            $('#message-popup2 .message-popup2-content').css('background-color', '#EF201C');
                            $('#message-popup2 .message-popup2-content h4').text('Успешная регистрация!');
                            $('#message-popup2 .message-popup2-content p').text('Войдите в учётную запись для продолжения');
                            break;
                        case 'NOTOK':
                            $('#message-popup2').slideDown();
                            $('#message-popup2 .message-popup2-content').css('background-color', '#EF201C');
                            $('#message-popup2 .message-popup2-content h4').text('Упс...');
                            $('#message-popup2 .message-popup2-content p').text(data.message);
                            break;
                    }
                }
            ); 
        }else{
            $('#message-popup2').slideDown();
            $('#message-popup2 .message-popup2-content').css('background-color', '#EF201C');
            $('#message-popup2 .message-popup2-content h4').text('Упс...');
            $('#message-popup2 .message-popup2-content p').text('Введите пароль!');            
        }
    }else{
        $('#message-popup2').slideDown();
        $('#message-popup2 .message-popup2-content').css('background-color', '#EF201C');
        $('#message-popup2 .message-popup2-content h4').text('Упс...');
        $('#message-popup2 .message-popup2-content p').text('Пароли не совпадают!');
    }
}
/* login */
function login(){
        $.post(
            url + '/api/login/',
            {email: $('#email').val(), password: $('#password').val()},
            function(data2){
                console.log(data2);
                    switch(data2.status){
                        case 'OK':
                            localStorage.setItem('user_id', data2.data.id);
                            localStorage.setItem('email', data2.data.email);
                            localStorage.setItem('password_hash', data2.data.password_hash);
                            window.location.href='index.html';
                            break;
                        case 'NOTOK':
                            $('#message-popup1').slideDown();
                            $('#message-popup1 .message-popup1-content').css('background-color', '#EF201C');
                            $('#message-popup1 .message-popup1-content h4').text('Упс...');
                            $('#message-popup1 .message-popup1-content p').text(data2.message);
                            break;
                    }
                }
        );
}
/* chats list */
async function chat_info(id){
    let php_data;
    $.ajax({
      method: 'POST',
      url: url + '/api/chat_info/',
      async: false, 
      dataType: 'json',
      data: {email: localStorage.getItem('email'), password: localStorage.getItem('password_hash'), chat_id: id, hash: true},
      success: function (json) {
        js_data = json.data;
      }
    });
    return Promise.resolve(js_data);
}
async function add_chats(chat = []){
    for(item of chat){
        let info = await chat_info(item);
        let message = await message_list(item);
        console.log(message);
        let message_length = message.length - 1;
        console.log(info)
        $('.home .content').append("<a href='?chat=" + chat + "'>" + "<li>\
            <img src='img/standart-avatar.jpg' alt=''>\
            <div style='display: flex; flex-direction: column; margin-left: 1em; padding: 0;'>\
                <p id='chat-name'>" + info.name + "</p>\
                <p id='chat-last_message'>" + message[message_length][0] + "</p>\
            </div>\
        </li></a>");
    }
}
function chats_list(){
    $.ajax({
        method: 'POST',
        url: url + '/api/chat_list/',
        async: false, 
        dataType: 'json',
        data: {email: localStorage.getItem('email'), password: localStorage.getItem('password_hash'), hash: true},
        success: function (data2) {
            switch(data2.status){
                case 'OK':
                    add_chats(data2.data);
                    //console.log(data2);
                    break;
                case 'NOTOK':
                    console.log(data2.message);
                    break;
            }
        }
      });
}
/* Show messages */
async function message_list(chat){
    $.ajax({
        method: 'POST',
        url: url + '/api/chat_messages/',
        async: false, 
        dataType: 'json',
        data: {email: localStorage.getItem('email'), password: localStorage.getItem('password_hash'), hash: true, chat_id: chat},
        success: function (data2) {
            switch(data2.status){
                case 'OK':
                    js_data = data2.data.messages
                    break;
                case 'NOTOK':
                    console.log(data2.message);
                    break;
            }
        }
    });
    return Promise.resolve(js_data)
}
async function message_show(chat){
    $('.chat ul').empty();
    let messages = await message_list(chat);
    for(item of messages){
        if(item[2] == localStorage.getItem('user_id')){
            $('.chat ul').append("\
                <li class='my-message'>\
                    <div class='col-12 col-sm-5 col-md-5 col-xl-5 message'>\
                        <div style='display: flex; flex-direction: column;'>\
                            <p id='chat-message_author'>Вы</p>\
                            <p id='chat-message'>" + item[0] + "</p>\
                        </div>\
                    </div>\
                </li>\
            ");
        }else{
            $('.chat ul').append("\
            <li class='people-message'>\
                <div class='col-12 col-sm-5 col-md-5 col-xl-5 message'>\
                    <img src='img/standart-avatar.jpg' alt=''>\
                    <div style='display: flex; flex-direction: column;'>\
                        <p id='chat-message_author'>Никнейм</p>\
                        <p id='chat-message'>" + item[0] + "</p>\
                    </div>\
                </div>\
            </li>\
        ");
    }
        }
        console.log(item[0])
    console.log(messages);
}
/* Send message */
function send_message(chat){
    $.ajax({
        method: 'POST',
        url: url + '/api/send_message/',
        async: false, 
        dataType: 'json',
        data: {email: localStorage.getItem('email'), password: localStorage.getItem('password_hash'), hash: true, chat_id: chat, message: $('#message-input').val()},
        success: function (data2) {
            switch(data2.status){
                case 'OK':
                    console.log(data2.data);
                    $('.chat ul').append("\
                        <li class='my-message'>\
                            <div class='col-12 col-sm-5 col-md-5 col-xl-5 message'>\
                                <div style='display: flex; flex-direction: column;'>\
                                    <p id='chat-message_author'>Вы</p>\
                                    <p id='chat-message'>" + $('#message-input').val() + "</p>\
                                </div>\
                            </div>\
                        </li>\
                    ");
                    break;
                case 'NOTOK':
                    console.log(data2.message);
                    break;
            }
        }
    });
}
/* timer (interval) chat */
async function timer_chat(chat){
    let old_message = await message_list(chat);
    let check_messages = setInterval(() => timer_func(), 10000);
    async function timer_func(){
    let messages = await message_list(chat);
    if(messages !== old_message){
            old_message = await message_list(chat);
            message_show(chat);
        }
        if(!chat_id.includes('?chat')){
            clearTimeout(check_messages);
        }
    }
}