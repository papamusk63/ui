##########################################################################
# FileName - login.py
# Login page for authentication
# NOTE - you cannot add much to spice up the GUI unless it exists
#        in this file (or the stuff included) as Apache will block it
#        until after the user is authenticated (for example, fancy gifs)
#########################################################################
#include 'XML_RPC.py';
include 'common_func.py';

$myhost      = $_SERVER['HTTP_HOST'];

# domain is set to the last 2 dots only to reduce the amount of times to log on
$domainPieces = explode(".", $myhost);
$numDomains = count($domainPieces);
$domain = ".".$domainPieces[$numDomains - 2].".".$domainPieces[$numDomains - 1];

$emailCookie = 'GUIAuth';
$secureCookie= 'GoogleAuth';
$loggedIn = 0;
$secret_word = 'B1nar,ytR33';

# Message text line on GUI
$msg = "";

# user provided password
if (isset($_POST['access_password'])) {

    $user = isset($_POST['access_username']) ? $_POST['access_username'] : '';
    $passwd = $_POST['access_password'];

    # Get the locale
    $here = getLocale();
    if ($here == "Kanata") {
        $site = "138.120.178.252";
    }
    if ($here == "MtnView") {
        $site = "sso.mv.usa.alcatel.com:443";
    }
    if ($here == "NuageMv" or $here == "NuageAnt" or $here == "NuageRa" or $here == "NuageBa" or $here == "NuageWf" or $here == "NuageBt") {

        $ldap['host'] = "ldap://nuageldap1.mv.nuagenetworks.net";
	$ldap['user'] = "uid=$user,cn=users,cn=accounts,dc=us,dc=alcatel-lucent,dc=com";
	$ldap['filter'] = "(&(objectClass=*)(memberof=CN=nuage-engineering,cn=groups,cn=accounts,dc=us,dc=alcatel-lucent,dc=com))";
	$ldap['attr'] = array("mail");
        $ldap['conn'] = ldap_connect($ldap['host']);
	#ldap_set_option(NULL, LDAP_OPT_DEBUG_LEVEL, 255);
        if($ldap['conn'])
        {
            $ldap['bind'] = ldap_bind($ldap['conn'], $ldap['user'], $passwd);
        }

        # Here for consistency but unused
        $site = "sso.mv.usa.alcatel.com:443";
    }
    if ($here == "Antwerp") {
        $site = "138.203.16.150";
    }
    if ($here == "Naperville") {
        $site = "135.2.40.7";
    }
    if ($here == "Bratislava") {
        $site = "135.243.195.220";
    }
    # location of the web service receptor, should be placed in the same place on every server
    $location = "/authServer.php";

    # if we bind the ldap server, just proceed through ldap auth, otherwise,
    # call the web service, params are like so
    # XMLRPC_request(site, location, methodName, params, user_agent) user_agent is optional
    if(!$ldap['bind'])
    {
        $success=1;
    }
    else
    {
	 $ldap['result'] = ldap_search($ldap['conn'], $ldap['user'], $ldap['filter'], $ldap['attr']);
	 $result=ldap_get_entries($ldap['conn'], $ldap['result']);
	 $success=1;
	 $response=array($result['count'],  $result[0]['mail'][0]);
    }
    if($success) {
        if (!$response[0]) {
            # output an error
            $msg = "Incorrect Username/Password or Access Denied";
        } else {
            $loggedIn = 1;
            $emailAddress = $response[1];
            # if no email address, set it to the username
            if ($emailAddress == "") {
                $emailAddress = $user;
            }
            $msg = "Successfully Authenticated.";
        }
        unset($_POST['access_username']);
        unset($_POST['access_password']);
        unset($_POST['Submit']);
    } else {
        $msg = "Cannot communicate with authenticating web service, try again later.";
    }
}
else
{
    if ($_COOKIE[$secureCookie]!='')
    {
        unset ($user);
        list($c_username,$cookie_hash) = split(',',$_COOKIE[$secureCookie]);

        if (md5($c_username.$secret_word) == $cookie_hash) {
            $user = $c_username;
            $loggedIn = 1;
            $msg = "Already Authenticated";
        } else {
            $loggedIn = 0;
            $msg = "Session Cookie no good.";
        }

    }
     if (! isset($_COOKIE[$emailCookie]))
     {
         $loggedIn = 0;
         $msg = "";
     }
}

if ($loggedIn)
{
    header("HTTP/1.0 200 OK");     #Force it to be OK. Trust me.
    header("X-Username: $user");
    header("X-Groups: schedules");
    if ($_COOKIE[$secureCookie]== ''){
        setcookie($secureCookie, $user.','.md5($user.$secret_word), time() + 60 * 60 * 24 * 7, "/", $domain);
    }
    if ($_COOKIE[$emailCookie]== ''){
        setcookie($emailCookie , $emailAddress,                     time() + 60 * 60 * 24 * 7, "/", $domain);
    }

    # redirect back to the calling page
    $sourcePage = $_GET['page'];

    if ($sourcePage != "")
    {
        if (! preg_match('/^http[s]*:\/\//',$sourcePage) )
        {
            $sourcePage = "http://".$myhost . $sourcePage;
        }
        header( "refresh: 0; url=$sourcePage");
        exit;
    }
    # else just someone setting a cookie I guess, not so bad
}
else
{
    header("HTTP/1.0 401 Unauthorized");
    if ($_COOKIE[$secureCookie]!=''){ #Delete existing cookies
        setcookie($secureCookie, "$user",         time() - 3600 * 25 , "/", $domain);
    }
    if ($_COOKIE[$emailCookie]!=''){
        setcookie($emailCookie,  "$emailAddress", time() - 3600 * 25 , "/", $domain);
    }
}

########################################################################
# Ugly GUI
########################################################################
header("Cache-Control: no-cache, must-revalidate"); // HTTP/1.1
?>

<html>
<head>
<title>Login to Testbed GUIs</title>
</head>
<body bgcolor="white" text="black">
<p>
<form name="myForm" method="post">
<?php if (getLocale() == "NuageMv" or getLocale() == "NuageAnt" or getLocale() == "NuageRa" or getLocale() == "NuageBa" or getLocale() == "NuageBt") { ?>
<div style="margin-left:auto; margin-right:auto; margin-top:50px; width:500px; background-color:#FFFAF2">
<font size=+1><b>Nuage regression testbed GUI Login</b></font>
<br><br>
Enter your CSL and Nuage password <br><i>(alternative: use your CVS/DTS/7750Admin credentials)</i>
<br><br>
<div style="width:250px">
<div style="text-align:right" >CSL:<input name="access_username" type="text" size=12></div>
<div style="text-align:right" >Nuage Password:<input name="access_password" type="password" size=12></div>
</div>
<br>
<div style="text-align:center"><input style="width:120px" name="submit" type="submit" value="Submit"></div>
<br>
<div style="text-align:center"><bold><font color="Red" size=4><?php echo $msg ?></font></bold></div>
</div>
<?php }else{ ?>
<font size=+1>7x50/7710 Regression Testbed GUI Login</font>
<br><br>
Enter Username and Password (use your CVS/DTS/7750Admin credentials)
<br><br>
<table cellspacing=0 cellpadding=0 width=400 align="left">
<tr><td>Username:</td><td>
<tr><td><input name="access_username" type="text" size=12></td></tr>
<tr><td>Password: </td><td>
<tr><td><input name="access_password" type="password" size=12></td></tr>
<tr><td></td></tr>
<br><br>
<tr><td colspan=2 ><input name="submit" type="submit" value="Submit"></td></tr>
<tr><td><bold><font color="Red" size=4><?php echo $msg ?></font></bold></td></tr>
</table>
<?php } ?>
</form>
<script type="text/javascript">
document.myForm.access_username.focus();
</script>
</body>
</html>
