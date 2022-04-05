function setMyCookie() {
    // get the domain
    var d = document.myform.domain.value;
    // get what the user selected
    var w = document.myform.mylist.selectedIndex;
    var selected_text = document.myform.mylist.options[w].text;
    // get the checkbox value
    var checked = 0;
    if (document.myform.priv.checked) {
        var checked = 1;
    }
    // get the offline checkbox value
    var ochecked = 0;
    if (document.myform.offline.checked) {
        var ochecked = 1;
    }
    // get the timing checkbox value
    var timing = 0;
    if (document.myform.timing.checked) {
        var timing = 1;
    }
    var cookieValue = checked+"|"+selected_text+"|"+ochecked+"|"+timing;
    // set the cookie
    createCookie('SrGuiSelect',cookieValue,0,d);
    // the reasonFilter is only used when displaying myJobs or regressionJobs. In any other case, delete the cookie containing the filter.
    if (document.myform.reasonFilter.value != "" && selected_text != "myJobs" && selected_text != "regressJobs" ) {
        createCookie('SrReasonFilter',"deleteCookie",-1,d);
    }
        
    // reload the page with the new settings
    javascript:location.reload(true);
}
function setReasonFilter() {
     var reasonFilter = window.prompt("Retain only the beds with jobs where the '-reason' field contains the following string:","");
     var d = document.myform.domain.value;
     if ( reasonFilter != "" && reasonFilter != null ) {
        createCookie('SrReasonFilter',reasonFilter,0,d);
     } else {
        createCookie('SrReasonFilter',"deleteCookie",-1,d);
     }
     javascript:location.reload(true);
}
 function createCookie(name,value,days,domain) {
        if (days) {
                var date = new Date();
                date.setTime(date.getTime()+(days*24*60*60*1000));
                var expires = "; expires="+date.toGMTString();
        }
        else var expires = "";
    if (domain == "") {
        document.cookie = name+"="+value+expires+"; path=/";
    } else {
        document.cookie = name+"="+value+expires+"; domain="+domain+"; path=/";
    }
}