import http.server
import threading
import argparse
import time

from prometheus_client import Counter, Gauge
from prometheus_client import start_http_server

HTTP_HOST = '0.0.0.0'
HTTP_PORT = 8080
METRICS_PORT = 8081

parser = argparse.ArgumentParser()
parser.add_argument('--NUMBER_REQUESTS', default='100', type=int)
parser.add_argument('--TIME_FOR_CURRENT_RPS', default='10', type=int)
parser.add_argument('--TIME_FOR_AVG_RPS', default='60', type=int)
args = parser.parse_args()
NUMBER_REQUESTS = args.NUMBER_REQUESTS
TIME_FOR_CURRENT_RPS = args.TIME_FOR_CURRENT_RPS
TIME_FOR_AVG_RPS = args.TIME_FOR_AVG_RPS

TOTAL_REQUESTS = Counter('requests_total', 'Total Requested')
CURRENT_RPS = Gauge('current_rps', 'Current RPS / per 10 seconds')
AVG_RPS = Gauge('avg_rps', 'AVG RPS / per 60 seconds')
AVG_RPS_FOR_REQUESTS = Gauge(f'avg_rps_per_{NUMBER_REQUESTS}_request', f'Current RPS / per {NUMBER_REQUESTS} requests.')


class MyHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        TOTAL_REQUESTS.inc()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"GET\n")

    def do_POST(self):
        TOTAL_REQUESTS.inc()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"POST\n")

    def do_PUT(self):
        TOTAL_REQUESTS.inc()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"PUT\n")

    def do_HEAD(self):
        TOTAL_REQUESTS.inc()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"HEAD\n")


class CurrentRps(object):
    def __init__(self, interval=1):
        self.interval = interval
        thread = threading.Thread(target=self.get_current_rps, args=())
        thread.daemon = True
        thread.start()

    def _get_requests_value(self):
        total_requests = TOTAL_REQUESTS.collect()[0].__getattribute__("samples")[0].value
        return total_requests

    def get_current_rps(self):
        while True:
            started_measure_time = time.time()
            requests_count1 = self._get_requests_value()
            while True:
                total_time = time.time() - started_measure_time
                if total_time >= TIME_FOR_CURRENT_RPS:
                    requests_count2 = self._get_requests_value()
                    total_requests = requests_count2 - requests_count1
                    CURRENT_RPS.set(total_requests // total_time)
                    started_measure_time = time.time()
                    requests_count1 = self._get_requests_value()


class AvgRps(object):
    def __init__(self, interval=1):
        self.interval = interval
        thread = threading.Thread(target=self.get_avg_rps, args=())
        thread.daemon = True
        thread.start()

    def _get_requests_value(self):
        total_requests = TOTAL_REQUESTS.collect()[0].__getattribute__("samples")[0].value
        return total_requests

    def get_avg_rps(self):
        while True:
            started_measure_time = time.time()
            requests_count1 = self._get_requests_value()
            while True:
                total_time = time.time() - started_measure_time
                if total_time >= TIME_FOR_AVG_RPS:
                    requests_count2 = self._get_requests_value()
                    total_requests = requests_count2 - requests_count1
                    AVG_RPS.set(total_requests // total_time)
                    started_measure_time = time.time()
                    requests_count1 = self._get_requests_value()


class AvgRpsPerRequest(object):
    def __init__(self, interval=1):

        self.interval = interval
        thread = threading.Thread(target=self.get_avg_rps, args=())
        thread.daemon = True
        thread.start()

    def _get_requests_value(self):
        total_requests = TOTAL_REQUESTS.collect()[0].__getattribute__("samples")[0].value
        return total_requests

    def get_avg_rps(self):
        while True:
            started_measure_time = time.time()
            requests_count1 = self._get_requests_value()
            while True:
                requests_diff = self._get_requests_value() - requests_count1
                if requests_diff >= NUMBER_REQUESTS:
                    total_time = time.time() - started_measure_time
                    requests_count = self._get_requests_value()
                    AVG_RPS_FOR_REQUESTS.set(requests_count // total_time)
                    started_measure_time = time.time()
                    requests_count1 = self._get_requests_value()


if __name__ == '__main__':
    start_http_server(METRICS_PORT)
    avg_rps = AvgRps()
    avg_rps_per_request = AvgRpsPerRequest()
    CurrentRps = CurrentRps()
    server = http.server.HTTPServer((HTTP_HOST, HTTP_PORT), MyHandler)
    server.serve_forever()
