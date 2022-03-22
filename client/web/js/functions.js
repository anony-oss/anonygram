function account_exit(){
    localStorage.removeItem('email');
    localStorage.removeItem('password');
    window.location.href='auth.html';
}
function check_auth(){
    if(localStorage.getItem('email') == '' || localStorage.getItem('password_hash') == '' || localStorage.getItem('email') == undefined || localStorage.getItem('password_hash') == undefined){
        window.location.href='auth.html';
    }
}