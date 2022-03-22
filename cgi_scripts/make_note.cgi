#!/usr/bin/perl -w

use CGI qw(:standard);
use POSIX qw/strftime/;
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
my $date = strftime('%b %d %H:%M', localtime);
my $host_ip = $FORM{host_ip};
my $host  = $FORM{host};
my $note  = $FORM{note};
my $user  = $FORM{user};
my $fileName = "";

my $maxNotes = 100;
for ($i = 1 ; $i <= $maxNotes ; $i++) {
    $fileName = "/$host/jobs/note_$i";
    if ( ! -e $fileName ) {
        last;
    }
}

if ($fileName ne "") {
    open FILE, ">$fileName" or die $!."\n";
    print FILE "$date : $user : $note\n";
    close FILE;
}

# also append to bednotes to keep a history
open FILE, ">>/$host/jobs/.bednotes" or die $!."\n";
print FILE "$date : $user : CREATED : $note\n";
close FILE;

print "<META http-equiv=\"REFRESH\" content=\"0; url=http://$host_ip/jobs/jobs_index.php\">";


