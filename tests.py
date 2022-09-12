import unittest
from unittest.mock import patch, mock_open
from task import parse_log_file, generate_log_summary, LogEntry
from ipaddress import ip_address

class TestTask(unittest.TestCase):
    def setUp(self):
        self.mock_entries = [
            LogEntry(ip_address('1.1.1.1'), '/endpoint1/'),
            LogEntry(ip_address('1.1.1.2'), '/endpoint2/'),
            LogEntry(ip_address('1.1.1.2'), '/endpoint2/'),
            LogEntry(ip_address('1.1.1.3'), '/endpoint3/'),
            LogEntry(ip_address('1.1.1.3'), '/endpoint3/'),
            LogEntry(ip_address('1.1.1.3'), '/endpoint3/'),
            LogEntry(ip_address('1.1.1.4'), '/endpoint4/'),
            LogEntry(ip_address('1.1.1.4'), '/endpoint4/'),
            LogEntry(ip_address('1.1.1.4'), '/endpoint4/'),
            LogEntry(ip_address('1.1.1.4'), '/endpoint4/'),
            LogEntry(ip_address('2001:db8:3333::6666:7777:8888'), '/endpoint5/'),
        ]

    def test_generate_log_summary(self):
        summary = generate_log_summary(self.mock_entries)
        self.assertEqual(len(summary.requests_from_ip), 5, 'incorrect number of unique IPs')
        self.assertEqual(summary.requests_from_ip[ip_address('2001:db8:3333::6666:7777:8888')], 1, 'incorrect IP request count')
        self.assertEqual(summary.requests_from_ip[ip_address('1.1.1.1')], 1, 'incorrect IP request count')
        self.assertEqual(summary.requests_from_ip[ip_address('1.1.1.4')], 4, 'incorrect IP request count')
        self.assertEqual(summary.requests_from_ip[ip_address('1.1.1.0')], 0, 'incorrect IP request count')
        self.assertEqual(summary.requests_to_endpoint['/endpoint1/'], 1, 'incorrect endpoint request count')
        self.assertEqual(summary.requests_to_endpoint['/endpoint4/'], 4, 'incorrect endpoint request count')
        self.assertEqual(summary.requests_to_endpoint['/endpoint0/'], 0, 'incorrect endpoint request count')

    def test_parse_log_file(self):
        logfile_mock = """1.1.1.1 - - [10/Jul/2018:22:21:28 +0200] "GET /endpoint1/ HTTP/1.1" 200 3574 "-" "Mozilla/5.0 (X11; U; Linux x86_64; fr-FR) AppleWebKit/534.7 (KHTML, like Gecko) Epiphany/2.30.6 Safari/534.7"
1.1.1.2 - - [10/Jul/2018:22:21:28 +0200] "GET /endpoint2/ HTTP/1.1" 200 3574 "-" "Mozilla/5.0 (X11; U; Linux x86_64; fr-FR) AppleWebKit/534.7 (KHTML, like Gecko) Epiphany/2.30.6 Safari/534.7"
1.1.1.2 - - [10/Jul/2018:22:21:28 +0200] "GET /endpoint2/ HTTP/1.1" 200 3574 "-" "Mozilla/5.0 (X11; U; Linux x86_64; fr-FR) AppleWebKit/534.7 (KHTML, like Gecko) Epiphany/2.30.6 Safari/534.7"
1.1.1.3 - - [10/Jul/2018:22:21:28 +0200] "GET /endpoint3/ HTTP/1.1" 200 3574 "-" "Mozilla/5.0 (X11; U; Linux x86_64; fr-FR) AppleWebKit/534.7 (KHTML, like Gecko) Epiphany/2.30.6 Safari/534.7"
1.1.1.3 - - [10/Jul/2018:22:21:28 +0200] "GET /endpoint3/ HTTP/1.1" 200 3574 "-" "Mozilla/5.0 (X11; U; Linux x86_64; fr-FR) AppleWebKit/534.7 (KHTML, like Gecko) Epiphany/2.30.6 Safari/534.7"
1.1.1.3 - - [10/Jul/2018:22:21:28 +0200] "GET /endpoint3/ HTTP/1.1" 200 3574 "-" "Mozilla/5.0 (X11; U; Linux x86_64; fr-FR) AppleWebKit/534.7 (KHTML, like Gecko) Epiphany/2.30.6 Safari/534.7"
1.1.1.4 - - [10/Jul/2018:22:21:28 +0200] "GET /endpoint4/ HTTP/1.1" 200 3574 "-" "Mozilla/5.0 (X11; U; Linux x86_64; fr-FR) AppleWebKit/534.7 (KHTML, like Gecko) Epiphany/2.30.6 Safari/534.7"
1.1.1.4 - - [10/Jul/2018:22:21:28 +0200] "GET /endpoint4/ HTTP/1.1" 200 3574 "-" "Mozilla/5.0 (X11; U; Linux x86_64; fr-FR) AppleWebKit/534.7 (KHTML, like Gecko) Epiphany/2.30.6 Safari/534.7"
1.1.1.4 - - [10/Jul/2018:22:21:28 +0200] "GET /endpoint4/ HTTP/1.1" 200 3574 "-" "Mozilla/5.0 (X11; U; Linux x86_64; fr-FR) AppleWebKit/534.7 (KHTML, like Gecko) Epiphany/2.30.6 Safari/534.7"
1.1.1.4 - - [10/Jul/2018:22:21:28 +0200] "GET /endpoint4/ HTTP/1.1" 200 3574 "-" "Mozilla/5.0 (X11; U; Linux x86_64; fr-FR) AppleWebKit/534.7 (KHTML, like Gecko) Epiphany/2.30.6 Safari/534.7"
2001:db8:3333::6666:7777:8888 - - [10/Jul/2018:22:21:28 +0200] "GET /endpoint5/ HTTP/1.1" 200 3574 "-" "Mozilla/5.0 (X11; U; Linux x86_64; fr-FR) AppleWebKit/534.7 (KHTML, like Gecko) Epiphany/2.30.6 Safari/534.7"
INVALID_IP - - [10/Jul/2018:22:21:28 +0200] "GET /endpoint0/ HTTP/1.1" 200 3574 "-" "Mozilla/5.0 (X11; U; Linux x86_64; fr-FR) AppleWebKit/534.7 (KHTML, like Gecko) Epiphany/2.30.6 Safari/534.7" """
        try:
            with patch('__main__.open', new=mock_open(read_data=logfile_mock)):
                with open('test_data.log', 'r') as logfile:
                    log_entries = parse_log_file(logfile)
                    self.assertEqual(len(log_entries), len(self.mock_entries), 'incorrect number of log entries')
                    for (entry1, entry2) in zip(log_entries, self.mock_entries):
                        self.assertEqual(entry1.ip, entry2.ip, 'incorrect IP from parsed logfile')
                        self.assertEqual(entry1.endpoint, entry2.endpoint, 'incorrect endpoint from parsed logfile')
        except IOError:
            print("Failed to open mock logfile")

if __name__ == '__main__':
    unittest.main()

