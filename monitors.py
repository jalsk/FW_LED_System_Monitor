# Built In Dependencies
import time
import psutil
import os

if os.name == 'nt':
    import wmi

class DiskMonitor:
    def __init__(self, hysterisis_time = 20):
        self.read_usage_history = [0]
        self.write_usage_history = [0]
        self.history_times = [0]
        self.highest_read_rate = 0.00001
        self.highest_write_rate = 0.00001
        self.max_history_size = hysterisis_time

    def get(self):
        """
        Gets the percentage of the system's disk throughput for reading and writing.

        Returns:
            A tuple containing the percentages of the system's disk throughput for reading
              and writing data as floats between 0.0 and 1.0. This is a ratio based on
              the highest disk throughput rate over the history of the monitor.
        """
        try:
            disk_io = psutil.disk_io_counters()
            read_usage = disk_io.read_bytes
            write_usage = disk_io.write_bytes
            self.read_usage_history.append(read_usage)
            self.write_usage_history.append(write_usage)
            self.history_times.append(time.time())
            if len(self.read_usage_history) > self.max_history_size:
                self.read_usage_history = self.read_usage_history[-self.max_history_size:]
                self.write_usage_history = self.write_usage_history[-self.max_history_size:]
                self.history_times = self.history_times[-self.max_history_size:]

            read_diff = self.read_usage_history[-1] - self.read_usage_history[0]
            write_diff = self.write_usage_history[-1] - self.write_usage_history[0]
            time_diff = self.history_times[-1] - self.history_times[0]
            read_rate = read_diff / time_diff
            write_rate = write_diff / time_diff
            self.highest_read_rate = max(self.highest_read_rate, read_rate)
            self.highest_write_rate = max(self.highest_write_rate, write_rate)
            read_percent = min(1.0, read_rate / self.highest_read_rate)
            write_percent = min(1.0, write_rate / self.highest_write_rate)
            return read_percent, write_percent
        except Exception as e:
            print(f"Error in DiskMonitor.get(): {e}")
            return 0, 0

class NetworkMonitor:
    def __init__(self, hysterisis_time = 20):
        self.sent_usage_history = [0]
        self.recv_usage_history = [0]
        self.history_times = [0]
        self.highest_sent_rate = 0.00001
        self.highest_recv_rate = 0.00001
        self.max_history_size = hysterisis_time

    def get(self):
        """
        Gets the percentage of the system's network usage.

        Returns:
            A tuple containing the percentages of the system's network usage for sending
              and receiving data as floats between 0.0 and 1.0. This is a ratio based on
              the highest network usage rate over the history of the monitor.
        """
        try:
            net_io = psutil.net_io_counters()
            sent_usage = net_io.bytes_sent
            recv_usage = net_io.bytes_recv
            self.sent_usage_history.append(sent_usage)
            self.recv_usage_history.append(recv_usage)
            self.history_times.append(time.time())
            if len(self.sent_usage_history) > self.max_history_size:
                self.sent_usage_history = self.sent_usage_history[-self.max_history_size:]
                self.recv_usage_history = self.recv_usage_history[-self.max_history_size:]
                self.history_times = self.history_times[-self.max_history_size:]

            sent_diff = self.sent_usage_history[-1] - self.sent_usage_history[0]
            recv_diff = self.recv_usage_history[-1] - self.recv_usage_history[0]
            time_diff = self.history_times[-1] - self.history_times[0]
            sent_rate = sent_diff / time_diff
            recv_rate = recv_diff / time_diff
            self.highest_sent_rate = max(self.highest_sent_rate, sent_rate)
            self.highest_recv_rate = max(self.highest_recv_rate, recv_rate)
            sent_percent = min(1.0, sent_rate / self.highest_sent_rate)
            recv_percent = min(1.0, recv_rate / self.highest_recv_rate)
            return sent_percent, recv_percent
        except Exception as e:
            print(f"Error in NetworkMonitor.get(): {e}")
            return 0, 0

class CPUMonitor:
    def __init__(self, hysterisis_time = 10):
        self.cpu_count = psutil.cpu_count() // 2 # 2 logical cores per physical core
        self.cpu_usage_history = [[] for _ in range(self.cpu_count)]
        self.history_times = []
        self.max_history_size = hysterisis_time

    def get(self):
        """
        Gets the percentage of the system's CPU usage per core.

        Returns:
            A list of values between 0.0 and 1.0 which is scaled to the CPU usage per core
        """
        try:
            cpu_usage = psutil.cpu_percent(percpu=True)
            for i in range(self.cpu_count):
                useage = 2 * max(cpu_usage[2*i], cpu_usage[2*i+1]) # Combine logical cores
                if useage > 100:
                    useage = 100
                self.cpu_usage_history[i].append(useage / 100.0)
            self.history_times.append(time.time())
            if len(self.cpu_usage_history[0]) > self.max_history_size:
                for i in range(self.cpu_count):
                    self.cpu_usage_history[i] = self.cpu_usage_history[i][-self.max_history_size:]
                    self.history_times = self.history_times[-self.max_history_size:]
            cpu_percentages = [sum(core_history) / self.max_history_size for core_history in self.cpu_usage_history]
            # Somehow cpu_percentages can have values greater than 1 so we clamp them
            return cpu_percentages
        except Exception as e:
            print(f"Error in CPUMonitor.get(): {e}")
            return [0] * self.cpu_count

class MemoryMonitor:
    @staticmethod
    def get():
        """
        Gets the percentage of the system's memory usage.

        Returns:
            A value between 0.0 and 1.0 which is scaled to the memory usage
        """
        return psutil.virtual_memory().percent / 100.0
    

class BatteryMonitor:
    @staticmethod
    def get():
        """
        Gets the percentage of the battery's charge and whether it is plugged in.

        Returns:
            A tuple containing the battery percentage as a float between 0.0 and 1.0 and whether it is plugged in
        """
        battery = psutil.sensors_battery()
        if battery is not None:
            battery_percentage = battery.percent / 100.0
            if os.name == "nt":
                battery_plugged = battery.power_plugged
            else:
                bat_status = open('/sys/class/power_supply/BAT1/status', 'r').read().strip()
                battery_plugged = (bat_status != 'Discharging')
            return battery_percentage, battery_plugged
        

def get_monitor_brightness():
    """
    Gets the brightness of the main laptop display so that we can scale the LED Matrix
      brightness to match. Handles operating system or configuration specific logic to
      retrieve the brightness value.

    Returns:
        A value between 0.0 and 1.0 which is scaled to the monitor's brightness
    """
    try:
        if os.name == 'nt':
            return wmi.WMI(namespace='wmi').WmiMonitorBrightness()[0].CurrentBrightness / 100.0
        else:
            gpu_designator = os.listdir('/sys/class/backlight')[0] # Get the gpu designator
            brightness_max = int(open(f'/sys/class/backlight/{gpu_designator}/max_brightness', 'r').read())
            return int(open(f'/sys/class/backlight/{gpu_designator}/brightness', 'r').read()) / brightness_max
    except Exception as e:
        print(f"Error in get_monitor_brightness(): {e}")
        return 1.0


if __name__ == "__main__":
    print(get_monitor_brightness())