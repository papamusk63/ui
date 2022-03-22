#!/usr/bin/perl -w

use CGI qw(:standard);
print header();

my $dir = param('dir');
my $refer = param('refer');

open FILE, ">/$dir/failureChecked" or die $!."\n";
close FILE;

print "<META http-equiv=\"REFRESH\" content=\"0; url=$refer\">";
