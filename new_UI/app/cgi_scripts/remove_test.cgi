#!/usr/bin/perl -w

use CGI qw(:standard);
use Net::FTP;
use IO::Handle;
use IO::File;
select(STDOUT); # default
$| = 1;
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
my $currenttest_id;
my $currentact;
my $act;
my $totestbed_alph;
my $totesbed_ip;
my $j = -1;
my $goon = "yes";
foreach $pair (@pairs)
{
    ($name0, $value0) = split(/=/, $pair);
    $value0 =~ tr/+/ /;
    $value0 =~ s/%(..)/pack("C", hex($1))/eg;
    my $name=url_decode($name0);
    my $value=url_decode($value0);
    $FORM{$name} = $value;
    if($name =~ m/mremove/) {
        $act = $value;
    }
    if($name =~ m/totestbed/) {
        $totestbed_alph = $value;
    }
    if($name =~ m/testid/) {
        push(@testids, $value);
        $currenttest_id = $value;
        $j = $j + 1;
    }
    #print ("name $name value $value <BR>\n");
}

my $notestids = "no";
if (!@testids) {
    $goon = "no";
    $notestids = "yes";
}

if ($goon eq "yes") {
if ($act eq "Move") {
    if ($totestbed_alph eq "") {
        print ("<font color=\"#FF0000\" size=\"4\">no testbed to move to</font> <BR>\n");
        $goon = "no";
    } else {
        my $res = `/usr/global/bin/tclsh /usr/global/bin/debugRegressParams -report normal -testbed $totestbed_alph -attribute IP`;
        if ($res eq "") {
            print ("<font color=\"#FF0000\" size=\"4\">$totestbed_alph is not a valid testbed name</font> <BR>\n");
            # sleep 5;
            $goon = "no";
        } else {
            my @elems = split(' ', $res);
            my $ip_addr = $elems[2];
            $totestbed_ip = $ip_addr;
        }
    }
}
}

my $host_ip = $FORM{host_ip};
my $host  = $FORM{host};
#$ENV{CVSROOT} = $host;
my $wait = 0;

if ($goon eq "yes") {

$ftp = Net::FTP->new($host) or return "Can't ftp to $host: $!<br>";
$ftp->login($host, "tigris");

my $i = 0;
foreach (@testids) {
    my $to_rm = "/$host/jobs/$_/";
    if ($act eq "Move") {
        eval {
            if ($totestbed_alph eq $host) {
                # cannot move job to the same testbed
                print ("<font color=\"#FF0000\" size=\"4\">cannot move job $_ from $host to the same bed $totestbed_alph</font> <BR>\n");
                $i = $i + 1;
                $wait = 20;
                next;
            }
            # can the target testbed run this job?
            open FILE, "$to_rm/args" or die "Couldn't open file: $!";
            my $args = <FILE>;
            chomp $args;
            my $args2 = "-testbed $totestbed_alph $args";
            chomp $args2;
            close FILE;
            my $resultString = `/usr/global/bin/regress -debugRegress true $args2`;
            my $hasAbort = `echo "$resultString" | grep "^ABORT:" | wc -l`;
            # this test doesn't work well with customGash case so ignore it if - Can't find customGash control file '/var/www/.customGash'.
            if ((index($resultString, 'find customGash control file')) != -1 ) {
                $hasAbort = 0;
            }
            if ($hasAbort > 0)
            {
                my $reasonAbort = `echo "$resultString" | grep "^ABORT:"`;
                print ("<font color=\"#FF0000\" size=\"4\">cannot move job $_ to $totestbed_alph:<BR>$reasonAbort</font> <BR>\n");
                $i = $i + 1;
                $wait = 20;
                next;
            } else {
                print ("<font color=\"#FF0000\" size=\"4\">OK to move job $_ to $totestbed_alph</font> <BR>\n");
            }
        };
        if ($@) {
            print ("<font color=\"#FF0000\" size=\"4\">move failed: $@</font> <BR>\n");
            $i = $i + 1;
            next;
        }
        eval {
            print "ftp connect to $totestbed_alph <BR>";
            $ftp1 = Net::FTP->new($totestbed_ip, Timeout => 5, Passive => 1, Debug => 3) or die "Can't connect to $totestbed_ip: $@ <BR>";
            $ftp1->login($totestbed_alph, "tigris") or die "Couldn't authenticate.<BR>";
            $ftp1->binary;
            $ftp1->cwd("/$totestbed_alph/jobs");
            $ftp1->mkdir($_);
            $ftp1->site("CHMOD 777 $_");
            $ftp1->cwd($_);
            opendir(DIR, "$to_rm");
            my @files = readdir(DIR);
            foreach my $file (@files) {
                if (not -d $file) {
                    if ($file ne "args") {
                        print "ftp putting $file <BR>";
                        $ftp1->put("$to_rm/$file") or die "Something is wrong here putting $file\n";
                    }
                }
            }
            # move args file - it has to be the last one to be moved
            if (-e "$to_rm/args") {
                print "ftp putting args <BR>";
                $ftp1->put("$to_rm/args") or die "Something is wrong here putting args\n";
            }
            $ftp1->quit();
        };
        if ($@) {
            $goon = "no";
            print ("<font color=\"#FF0000\" size=\"4\">move failed: $@</font> <BR>\n");
            last;
        }
    }
    if ($goon eq "yes") {
        system("rm -rf $to_rm");
    }
    $i = $i + 1;
}
}

if (($goon eq "no") && ($notestids eq "no")) {
    $wait = 10;
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
print "document.getElementById(\"timer\").innerHTML=\"Back in \" + count + \" secs\";";
print "}";
print "</script>";
print "<span id=\"timer\">Back in $wait secs</span><BR>";
print "<META http-equiv=\"REFRESH\" content=\"$wait; url=http://$host_ip/new_UI/jobs\">";



