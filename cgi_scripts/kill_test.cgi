#!/usr/bin/perl -w

###########################################################################
#
# File Name:    kill_test.cgi
#
# Author:       Sean Yang
# Created:      Nov 01, 2005
# Modified:	    Apr 25, 2008
#               ssteg - restructured Mar 30 2009, didn't work properly
#
# Version:      2.1
# Description:  script that enables regression job killing from html page
#
###########################################################################

use CGI qw(:standard);
use Net::Telnet ();
print header();

sub url_decode ($) {
  my $str = shift;
  $str =~ tr/+/ /;
  $str =~s /%([0-9a-z]{2})/chr(hex($1))/ieg;
  return $str;
}

sub wait_kill {
    my $pid = $_[0];
    my $maxwait = $_[1];
    my $exefile = "/proc/$pid/exe";
    my $count = 0;
    while ($count <= $maxwait) {
        if (-e $exefile) {
            sleep 1;
            $count++;
        } else {
            print ("$pid killed in $count seconds <BR>\n");
            return "done";
        }
    }
    print ("<font color=red>didn't succeeded to kill $pid in $maxwait seconds </font><BR>\n");
    return "notdone";
}



# Read in text
$ENV{'REQUEST_METHOD'} =~ tr/a-z/A-Z/;
local ($buffer, @pairs, $pair, $name, $value, %FORM);
if ($ENV{'REQUEST_METHOD'} eq "GET")
{
    $buffer = $ENV{'QUERY_STRING'};
}
# Split information into name/value pairs
@pairs = split(/&/, $buffer);
my @testids;
foreach $pair (@pairs)
{
    ($name0, $value0) = split(/=/, $pair);
    $value0 =~ tr/+/ /;
    $value0 =~ s/%(..)/pack("C", hex($1))/eg;
    my $name=url_decode($name0);
    my $value=url_decode($value0);
    $FORM{$name} = $value;
    if($name =~ m/testid/) {
        push(@testids, $value);
    }
    #print ("name $name value $value <BR>\n");
}
my $host_ip = $FORM{host_ip};
my $host  = $FORM{host};

$t = new Net::Telnet ($host) or print "can't telnet $host: $!<br>";
$t->login($host, "tigris") or print "can't login $host: $!<br>";

# the jobid ex/ P2n-2009.Mar26.08:03:25.ipd.regress
my $jobid  = $FORM{testid};
# one of remove, immediate, etc.
my $level  = $FORM{level};
# user typed reason
my $reason  = $FORM{reason};
# the path
my $testdir  = $FORM{testdir};
# the results directory without the path ex/ 11:23:57.regressiondb
my $result_id  = $FORM{resultid};
# the current suite, on the GUI page, could be old if no refresh
my $current_suite  = $FORM{currentSuite};
# the current test, on the GUI page, could be old if no refresh
my $current_test  = $FORM{currentTest};
# user email address if authenticated
my $user  = $FORM{user};
# what test to stop in the future, note cannot stop current running test
my $afterTestName  = $FORM{aftertestname};
# where to re-submit the run
my $onTestbed  = $FORM{ontestbed};

$reason = "N/A" if (!$reason);
my $wait = 0;
my $log = "/var/log/regressd.log";
my $kill_reason = "";

if ($level eq "remove") {
    $t->cmd("rm /$host/$testdir/$result_id/deferredKill_suite") if (-e "/$host/$testdir/$result_id/deferredKill_suite");
    $t->cmd("rm /$host/$testdir/$result_id/deferredKill_test") if (-e "/$host/$testdir/$result_id/deferredKill_test");
    $t->cmd("rm /$host/$testdir/$result_id/deferredKill") if (-e "/$host/$testdir/$result_id/deferredKill");
    print "Removing deferred regression kill...";
    # attain the pid of the gash session and send it a signal to go look at the deferr files
    my @fbs =  `ps -ef | grep -P "bin/master|pygash|pip" | grep -vP "callmaster|runregress|grep"`;
    for (@fbs) {
        print ">>$_<BR>";
        if (/$testdir/) {
                print "Matching .. $testdir<BR>";
            my @parts = split /(\s+)/, $_;
            my $pid = $parts[2];
            $t->cmd("kill -10 $pid") or print "can't kill: $!<BR>";
        }
        $pygash_tmp = "/tmp/pygash/bin/pygash";
        if (index($_, $pygash_tmp) != -1) {
          print "Trying to kill pygash completely";
          my @parts = split /(\s+)/, $_;
          my $pid = $parts[2];
          $t->cmd("kill -10 $pid") or print "can't kill: $!<BR>";
        }
    }
} else {
    # if there are any kill files, just remove them now for all cases below
    $t->cmd("rm /$host/$testdir/$result_id/deferredKill_suite") if (-e "/$host/$testdir/$result_id/deferredKill_suite");
    $t->cmd("rm /$host/$testdir/$result_id/deferredKill_test") if (-e "/$host/$testdir/$result_id/deferredKill_test");
    $t->cmd("rm /$host/$testdir/$result_id/deferredKill") if (-e "/$host/$testdir/$result_id/deferredKill");
    if ($level eq "immediate") {
        # procedure for immediate is, check is gash running (callmaster) and if not signal runregress
        # to halt. If callmaster is running signal runregress to stop and kill the callmaster
        print "echo $user - $reason > /$host/$testdir/$result_id/kill_9<BR>";
        $kill_reason = "Immediate kill with reason: $reason";
        $t->cmd("echo '$user - $reason|$current_suite::$current_test' > /$host/$testdir/$result_id/kill_9");
        # time for the regression to be wrapped up page to stick
        $wait = 3;
        $callMaster = 0;
        # kill gash if it is running yet
        my @fbs =  `ps -ef | grep -P "bin/master|pygash|pip" | grep -vP "callmaster|runregress|grep"`;
        for (@fbs) {
            print ">>$_<BR>";
            if (/$testdir/) {
             print "Matching .. $testdir<BR>";
                # only signal runregress if we didn't find a callmaster
                $callMaster = 1;
                my @parts = split /(\s+)/, $_;
                my $pid = $parts[2];
                $t->cmd("kill -9 $pid") or print "can't kill: $!<BR>";
                wait_kill ($pid, 5);
            }

              $pygash_tmp = "/tmp/pygash/bin/pygash";
              if (index($_, $pygash_tmp) != -1) {
                print "Trying to kill pygash completely";
                my @parts = split /(\s+)/, $_;
                my $pid = $parts[2];
                $t->cmd("kill -9 $pid") or print "can't kill: $!<BR>";
                wait_kill ($pid, 5);
              }
        }
        # if callmaster was not running, we must signal runregress to die, no choice
        # I don't think that it is possible to ever get in here as the GUI only enables the
        # kill button when the callmaster is running, but just in case I guess
        if ($callMaster eq 0) {
            # signal runregress to stop
            my @mbs = `ps -ef | grep runregress.sh`;
            for (@mbs) {
                if (/$jobid/) {
                        print "$_<BR>";
                    my @parts = split /(\s+)/, $_;
                    my $pid = $parts[2];
                    $t->cmd("kill -HUP $pid") or print "can't kill: $!<BR>";
                    wait_kill ($pid, 5);
                }
            }
        }
    } elsif (($level eq "afterTest") || ($level eq "afterSuite") || ($level eq "afterName") || ($level eq "resumeImmediate") || ($level eq "resumeAfterTest") ) {
        # procedure for all delay type kills below is to create the kill file to trigger gash to stop
        # everything else quitting gracefully should be magic
        if ($level eq "afterSuite") {
            print "echo $user - $reason > /$host/$testdir/$result_id/deferredKill_suite<BR>";
            $t->cmd("echo '$user - $reason|$current_suite' > /$host/$testdir/$result_id/deferredKill_suite");
            $kill_reason = "kill after suite $current_suite with reason: $reason";
        } elsif ($level eq "afterTest") {
            print "echo $user - $reason > /$host/$testdir/$result_id/deferredKill_test<BR>";
            $t->cmd("echo '$user - $reason|$current_suite::$current_test' > /$host/$testdir/$result_id/deferredKill_test");
            $kill_reason = "kill after test $current_suite::$current_test with reason: $reason";
        } elsif ($level eq "resumeImmediate") {
            print "echo $user - immediate $onTestbed > /$host/$testdir/$result_id/deferredKill<BR>";
            $t->cmd("echo 'immediate $onTestbed' > /$host/$testdir/$result_id/deferredKill");
            $kill_reason = "immediate rescheduling with reason: $reason";
        } elsif ($level eq "resumeAfterTest") {
            print "echo $user - nexttest $onTestbed > /$host/$testdir/$result_id/deferredKill<BR>";
            $t->cmd("echo 'nexttest $onTestbed' > /$host/$testdir/$result_id/deferredKill");
            $kill_reason = "rescheduling after test $current_suite::$current_test with reason: $reason";
        } elsif ($level eq "afterName") {
            print "echo $user - $reason > /$host/$testdir/$result_id/deferredKill_test<BR>";
            $t->cmd("echo 'afterNamedTest $afterTestName - $user - $reason' > /$host/$testdir/$result_id/deferredKill_test");
            $kill_reason = "kill after test $afterTestName with reason: $reason";
        }
        if (($level eq "resumeImmediate") || ($level eq "resumeAfterTest") ) {
            $wait = 8;
        }
        # attain the pid of the gash session and send it a signal to go look at the deferr files
        my @fbs =  `ps -ef | grep -P "bin/master|pygash|pip" | grep -vP "callmaster|runregress|grep"`;
        for (@fbs) {
            print ">>$_<BR>";
            if (/$testdir/) {
                    print "Matching .. $testdir<BR>";
                my @parts = split /(\s+)/, $_;
                my $pid = $parts[2];
                $t->cmd("kill -10 $pid") or print "can't kill: $!<BR>";
                wait_kill ($pid, 5);
            }

            $pygash_tmp = "/tmp/pygash/bin/pygash";
            if (index($_, $pygash_tmp) != -1) {
              print "Trying to kill pygash completely";
              my @parts = split /(\s+)/, $_;
              my $pid = $parts[2];
              $t->cmd("kill -10 $pid") or print "can't kill: $!<BR>";
              wait_kill ($pid, 5);
            }

        }
    }
}

# log the IP and Machine name of the killer
open (LOG, ">>$log") or print "<font color=red>Can not open file $log</font><BR>";

my $output = `hostname -s`;
print "$output\n";

($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime(time);
printf LOG "[%4d-%02d-%02d %02d:%02d:%02d]: ", $year+1900,$mon+1,$mday,$hour,$min,$sec;
print LOG "HELP $host_ip $user KILLED: $jobid : -REASON: $reason -LEVEL: $level\n";
close LOG;

my $path="/$host";
$t->cmd("cd $path");
$t->cmd("echo $kill_reason > kill_reason");
$t->cmd("chmod 777 $path/kill_reason");

print "<script type=\"text/javascript\">";
print "var count=$wait;";
print "var counter=setInterval(timer, 1000);";
print "function timer()";
print "{";
print "count=count-1;";
print "if (count <= 0)";
print "{";
print "clearInterval(counter);";
print "return";
print "}";
print "document.getElementById(\"timer\").innerHTML=count + \" secs\";";
print "}";
print "</script>";
print "<h3><img src=http://$host_ip/status/masterlog/img/processing.gif> ... regression to be wrapped up in <span id=\"timer\">$wait secs</span> ... <img src=http://$host_ip/status/masterlog/img/processing.gif></h3>";
# redirect back to the jobs page
print "<META http-equiv=\"REFRESH\" content=\"$wait; url=http://$host_ip/jobs/jobs_index.php\">";
