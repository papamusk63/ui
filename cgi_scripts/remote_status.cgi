#!/usr/bin/perl -w

use warnings;
use Net::FTP;
use Net::Ping;
use Date::Manip;
$ENV{LANG}='C';
use Time::Local;

print "Content-type: text/html\n\n";

my %testbed_ip;
my %testbed_status;
my %testbed_waiting;
my %testbed_paused_info;
my %testbed_running;
my %testbed_notes;
my %testbed_dates;
my %job_finish_time;
my %months = ( 
	Jan => "Month_01",
	Feb => "Month_02",
	Mar => "Month_03",
	Apr => "Month_04",
	May => "Month_05",
	Jun => "Month_06",
	Jul => "Month_07",
	Aug => "Month_08",
	Sep => "Month_09",
	Oct => "Month_10",
	Nov => "Month_11",
	Dec => "Month_12" );


ip_list();

my $me = "krtb2";
my $my_ip = $testbed_ip{$me};

my $remote_host = "172.22.184.101";
my $remote_name = "quickbed";

my $testBed_loc = "/usr/global/regression";
my $css_loc = "css/quick.css";
my $overlib_loc = "http://$my_ip/status/masterlog/js/overlib/overlib.js";
my $result_index = "http://$my_ip/status/result_index.txt";
#-------------------------------------#
my $bed_status = "bed_status_r";
my $job_waiting = "job_waiting_r";
my $job_running = "job_running_r";
my $finish_time = "finish_time_r";
my $pause_info = "pause_info_r";
my $special_notes = "special_notes_r";
my $bed_dates = "bed_dates_r";
#-------------------------------------e
get_remote();
print <<HERE;
<html>
<head>
	<script src="http://172.22.184.101/status/test.php"></script>
	<link rel="stylesheet" type="text/css" href=$css_loc>
	<script language=Javascript src=$overlib_loc></script>
	<div id="overDiv" style="position:absolute; visibility:hidden; z-index:1000;"></div>
</head>
<body class=right>
HERE

print "<script language=\"JavaScript\">setTimeout('location.reload(true)',0);</script>\n" if (!(-f "$bed_status"));

get_completion_times();
get_job_running();
get_job_waiting();
get_special_notes();
get_dates();
get_paused_info();

get_test_bed_list();
print "</td></tr></table>";
print "</body></html>";
#--------------------------------------------------------------#
# get the list of test beds, print out according to the status #
#--------------------------------------------------------------#
sub get_test_bed_list {
	open STATUS, "<$bed_status" or die "$!:$bed_status\n";
	while (<STATUS>) {
		chomp;
		my ($bed, $status) = split /\|/, $_;
		push @{$testbed_status{$status}}, $bed;
	}
	close STATUS;
	
	print "<table  border=1 width=100%>";
	for (keys %testbed_status) {
		print_title($_);
		foreach my $tb (@{$testbed_status{$_}}) {
#			next if (!$testbed_ip{$tb});
			my $state_down = check_status($tb);
			if ($state_down =~ /$tb/i) {
			print "$tb";
				#print_down($tb);
				next;
			}
			get_inprogress($tb) if ( /inprogress/ );
			get_idle($tb)       if ( /idle/ );
			get_paused($tb)     if ( /paused/ );
		}	
	}
	print "</table>";
}	
#------------------------------------------#
# print out status of test bed in progress #
#------------------------------------------#
sub get_inprogress {
	my $tb = shift;
	my $host = $testbed_ip{$tb} ? $testbed_ip{$tb} : $tb;
        
	my $number_of_waiting = $testbed_waiting{$tb};
	my $s = $number_of_waiting gt 1? "s" : "";
	my $image = $number_of_waiting gt 0? "<img src=images/job_waiting.gif title=Checkout detail>" : " ";
        my $job_waiting_string = "<a href=http://$host/jobs/ title=Checkout detail>".$image.$number_of_waiting." job$s waiting</a>";

	my $result_url 	= ${$testbed_running{$tb}}{"url"};
	my $job_id  	= ${$testbed_running{$tb}}{"jobid"};
	my $args 	= ${$testbed_running{$tb}}{"args"};
	my $version 	= ${$testbed_running{$tb}}{"version"};

	my $time_left = get_time_left($job_id);	
	$time_left = "Waiting..." if (!$time_left);
	if ($job_id =~ /alcatel/) {
		$job_id =~ s/\@alcatel\.com.*//;
	} else {
		$job_id =~ s/\(UTC\)//;
	}
	
#	my $masterlog_cgi = $result_url."masterlog.cgi";
	my $masterlog_cgi = $result_url."test_console.txt";

	my $daily_summary_url = $result_url;
	$daily_summary_url =~ s/(\d+)\:(\d+).*//;
	my $notes = "n/a";
	$notes = $testbed_notes{$tb} if ($testbed_notes{$tb});
# print out the status
print <<MARKER;
<tr><td class=tb_inprogress ><a class=tb href=\"$daily_summary_url\" title=\"$host\">$tb</a></td>
<td class=test_name><a href=$result_url title='Result index'>$job_id</a></td>
<td class=time_left>$time_left</td>
<td class=version>$version</td>
<td class=args>$args</td>
<td class=masterlog><a href=$masterlog_cgi title='Masterlog'><img src=images/mstl.gif></a></td>
<td class=job_waiting width=100px>$job_waiting_string</td>
<td class=notes>$notes</td>
</tr>
MARKER

}

sub get_paused {
	my $tb = shift;
	my $host = $testbed_ip{$tb} ? $testbed_ip{$tb} : $tb;

	my $number_of_waiting = $testbed_waiting{$tb};
        my $s = $number_of_waiting gt 1? "s" : "";
        my $image = $number_of_waiting gt 0? "<img src=images/job_waiting.gif title=Checkou
t detail>" : " ";
        my $job_waiting_string = "<a href=http://$host/jobs/ title=Checkout detail>".$image
.$number_of_waiting." job$s waiting</a>";

        my $latest_date = $testbed_dates{$tb};
        my $daily_summary_url = "http://$host/results/$latest_date";
        my $notes = "n/a";
        $notes = $testbed_notes{$tb} if ($testbed_notes{$tb});

	my $reason = $testbed_pause_info{$tb};
			
print <<MARKER;
<tr><td class=tb_paused><a class=tb href=\"$daily_summary_url\" title=\"$host\">$tb</a></td>
<td class=masterlog colspan=5>$reason</td>
<td class=job_waiting>$job_waiting_string</td>
<td class=notes>$notes</td>
</tr>
MARKER

}


sub get_idle {
	my $tb = shift;
	my $host = $testbed_ip{$tb} ? $testbed_ip{$tb} : $tb;
	
	my $number_of_waiting = $testbed_waiting{$tb};
        my $s = $number_of_waiting gt 1? "s" : "";
        my $image = $number_of_waiting gt 0? "<img src=images/job_waiting.gif title=Checkout detail>" : " ";
        my $job_waiting_string = "<a href=http://$host/jobs/ title=Checkout detail>".$image.$number_of_waiting." job$s waiting</a>";
	
	my $latest_date = $testbed_dates{$tb};
	my $daily_summary_url = "http://$host/results/$latest_date";
	my $notes = "n/a";
        $notes = $testbed_notes{$tb} if ($testbed_notes{$tb});
	
print <<MARKER;
<tr><td class=tb_idle ><a class=tb href=\"$daily_summary_url\" title=\"$host\">$tb</a></td>
<td class=masterlog colspan=5> &nbsp</td>
<td class=job_waiting>$job_waiting_string</td>
<td class=notes>$notes</td></tr>
MARKER

}

sub get_stopped {
	
}

#--------------------------------------------#
# get the time left for current running test #
#--------------------------------------------#
sub get_time_left {
	my $job_id = shift;
	
	my $time_to_return;
	my $finish_time = $job_finish_time{$job_id};
	if (!$finish_time) {
		$time_to_return = "Waiting...";
	} elsif ($finish_time eq "unknown") {
		$time_to_return = "Waiting...";
	} else {	
		my $current = ParseDate("today");
		my $finish = ParseDate($finish_time);
	       	my $time_diff = DateCalc($current,$finish,1);
			
		my @time_left = split /\:/, $time_diff;
        	if ($time_left[0] =~ m/\-/) {
        		$time_to_return = "00:00:00";
		}else{
        		my $sec = pop @time_left;
                	my $min = pop @time_left;
		        my $hour = pop @time_left;
			my $day = pop @time_left;
        		my $mth = pop @time_left;
	                my $yr = pop @time_left;
			
		        $time_to_return .= $yr." yr " 	if ($yr gt '0');
        		$time_to_return .= $mth." mth "	if ($mth gt '0');
	                $time_to_return .= $day." day "	if ($day gt '0');

			if ($hour ge '0') {
				$hour = "0".$hour if ($hour < 10);
				$time_to_return .= $hour.":";
			}
			if ($min ge '0') {
				$min = "0".$min if ($min < 10);
                                $time_to_return .= $min.":";
                        }
			if ($sec ge '0') {
				$sec = "0".$sec if ($sec < 10);
                                $time_to_return .= $sec;
                        }
        	}
	}
	
	return $time_to_return;
}


sub check_status {
	my $tb = shift;
        my $host = $testbed_ip{$tb}? $testbed_ip{$tb} : $tb;

	$p = Net::Ping->new();
	$p->ping($host) or return "Can't ping $host: $!<br>";
	$p->close();
	return "good";
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
			if ($record) {
				if ($1 =~ /quickbed/ ) {
					$tb = "quickbed";
				}else{
					$tb = $1;
				}
			}
                }
                elsif ( /FTP_SERVER=(.*)\;\;/ ) {
                        $testbed_ip{$tb} = $1 if $record;
                        $tb = "";
                }
        }
        close FILE;
}


sub print_title {
	my $type = shift;
	if ($type =~ /inprogress/ ) {
print <<HERE;
		<tr><td class=title_bar>Test Bed</td>
		<td class=title_bar>Job</td>
		<td class=title_bar>Time Left</td>
		<td class=title_bar>Version</td>
		<td class=title_bar>Args</td>
		<td class=title_bar>Test Console Log</td>
		<td class=title_bar>Jobs Waiting</td>
		<td class=title_bar>Purpose/Notes</td></tr>
HERE
	}
	if ($type =~ /idle/ ) {
print <<HERE;
		<tr><td class=title_bar>Test Bed</td>
		<td class=title_bar colspan=5> &nbsp </td>
		<td class=title_bar>Jobs Waiting</td>
		<td class=title_bar>Purpose/Notes</td></tr>
HERE
	}
	if ($type =~ /paused/ ) {
print <<HERE;
                <tr><td class=title_bar>Test Bed</td>
                <td class=title_bar colspan=5>Reason</td>
                <td class=title_bar>Jobs Waiting</td>
                <td class=title_bar>Purpose/Notes</td></tr>
HERE

	}
}

sub get_job_running {
	open RUNNING, "<$job_running" or return "$!:$job_running\n";

	while (<RUNNING>) {
		chomp;
		my ($bed, $jobid, $version, $args, $url) = split /\|/, $_;
		$version =~ s/^.*: //;
		$args =~ s/^.*: //;
		$url =~ s/^.*: //;
		
		${$testbed_running{$bed}}{"version"} 	  = $version;
		${$testbed_running{$bed}}{"args"} 	  = $args;
		${$testbed_running{$bed}}{"url"} 	  = $url;
		${$testbed_running{$bed}}{"jobid"} 	  = $jobid;
	}
	close RUNNING;
	
}

sub get_job_waiting {
	open WAIT, "<$job_waiting" or die "$!:$job_waiting\n";
	while (<WAIT>) {
		chomp;
		my ($bed, $waiting) = split /\|/, $_;
		$testbed_waiting{$bed} = $waiting;
	}
	close WAIT;
}

sub get_paused_info {
	open PAUSE, "<$pause_info" or die "$!:$pause_info\n";
	while (<PAUSE>) {
		chomp;
		my ($bed, $reason) = split /\|/, $_;
		$testbed_pause_info{$bed} = $reason;
	}
	close PAUSE;
}

sub get_completion_times {
	open FINISH, "<$finish_time" or die "$!:$finish_time\n";
	while (<FINISH>) {
		chomp;
		my ($jobid, $time) = split /\|/, $_;
		$time =~ s/\.$//;
		$job_finish_time{$jobid} = $time;
	}
	close FINISH;
}

sub get_special_notes {
	open NOTE, "<$special_notes" or die "$!:$special_notes\n";
	while (<NOTE>) {
		chomp;
		next if ( /MtnView:|Kanata:/ );
		my ($bed, $notes) = split /\|/, $_;
		$notes =~ s/\- //;
		$testbed_notes{$bed} = $notes;
	}
	close NOTE;
}

sub get_dates {
	open DATE, "<$bed_dates" or die "$!:$bed_dates\n";
	while (<DATE>) {
		chomp;
		my ($bed, $date) = split /\|/, $_;
		my ($dw, $month, $day, $time, $t, $year) = split / /, $date;
		my $new_day = $month."_".$day;
		my $new_month = $months{"$month"};
		$testbed_dates{$bed} = "$year/$new_month/$new_day/";
	}
	close DATE;
}

sub get_remote {
	$ftp = Net::FTP->new($remote_host) or die "Can't ftp to $remote_host: $!<br>";
        $ftp->login($remote_name, "tigris") or print "$!";
	$ftp->cwd("/$remote_name/status/") or print "$!";
	my $tmp = $ftp->ls(".");
        $ftp->get("bed_status", $bed_status);
        $ftp->get("job_waiting", $job_waiting);
	$ftp->get("job_running", $job_running);
	$ftp->get("finish_time", $finish_time);
	$ftp->get("pause_info", $pause_info);
	$ftp->get("special_notes", $special_notes);
	$ftp->get("bed_dates", $bed_dates);
	
}

sub print_down {
	my $tb = shift;
print <<MARKER;
<tr><td class=tb_down width=100px>$tb</td>
<td class=tb_down colspan=7> <can't ping $tb> </td></tr>
MARKER

}
