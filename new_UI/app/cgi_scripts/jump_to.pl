#!/usr/bin/perl


=head1 NAME

jump_to.pl - moves a test to another position of the waiting queue

=head1 SYNOPSIS

jump_to.pl  [ <arguments> ]

=head1 DESCRIPTION

Moves your test to another position of the waiting queue.

=head1 ARGUMENTS

=over 4

=item -test

The test name, can be copied from /testbed/jobs/ 

=item -position

Supported values are "0","1","2"... 

=item -help

Print a brief help message


=cut




use strict;
use warnings;

use Getopt::Long;
use Pod::Usage;

my $hostname = $ENV{HOSTNAME};
my @testbed = split /\./, $hostname;
my ($position, @test, @jobs);
GetOptions ( 	'help|?' => sub{ pod2usage(1) },
		'test=s' =>\@test,
		'position=s' => \$position ) or pod2usage(1);

get_queue();

if ($position eq '0') {
	insert($jobs[0]);
}else{
	insert($jobs[$position]);
}


sub get_queue {
	my $jobs_dir = "/$testbed[0]/jobs/";
	opendir JOBS, $jobs_dir or die $!."\n";
        @jobs = grep /200.*/, readdir JOBS;
        closedir JOBS;
	print "<< $_ >>\n" for sort {$a <=> $b } @jobs;
}

sub insert {
	my $test_b = shift;
	print $test_b;
	my $time_b = get_time($test_b);
	my ($hour_b, $min_b, $sec_b) = split /\:/, $time_b;
	my $new_time;
	if( $sec_b ){
		if ($sec_b lt '59') { 
			my $sec_new = $sec_b + 1;
			$sec_new = "0".$sec_new if ($sec_new lt '10');
			$new_time = $hour_b.":".$min_b.":".$sec_new;
		}else{
			my $min_new = $min_b + 1;
	                $min_new = "0".$min_new if ($min_new lt '10');
			my $hour_new = $hour_b + 1;
                	$hour_new = "0".$hour_new if ($hour_new lt '10');
			$new_time = $min_b lt '59' ? $hour_b.":".$min_new.":00" : $hour_new.":00:00";
		}
	}else{
		 my $min_new = $min_b + 1;
                 $min_new = "0".$min_new if ($min_new <= 9);
                 my $hour_new = $hour_b + 1;
                 $hour_new = "0".$hour_new if ($hour_new lt '10');
                 $new_time = $min_b lt '59' ? $hour_b.":".$min_new : $hour_new.":00";
	}
	my @parts = split /\./, $test[0];
	$parts[2] = $new_time;
	my $new_test = join ".", @parts;
	`mkdir $new_test`;
#	`mkdir /$testbed[0]/jobs/$new_test`;
#	`cp -r /$testbed[0]/jobs/$test[0]/ /$testbed[0]/jobs/$new_test/`;
	
}

sub get_time {
	my $test = shift;
	my @parts = split /\./, $test;
	my $time = $parts[2];
	return $time;
}
