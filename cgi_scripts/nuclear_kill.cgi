#!/usr/bin/perl -w

###########################################################################
#
#  NUCLEAR KILL BUTTON
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
my $name;
my $value;

foreach $pair (@pairs)
{
    ($name0, $value0) = split(/=/, $pair);
    $value0 =~ tr/+/ /;
    $value0 =~ s/%(..)/pack("C", hex($1))/eg;
    $name=url_decode($name0);
    $value=url_decode($value0);
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
my $jobid  = $FORM{testid};
my $reason  = $FORM{reason};
my $testdir  = $FORM{testdir};
my $result_id  = $FORM{resultid};

$reason = "N/A" if (!$reason);

my $wait = 0;

if (($name eq "OK") && ($value eq "OK") ) {
	#creates a file, which store kill reason
		open FILE, ">/$host/$testdir/$result_id/DoNotParse2regressionDb.txt" or die "Couldn't open file: $!";
		print FILE "$reason\n";
		close FILE;
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
                $t->cmd("kill -2 `ps -C tail --ppid $pid -opid=` $pid") or print "can't kill: $!<BR>";
                wait_kill ($pid, 5);
            }

            $pygash_tmp = "/tmp/pygash/bin/pygash";
            if (index($_, $pygash_tmp) != -1) {
              print "Trying to kill pygash completely";
              my @parts = split /(\s+)/, $_;
              my $pid = $parts[2];
              $t->cmd("kill -2 `ps -C tail --ppid $pid -opid=` $pid") or print "can't kill: $!<BR>";
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
    }

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
