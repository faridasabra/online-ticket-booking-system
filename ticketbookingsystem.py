import simpy
import numpy as np
import pandas as pd

# Define basic parameters
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
        self.idle_time = [0] * num_servers  # Track idle times per server
        self.env.process(self.monitor_queue())

    def monitor_queue(self):
        while True:
            self.queue_lengths.append(len(self.server.queue))
            yield self.env.timeout(0.5)

    def process_request(self, request_id):
        arrival = self.env.now
        queue_length_at_arrival = len(self.server.queue)

        # Check if any server is busy
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

            # Start processing the request
            start_service = self.env.now
            queue_time = start_service - arrival

            # Find the first available server and mark it as busy
            for i in range(len(self.server_busy)):
                if not self.server_busy[i]:
                    # Add idle time before the service starts
                    if self.last_service_end[i] < start_service:
                        self.idle_time[i] += start_service - self.last_service_end[i]
                    self.server_busy[i] = True  # Mark this server as busy
                    self.last_service_end[i] = start_service  # Update the time when this server starts serving
                    break

            # Process the request for the specified service time
            yield self.env.timeout(service_time)
            end_service = self.env.now

            self.total_processed += 1
            self.total_busy_time += service_time

            # Once the service is complete, mark the server as idle
            for i in range(len(self.server_busy)):
                if self.server_busy[i]:  # Find the busy server
                    self.server_busy[i] = False  # Mark the server as idle
                    self.last_service_end[i] = end_service  # Update the time when this server becomes idle
                    break

            # Calculate the total time spent (start_time + end_time)
            total_time_spent = end_service - start_service  # Correcting the calculation

            # Calculate the server status after the request
            server_status = "busy" if any(self.server_busy) else "not busy"

            # Log the customer details
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
        # First customer arrives at time 0
        self.env.process(self.process_request(0))
    
        # For subsequent customers, generate random inter-arrival times
        for i in range(1, total_requests):
            yield self.env.timeout(np.random.exponential(1 / arrival_rate))
            self.env.process(self.process_request(i))


def run_simulation():
    env = simpy.Environment()
    system = TicketBookingSystem(env, num_servers)
    env.process(system.generate_requests(user_count))
    env.run(until=simulation_time)

    df = pd.DataFrame(system.customers)

    # Handling potential NaN values before metrics calculations
    df.fillna(0, inplace=True)  # Filling NaN with 0 for calculations

    # Metrics
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

# Run the simulation
customer_table, sim_metrics = run_simulation()

# Save to TXT
with open("customer_table.txt", "w", encoding="utf-8") as f:
    f.write("=== Customer Table ===\n\n")
    f.write(customer_table.to_string(index=False))

print("Customer Table (first 10 rows):")
print(customer_table.head(10))  # Display first 10 rows in console

print("\nSimulation Metrics (in Minutes):")
for key, value in sim_metrics.items():
    if "Time" in key:
        print(f"{key}: {value / 60:.4f} min")
    else:
        print(f"{key}: {value:.4f}" if isinstance(value, float) else f"{key}: {value}")