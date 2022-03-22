#!/usr/bin/perl -w
###################################1#####################################################
# index.cgi -- 

# This script is supposed to log on all spr ftp servers, check for all test results 
# and create a tree menu on a web page of all results.
# 
#########################################################################################
# Version: 1.0 
# Sean Yang
# Jan 15, 05
#########################################################################################
use Net::FTP;
use Net::Ping;
print "Content-type: text/html\n\n";
my $ip_page = "#";
#my @testBedList;
#######################################################################################
# ------------------ Configure the ip address page url here (OPTIONAL) -------------- #
#######################################################################################
$ip_page = "http://rdnweb.ca.alcatel.com/twiki/bin/view/Kanata7750/TestBedIP";
#######################################################################################
my %testbed_ip;
ip_list();


my @testBedList;
my $testBed_loc = "/usr/global/regression/";
get_test_bed_list();
#======================================================================================#
#******************** NOTHING MUST BE CHANCED STARTS HERE *****************************#
#======================================================================================#

# list that stores output info of spr ftp servers 
#
my %testbeds;
my $tree_nodes_file = "tree_nodes.js";

getYears($_) for (@testBedList);
unlink("tree_nodes.js") if (-e $tree_nodes_file);

open(FILE, ">$tree_nodes_file");
print FILE "var TREE_NODES = [\n";

foreach my $testBed (sort @testBedList) {
	print $testBed;
	my $yrParentCount = 0;
	my $mthParentCount = 0;
	my $upper = $testBed;
	$upper =~ tr/a-z/A-Z/;
	if ($ip_page eq "#") {
		print FILE "\t[\"".$testBed."\", \"\", \"right\",\n";	
	}else{
		print FILE "\t[\"".$testBed."\", \"".$ip_page."#Test_Bed_".$upper."\", \"right\",\n";
	}
	foreach my $yr (sort keys %{$testbeds{$testBed}}) {
		print FILE "\t\t[\"".$yr."\", null, null,\n";
		foreach my $mth (sort keys %{${$testbeds{$testBed}}{$yr}}) {
			print FILE "\t\t\t[\"".$mth."\", null, null,\n";
			foreach my $day (sort @{${${$testbeds{$testBed}}{$yr}}{$mth}}) {
				print FILE "\t\t\t\t[\"".$day."\", \"http://".$testbed_ip{$testBed}."/results/".$yr."/".$mth."/".$day."/\", \"right\"],\n";
			}
			print FILE "\t\t\t],\n";
		}
		print FILE "\t\t],\n";
	}
	print FILE "\t],\n";
}
print FILE "];";


sub getYears() {
	my $tb = shift;
	
	my %years;
	my $host = $testbed_ip{$tb};

	# connect to the FTP server
	#
	$ftp = Net::FTP->new($host) or die "Can't ftp to $host: $!<br>";
	$ftp->login($tb, "tigris"); 
	my $newDir = "../../".$tb."/results";
	$ftp->cwd($newDir); 
	my @details = $ftp->dir() or die "Can't get file list: $!<br>";
	foreach my $detail(@details) {
		my ($permission, @tmp) = split(/\s/, $detail);
		my $entry = pop @tmp;
		
		if($permission =~ m/d/) {
			my %months;
			my $ref = &getMonths($entry, %months);
			$years{$entry} = $ref;  
		}
	}
	
	foreach $y (keys %years) {
		if(!(($y eq "2004") or ($y eq "2005"))) {
			delete $years{$y};
		}
	}
	$testbeds{$tb} = \%years;
	$ftp->quit;
}



sub getMonths() {
	my $year = shift;
	my %months = shift;
	my $newDir = $year;
	
	my %toReturn;
	$ftp->cwd($newDir);
	my @entries = $ftp->ls() or return "Can't get file list: $!<br>";

	foreach my $month (@entries) {
		my @days = '';
		my $ref = &getDays($month, @days);
			
		$months{$month} = $ref;
	}
	foreach $m (keys %months) {
		if(!($m eq "")) {
			$toReturn{$m} = $months{$m};
		}else{
			if ($m eq "") {
				delete $months{$m};
			}
		}
	}

	$ftp->cwd("../"); 
	return \%toReturn;
}


sub getDays() {
	my $month = shift;
	my @days = shift;
	my $newDir = $month;
	
	my @toReturn;
	$ftp->cwd($newDir); 
	my @entries = $ftp->ls() or die "Can't get file list: $!<br>";
	foreach my $day (@entries) {
		push @days, $day; 
	}
	
	$ftp->cwd("../"); 
	
	foreach  (@days) {
		if(!($_ eq "")) {
			unshift @toReturn, $_;
		}
	}	
	return \@toReturn;
}

sub check_status {
        my $tb = shift;
        my $host = $testbed_ip{$tb};
        $p = Net::Ping->new();
        $p->ping($host) or return "Can't ping $host: $!<br>";
        $p->close();

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
sub get_test_bed_list {
        opendir BEDS, $testBed_loc or die $!."\n";
        my @testBed_status = grep /[a-zA-Z]/, readdir BEDS;
        closedir BEDS;

        for my $status (@testBed_status) {
		next if ($status =~ /LOCALE/);
                opendir BED, $testBed_loc."/".$status or die $!."\n";
                my @tbs = grep /[a-zA-Z]/, readdir BED;
                foreach my $bed (sort @tbs) {
                        next if ($bed !~ /krtb/);
			my $server_down = check_status($bed);
			if ($server_down) {
                        	next if ($server_down =~ /$bed/);
			}
			push @testBedList, $bed;
                }
                closedir BED;
        }
}

close (FILE);

