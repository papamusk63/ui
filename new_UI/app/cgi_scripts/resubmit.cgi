#!/usr/bin/perl -w

use CGI qw(:standard);
use IO::File;
use Net::Telnet ();
use POSIX qw(strftime);
print header();

sub url_decode ($) {
  my $str = shift;
     $str =~ tr/+/ /;
     $str =~s /%([0-9a-z]{2})/chr(hex($1))/ieg;
  return $str;
}

my $wait = 1;
# Read in text
$ENV{'REQUEST_METHOD'} =~ tr/a-z/A-Z/;
#local ($buffer, @pairs, $pair, $name, $value, %FORM);
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
   # print ("name $name value $value <BR>\n");
}

my $host_ip  = $FORM{host_ip};
my $myhost = $FORM{myhost};
my $host  = $FORM{host};
   #recieving arguments from the textarea on masterlog page
my $arguments  = $FORM{arguments};
   #user email address if authenticated
my $user  = $FORM{user};
   #path to the results
my $test_dir  = $FORM{test_dir};
my $priority;
   #the jobid of new run ex/ P3n-2016.Mar26.08:03:25.ipd.regress
my $new_JobID;
my $t = new Net::Telnet ($host_ip);
$t->login($host, "tigris") or print  "can't logon to $host";

if ($arguments =~ /customGash/) {
#looking into inprogress file to get JobID of finished run
#we need for defying priority of a new run
   my $ifh = new IO::File;
      if (!defined($ifh->open("< /$test_dir/inprogress"))) {
           die "Can not open open file";
      }
        my $line;
        my $path;
        while (defined($line = <$ifh>))
        {
               chomp $line;
               my @elems;
               if ( $line =~ m/JobID / )
               {
                   @elems =  split (' ', $line);
                   my $old_JobID = $elems[4];
                   $priority = (split /n/, $old_JobID)[0];
               }
         }
    $now_string = strftime "%Y.%b%d.%H:%M:%S", gmtime();
       #creating JobID of new run
    $new_JobID = "${priority}n-$now_string-$$.$user";
    $t->cmd("cd /$host/jobs/");
    $t->cmd("mkdir $new_JobID");
       #copying customGash files from resuts_directory to jobs_directory
    $t->cmd("cp /$test_dir/{customGash.tar.Z,version.txt} /$host/jobs/$new_JobID/");

       #creating args and priority files in jobs_directory
    my $argsfile = "/$host/jobs/$new_JobID/args";
    my $priorityfile = "/$host/jobs/$new_JobID/priority.txt";
    $t->cmd("echo $arguments >  $argsfile");
    $t->cmd("echo $priority >  $priorityfile");
    $regress_url = "/home/$host/ws/gash/global/bin/";
    $t->cmd("cd $regress_url");
       #regress command
    my $command = "/usr/global/bin/regress -testbed $host $arguments -notify $user";
    $t->cmd("$command");
    $t->cmd("chmod -R 777 /$host/jobs/$new_JobID");

 } else {

    $regress_url = "/home/$host/ws/gash/global/bin/";
    $t->cmd("cd $regress_url");
    my $command = "/usr/global/bin/regress -testbed $host $arguments -notify $user";
    $t->cmd("$command");

 }
# redirect back to the jobs page
print "<META http-equiv=\"REFRESH\" content=\"$wait; url=http://$myhost/new_UI/jobs\">";
