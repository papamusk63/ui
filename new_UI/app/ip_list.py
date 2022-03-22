<?php

##########################################################################
# FileName - ip_list.php
# Common ip functions
##########################################################################

##########################################################################
# Name - getIPs
##########################################################################
function getIPs() {
	global $ip_list;
    $regress_file = "/usr/global/bin/regress";
    $lines = file($regress_file);
    $record = 0;
    foreach ($lines as $line) {
        $line = rtrim($line);
        if (preg_match('/function SetFtpParams/', $line)) {
            $record = 1;
        }
        if ($record) {
            if (preg_match('/esac/', $line)) {
                return;
            }
            if (preg_match('/(\S+)\)/', $line, $matches_tb)) {
                $tb = $matches_tb[1];
            }
            if (preg_match('/FTP_SERVER=(.*)\;\;/', $line, $matches_ip)) {
                $ip = $matches_ip[1];
                $ip_list[$tb] = $ip;
            }
        }
    }
}

##########################################################################
# Name - getIPs
# Description - fills many structures with the data found in
# /usr/global/bin/regress
# returns - nothing but filled in structures
##########################################################################
function getIPs_f() {
    global $test_beds;
    global $ip_list;
    global $bed_types;
    global $bed_locales;
    global $kan_list;
    global $mtv_list;
    global $ant_list;

    $regress_file = "/usr/global/bin/regress";
	$lines = file($regress_file);
    $record = 0;
    foreach ($lines as $line) {
        $line = trim($line);
        if (preg_match('/^#/', trim($line))) {
            continue;
        }
        if (preg_match('/function SetFtpParams/', $line)) {
            $record = 1;
        }
        if ($record) {
            if (preg_match('/esac/', $line)) {
                return;
            }
            # ssteg - there was a bug here, it used to pick out the function line too
            if (preg_match('/(.*)\)$/', $line, $matches_tb)) {
                if (strpos($matches_tb[1], '(') === false) {
                    $tb = $matches_tb[1];
                    $test_beds[] = $tb;
                }
            } else if (preg_match('/bed_locale=(\S+)/', $line, $matches_locale)) {
                $bed_locale = $matches_locale[1];
                $bed_locales[$tb] = $bed_locale;
            } else if (preg_match('/bed_type=(\S+)/', $line, $matches_type)) {
                $bed_type = $matches_type[1];
                $bed_types[$tb] = $bed_type;
            } else if (preg_match('/FTP_SERVER=(.*)\;\;/', $line, $matches_ip)) {
                $ip = $matches_ip[1];
                $ip_list[$tb] = $ip;
                if (preg_match('/^138.120/', $ip)) {
                    $kan_list[$tb]=$ip;
                } else if (preg_match('/^172.22/', $ip)) {
                    $mtv_list[$tb]=$ip;
                } else if (preg_match('/^138.203/', $ip)) {
                    $ant_list[$tb]=$ip;
                }
            }
        }
    }
}

?>
