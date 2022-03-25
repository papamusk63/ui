function setCookie() {
    // get the checkbox value
    var checked = 0;
    if (document.myform2.sub.checked) {
        var checked = 1;
    }
    var cookieValue = checked;
    // set the cookie
    createCookie('SrGuiSubTest',cookieValue,0);
    // reload the page with the new settings
    javascript:location.reload(true);
}
function createCookie(name,value,days) {
    if (days) {
        var date = new Date();
        date.setTime(date.getTime()+(days*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
    }
        else var expires = "";
    document.cookie = name+"="+value+expires+"; path=/";
}
function check_args(form) {
    if (form.arguments.value == "") {
        alert("You must enter arguments!");
        form.arguments.focus();
        return false;
    }
    return true;
}