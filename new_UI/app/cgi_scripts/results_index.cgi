#!/usr/bin/perl
#########################################################################################
# results_index.cgi --
#
# This script is supposed to read the /testbed/results/ for all the tests submitted of
# day, and generate a list with each test contains the following info:
#       1. The test name;
#       2. The version of the load used by the test;
#       3. The arguments passed with the test;
#       4. The number of PASSED / FAILED / SKIPPED tests so far (including suite cleanup/setups);
#          [ if there's a on going test, this section shows the most recent results, as
#            well as the time left for the test ];
#       5. The link to masterlog.cgi;
#########################################################################################
# **Notice**:   This scripts parses the result.txt which is generated at by masterlog.cgi,
#               I had  runregress.sh shell script to call masterlog.cgi each time a test
#               gets executed, in this way, the results_index page will be able to provide
#               infomation smarter;
#########################################################################################
# How the script works:
#               We keep in mind of a list of key words:
#                       BEGIN, END, RESULT, ERROR, CRIT
#               every test has a default resulting status: PROCESSING,
#               once we are encountered by RESULT / END / ERROR / CRIT tag,
#               we change it to the corresponding status.
#               After we read through the log file, we compare the results we get with
#               the result generated in the email.txt, if there's any mismatching, we
#               go to index.html to fetch the url of the mismatching test and show it
#               on the web page.
#########################################################################################
# Version: 1.0
# Sean Yang
# Mar 22, 05
#########################################################################################
use Date::Manip;
$ENV{LANG}='C';
print "Content-type: text/html\n\n";
my $location = $ENV{REQUEST_URI};
my %testbed_ip;

ip_list();

###########################
# Configure test bed here #
###########################
my $testBed = "krtb2";     #
###########################
my $my_ip = $testbed_ip{$testBed};      #
###########################

#======================================================================================#
#******************** NOTHING MUST BE CHANCED STARTS HERE *****************************#
#======================================================================================#
chdir "/".$testBed."/".$location or die;

my @url_temp = split/\//, $location;
my $today = $url_temp[-1];

my $masterlog_dir = "/var/www/cgi-bin/";
my $masterlog_script = $masterlog_dir."masterlog.cgi";
my $host = "http://$my_ip/status/result_index/";
my $css_loc = $host."css/results_index.css";
my $js_loc = $host."js/results_index.js";
my $current_processing = '';
my $id = 0;
my $test_case_left = 0;
my $time_left = '';
my $current_case = '';

# --------------------------------------- get dirs --------------------------------------------#
opendir HERE, '.' or die;
my @dirs = sort grep !/^\.\.?$/, 
		grep -d, 
		readdir HERE;
closedir HERE;


print <<EOT;
<html>
<head>
<script language=JavaScript1.2>function refresh(){    window.location.reload( false );}</script>
</head>
<body>
<script language="JavaScript" src=$js_loc></script>
<link rel="stylesheet" type="text/css" href=$css_loc>
EOT

print "<p class=top><a href=\"javascript:refresh()\"><img src='".$host."img/refresh.gif' title='Refresh'></a>  Test results of:  $today</p>";
print "<table><tr>\n";
print "<th class='test_run'>Test Run</th>\n";
print "<th class='masterlog'>Log</th>\n";
print "<th class='version'>Load Version</th>\n";
print "<th class='arg'>Arguments</th>\n";
print "<th class='result'>Results (P/F/S)</th></tr>\n";


for my $dir ( @dirs )
{
open VERSION, "$dir/version.txt";	
my $version = <VERSION>;	
close VERSION;
chomp $version;
open ARGS, "$dir/args";	
my $args = <ARGS>;	
close ARGS;
chomp $args;

my @results = '';
print "<tr><td class='dir'><a href='./$dir'>$dir</a></td>";
print "<td align='center' id='".++$id."' onMouseover=\"over(".$id.", '".$host."')\" onMouseout=\"out(".$id.", '".$host."')\"><a href='./$dir/masterlog.cgi'><img id='".++$id."' src='".$host."img/M.png' alt='Master Log'></img></a></td>";
print "<td align='center'>$version</td>";
print "<td align='center'><font class='arg_c'>$args</font></td>";

if( -f "$dir/result.txt" )	{
	open MASTER, "$dir/result.txt";
	while( <MASTER> )	{
		push @results, $_;
	}
	close MASTER;

	if( -f "$dir/masterlog.html") {
		print "<td align='center'><font class='pass'>$results[1]</font> / <font class='fail'>$results[2]</font> / <font class='skip'>$results[3]</font></td>\n";
	}else{
		my $tmp_result = &read_masterlog($dir);
		my ($nbr_passed, $nbr_failed, $nbr_skipped) = split(/\|/, $tmp_result);
		if($current_processing) {
			print "<td class='pending_1' align='center'>pending<blink>...</blink><br/>so far:&nbsp<font class='pass_1'>$nbr_passed</font>/<font class='fail_1'>$nbr_failed</font>/<font class='skip_1'>$nbr_skipped</font><br/>processing:<font class='current_p'>$current_processing</font><br/>time Left:<font class='time'>$time_left</font></td>\n";
		}else{
			print "<td class='pending_1' align='center'>pending<blink>...</blink><br/>so far:&nbsp<font class='pass_1'>$nbr_passed</font>/<font class='fail_1'>$nbr_failed</font>/<font class='skip_1'>$nbr_skipped</font></td>\n";
		}
	}
}else{
	if( -f "$dir/masterlog.txt") {
		my $tmp_result = &read_masterlog($dir);
		my ($nbr_passed, $nbr_failed, $nbr_skipped) = split(/\|/, $tmp_result);
		if($current_processing) {
			print "<td class='pending_1' align='center'>pending<blink>...</blink><br/>so far:&nbsp<font class='pass_1'>$nbr_passed</font>/<font class='fail_1'>$nbr_failed</font>/<font class='skip_1'>$nbr_skipped</font><br/>processing:<font class='current_p'>$current_processing</font><br/>time Left:<font class='time'>$time_left</font></td>\n";
		}else{
			print "<td class='pending_1' align='center'>pending<blink>...</blink><br/>so far:&nbsp<font class='pass_1'>$nbr_passed</font>/<font class='fail_1'>$nbr_failed</font>/<font class='skip_1'>$nbr_skipped</font></td>\n";
		}
	}else{
		print "<td class='pending' align='center'>pending<blink>...</blink></td></tr>\n";
	}
}
}
print "</table></body></html>\n";
# ---------------------------------------------------------------------------------------------#


sub read_masterlog {
my $master_dir = shift;

my @tests = '';
open MASTER, "$master_dir/masterlog.txt" or die $!;
while(<MASTER>)
{
	if( /A total of (\d+) tests should be executed/ ) {	
		$test_case_left = $1;

	}elsif(( /All tests should be completed by (.*)\./) or ( /Estimated time of regression completion is (.*)\./)) {
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

			$time_left .= $yr."yr " if ($yr gt '0');
			$time_left .= $mth."mth " if ($mth gt '0');
			$time_left .= $day."day " if ($day gt '0');
			$time_left .= $hour."h " if ($hour gt '0');
			$time_left .= $min."m " if ($min gt '0');
			$time_left .= $sec."s" if ($sec gt '0');

			$time_left = "FINISHED" if(!$time_left);
		}

	}elsif( /BEGIN ::TestDB::Test([^:]+)::(\S+)/ ) {	
		$cleanupFailed = 0;		
		$setupFailed   = 0;		
		$caseFailed    = 0;		

		if($1 eq 'Suite') {
			$current_suite = $2;
			$suite_status = 'PROCESSING';
		
		}elsif($1 eq 'Case') {
			$current_case = $2;
		}
		$current_task = $1;
		push @tests, [ $1, $2 ];

	}elsif( /This test (\S+) should take about (\d+)/ ) {	
		my( $test ) = grep $_->[1] eq $1, 
						  grep $_->[0] eq 'Case', 
						  reverse @tests;
			$test->[2] = $2;

		}elsif( /TestCase (\S+) took a total of (\d+)/ )	{	
			my( $test ) = grep $_->[1] eq $1, 
						  grep $_->[0] eq 'Case', 
						  reverse @tests;
			$test->[3] = $2;

		}elsif( /Test(\S+) (\S+) should take about (\d+)/ ) {	
			my( $test ) = grep $_->[1] eq $2, 
						  grep $_->[0] eq $1, 
						  reverse @tests;
			$test->[2] = $3;

		}elsif( /Test(\S+) (\S+) took a total of (\d+)/ ) {	
			my( $test ) = grep $_->[1] eq $2, 
						  grep $_->[0] eq $1, 
						  reverse @tests;
			$test->[3] = $3;

		}elsif( /RESULT: (\w+): Test Case (\S+)/i ) {
			my( $test ) = grep $_->[1] eq $current_case, 
						  grep $_->[0] eq 'Case', 
						  reverse @tests;
			if(! $test) {
				my ($tmp, $caseName) = split(/\_/, $current_case);
				($test) = grep $2 =~ m/$current_suite/i,  
						  grep $2 =~ m/$caseName/i, 
						  reverse @tests;
			}	
			$test->[4] = $1 if(! $test->[4]);

			if($1 ne 'PASSED') {
				my( $test )	= grep $_->[1] eq $current_suite, 
							  grep $_->[0] eq 'Suite', 
							  reverse @tests;
				if($l eq 'SKIPPED') {
					$test->[4]    = 'SKIPPED';
				}else{
					$test->[4]    = 'FAILED';
					$suite_status = 'FAILED';
				}
			}

		}elsif( /CRIT: (.*)/ ){
			if( $current_task eq 'SuiteCleanup' ) {
				$cleanupFailed = 1;
				my( $test ) = grep $_->[1] eq $current_suite, 
							  grep $_->[0] eq 'SuiteCleanup', 
							  reverse @tests;
				$test->[4]  = 'FAILED';
			}elsif( $current_task eq 'SuiteSetup' ) {
				$setupFailed = 1;
				my( $test ) = grep $_->[1] eq $current_suite, 
							  grep $_->[0] eq 'SuiteSetup', 
							  reverse @tests;
				$test->[4]  = 'FAILED';
			}elsif( $current_task eq 'Case' ) {
				my( $test ) = grep $_->[1] eq $current_case, 
							  grep $_->[0] eq 'Case', 
							  reverse @tests;
				$test->[4]  = 'FAILED';
			}
			my( $test )	= grep $_->[1] eq $current_suite, 
						  grep $_->[0] eq 'Suite', 
						  reverse @tests;
			$test->[4]	  = 'FAILED';
			$suite_status = 'FAILED';

		}elsif( /END ::TestDB::TestSuiteCleanup::(\S+)/ ) {
			my( $test ) = grep $_->[1] eq $1, 
						  grep $_->[0] eq 'SuiteCleanup', 
						  reverse @tests;
			$test->[4] = 'PASSED' if ( !$cleanupFailed );

		}elsif( /END ::TestDB::TestSuiteSetup::(\S+)/ ) {
			my( $test ) = grep $_->[1] eq $1, 
						  grep $_->[0] eq 'SuiteSetup', 
						  reverse @tests;
			$test->[4] = 'PASSED' if ( !$setupFailed );

		}elsif( /END ::TestDB::TestSuite::(\S+)/ ) {
			my( $test ) = grep $_->[1] eq $1, 
						  grep $_->[0] eq 'Suite', 
						  reverse @tests;
			$test->[4] = 'PASSED' if ($suite_status ne 'FAILED');
		}
	}
	close MASTER;
	# ============================ #
	# Calculate the 'PASS/FAILED's #	
	# ============================ #
	my $passed = 0;
	my $failed = 0;
	my $skipped = 0;

	for( grep $_->[0] ne 'Suite', @tests ){
		
		if( $_->[4] eq 'FAILED' ) {
			$failed++;
		}elsif( $_->[4] eq 'PASSED' ) {
			$passed++;
		}elsif( $_->[4] eq 'SKIPPED' ) {
			$skipped++;
		}elsif( $_->[4] eq '' ) {
			$current_processing = $_->[1];
		}
		
	}
	$passed  ||= '0';
	$failed  ||= '0';
	$skipped ||= '0';

	return $passed."|".$failed."|".$skipped;

}


sub get_time_left {
	my $finish_string = shift;

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
		
		$time_left .= $yr." Year " if ($yr gt '0');
		$time_left .= $mth." Month " if ($mth gt '0');
		$time_left .= $day." Day " if ($day gt '0');
		$time_left .= $hour." Hour " if ($hour gt '0');
		$time_left .= $min." Minutes " if ($min gt '0');
		$time_left .= $sec." Seconds " if ($sec gt '0');
		
		$time_left = "FINISHED" if(!$time_left);
		
	}
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

