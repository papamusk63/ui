<?php

$q = "";
if (isset($_GET['q'])) {
    $q=$_GET['q'];
}
$y = "";
if (isset($_GET['y'])) {
    $y=$_GET['y'];
}
$m = "";
if (isset($_GET['m'])) {
    $m=$_GET['m'];
}

$seed = "";
if (isset($_GET['seed'])) {
    $seed=$_GET['seed'];
}

$myhost = $_SERVER['HTTP_HOST'];
$host = trim(`hostname -s`);
# rowserver variable only exists on rowservers, serving virtual beds
$rowserver = getenv('ROWSERVER');
if ($rowserver == $host) {
       #we need the virtual host name iso the rowserver
       $temp = $_SERVER['SERVER_NAME'];
       list($host, $domain_not_wanted) = explode('.', $temp, 2);
     }
# else we are in a non-virtual environment -- do nothing: host var is ok as is

include "/$host/status/common_func.php";

# obtain all testbed info from regress.params
$aTb = FillTestbedArray("/usr/global/bin/regress.params");

$host_ip = $aTb[$host]['IP'];
if (!$host_ip) {
    $host_ip = $host;
}
unset($aTb);
$seed=time();

?>

<head>

<?php

# change dir here is there 'just in case' it does any good in helpng the javascript functions
# load. Sometimes they don't load so this chdir can't hurt
chdir("/$host/status");

?>

<link rel="stylesheet" type="text/css" href="css/test.css">
<script type="text/javascript" src="cooltree.js"></script>
<script type="text/javascript" src="livesearch.js"></script> 
<script type="text/Javascript" src="overlib.js"></script>
<script type="text/javascript" src="results_index.js"></script>

<?php
echo "<title> [$host]: Daily Summary </title></head>";

$archive_server = exec("cat /etc/homedir_cleanup/archive_server");
$tree_file = "tree_nodes.js";
$i = 0;
$latest_month = 0;
$latest_year = 0;
$stack = array();
$file_d = fopen($tree_file, "w");

fwrite($file_d, "var TREE1_NODES = [\n");
fwrite($file_d, "['$host', null, null,\n");
get_years("$host", $file_d);
fwrite($file_d, "],\n");

if($archive_server){
	fwrite($file_d, "['$archive_server', null, null,\n");
	get_archive("$host", $file_d);
	fwrite($file_d, "],\n");
}
fwrite($file_d, "];\n");
fclose($file_d);
$latest_year++;
$latest_month++;

if ($q) {
    echo "<body onLoad=\"showResult('$q&seed=$seed')\">\n";
}else{
    echo "<body onLoad=\"showResult('$last_entry&seed=$seed')\">\n";
}

?>
<div id="overDiv" style="position:absolute; visibility:hidden; z-index:1000;"></div>

<table border="0" cellspacing="0" cellpadding="0" width="100%" style="height: 100%;">
    <tr>
    	<td width="15%" style="color: #FFFFFF; font-size: 40pt">padding padding padding</td>
        <td valign="top"><div id="livesearch">  </div></td>
	</tr>
</table>

<script type="text/javascript" src="tree_nodes.js"></script>
<script type="text/javascript" src="tree_format.js"></script>

<script type="text/javascript">
    var tree = new COOLjsTree("tree1", TREE1_NODES, TREE1_FORMAT);
<?php    

# expand tree nodes
if (!$y) {
    $y = $latest_year;
}
if (!$m) {
    $m = $latest_month;
}
echo "  tree.expandNode(0);
        tree.expandNode($y);
        tree.expandNode($m);
        tree.draw();\n";

$fd2 = fopen("latest", "w");
fwrite($fd2, "http://$myhost/results/$last_entry/");
fclose($fd2);

?>    
</script>
</body>
</html>

<?php
#
#PHP: functions

function get_years($bed, $file_d) {
	global $stack;
	global $latest_year;
	global $i;
	$dir = "/$bed/results/";
	$fd = opendir ($dir);
	if ($fd) {
		while ($part = @readdir($fd)) {
			if ($part != "." && $part != ".." && (!preg_match('/\.html/', $part)) && (!preg_match('/\.ico/', $part))) {
				$years[] = $part;	
			}
		}
		sort($years);
		foreach ($years as $part) {	
			if (is_dir($dir.$part)) {
				fwrite($file_d, "\t['$part', null, null,\n");
				$latest_year = $i;
				$i++;
				get_months($dir, $part, $i, $file_d);
				fwrite($file_d, "\t],\n");
			}
			if (!(is_dir($dir.$part))) {
				array_push($stack, $part);
			}
		}
	}
}

function get_months($dir, $year, $y_num, $file_d) {
	global $i;
	global $latest_month;
	global $latest_year;

	$year_dir = $dir."$year/";
	$fd = @opendir ($year_dir);
	$months = array();
    if ($fd) {
        while ($part = @readdir($fd)) {
            if ($part != "." && $part != "..") {
        		$months[]=$part;
            }
        }
		sort($months);
		foreach ($months as $m) {
			fwrite($file_d, "\t\t['$m', null, null,\n");
			$latest_month = $i;
			$i++;
            get_days($dir, $year, $y_num, $m, $i, $file_d);
            fwrite($file_d, "\t\t],\n");
		}
    }
}

function get_days($dir, $year, $y_num, $month, $m_num, $file_d) {
	global $myhost;
	global $i;
	global $last_entry;
	
	$month_dir = $dir."$year/$month/";
	$fd = @opendir ($month_dir);
    if ($fd) {
        while ($part = @readdir($fd)) {
            if ($part != "." && $part != "..") {
	     		$days[]=$part;
            }
        }
		sort($days);
		foreach ($days as $d) {
			$i++;
            fwrite($file_d, "\t\t\t['</a><div class=\"item\" style=\"padding: 0 10px; background: #808080\"><a href=\"http://$myhost/status/result.php?q=$year/$month/$d&y=$y_num&m=$m_num&d=$i\">$d</a></div><a>', null, null], \n");
           	$last_entry = "$year/$month/$d";
        }
    }
}

function read_from_archive($dir) {
	$result = preg_split("/\s/", shell_exec("rsync rsync://$dir --list-only | awk '{print \$NF}'"), NULL, PREG_SPLIT_NO_EMPTY);
	$output = array();
	foreach ($result as $part) {
		if ($part != "." && $part != ".." && (!preg_match('/\.html/', $part))) {
			$output[] = $part;
		}
	}
	sort($output);
	return $output;
}

function get_archive($bed, $file_d) {
	global $stack;
	global $latest_year;
	global $i;
	global $archive_server;
	$dir = "$archive_server/results/$bed/";
	$years = read_from_archive($dir);
	foreach ($years as $part) {
		fwrite($file_d, "\t['$part', null, null,\n");
		$latest_year = $i;
		$i++;
		$year = $part;
		$y_num = $i;
		$year_dir = $dir."$year/";
		$months = read_from_archive($year_dir);
		foreach ($months as $m) {
			fwrite($file_d, "\t\t['$m', null, null,\n");
			$latest_month = $i;
			$i++;
			$month = $m;
			$m_num = $i;
			$month_dir = $dir."$year/$month/";
			$days = read_from_archive($month_dir);
			foreach ($days as $d) {
				$i++;
				fwrite($file_d, "\t\t\t['</a><div class=\"item\" style=\"padding: 0 10px; background: #808080\"><a href=\"http://$archive_server/status/result.php?name=$bed&q=$year/$month/$d&y=$y_num&m=$m_num&d=$i\" target=\"_blank\">$d</a></div><a>', null, null], \n");
			}
			fwrite($file_d, "\t\t],\n");
		}
		fwrite($file_d, "\t],\n");
	}
}

#END: functions

?>
