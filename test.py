from lib import *

# K_Factore | MLFQ
algorith = MLFQ

def test_many_small():
    reset_metrics()
    os = OS(algorith)

    processes = [
        Process(arrival_time=i, burst_time=2, deadline=20)
        for i in range(10)
    ]

    for p in processes:
        os.add_process(p)

    os.run()
    print("=== Many Small Processes ===")
    print(os.evaluation())

def test_few_large():
    reset_metrics()
    os = OS(algorith)

    processes = [
        Process(arrival_time=0, burst_time=50, deadline=100),
        Process(arrival_time=0, burst_time=60, deadline=120),
        Process(arrival_time=0, burst_time=40, deadline=90),
    ]

    for p in processes:
        os.add_process(p)

    os.run()
    print("=== Few Large Processes ===")
    print(os.evaluation())
    
def test_mixed():
    reset_metrics()
    os = OS(algorith)

    processes = [
        Process(0, 5, 30),
        Process(1, 20, 50),
        Process(2, 3, 25),
        Process(3, 25, 60),
        Process(4, 2, 20),
        Process(5, 15, 45),
        Process(6, 1, 15),
    ]

    for p in processes:
        os.add_process(p)

    os.run()
    print("=== Mixed Processes ===")
    print(os.evaluation())

def test_starvation():
    reset_metrics()
    os = OS(algorith)

    # long job duluan
    os.add_process(Process(0, 100, 200))

    # banyak short job datang terus
    for i in range(1, 20):
        os.add_process(Process(i, 2, 50))

    os.run()
    print("=== Starvation Test ===")
    print(os.evaluation())
    
if __name__ == "__main__":
    test_many_small()
    test_few_large()
    test_mixed()
    test_starvation()