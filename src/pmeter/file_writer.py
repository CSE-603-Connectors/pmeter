from email.policy import default
import multiprocessing
import json
from datetime import date, datetime
import psutil
import platform
from tcp_latency import measure_latency


class ODS_Metrics():

    def __init__(self):
        #kernel metrics 
        self.active_core_count = 0
        self.cpu_frequency = 0.0
        self.energy_consumed = 0.0
        self.cpu_arch = ""
        #network metrics
        self.interface= ""
        self.rtt = 0.0
        self.bandwidth = 0.0
        self.bandwidth_delay_product = 0.0
        self.packet_loss_rate = 0.0
        self.link_capacity = 0.0
        self.bytes_sent = 0.0
        self.bytes_recv = 0.0
        self.packets_sent = 0
        self.packets_recv = 0
        self.dropin = 0
        self.dropout = 0
        self.nic_speed = 0 #this is in mb=megabits
        self.nic_mtu = 0 #max transmission speed of nic
        #identifying properties
        self.start_time=""
        self.end_time=""
        self.count = 0
        self.latency = []

    # def active_core_count(self):
    #     self.active_core_count = multiprocessing.cpu_count()

    def to_file(self, file_name):
        j = json.dumps(self.__dict__)
        with open(file_name, "a+") as f:
            f.write(j + "\n")
    
    def measure(self, interface='', measure_tcp=True, measure_udp=True, measure_kernel=True, measure_network=True, print_to_std_out=False, latency_host="http://google.com"):
        self.start_time = datetime.now().__str__()
        self.interface = interface
        if measure_kernel:
            self.active_core_count = multiprocessing.cpu_count()
            self.cpu_frequency = psutil.cpu_freq()
            self.cpu_arch = platform.platform()
        if measure_network:
            print('Getting metrics of: ' + interface)
            nic_counter_dic = psutil.net_io_counters(pernic=True)
            interface_counter_tuple = nic_counter_dic[interface]
            print(interface_counter_tuple)
            # snetio(bytes_sent=179353738, bytes_recv=1961293807, packets_sent=1699113, packets_recv=2477127, errin=0, errout=0, dropin=0, dropout=0)
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
            print(interface_stats)
            # snicstats(isup=True, duplex=<NicDuplex.NIC_DUPLEX_UNKNOWN: 0>, speed=0, mtu=9001)
            self.nic_mtu = interface_stats[3]
            self.nic_speed = interface_stats[2]
            self.latency = measure_latency(host='google.com')
            print(self.latency)
        if measure_tcp:
            print('Measuring tcp')
            psutil.net_connections(kind="tcp")
        if measure_udp:
            print('Measuring udp')
            psutil.net_connections(kind="udp")
        self.end_time=datetime.now().__str__()
        if(print_to_std_out):
            print(json.dumps(self.__dict__))
        
        self.to_file("pmeter_measure.txt")

    def defaultconverter(o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

