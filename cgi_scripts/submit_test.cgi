#!/usr/bin/perl -w

use CGI qw(:standard);
use Net::Telnet ();
print header();

my $testbed = param('testbed');
my $version = param('version');
my $notify = param('notify');
my $cc = param('cc');
my $runLevel = param('runLevel');
my $options = param('options');
my $runSuite = param('runSuite');
my $runTest = param('runTest');
my $gashArgs = param('gashArgs');
my $additionals = param('additionals');


my $host_loc = "css/allBeds.css";
my $regress_url;
my $regress_file;
my $command;
my %testbed_ip;

ip_list();


$host = $testbed_ip{$testbed};
$regress_url = "/home/$testbed/ws/gash/global/bin/";
$regress_file = "regress";

if ($version eq "other") {
	my $directory = param('directory');
	$command = "-d ".$directory;
}else{
	my $load = param($version."_loads");
	$command = "-d ".$load;
}
	
$command .= " -notify ".$notify if ($notify);
$command .= " -cc ".$cc if ($cc);
$command .= " -runLevel ".$runLevel;
$command .= " -testbed ".$testbed;
$command .= " ".$options if ($options);
$command .= " -- -runSuite ".$runSuite if ($runSuite);
$command .= " -runTest ".$runTest if ($runTest);
$command .= " ".$gashArgs if ($gashArgs);
$command .= " ".$additionals if ($additionals);

print $command;

$t = new Net::Telnet ($host);
$t->login($testbed, "tigris") or print  "can't logon to $host";

submit_test();

sub submit_test {
	$t->cmd("cd $regress_url");
#	my @regress_help = $t->cmd("./$regress_file $command");
	
	print "<html><head><title>regress help</title></head><body>\n";
	print "<link rel=stylesheet type=text/css href=$css_loc>\n";
#	print "<table border=1><tr><td>\n";
#	print "<table>\n";
#	for (@regress_help) {
#		if ( /\-(\S+)/ ) {
#			print "<tr><td class=helpFontClass>$_</td></tr>\n";
#		}else{
#			print "<tr><td class=tb_content>$_</td></tr>\n";
#		}
#	}
#	print "<tr><td class=tb_content><a href=allBeds.cgi><img src=go_home.gif>Home</a></td></tr>";
#	print "</table></td></tr></table>";
	print "<a href=allBeds.cgi><img src=go_home.gif>Home</a>";
	print "</body></html>";
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

