#!/usr/bin/perl -w

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

my $old_fh = select(STDOUT);
$| = 1;
select($old_fh);

print "logging into $host linux <BR>";

$t = new Net::Telnet (Timeout => 90);
$t->open($host);
#$t = new Net::Telnet ($host) or print "can't telnet $host: $!<br>";
$t->login($host, "tigris") or print "can't login $host: $!<br>";

$t->cmd("cd /$host/ws/gash/bin");
print "powering off DUTs for $host............wait<BR>";
$t->cmd("powercycle.tcl $host off");
print "done <BR>";
my $wait = 2;

# redirect back to the jobs page
print "<META http-equiv=\"REFRESH\" content=\"$wait; url=http://$host_ip/new_UI/jobs\">";



