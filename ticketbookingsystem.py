import simpy
import numpy as np
import matplotlib.pyplot as plt

arrival_rate = 2.5  
service_time = 0.2  
simulation_time = 100  
dropped_threshold = 0.5  

class TicketBookingSystem:
    def __init__(self, env, num_servers):
        self.env = env
        self.server = simpy.Resource(env, num_servers)
        self.response_times = []
        self.total_busy_time = 0  
        self.dropped_requests = 0  

    def process_request(self, request_id):
        arrival_time = self.env.now  
        with self.server.request() as request:
            yield request  
            wait_time = self.env.now - arrival_time  

            if wait_time > dropped_threshold:
                self.dropped_requests += 1
                return  

            self.total_busy_time +=service_time  
            yield self.env.timeout(service_time)  
        
        response_time = self.env.now - arrival_time
        self.response_times.append(response_time)

def generate_requests(env, system):
    request_id = 0
    while True:
        yield env.timeout(np.random.exponential(1 / arrival_rate))  
        env.process(system.process_request(request_id))  
        request_id += 1

def run_simulation(num_servers):
    env = simpy.Environment()
    system = TicketBookingSystem(env, num_servers)
    env.process(generate_requests(env, system))
    env.run(until=simulation_time)

    utilization = system.total_busy_time / (simulation_time * num_servers)

    return {
        "average_response_time": np.mean(system.response_times),
        "server_utilization": utilization,
        "dropped_requests": system.dropped_requests
    }

server_counts = [1, 2, 3, 5, 13]
results = {}

for servers in server_counts:
    stats = run_simulation(servers)
    results[servers] = stats

# extracting values for plotting
avg_response_times = [results[s]["average_response_time"] for s in server_counts]
utilizations = [results[s]["server_utilization"] for s in server_counts]
dropped_requests = [results[s]["dropped_requests"] for s in server_counts]

# plotting response time vs. number of servers
plt.figure(figsize=(8, 5))
plt.plot(server_counts, avg_response_times, marker='o', linestyle='-', label="Avg Response Time")
plt.axhline(y=dropped_threshold, color='r', linestyle='--', label="500ms Threshold")
plt.xlabel("Number of Servers")
plt.ylabel("Avg Response Time (seconds)")
plt.title("Response Time vs Number of Servers")
plt.legend()
plt.grid()
plt.savefig("response_time.png", dpi=300)

# plotting server utilization vs. number of servers
plt.figure(figsize=(8, 5))
plt.plot(server_counts, utilizations, marker='s', linestyle='-', label="Server Utilization")
plt.xlabel("Number of Servers")
plt.ylabel("Utilization (0-1 scale)")
plt.title("Server Utilization vs Number of Servers")
plt.axhline(y=0.85, color='r', linestyle='--', label="85% Threshold (Risk of Overload)")
plt.legend()
plt.grid()
plt.savefig("server_utilization.png", dpi=300)

# plotting dropped requests vs. number of servers
plt.figure(figsize=(8, 5))
plt.plot(server_counts, dropped_requests, marker='x', linestyle='-', label="Dropped Requests")
plt.xlabel("Number of Servers")
plt.ylabel("Dropped Requests")
plt.title("Dropped Requests vs Number of Servers")
plt.grid()
plt.legend()
plt.savefig("dropped_requests.png", dpi=300)

# final results
table_data = []
for servers, stats in results.items():
    table_data.append([
        servers,
        f"{stats['average_response_time']:.3f}s",
        f"{stats['server_utilization']:.2%}",
        stats['dropped_requests']
    ])

headers = ["Servers", "Avg Response Time", "Utilization (%)", "Dropped Requests"]

fig, ax = plt.subplots(figsize=(6, 3))
ax.axis("tight")
ax.axis("off")
table = ax.table(cellText=table_data, colLabels=headers, cellLoc="center", loc="center")

table_filename = "simulation_results.png"
plt.savefig(table_filename, dpi=300, bbox_inches="tight")