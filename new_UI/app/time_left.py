import time
from datetime import date, datetime
import math
import re


months_hash = { 
        'Jan' : "01",
        'Feb' : "02",
        'Mar' : "03",
        'Apr' : "04",
        'May' : "05",
        'Jun' : "06",
        'Jul' : "07",
        'Aug' : "08",
        'Sep' : "09",
        'Oct' : "10",
        'Nov' : "11",
        'Dec' : "12" }


def getTimeLeft (a_date: str) -> int: 
        """
        Description - Provides the days between today and the input date
        Input - Date
        Output - Date        
        """
        
        global months_hash
        the_o = time.strftime("%z")
        
        times = a_date.split('/ /') 
        yr = times[5] 
        mth = times[1]
        mth = months_hash[mth]
        day = times[2]
        the_time = times[3]
        

        a_date = f"{yr}-{mth}-{day} {the_time} {the_o}"
        today = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
        diff = time_diff(today, a_date)
        return diff


def date_to_time(a_date: str) -> int: 
        """
        Description - Number of seconds between input date and epoch
        Input - Date as a string
        Output - Number of seconds in integer
        """
        global months_hash
        the_o = time.strftime("%z")
        
        times = a_date.split('/ /') 
        yr = times[5]
        mth = times[1]
        mth = months_hash[mth]
        day = times[2]
        the_time = times[3]

        a_date = "{yr}-{mth}-{day} {the_time} {the_o}"

        time_in_sec = int(datetime.strptime(a_date, '%Y-%m-%d %H:%M:%S %z').timestamp())
        return time_in_sec


def time_diff(date1: str, date2: str) -> int:
        """
        Description - Difference between date 1 and date 2 in seconds
        Input - Date 1 and date 2
        Output - Integer second difference between date 1 and date 2 
        """        
        date1 = int(datetime.strptime(date1, '%Y-%m-%d %H:%M:%S %z').timestamp())
        date2 = int(datetime.strptime(date2, '%Y-%m-%d %H:%M:%S %z').timestamp())
        diff = date1 - date2

        return diff

def append_zero (arg: str) -> str:
        """
        Decription - Adding "0" before the number if it is between 0 and 10. Eg. 4 becomes "04" but 43 remains "43"
        Input - Float
        Output - String
        """
        if ((int(arg) < 10) and (int(arg) >= 0)):
                arg = f"0{arg}"
        
        return arg

def sum_time (tis:int) ->str:
        """
        Decription - Converts seconds into hrs:min:sec
        Input - Float
        Output - String
        """
        tis_h = math.floor(tis / 3600)
        tis_m = math.floor((tis % 3600) / 60)
        tis_s = (tis % 3600) % 60
        tis_h = append_zero(tis_h)
        tis_m = append_zero(tis_m)
        tis_s = append_zero(tis_s)

        return f"{tis_h}:{tis_m}:{tis_s}"


def format_time (string:str) -> int: 
        """
        Decription - Convert time string into seconds
        Input - String
        Output - int
        """
        if (re.search(r'(\d+) days and (\d+) hour', string)):
                matches = re.search(r'(\d+) days and (\d+) hour',string).groups()
                time_in_sec = matches[0]*86400 + matches[1]*3600

        elif (re.search(r'(\d+) hours and (\d+) minute', string)):
                matches =  re.search(r'(\d+) hours and (\d+) minute', string).groups()
                time_in_sec = matches[0]*3600 + matches[1]*60

        elif (re.search(r'(\d+) minutes and (\d+) second', string)):
                matches = re.search(r'(\d+) minutes and (\d+) second', string).groups()
                time_in_sec = matches[0]*60 + matches[1]

        elif (re.search(r'(\d+) second', string)):
                matches = re.search(r'(\d+) second', string).groups()
                time_in_sec = matches[0]

        return time_in_sec

def format_time_reverse (time_in_sec: int) -> str: 
        """
        Decription - Convert time from second to human read friendly format like 01:05:23
        Input - Int
        Output - String
        """
        hour = int(time_in_sec/3600)
        minute = int(time_in_sec%3600/60)
        sec = time_in_sec%3600%60
        
        if (hour < 10):
                hour = f"0{hour}"
        
        if (minute < 10): 
                minute = f"0{minute}"
        
        if (sec < 10):
                sec = f"0{sec}"
        
        return (f"{hour}:{minute}:{sec}")


def format_time_reverse_nice (time_in_sec:int) -> str:
        """
        Description - Returns time from second to human read friendly format like 1h 5m 2s
        Input - Int
        Output - String
        """         
        hour = int(time_in_sec/3600)
        minute = int(time_in_sec%3600/60)
        sec = time_in_sec%3600%60;
        sec = f"{sec}s"
        if (hour == 0):
                if (minute == 0):
                        return f"{sec}"
                
                minute = f"{minute}m"
                return f"{minute} {sec}"
        
        hour = f"{hour}h"
        minute = f"{minute}m"
        return f"{hour} {minute} {sec}"

def microtime_float () -> float: 
        """
        Description - Returns the microseconds since epoch, in UTC 
        Input - None
        Output - Float
        """    
        return time.time()*1000

