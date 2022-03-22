#!/usr/bin/perl -w

use CGI qw(:standard);
use Net::Telnet ();
print header();

my $testbed = param('testbed');
my $css_loc = "css/allBeds.css";
my %testbed_ip;
ip_list();

my $host;
my $regress_url;
my $regress_file;

$host = $testbed_ip{$testbed};
$regress_url = "/home/$testbed/ws/gash/global/bin/";
$regress_file = "regress";

$t = new Net::Telnet ($host);
$t->login($testbed, "tigris");

get_help();

sub get_help {
	$t->cmd("cd $regress_url");
	my @regress_help = $t->cmd("./$regress_file -help");
	
	print "<html><head><title>regress help</title></head><body>\n";
	print "<link rel=stylesheet type=text/css href=$css_loc>\n";
	print "<table border=1><tr><td>\n";
	print "<table>\n";
	for (@regress_help) {
		if ( /\-(\S+)/ ) {
			print "<tr><td class=helpFontClass>$_</td></tr>\n";
		}else{
			print "<tr><td class=tb_content>$_</td></tr>\n";
		}
	}
	print "</table></td></tr></table></body></html>\n";
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

