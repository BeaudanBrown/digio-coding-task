import re
import sys
from collections import defaultdict
from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import TextIO

class LogEntry():
    def __init__(self, ip: IPv4Address|IPv6Address, endpoint: str) -> None:
        self.ip = ip
        self.endpoint = endpoint

class LogSummary():
    def __init__(self) -> None:
        self.requests_from_ip : defaultdict[IPv4Address|IPv6Address, int] = defaultdict(int)
        self.requests_to_endpoint : defaultdict[str, int] = defaultdict(int)

def parse_log_file(logfile: TextIO) -> list[LogEntry]:
    logged_requests : list[LogEntry] = []
    for line in logfile:
        # Could have better regex to get more information from logfile if wanted
        match = re.match(r'(?P<ip>\S+).*\] "\S+ (?P<url>\S+)', line)
        if match is None:
            print('Failed to parse log line: {}'.format(line))
            continue
        try:
            ip = ip_address(match.group('ip'))
        except ValueError:
            print('Invalid ip address logged {}'.format(match.group('ip')))
            continue
        logged_requests.append(LogEntry(ip, match.group('url')))
    return logged_requests

def generate_log_summary(requests: list[LogEntry]) -> LogSummary:
    summary = LogSummary()
    for request in requests:
        summary.requests_from_ip[request.ip] += 1
        summary.requests_to_endpoint[request.endpoint] += 1
    return summary

def print_log_summary(summary: LogSummary) -> None:
    print('Number of unique IP addresses: {}'.format(len(summary.requests_from_ip)))
    print('Top 3 most visited URLs:')
    # Sort the dictionaries in descending order by count and grab the first 3 elements
    for url, count in sorted(summary.requests_to_endpoint.items(), key=lambda x: x[1], reverse=True)[:3]:
        print('\t{}\tvisited {} time(s)'.format(url, count))
    print('Top 3 most active IP addresses:')
    for ip, count in sorted(summary.requests_from_ip.items(), key=lambda x: x[1], reverse=True)[:3]:
        print('\t{}\t{} requests'.format(ip.exploded, count))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Invalid command line arguments.\nFormat should be "python parse-logfile.py <log filename>"')
        sys.exit(1)

    filename = sys.argv[1]
    try:
        with open(filename, 'r') as logfile:
            logged_requests = parse_log_file(logfile)
            summary = generate_log_summary(logged_requests)
            print_log_summary(summary)
    except IOError:
        print('Could not open logfile: {}'.format(filename))
