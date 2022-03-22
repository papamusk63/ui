#!/usr/bin/perl -w
######################################################################
#
#
#
#
#
#
#
######################################################################

use warnings;
use Net::FTP;
use Net::Ping;
use Date::Manip;
$ENV{LANG}='C';
use Time::Local;

print "Content-type: text/html\n\n";

my %testbed_ip;

ip_list();

#####################################################################
my $me = "krtb2";
my $my_ip = $testbed_ip{$me};


######################################
# Place to get the list of test beds #
######################################
my $testBed_loc = "/usr/global/regression";
my $css_loc = "css/allBeds.css";
my $overlib_loc = "http://$my_ip/status/masterlog/js/overlib/overlib.js";
my $result_index = "http://$my_ip/status/result_index.txt";

print <<MARKER;
<html>
<head>
	<link rel="stylesheet" type="text/css" href=$css_loc>
	<script language=Javascript src=$overlib_loc></script>
	<div id="overDiv" style="position:absolute; visibility:hidden; z-index:1000;"></div>
</head>
<body class=right>
	<table width=100%>
	<tr><td class=textFontClass align=left></td>
	<td class=textFontClass align=left>
		<table border=1 width=100%>
			<tr>
			<td class=textFontClass align=center><a href="result_list.html" target="_blank"><img src="images/M.gif" alt="Test Result List"></a><br>Test Result List</td>
			<td class=textFontClass align=center>
			<a href="http://rdnweb.ca.alcatel.com/twiki/bin/view/Kanata7750/TestBedIP" target="_blank"><img src="images/ip_all.gif" alt="IP Addresses" border="0" ></img></a><br>IP Addresses
			</td>
			<td class=textFontClass align=center><a href="http://rdnweb.ca.alcatel.com/twiki/bin/view/Kanata7750/TestBedInfo" target="right"><img src="images/twiki.gif" alt="TestBedInfo" border="0" ></img></a><br>Test Bed Info
                        </td>
			<td class=textFontClass align=center>
			<a href="http://rdnweb.ca.alcatel.com/sr/" target="_blank"><img src="images/twiki.gif" alt="old sr page" border="0" ></img></a><br>Old SR Page
                        </td>
			</tr>
			
			<tr><td class=tip colspan=4>
                        <img src=images/job_waiting.gif> Tests Waiting &nbsp &nbsp
                        <img src=images/kill_test.png> Kill Current Running Test &nbsp &nbsp
                        <img src=images/mstl.gif> Check Masterlog &nbsp &nbsp
                        <img src=images/release.jpg> Release Test Bed
                        </td></tr>
		</table>

MARKER

get_test_bed_list();
print "</td></tr></table>";
print "</body></html>";
#--------------------------------------------------------------#
# get the list of test beds, print out according to the status #
#--------------------------------------------------------------#
sub get_test_bed_list {
	opendir BEDS, $testBed_loc or die $!."\n";
	my @testBed_status = grep /[a-zA-Z]/, readdir BEDS;
	closedir BEDS;

	print "<table  border=1 width=100%>";	
	for my $status (@testBed_status) {
		print "<tr><td style=\"background-color: #ddddff; font-size: 14px; font-weight: bold;\">$status</td></tr>";	
		print "<tr><td class=flat>";
		opendir BED, $testBed_loc."/".$status or die $!."\n";
		my @tbs = grep /[a-zA-Z]/, readdir BED;
		print "<table><tr>";
		foreach my $bed (sort @tbs) {
			next if (!($bed =~ /krtb/));
			my $server_down = check_status($bed);
			if ($server_down =~ /$bed/i) {
				print "<td class=flat valign=top><table border=1><tr><td><table><tr><td class=tb_idle colspan=2>$bed<font size=1px color=#F5F5F5>-[ Offline ]</td></tr><tr><td class=tb_content colspan=2>Test bed not available...</td></tr></table></td></tr></table><br></td>";
			        next;
			}
			print "<td class=flat valign=top>";
			get_inprogress($bed) if ( $status eq "inprogress" );	
			get_paused($bed) if ( $status eq "paused" );
			get_idle($bed) if ( $status eq "idle" );
			get_stopped($bed) if ($status eq "stopped");
			print "</td>";
		}
		print "</tr></table>";
		closedir BED;
		print "</td></tr>";
	}
	print "</td></tr></table>";
}	

#------------------------------------------#
# print out status of test bed in progress #
#------------------------------------------#
sub get_inprogress {
	my $tb = shift;
	my $host = $testbed_ip{$tb};
	my $jobs_url = "/$tb/jobs";
        my $inprogress_file = $jobs_url."/inprogress";
	my $result_index_file = "/$me/status/result_index.txt";
		
	$ftp = Net::FTP->new($host) or return "Can't ftp to $host: $!<br>";
	$ftp->login($tb, "tigris");
	$ftp->get($inprogress_file, "inprogress");
	$ftp->get($result_index_file, "result_index_tmp");

	my $index_url = get_result_index($tb, $result_index_file);	
	# pop up content for job waiting
	my $jobs_waiting_description = "<form action=remove_test.cgi method=POST><table width=500px><tr><td colspan=2 class=titleFontClass>Jobs Waiting: </td></tr>";
        my @jobs_waiting;
	# getting jobs there are waiting to be executed
        my @details = $ftp->dir($jobs_url) or die $!;
        foreach my $detail (@details) {
                my ($permission, @tmp) = split(/\s/, $detail);
                my $entry = pop @tmp;
                if($permission =~ /d/) {
                        push @jobs_waiting, $entry;
                        $jobs_waiting_description .= "<tr><td class=tb_content><input type=radio name=testname value=$tb|$entry> <a href=http://$host/jobs/$entry>$entry</a></td><td class=tb_content><input type=submit value=Remove></td></tr>";
                }
        }
        $jobs_waiting_description .= "</table></form>";
        my $number_of_waiting = scalar @jobs_waiting;
        my $pp_waiting = make_pop_up($jobs_waiting_description);
	my $s = $number_of_waiting gt 1? "s" : "";
        my $jobs_waiting = "<a href='' $pp_waiting title='".$number_of_waiting." job".$s." waiting'><img src=images/job_waiting.gif></img></a>" if( $jobs_waiting_description =~ m/http/ );
	# read the inprogress file to get arguments of the current test
	open FILE, "<inprogress" or die $!."-inprogress\n";
	@print_out = <FILE>;
	close FILE;
	for (@print_out) {
		if ( /Follow the results at(\s+): (\S+)/ ) {
			$result_url = $2;
		}elsif( /Submitter(\s+): (\S+)/ ){
			$submitter = $2;
		}elsif( /JobID \(submitted timestamp\)(\s+): (\S+)/ ) {
			$job_id = $2;
		}elsif( /Arguments passed to tests(\s+): (.*)/) {
			$args=$2;
		}
	}
	my $job_temp = $job_id;
	$job_temp =~ s/\@alcatel\.com//;
	my ($yr, $mth, $time, @rest) = split /\./, $job_temp;
	my $submitter_name = join " ", @rest;
	$test_name = $submitter_name." ($time $mth)";

	# masterlog page
	my @args = split /-/, $args;
	shift @args;

	my $masterlog_cgi = $result_url."masterlog.cgi";
	$result_url =~ s/http\:\/\/(\d+)\.(\d+)\.(\d+)\.(\d+)\///;
	$masterlog = $result_url."masterlog.txt";
	# time left for current test to run
	if (-f "/$tb/$masterlog") {
                my $time_left = get_time_left($masterlog, $tb);
        }else{
                my $time_left = "n/a";
        }

	
	
	$kill_description = "<form action=kill_test.cgi method=POST><table width=600px>";
	
	#------- pop up content for details -----------#
	$description = "<table width=600px>";
	$description .= "<tr><td class=titleFontClass>JobID:</td><td class=textFontClass>$job_id</td></tr>";
	$description .= "<tr><td class=titleFontClass>Arguments:</td><td class=textFontClass>$args</td></tr>";
	if ($tb =~ /spr/) {
		$kill_description .= "<tr><td class=tb_content><input type=radio name=testbed value=$tb checked><select name=type><option selected>-SIGQUIT</option><option>-SIGUSR1</option><option>-SIGUSR2</option></td><td class=tb_content><input type=submit value=Kill_current_regression></td></tr>";
		$kill_description .= "<tr><td class=tb_content colspan=2><i>-SIGQUIT: Shutdown of gash occurs immediately (i.e. the current test/suite does not complete);<br>-SIGUSR1: Shutdown of gash occurs after the current test completes;<br>-SIGUSR2: Shutdown of gash occurs after the current suite completes;</i></td></tr>";
	}else{
	$kill_description .= "<tr><td colspan=2 class=tb_content><input type=radio name=testbed value=$tb checked><input type=submit value=Kill_current_regression></td></tr>";
	}
	$description .= "</table>";
	$kill_description .= "</table></form>";
	#------------------ end -----------------------#
	$pause_bed = "<form action=pause_bed.cgi method=POST><table width=500px><tr><td class=tb_content><input type=radio name=action value=pause checked>Pause</td></tr><tr><td class=titleFontClass>Reason for pausing test bed: </td><td class=tb_content><input type=radio name=test_bed value=$tb checked>$tb</td></tr><tr><td colspan=2 class=tb_content><input type=text name=reason size=100></td></tr><tr><td class=tb_content><input type=submit value=OK></td></tr></table></form>";

	my $test_submit_description = test_submit_description($tb);
	my $pp_description = make_pop_up($description);
	my $pp_submit = make_pop_up($test_submit_description);
	my $pp_kill_description = make_pop_up($kill_description);
	my $pp_pause = make_pop_up($pause_bed);

# print out the status
print <<MARKER;
<table border=1><tr><td>
<table ><tr><td class=tb_inprogress colspan=2>$tb <font size=1px color=#F5F5F5>-[ inprogress ] $jobs_waiting</td></tr>
<tr><td class=titleFontClass><a href='' $pp_description><font color=#483D8B>$test_name</font></a></td><td><a href='' title='Kill Current Regression' $pp_kill_description><img src=images/kill_test.png></img></a></td></tr>
<tr><td class=titleFontClass>Time Left: $time_left</td><td><a href=$masterlog_cgi title='Masterlog'><img src=images/mstl.gif></a></td></tr>
<tr><td class=tb_content colspan=2 $pp_submit><a href=''><img src=images/submit_test.png></a></td></tr>
<tr><td class=tb_content colspan=2 $pp_pause><a href=''><img src=images/pause_bed.png></a></td></tr>
<tr><td class=tb_content colspan=2><a href=$index_url><img src=images/testList.gif></a></td></tr>

</table></td></tr></table><br>	
MARKER

}
sub get_paused {
	my $tb = shift;
	my $host = $testbed_ip{$tb};
	my $jobs_url = "/$tb/jobs";
	my $pause_file = $jobs_url."/pause";
	my $result_index_file = "/$me/status/result_index.txt";
	
	my $index_url = get_result_index($tb, $result_index_file);
	$ftp = Net::FTP->new($host) or return "Can't ftp to $host: $!<br>";
        $ftp->login($tb, "tigris");
        $ftp->get($pause_file, "pause");
	
	# pop up content for job waiting
	my $jobs_waiting_description = "<form action=remove_test.cgi method=POST><table width=500px><tr><td colspan=2 class=titleFontClass>Jobs Waiting: </td></tr>";
	my @jobs_waiting;
        my @details = $ftp->dir($jobs_url) or dir $!;
        foreach my $detail (@details) {
                my ($permission, @tmp) = split(/\s/, $detail);
                my $entry = pop @tmp;
                if($permission =~ /d/) {
			push @jobs_waiting, $entry;
			$jobs_waiting_description .= "<tr><td class=tb_content><input type=radio name=testname value=$tb|$entry> <a href=http://$host/jobs/$entry>$entry</a></td><td class=tb_content><input type=submit value=Remove></td></tr>";

                }
        }
	$jobs_waiting_description .= "</table></table>";
	my $number_of_waiting = scalar @jobs_waiting;
	my $pp_waiting = make_pop_up($jobs_waiting_description);
	my $s = $number_of_waiting gt 1? 's' : '';
        my $jobs_waiting = "<a href='' $pp_waiting title='".$number_of_waiting." job
".$s." waiting'><img src=images/job_waiting.gif></img></a>" if( $jobs_waiting_description =~ m/http/ );
	# read the pause file to get the reason for pausing test bed
	open FILE, "<pause" or die $!."\n";
	chomp;
	$print_out = <FILE>;
	close FILE;
	
	# pop up content for the test bed status
	$description = "<table width=500px><tr><td colspan=2 class=titleFontClass><form action=unpause_bed.cgi method=POST><input type=submit value=Unpause><input type=radio name=test_bed value=$tb checked>$tb</form></td></tr</table>";
	my $test_submit_description = test_submit_description($tb);
	my $pp_description = make_pop_up($description);
	my $pp_submit = make_pop_up($test_submit_description);

#print out the status
print <<MARKER;
<table border=1 class=tb3><tr><td>
<table class=tb3><tr>
<td class=tb_paused colspan=2>$tb <font size=1px color=#F5F5F5>-[ Paused ] $jobs_waiting</font></td></tr>
<tr><td class=titleFontClass>$print_out</td><td><a href='' title='Release Test Bed' $pp_description><img src=images/release.jpg></a></td></tr>
<tr><td class=tb_content colspan=2 $pp_submit><a href=''><img src=images/submit_test.png></a></td></tr>
<tr><td class=tb_content colspan=2><a href=$index_url><img src=images/testList.gif></a></td></tr>
</table></td></tr></table><br>
MARKER

}


sub get_idle {
	my $tb = shift;
	my $host = $testbed_ip{$tb};
	my $jobs_url = "/$tb/jobs";
	my $result_index_file = "/$me/status/result_index.txt";
	my $index_url = get_result_index($tb, $result_index_file);
        
	$ftp = Net::FTP->new($host) or return "Can't ftp to $host: $!\n";
        $ftp->login($tb, "tigris");

	my $jobs_waiting_description = "<form action=remove_test.cgi method=POST><table width=500px><tr><td colspan=2 class=titleFontClass>Jobs Waiting: </td></tr>";
        my @jobs_waiting;
	
        my @details = $ftp->dir($jobs_url) or return $! ;
        foreach my $detail (@details) {
                my ($permission, @tmp) = split(/\s/, $detail);
                my $entry = pop @tmp;
                if($permission =~ /d/) {
                        push @jobs_waiting, $entry;
                        $jobs_waiting_description .= "<tr><td class=tb_content><input type=radio name=testname value=$tb|$entry> <a href=http://$host/jobs/$entry>$entry</a></td><td class=tb_content><input type=submit value=Remove></td></tr>";

                }
        }
        $jobs_waiting_description .= "</table></table>";
        my $number_of_waiting = scalar @jobs_waiting;
        my $pp_waiting = make_pop_up($jobs_waiting_description);
	 my $jobs_waiting = "<a href='' $pp_waiting title='".$number_of_waiting." job".$s." waiting'><img src=images/job_waiting.gif></img></a>" if( $jobs_waiting_description =~ m/http/ );

	# pop up content for test bed details
	# pop up content for pause function
	$pause_bed = "<form action=pause_bed.cgi method=POST><table width=500px><tr><td class=tb_content><input type=radio name=action value=pause checked>Pause</td></tr><tr><td class=titleFontClass>Reason for pausing test bed: </td><td class=tb_content><input type=radio name=test_bed value=$tb checked>$tb</td></tr><tr><td colspan=2 class=tb_content><input type=text name=reason size=100></td></tr><tr><td class=tb_content><input type=submit value=OK></td></tr></table></form>";
	$test_submit_description = test_submit_description($tb);
	$pp_pause = make_pop_up($pause_bed);
	$pp_submit = make_pop_up($test_submit_description);

print <<MARKER;
<table border=1><tr><td>
<table><tr>
<td class=tb_idle colspan=2>$tb<font size=1px color=#F5F5F5>-[ Idle ] $jobs_waiting</td></tr>
<tr><td class=tb_content colspan=2 $pp_submit><a href=''><img src=images/submit_test.png></a></td></tr>
<tr><td class=tb_content colspan=2 $pp_pause><a href=''><img src=images/pause_bed.png></a></td></tr>
<tr><td class=tb_content colspan=2><a href=$index_url><img src=images/testList.gif></a></td></tr>
</table></td></tr>
</table><br>
MARKER

}

sub get_stopped {
	
}

#--------------------------------------------#
# get the time left for current running test #
#--------------------------------------------#
sub get_time_left {
	my $masterlog = shift;
	my $tb = shift;
	my $host = $testbed_ip{$tb};
	
	$ftp = Net::FTP->new($host) or return "Can't ftp to $host: $!<br>";
        $ftp->login($tb, "tigris");
	my @masterlog_txt = $ftp->ls("/$tb/$masterlog");
	if ($masterlog_txt[0]) {
	        $ftp->get("/$tb/$masterlog", "masterlog.txt");	
	
		open MASTER, "<masterlog.txt" or die $!;
		while (<MASTER>) {
		if(( /All tests should be completed by (.*)\./) or ( /Estimated time of regression completion is (.*)\./)) {
                	$finish_string = $1;
	                $current = ParseDate("today");
        	        $finish = ParseDate($finish_string);
                	$time_diff = DateCalc($current,$finish,1);
			

	                my @time_left = split /\:/, $time_diff;
        	        if($time_left[0] =~ m/\-/) {
                	        $time_left = "FINISHED";
	                }else{
        	                my $sec = pop @time_left;
                	        my $min = pop @time_left;
                        	my $hour = pop @time_left;
	                        my $day = pop @time_left;
        	                my $mth = pop @time_left;
                	        my $yr = pop @time_left;
				$time_left = "";
	
        	                $time_left .= $yr."yr " if ($yr gt '0');
                	        $time_left .= $mth."mth " if ($mth gt '0');
                        	$time_left .= $day."day " if ($day gt '0');
	                        $time_left .= $hour."h " if ($hour gt '0');
        	                $time_left .= $min."m " if ($min gt '0');
                	        $time_left .= $sec."s" if ($sec gt '0');

                        	$time_left = "FINISHED" if(!$time_left);
                	}	
			}
		}
		close MASTER;
	}else{
		my $time_left = "WAITING...";
	}
	return $time_left;
}

sub get_result_index {
        my $tb = shift;
	my $file = shift;
        
	open FILE, "<$file" or return $!;
        my ($index_url) = <FILE>;
        close FILE;

        $index_url =~ s/$my_ip/$testbed_ip{$tb}/;
        return $index_url;
}


sub get_loads {
        my $tb = shift;
        my $host = $testbed_ip{$tb};
        my $img_url;
  	      
	$ftp = Net::FTP->new($host) or return "Can't ftp to $host: $!<br>";
        $ftp->login($tb, "tigris");
	my @images;
	my %loads;

        $host = $tb.".ca.newbridge.com";
        $img_path = "/usr/global/images/";
	for ($ftp->ls($img_path)) {
		if ( /(\d)\.(\d)/ ) {
			my $version = $1.".".$2;
			for ($ftp->ls($img_path."$version/")) {
				push @{$loads{$version}}, $_ unless ( /private/ );
			}
		}
	}
	return \%loads;
		
}

sub test_submit_description {
	my $test_bed = shift;

	my $description = "<form action=get_help.cgi method=POST><table width=500px><tr><td class=titleFontClass><input type=radio name=testbed value=$test_bed checked><input type=submit value=HELP></td></tr></table></form>";	
	$description .= "<form action=submit_test.cgi method=POST>";
	my $loads = get_loads($test_bed);
	$description .= "<table width=500px>";
	$description .= "<tr><td class=titleFontClass>-d:</td><td class=testFontClass>";
	for my $version (sort keys %$loads) {
		$description .= "<input type=radio name=version value=$version>$version</input> <select name=".$version."_loads>";
		$description .= "<option>$_</option>" for @{$loads->{$version}};
		$description .="</select><br>";
	}
	$description .= "<input type=radio name=version value=other><input type=text size=50% name=directory value=/usr/global/images/></input><br>";
	$description .= "</td></tr>";
	$description .= "<tr><td class=titleFontClass>-notify:</td><td class=textFontClass><input type=text name=notify size=60%></td></tr>";
        $description .= "<tr><td class=titleFontClass>-cc:</td><td class=textFontClass><input type=text name=cc size=60%></td></tr>";
        $description .= "<tr><td class=titleFontClass>-testBed:</td><td class=textFontClass><input type=text size=60% name=testbed value=$test_bed></td></tr>";
	$description .= "<tr><td class=titleFontClass>-runLevel:</td><td class=textFontClass><select name=runLevel><option selected>quick</option><option>regular</option><option>regularOnly</option><option>extensive</option><option>extensiveOnly</option></select></td></tr>";
	$description .= "<tr><td class=titleFontClass>other options:</td><td class=textFontClass><input type=text size=60% name=options></td></tr>";
	$description .= "<tr><td class=titleFontClass>-- -runSuite:</td><td class=textFontClass><input type=text name=runSuite value=Sanity size=60%></td></tr>";
	$description .= "<tr><td class=titleFontClass>-runTest:</td><td class=textFontClass><input type=text name=runTest size=60%></td></tr>";
	$description .= "<tr><td class=titleFontClass>additonal gash args:</td><td class=textFontClass><input type=text size=60% name=gashArgs></td></tr>";
	$description .= "<tr><td colspan=2 class=titleFontClass>other args:</td></tr><tr><td colspan=2 class=textFontClass><input type=text size=80% name=addtionals></td></tr>";
	$description .= "<tr><td class=textFontClass><input type=submit value=Send></td></tr>";
	$description .= "</table></form>";
	return $description;
}

sub make_pop_up {
	my $description = shift;
	return "onclick=\"return overlib('$description',OFFSETX,20,BGCOLOR,'#000000',CSSCLASS,TEXTFONTCLASS,'textFontClass',FGCLASS,'fgClass',BGCLASS,'bgClass',CAPTIONFONTCLASS,'capfontClass',CLOSEFONTCLASS,'capfontclass',CAPTION,'Details',STICKY);\" onclick=\"return nd();\"";
}

sub check_status {
	my $tb = shift;
        my $host = $testbed_ip{$tb};
	$p = Net::Ping->new();
	$p->ping($host) or return "Can't ping $host: $!<br>";
	$p->close();
}

sub ip_list {
        my $file = "/usr/global/bin/regress";
        my $record = 0;
        my $tb = "";
        open FILE, "<$file" or die "can not open file: $!\n";
        while (<FILE>) {
                if ( /function SetFtpParams/ ) {
                        $record = 1;
                }
                elsif ( /esac/ ) {
                        return if $record;
                }
                elsif ( /(\S+)\)/ ) {
                        $tb = $1 if $record;
                }
                elsif ( /FTP_SERVER=(.*)\;\;/ ) {
                        $testbed_ip{$tb} = $1 if $record;
                        $tb = "";
                }
        }
        close FILE;
}

