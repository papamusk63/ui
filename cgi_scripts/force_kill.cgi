#!/usr/bin/perl -w

###########################################################################
#
# File Name:    force_kill.cgi
#
# Author:       Sean Yang
# Created:      Nov 01, 2005
# Modified:	Aug 15, 2007
#
# Version:      2.0
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

$t = new Net::Telnet ($host) or print "<font color=red>can't telnet $host: $!</font><br>";
$t->login($host, "tigris") or print "<font color=red>can't login $host: $!</font><br>";

# the id ex/ P2n-2009.Mar26.08:03:25.ipd.regress
my $id = $FORM{testid};
#my $path = $FORM{entry};
my $path = "/$host";
my $result_id = $FORM{resultid};

my $dead = 0;
my $stop = 0;

$t->cmd("rm -rf /$host/jobs/$id") if $id;
my @fbs = `ps -ef | grep runregress.sh`;
my @gbs =  `ps -ef | grep -P "bin/master|pygash|pip" | grep -vP "callmaster|runregress|grep"`;
my $log = "/var/log/regressd.log";

for (@gbs) {
    print ">>GBS$_<BR>";
    if (/$result_id/) {
        print "Matching ... $result_id<BR>";
        my @parts = split /(\s+)/, $_;
        my $pid = $parts[2];
        print "kill -HUP $pid<BR>";
        $t->cmd("kill -HUP $pid") or print "can't kill: $!<BR>";
        $stop = 1;
    }
}

if (!$stop) {
    for (@fbs) {
        print ">>FBS$_<BR>";
        if (/$id/) {
            print "Matching ... $id<BR>";
            my @parts = split /(\s+)/, $_;
            my $pid = $parts[2];
            print "kill -2 `ps -C tail --ppid $pid -opid=` $pid<BR>";
            $t->cmd("kill -2 `ps -C tail --ppid $pid -opid=` $pid") or print "can't kill: $!<BR>";
        }

        $pygash_tmp = "/tmp/pygash/bin/pygash";
        if (index($_, $pygash_tmp) != -1) {
          print "Trying to kill pygash completely";
          my @parts = split /(\s+)/, $_;
          my $pid = $parts[2];
          print "kill -2 `ps -C tail --ppid $pid -opid=` $pid<BR>";
          $t->cmd("kill -2 `ps -C tail --ppid $pid -opid=` $pid") or print "can't kill: $!<BR>";
        }
    }
}

if (!$stop) {
    my @tbs = `ps -ef | grep regress_live_patch.sh | grep -v "grep"`;
    for (@tbs) {
        print ">>TBS$_<BR>";
        my @parts = split /(\s+)/, $_;
        my $pid = $parts[2];
        print "kill -2 `ps -C tail --ppid $pid -opid=` $pid<BR>";
        $t->cmd("kill -2 `ps -C tail --ppid $pid -opid=` $pid") or print "can't kill: $!<BR>";
    }
}


my $reason = "$id Force killed";
$t->cmd("cd $path");
$t->cmd("echo $reason > kill_reason");

#
# log the IP and Machine name of the killer
#
open (LOG, ">>$log") or print "<font color=red>Can not open file $log</font><BR>";

my $output = `hostname -f`;
print "NSLOOKUP: $output<BR>";

($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime(time);
printf LOG "[%4d-%02d-%02d %02d:%02d:%02d]: ", $year+1900,$mon+1,$mday,$hour,$min,$sec;
print LOG "$host_ip KILLED: $id : -REASON: $reason -LEVEL: FORCE\n";

close LOG;

$t->cmd("chmod 777 $path/kill_reason");

#
# end
#
my $wait = 8;
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
