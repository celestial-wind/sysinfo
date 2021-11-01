#!/usr/bin/env python3
"""
sysinfo.py
@author: kyle miller
"""


class Color:
    """Color codes."""

    purple = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


'''conversion factor for kilobytes to gigabytes'''
kb2gb = 1000000

'''conversion factor for seconds to days'''
s2d = 86400

'''conversion factor for milidegree Celsisus to Celsisus'''
mc2c = 1000

'''conversion factor for Celsius to Kelvin'''
c2k = 273.15

'''conversion factor for Celsisus to Fahrenheit'''
c2f = 9/5

'''offset freezing temperature factor for Celsisus to Fahrenheit'''
freezetemp = 32

'''conversion factor to convert to percentage'''
d2p = 100


def getInfo(file):
    """Return system information."""
    # main fetch, followed by specifics
    info = subprocess.getoutput(["cat " + file])

    # fetch kernel info
    if file == "/proc/version":
        version = info.lower()
        version = version.replace("version", "").replace("linux", "").strip()
        versionList = version.split()
        return_string = ' '.join(versionList)
        return return_string

    # fetch hostname
    elif file == "/etc/hostname":
        return_string = info.lower()
        return return_string

    # fetch uptime/idletime
    elif file == "/proc/uptime":
        up = info.split(" ")

        # uptime
        if float(up[0]) > s2d:
            updays = float(up[0]) / s2d
            if args.verbose:
                return_string = (
                    f"uptime: {float(up[0]):5.5} secs :: {updays:5.5} days")
            else:
                return_string = f"uptime: {updays:3.3} days"

        else:
            return_string = f"uptime: {float(up[0]):3.2} secs"

        # idletime
        if float(up[1]) > s2d:
            idledays = float(up[1]) / s2d
            if args.verbose:
                idle_string = (
                    f"idletime: {float(up[1]):5.5} secs :: {idledays:5.5} days"
                )
            else:
                idle_string = f"idletime: {idledays:3.3} days"
            return_string = return_string + "\n" + idle_string

        else:
            idle_string = f"idletime: {float(up[1]):3.2} secs"
            return_string = return_string + "\n" + idle_string

        return return_string

    # fetch cpu temperature
    elif file == "/sys/class/thermal/thermal_zone0/temp":

        info = float(info)
        info = info // mc2c
        highTemp = True if (info > 55) else False

        if args.kelvin:
            info = info + c2k
            return_string = f"{info:5.5} K"
        elif args.fahrenheit:
            info = (info * c2f) + freezetemp
            return_string = f"{info:5.5}°F"
        else:
            if args.verbose:
                return_string = f"{info:5.5}°C"
            else:
                return_string = f"{info:3.3}°C"

        if highTemp:
            return_string = Color.RED + return_string + Color.END

        return return_string

    # fetch memory status
    elif file == "/proc/meminfo":

        memTotal = re.search(r'MemTotal:\s+\w+', info)
        memTotal = memTotal.group()
        memTotalLower = memTotal.lower()
        memTotalFloat = float(memTotal.strip("MemTotal:")) / kb2gb

        memFree = re.search(r'MemFree:\s+\w+', info)
        memFree = memFree.group()
        memFreeLower = memFree.lower()
        memFreeFloat = float(memFree.strip("MemFree:")) / kb2gb

        memAvailable = re.search(r'MemAvailable:\s+\w+', info)
        memAvailable = memAvailable.group()
        memAvailableLower = memAvailable.lower()
        memAvailableFloat = float(memAvailable.strip("MemAvailable:")) / kb2gb

        if args.verbose:
            total = f"{memTotalLower} kb :: {memTotalFloat:5.5} gb\n"
            free = (
                f"{memFreeLower} kb :: {memFreeFloat:5.5} gb \
                ({(memFreeFloat/memTotalFloat)*d2p:3.3}%)\n")
            available = (
                f"{memAvailableLower} kb :: {memAvailableFloat:5.5} gb \
                    ({(memAvailableFloat/memTotalFloat)*d2p:3.3}%)")

        else:
            total = f"memtotal: {memTotalFloat:3.3} gb\n"
            free = (
                f"memfree: {memFreeFloat:3.3} gb  \
                    ({(memFreeFloat/memTotalFloat)*d2p:3.3}%)\n")
            available = (
                f"memavailable: {memAvailableFloat:3.3} gb  \
                    ({(memAvailableFloat/memTotalFloat)*d2p:3.3}%)")

        return_string = total + free + available
        return return_string

    # fetch process information (total number of forks)
    elif file == "/proc/stat":
        stats = re.search(r'processes\s+\w+', info)
        stats = stats.group()
        stats = stats.split(" ")
        return_string = f"{{{stats[1]}}}"
        return return_string

    # fetch cpu load average
    elif file == "/proc/loadavg":
        load = info.split()
        five = float(load[0]) * d2p
        ten = float(load[1]) * d2p
        fifteen = float(load[2]) * d2p
        # processes = load[3].split("/")
        # runningprocesses = processes[0]
        # totalprocesses = processes[1]
        return_string = f"loadavg: {five:3.3}% | {ten:3.3}% | {fifteen:3.3}%"
        return return_string

    # fetch dns information
    elif file == "/etc/resolv.conf":

        dns = re.findall(r'\d+\.\d+\.\d+\.\d+', info)

        return_string = '/'.join(dns)
        return return_string


'''main program'''
if __name__ == "__main__":
    # from sys import argv
    import subprocess
    import re
    import argparse

    # argparse stuff
    parser = argparse.ArgumentParser(description='view system information')
    parser.add_argument('-v', "--verbose", action="store_true",
                        help="displays numerical quantities to high precision")
    parser.add_argument('-i', "--ipaddr", action="store_true",
                        help="displays current network information")
    parser.add_argument('-d', "--dns", action="store_true",
                        help="displays current dns server(s)")
    parser.add_argument('-k', "--kelvin", action="store_true",
                        help="displays temperature in Kelvin units")
    parser.add_argument('-f', "--fahrenheit", action="store_true",
                        help="displays temperature in Fahrenheit units")
    parser.add_argument('-b', "--battery", action="store_true",
                        help="displays battery information")
    parser.add_argument('-s', "--storage", action="store_true",
                        help="displays storage information")
    parser.add_argument('-c', "--cpu", action="store_true",
                        help="displays cpu information")
    parser.add_argument('-l', "--load", action="store_true",
                        help="displays load averages and top 10 processes")
    parser.add_argument('-t', "--time", action="store_true",
                        help="displays the current time")
    parser.add_argument(
        '-q', "--quiet", action="store_true", help="mutes header")
    args = parser.parse_args()

    if not args.quiet:
        print(Color.BOLD + "[sysinfo]\n" + Color.END)

    '''fetch network node hostname'''
    try:
        hostname = getInfo("/etc/hostname")
        print(f"hostname: {hostname}\n")

    except Exception as e:
        print("[[ unable to fetch network node hostname ]]")
        if not args.quiet:
            print(e.with_traceback())
        pass

    '''fetch the time'''
    try:
        if args.time:
            if args.verbose:
                time = subprocess.check_output(
                    ["date"]).lower().decode("utf-8").rstrip()
            else:
                time = subprocess.check_output(
                    ["date", "+%r"]).lower().decode("utf-8").rstrip()
            print(f"time: {time}\n")

    except Exception as e:
        print("[[ error fetching time]]")
        if not args.quiet:
            print(e.with_traceback())
        pass

    '''fetch kernel information'''
    try:
        version = getInfo("/proc/version")
        print(f"kernel: {version}\n")

    except Exception as e:
        print("[[ error fetching kernel information]]")
        if not args.quiet:
            print(e.with_traceback())
        pass

    '''fetch total uptime and idle time in seconds'''
    try:
        uptime = getInfo("/proc/uptime")
        print(f"{uptime}\n")

    except Exception as e:
        print("[[ error fetching uptime/idle time]]")
        if not args.quiet:
            print(e.with_traceback())
        pass

    '''fetch cpu temperature in degress centigrade and current speed'''
    try:
        cpu_temp = getInfo("/sys/class/thermal/thermal_zone0/temp")
        cpu_speed = subprocess.check_output(
            ["lscpu"]).lower().decode('utf-8').rstrip()
        speed = re.search(r'cpu mhz:\s+\w+.\w+', cpu_speed)
        speed = speed.group().split()
        print(f"cputemp: {cpu_temp}\n\ncpuspeed: {speed[2]} mhz\n")

    except Exception as e:
        print("[[ error fetching CPU temperature]]")
        if not args.quiet:
            print(e.with_traceback())
        pass

    '''fetch memory information'''
    try:
        meminfo = getInfo("/proc/meminfo")
        print(f"{meminfo}\n")

    except Exception as e:
        print("[[ error fetching memory information]]")
        if not args.quiet:
            print(e.with_traceback())
        pass

    '''fetch load avg and processes'''
    try:
        if args.load:
            loadavg = getInfo("/proc/loadavg")
            print(f"{loadavg}\n")

    except Exception as e:
        print("[[ error fetching load avg/processes]]")
        if not args.quiet:
            print(e.with_traceback())
        pass

    '''fetch all the forks'''
    try:
        if args.load:
            forks = getInfo("/proc/stat")
            processes = subprocess.check_output(
                ["ps", "-A", "--noheaders"]).lower().decode("utf-8").rstrip()
            count = processes.count("\n")

            resources = subprocess.check_output(
                ["ps", "aux", "--sort=-pcpu,+pmem"])
            resources = resources.lower().decode("utf-8").rstrip()
            resourcesList = resources.split("\n")
            for ndx, proc in enumerate(resourcesList):
                if ndx == 0:
                    resourcesList[ndx] = ' '.join(proc.split())
                else:
                    resourcesList[ndx] = ' '.join(proc[:88].split()) + '..'
            top10 = '\n'.join(resourcesList[0:10])

            print(
                f"forks: {forks}\n\nprocesses: \
                    {count}\n\n[::top10::]\n{top10}")

        else:
            forks = getInfo("/proc/stat")
            processes = subprocess.check_output(
                ["ps", "-A", "--noheaders"]).lower().decode("utf-8").rstrip()
            count = processes.count("\n")
            print(f"forks: {forks}\n\nprocesses: {count}")

            '''
         two good terminal commands are:
         ps -A --noheaders | wc -l :: prints number of procs
         ps aux --sort=-pcpu,+pmem :: prints procs by activity
         '''

    except Exception as e:
        print("[[ error fetching fork information]]")
        if not args.quiet:
            print(e.with_traceback())
        pass

    '''fetch network info'''
    try:
        if args.ipaddr:
            print("\nnetstat: ")
            subprocess.call(["ip", "-c", "addr"])

    except Exception as e:
        print("[[ error fetching network information]]")
        if not args.quiet:
            print(e.with_traceback())
        pass

    '''fetch dns info'''
    try:
        if args.dns:
            dns = getInfo("/etc/resolv.conf")
            print(f"\ndns: {dns}")

    except Exception as e:
        print("[[ error fetching dns information]]")
        if not args.quiet:
            print(e.with_traceback())
        pass

    '''fetch battery info'''
    try:
        if args.battery:
            binfo = subprocess.check_output(
                ["upower", "-i",
                 "/org/freedesktop/UPower/devices/battery_BAT0"])
            binfo = binfo.lower().decode("utf-8").rstrip()
            print("\nbattery: ")
            print(binfo)

    except Exception as e:
        print("[[ error fetching battery information]]")
        if not args.quiet:
            print(e.with_traceback())
        pass

    '''fetch storage info'''
    try:
        if args.storage:
            out = subprocess.check_output(
                ["df", "-h"]).lower().decode("utf-8").rstrip()
            print("\nstorage: ")
            print(out)

    except Exception as e:
        print("[[ error fetching storage information]]")
        if not args.quiet:
            print(e.with_traceback())
        pass

    '''fetch cpu info'''
    try:
        if args.cpu:
            cpu = subprocess.check_output(["lscpu"])
            cpu = cpu.lower().decode('utf-8').rstrip()
            print(f"\ncpu: \n{cpu}")

    except Exception as e:
        print("[[ error fetching CPU information]]")
        if not args.quiet:
            print(e.with_traceback())
        pass


else:
    import sys
    print("[error] :: standalone module, do not import")
    sys.exit(1)
