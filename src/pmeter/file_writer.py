from email.policy import default
import multiprocessing
from pathlib import Path
import json
import datetime
import psutil
import platform
from tcp_latency import measure_latency
import os
import time
import requests
from pythonping import ping
from datetime import datetime

class ODS_Metrics():

    def __init__(self):
        # kernel metrics
        self.interface = ""
        self.ods_user = ""
        self.active_core_count = 0
        self.cpu_frequency = []
        self.energy_consumed = 0.0
        self.cpu_arch = ""
        # network metrics
        self.rtt = 0.0
        self.bandwidth = 0.0
        self.bandwidth_delay_product = 0.0
        self.packet_loss_rate = 0.0
        self.link_capacity = 0.0
        self.bytes_sent = 0.0
        self.bytes_recv = 0.0
        self.bytes_sent_delta=0
        self.bytes_recv_delta=0
        self.packets_sent = 0
        self.packets_recv = 0
        self.packets_sent_delta=0
        self.packets_recv_delta=0
        self.dropin = 0
        self.dropout = 0
        self.dropin_delta=0
        self.dropout_delta=0
        self.nic_speed = 0  # this is in mb=megabits
        self.nic_mtu = 0  # max transmission speed of nic
        # identifying properties
        self.start_time = ""
        self.end_time = ""
        self.count = 0
        self.latency = []


    def set_user(self, user_passed):
        user = os.getenv('ODS_USER', '')
        if len(user_passed) > 0:
            self.ods_user = user_passed
        else:
            self.ods_user = user

    def measure(self, interface='', measure_tcp=True, measure_udp=True, measure_kernel=True, measure_network=True, print_to_std_out=False, latency_host="google.com"):
        self.start_time = datetime.now().__str__()
        self.interface = interface
        if measure_kernel:
            self.measure_kernel()
        if measure_network:
            print('Getting metrics of: ' + interface)
            # we could take the average of all speeds that every socket experiences and thus get a rough estimate of bandwidth??
            self.measure_network(interface)
            # self.measure_latency_rtt(latency_host)
        if measure_tcp:
            print('Measuring tcp')
            psutil.net_connections(kind="tcp")
        if measure_udp:
            print('Measuring udp')
            psutil.net_connections(kind="udp")
        self.end_time = datetime.now().__str__()
        if(print_to_std_out):
            print("\n", json.dumps(self.__dict__), "\n")
        # self.to_file()

    def find_rtt(self, url=None):
        default_rtt = 0
        new_rtt = -1
        try:
            response_list = ping(('8.8.8.8'))
            new_rtt = response_list.rtt_avg_ms
        except:
            try:
                if not url:
                    url = "http://www.google.com"
                t1 = time.time()
                r = requests.get(url)
                t2 = time.time()
                new_rtt = t2-t1
            except:
                new_rtt = default_rtt
        finally:
            return new_rtt if new_rtt != -1 else default_rtt

    def measure_kernel(self):
        self.active_core_count = multiprocessing.cpu_count()
        if platform.system() != 'Darwin':
            self.cpu_frequency = psutil.cpu_freq() #for some reason the m1 mac or maybe macs throw an error getting the frequency could also be my local set up.
        self.cpu_arch = platform.platform()
        self.active_core_count = multiprocessing.cpu_count()

    def measure_latency_rtt(self, latency_host="http://google.com"):
        self.latency = measure_latency(host=latency_host)
        self.rtt = self.find_rtt(latency_host)

    def measure_network(self, interface):
        nic_counter_dic = psutil.net_io_counters(pernic=True, nowrap=True)
        interface_counter_tuple = nic_counter_dic[interface]
        self.bytes_sent = interface_counter_tuple[0]
        self.bytes_recv = interface_counter_tuple[1]
        self.packets_sent = interface_counter_tuple[2]
        self.packets_recv = interface_counter_tuple[3]
        self.errin = interface_counter_tuple[4]
        self.errout = interface_counter_tuple[5]
        self.dropin = interface_counter_tuple[6]
        self.dropout = interface_counter_tuple[7]
        sys_interfaces = psutil.net_if_stats()
        interface_stats = sys_interfaces[self.interface]
        self.nic_mtu = interface_stats[3]
        self.nic_speed = interface_stats[2]

    def get_system_interfaces(self):
        nic_counter_dic = psutil.net_io_counters(pernic=True, nowrap=True)
        return nic_counter_dic.keys()

    def to_file(self, folder_path='',folder_name=".pmeter", file_name="pmeter_measure.txt"):
        print(folder_path)
        print(file_name)
        if not folder_path:
            folder_path = os.path.join(Path.home(), folder_name)
        else:
            folder_path = os.path.join(folder_path, folder_name)
        print(folder_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_path = os.path.join(folder_path, file_name)
        j = json.dumps(self.__dict__)
        with open(file_path, "a+") as f:
            f.write(j + "\n")

    def do_deltas(self, old_metric):
        self.bytes_sent_delta = self.bytes_sent - old_metric.bytes_sent
        self.bytes_recv_delta = self.bytes_recv - old_metric.bytes_recv
        self.packets_sent_delta = self.packets_sent - old_metric.packets_sent
        self.packets_recv_delta = self.packets_recv - old_metric.packets_recv
        self.errin_delta = self.errin - old_metric.errin
        self.errout_delta = self.errout - old_metric.errout
        self.dropin_delta = self.dropin - old_metric.dropin
        self.dropout_delta = self.dropout - old_metric.dropout


