from enum import Enum
from typing import Callable
from abc import ABC, abstractmethod
import heapq

# Performa Metrik
# 1. Mean Turnaround Time (MTT)
# 2. Mean Waiting Time (MWT)
# 3. Response Time (RT)
# 4. Number of Context Switching (NCS)
# 5. Number of Sort (NS)
# 6. Throughput
# 7. CPU Utilization
# 8. Fairness
# 9. Priority Imposition
# 10. Resource Balancing
# 11. Deadlines
# 12. Predictability

# region Evaluation
def turnaround_time(p):
    return p.finish_time - p.arrival_time

def waiting_time(p):
    return turnaround_time(p) - p.burst_time

def response_time(p):
    return p.start_time - p.arrival_time

def mean_turnaround(processes):
    return sum(turnaround_time(p) for p in processes) / len(processes)

def mean_waiting(processes):
    return sum(waiting_time(p) for p in processes) / len(processes)

def mean_response(processes):
    return sum(response_time(p) for p in processes) / len(processes)

import statistics

def fairness(processes):
    if len(processes) <= 1:
        return 0
    waits = [waiting_time(p) for p in processes]
    return statistics.pstdev(waits)

def predictability(processes):
    if len(processes) <= 1:
        return 0
    tats = [turnaround_time(p) for p in processes]
    return statistics.pvariance(tats)
# endregion
class Process:
    def __init__(self, arrival_time: int, burst_time: int, deadline: int) -> None:
        self.arrival_time = arrival_time 
        self.burst_time = burst_time 
        self.pcb = PCB()
        self.remaining_time = burst_time
        self.start_time = None
        self.finish_time = None
        self.quantum = None # Multi Level 
        self.deadline = deadline
        self.waiting_since = None # Multi Level Aging
        self.demotions = 0
        
    def __lt__(self, other): # for sorting
        return self.burst_time < other.burst_time
    def missed_deadline(self):
        return self.finish_time is not None and self.finish_time > self.deadline
        
class PState(Enum):
    NEW = 0
    READY = 1
    RUNNING = 2
    WAITING = 3
    TERMINATED = 4

global_pid = 9
        
def get_pid()->int:
    global global_pid
    global_pid+=1
    return global_pid
        
switching_count = 0
def raise_switch()->None:
    global switching_count
    switching_count+=1
        
sorting_count = 0
def raise_sorting()->None:
    global sorting_count
    sorting_count+=1
    
def reset_metrics():
    global switching_count, sorting_count
    switching_count = 0
    sorting_count = 0
        
class CPURegisters:
    def __init__(self, REG_0 = 0x0, REG_1 = 0x0, REG_2 = 0x0, REG_3 = 0x0, flag = 0x000,
                 stack_pointer = 0, instruction_reg = "", program_counter = 0x0) -> None:
        self.REG_0 = REG_0 
        self.REG_1 = REG_1 
        self.REG_2 = REG_2 
        self.REG_3 = REG_3 
        self.flag = flag 
        self.stack_pointer = stack_pointer 
        self.instruction_reg = instruction_reg 
        self.program_counter = program_counter 
        
class PCB:
    def __init__(self) -> None:
        self.pstate = PState.NEW
        self.pid = get_pid()
        self.CPU_regs = None
        
class OS:
    # Has Only 1 Core
    def __init__(self, scheduler: Callable[[list[bool]],None]):
        self.cpu = CPURegisters()
        self.scheduler = scheduler()
        self.time = 0
        self.processes = [] # Job queue
        self.all_processes = []
        self.idle_time = 0
        self.last_process: Process | None = None

    def is_all_done(self)->bool:
        return all(p.pcb.pstate == PState.TERMINATED for p in self.all_processes)

    def add_process(self, process: Process):
        self.processes.append(process)
        self.all_processes.append(process)

    def run(self):
        while not self.is_all_done():
            self.tick()
            self.time += 1
    
            
    def tick(self):
        # proses yang baru datang
        remaining = []
        for p in self.processes:
            if p.arrival_time == self.time:
                p.pcb.pstate = PState.READY
                self.scheduler.add_process(p)
            else:
                remaining.append(p)

        self.processes = remaining

        # ambil proses berikutnya
        current = self.scheduler.get_next_process(self.time)
        
        # Do work
        if current!=None:
            # Check if last process change for switch
            if current != self.last_process and self.last_process is not None:
                raise_switch()
            current.pcb.pstate = PState.RUNNING
            current.remaining_time -= 1

            if current.start_time is None:
                current.start_time = self.time

            if current.remaining_time == 0:
                current.finish_time = self.time + 1
                current.pcb.pstate = PState.TERMINATED
                self.scheduler.terminate_process(current)
        else:
            self.idle_time += 1
        self.last_process = current
            
    def resource_balancing(self):
        usages = [p.burst_time / self.time for p in self.all_processes]
        return statistics.pstdev(usages)

    def evaluation(self):
        if self.time == 0:
            return None
        # throughput = len(self.all_processes) / self.time
        # cpu_util = (self.time - self.idle_time) / self.time
        return {
            "MTT": mean_turnaround(self.all_processes),
            "MWT": mean_waiting(self.all_processes),
            "MRT": mean_response(self.all_processes),
            "Throughput": len(self.all_processes) / self.time,
            "CPU Util": (self.time - self.idle_time) / self.time,
            "NCS": switching_count,
            "NS": sorting_count,
            "Missed Deadline": sum(p.missed_deadline() for p in self.all_processes),
            "Resource Balancing": self.resource_balancing(),
            "Fairness": fairness(self.all_processes),
            "Predictability": predictability(self.all_processes),
            "Priority Imposition": sum(p.demotions for p in self.all_processes),
        }
        
class Scheduler(ABC):
    @abstractmethod
    def add_process(self, process: Process):
        pass
    @abstractmethod
    def get_next_process(self, current_time: int) -> Process:
        pass
    @abstractmethod
    def terminate_process(self, process: Process):
        pass
    
class MLFQ(Scheduler):
    """
    Aturan:
        Idea=>Memisahkan process berdasarkan kriteria CPU Burst nya
        Jika Process menggunakan CPU terlalu banyak, maka akan dipindah ke queue dengan priorias lebih rendah
        I/O Bound dan interactive process (real-time) ada di queue lebih tinggi
        Tambahan, jika sebuah process menunggu terlalu lama pada queue lebih rendah, maka akan dipindah ke queue lebih tinggi. Mencegah starvation
        Preemptive

    Args:
        Scheduler (_type_): implementation of Multi Level Dynamic Feedback
    """
    def __init__(self,
                 use_rr: bool = True, 
                 use_aging: bool = True,
                 aging_threshold: int = 20):
        self.queue1 = [] # Quantum 8
        self.quantum1 = 8
        self.queue2 = [] # Quantum 16
        self.quantum2 = 16
        self.queue3 = [] # FCFS (First Come First Serve)
        self.use_rr = use_rr
        self.use_aging = use_aging
        self.aging_threshold = aging_threshold
        
    def add_process(self, process: Process):
        process.quantum = self.quantum1
        process.waiting_since = 0
        self.queue1.append(process)
    
    def aging(self):
        if not self.use_aging:
            return
        for queue in [self.queue2, self.queue3]:
            for p in queue:
                p.waiting_since += 1
        # queue3 → queue2
        promote_q3 = []
        for p in self.queue3:
            if p.waiting_since >= self.aging_threshold:
                p.waiting_since = 0
                p.quantum = self.quantum2
                promote_q3.append(p)
        
        for p in promote_q3:
            self.queue3.remove(p)
            self.queue2.append(p)

        # queue2 → queue1
        promote_q2 = []
        for p in self.queue2:
            if p.waiting_since >= self.aging_threshold:
                p.waiting_since = 0
                p.quantum = self.quantum1
                promote_q2.append(p)
        
        for p in promote_q2:
            self.queue2.remove(p)
            self.queue1.append(p)
    
    def terminate_process(self, process: Process):
        for queue in [self.queue1, self.queue2, self.queue3]:
            for i in range(len(queue)):
                if process == queue[i]:
                    queue.pop(i)
                    return
    
    def get_next_process(self, current_time: int):
        self.aging()
        
        for queue in [self.queue1, self.queue2, self.queue3]:
            if queue:
                p = queue[0]
                p.waiting_since = 0
                if p.quantum is not None:
                    p.quantum -= 1
                
                if p.quantum == 0:
                    queue.pop(0)
                    
                    if queue is self.queue1:
                        p.demotions += 1
                        p.quantum = self.quantum2
                        self.queue2.append(p)
                    elif queue is self.queue2:
                        p.quantum = None
                        self.queue3.append(p)
                    else:
                        self.queue3.append(p)
                elif self.use_rr and queue is not self.queue3:
                    queue.append(queue.pop(0))
                return p
        return None
    
class K_Factore(Scheduler):
    """
    Menjalankan process dengan nilai K-Factor tertinggi.
    Jadi algoritma akan menghitung skor untuk setiap process dan mengambil process dengan score tertinggi.
    Bisa Non-Preemptive (skor dihitung sekali) atau Preemptive (skor dihitung terus menerus, dinamis)
    Di sini menggunakan sistem Preemptive

    Args:
        Scheduler (_type_): Implementation K-Factor
    """
    def __init__(self):
        self.queue: list[Process] = []
        self.k = 0.6
        
    def add_process(self, process: Process):
        self.queue.append(process)
        
    def terminate_process(self, process: Process):
        for i in range(len(self.queue)):
            if process == self.queue[i]:
                self.queue.pop(i)
                return
            
    def is_empty(self):
        return len(self.queue)==0
        
    def calculate_score(self, p: Process, current_time):
        waiting_time = current_time - p.arrival_time - (p.burst_time - p.remaining_time)
        return self.k * waiting_time + (1 - self.k) * (1 / p.burst_time)
        
    def get_next_process(self, current_time: int) -> Process | None:
        if (not self.is_empty()):
            raise_sorting()
            return max(self.queue, key=lambda p: self.calculate_score(p, current_time))
        else:
            return None

