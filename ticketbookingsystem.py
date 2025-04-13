import simpy
import numpy as np
import pandas as pd

service_time = 0.2
simulation_time = 100
total_requests = 1000
user_count = 500
num_servers = 1

class TicketBookingSystem:
    def __init__(self, env, num_servers):
        self.env = env
        self.server = simpy.Resource(env, capacity=num_servers)
        self.customers = []
        self.last_service_end = [0] * num_servers
        self.server_busy = [False] * num_servers
        self.total_busy_time = 0
        self.total_processed = 0
        self.dropped_requests = 0
        self.queue_lengths = []
        self.idle_time = [0] * num_servers
        self.env.process(self.monitor_queue())

    def monitor_queue(self):
        while True:
            self.queue_lengths.append(len(self.server.queue))
            yield self.env.timeout(0.5)

    def process_request(self, request_id):
        arrival = self.env.now
        queue_length_at_arrival = len(self.server.queue)
        server_status = "busy" if any(self.server_busy) else "not busy"

        with self.server.request() as req:
            result = yield req | self.env.timeout(0.5)
            if req not in result:
                self.dropped_requests += 1
                self.customers.append({
                    "Customer ID": request_id,
                    "Arrival time": arrival,
                    "Service start time": None,
                    "Service end time": None,
                    "Total time spent": None,
                    "Queue time": None,
                    "Queue length at arrival": queue_length_at_arrival,
                    "Server busy status": server_status,
                    "Server idle time": None,
                    "Dropped": True
                })
                return

            start_service = self.env.now
            queue_time = start_service - arrival

            for i in range(len(self.server_busy)):
                if not self.server_busy[i]:
                    if self.last_service_end[i] < start_service:
                        self.idle_time[i] += start_service - self.last_service_end[i]
                    self.server_busy[i] = True
                    self.last_service_end[i] = start_service
                    break

            yield self.env.timeout(service_time)
            end_service = self.env.now

            self.total_processed += 1
            self.total_busy_time += service_time

            for i in range(len(self.server_busy)):
                if self.server_busy[i]:
                    self.server_busy[i] = False
                    self.last_service_end[i] = end_service
                    break

            total_time_spent = end_service - start_service
            server_status = "busy" if any(self.server_busy) else "not busy"

            self.customers.append({
                "Customer ID": request_id,
                "Arrival time": arrival,
                "Service start time": start_service,
                "Service end time": end_service,
                "Total time spent": total_time_spent,
                "Queue time": queue_time,
                "Queue length at arrival": queue_length_at_arrival,
                "Server busy status": server_status,
                "Server idle time": max(self.idle_time),
                "Dropped": False
            })

    def generate_requests(self, user_count):
        arrival_rate = user_count / simulation_time
        self.env.process(self.process_request(0))
        for i in range(1, total_requests):
            yield self.env.timeout(np.random.exponential(1 / arrival_rate))
            self.env.process(self.process_request(i))

def run_simulation():
    env = simpy.Environment()
    system = TicketBookingSystem(env, num_servers)
    env.process(system.generate_requests(user_count))
    env.run(until=simulation_time)

    df = pd.DataFrame(system.customers)
    df.fillna(0, inplace=True)

    served = df[~df['Dropped']]
    avg_response_time = served['Total time spent'].mean()
    avg_wait_time = served['Queue time'].mean()
    max_wait_time = served['Queue time'].max()
    min_wait_time = served['Queue time'].min()
    throughput = len(served) / simulation_time
    drop_rate = system.dropped_requests / total_requests
    avg_queue_length = np.mean(system.queue_lengths)
    utilization = system.total_busy_time / (simulation_time * num_servers)

    metrics = {
        "Average Response Time": avg_response_time,
        "Average Wait Time": avg_wait_time,
        "Max Wait Time": max_wait_time,
        "Min Wait Time": min_wait_time,
        "Throughput (req/sec)": throughput,
        "Drop Rate": drop_rate,
        "Dropped Requests": system.dropped_requests,
        "Average Queue Length": avg_queue_length,
        "Server Utilization": utilization
    }

    return df, metrics

customer_table, sim_metrics = run_simulation()

with open("customer_table.txt", "w", encoding="utf-8") as f:
    f.write("=== Customer Table ===\n\n")
    f.write(customer_table.to_string(index=False))

print("Customer Table (first 10 rows):")
print(customer_table.head(10))

print("\nSimulation Metrics (in Minutes):")
for key, value in sim_metrics.items():
    if "Time" in key:
        print(f"{key}: {value / 60:.4f} min")
    else:
        print(f"{key}: {value:.4f}" if isinstance(value, float) else f"{key}: {value}")
