
    function check_note(form) {
        if (form.note.value == "") {
            alert("You must enter a message!");
            form.note.focus();
            return false;
        }
        return true;
    }
    function movejob(e) {
        if(!e) var e = window.event;
        if (e.keyCode) code = e.keyCode;
        else if (e.which) code = e.which;
        if(code==13) {
            document.getElementById('movebutton').click();
            return false;
        }
    }
    function checkAll(formId) {
        var frmId=document.getElementById(formId);
        var reclen =  frmId.length;
        for(i=0;i<reclen;i++) {
            if (frmId.elements[i].type == 'checkbox') {
                if(document.getElementById( 'slall' ).checked) {
                        frmId.elements[i].checked=true;
                } else {
                        frmId.elements[i].checked=false;
                }
            }
        }
    }
    function check_comment(form) {
        // use ajax to find if it's already paused
        var xmlhttp;
        if (window.XMLHttpRequest)
        {// code for IE7+, Firefox, Chrome, Opera, Safari
            xmlhttp=new XMLHttpRequest();
        }
        else
        {// code for IE6, IE5
            xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
        }
        // find out
        xmlhttp.open("GET","../ws/gash/regresstools/realtm_info.php?info=ispaused&t=" + Math.random(),false);
        xmlhttp.send();
        var isAlreadyPaused = xmlhttp.responseText;
        if (isAlreadyPaused =="yes") {
            // get pause file
            xmlhttp.open("GET","../ws/gash/regresstools/realtm_info.php?info=getpaused&t=" + Math.random(),false);
            xmlhttp.send();
            var contentPause = xmlhttp.responseText;
            var msg="Bed already paused - do you want to proceed? \n\npaused by:\n\n";
            var msg2 = msg.concat(contentPause);
            var r=confirm(msg2);
            if (r == false) {
                location.reload(true);
                return false;
            } else {
                if (form.pause_reason.value == "") {
                    alert("You must enter your reason for pausing the bed!");
                    form.pause_reason.focus();
                    return false;
                }
            }
        } else {
            if (form.pause_reason.value == "") {
                alert("You must enter your reason for pausing the bed!");
                form.pause_reason.focus();
                return false;
            }
        }
        return true;
    }
    function check_canunpause(form) {
        var xmlhttp;
        if (window.XMLHttpRequest)
        {// code for IE7+, Firefox, Chrome, Opera, Safari
            xmlhttp=new XMLHttpRequest();
        }
        else
        {// code for IE6, IE5
            xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
        }
        // find out
        xmlhttp.open("GET","../ws/gash/regresstools/realtm_info.php?info=ispaused&t=" + Math.random(),false);
        xmlhttp.send();
        var isPaused = xmlhttp.responseText;
        if (isPaused == "yes") {
            // get pause file
            xmlhttp.open("GET","../ws/gash/regresstools/realtm_info.php?info=getpaused&t=" + Math.random(),false);
            xmlhttp.send();
            var currentPauseContent = xmlhttp.responseText;
            var origPauseContent = document.getElementById("origpause").innerHTML;
            // compare with orig pause file
            if (currentPauseContent != origPauseContent) {
                var msg="Pause message changed - do you want to proceed? \n\ncurrent pause:\n\n";
                var msg2 = msg.concat(currentPauseContent);
                var r=confirm(msg2);
                if (r == false) {
                    location.reload(true);
                    return false;
                } else {
                    return true;
                }
             } else {
                return true;
             }
         } else {
             return true;
         }
    }

    function check_canresume (form) {
        var has_customgash=form.customgash.value;
        var level="none";

        for (i=0;i<form.level.length;i++) {
	        if (form.level[i].checked) {
		        level = form.level[i].value;
	        }
        }

        if ((has_customgash==1) && ( (level == "resumeImmediate") || (level == "resumeAfterTest") )) {
            // alert("customGash tests cannot be rescheduled!");
            // location.reload(true);
            // return false;
            // fixed: customGash tests can be rescheduled
            return true;
        }
        return true;
    }

    function check_confirm() {
       if (confirm('Are you sure?')==true ) {
           return true;
        }
        return false;
    }
