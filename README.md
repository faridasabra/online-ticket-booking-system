# Ticket Booking System Simulation

## Overview
This project simulates a **ticket booking system** using **SimPy**, a process-based discrete-event simulation framework. The simulation models the arrival of ticket requests, their processing by servers, and tracks key performance metrics such as **average response time, server utilization, and dropped requests** due to overload.

## Features
- **Simulates ticket request arrivals** based on an exponential inter-arrival time.
- **Models server resource allocation** using SimPy's `Resource`.
- **Calculates average response time** for processed requests.
- **Tracks server utilization** to measure system efficiency.
- **Counts dropped requests** when wait time exceeds a threshold.
- **Visualizes results in a PNG table** summarizing performance metrics.

## Technologies Used
- **Python 3**
- **SimPy** (Discrete-event simulation)
- **NumPy** (Statistical calculations)
- **Matplotlib** (Plotting results & generating table PNG)

## How It Works
### 1. Request Generation
The system generates ticket requests at a rate of **2.5 requests per second** using an **exponential distribution**.

### 2. Server Processing
- Servers process requests with an average **service time of 200ms (0.2s)**.
- If no server is available, requests **wait in a queue**.
- If a request waits too long (>500ms), it is **dropped**.

### 3. Performance Metrics
- **Average Response Time:** Time taken to process a request.
- **Server Utilization:** Percentage of time servers are busy.
- **Dropped Requests:** Requests that exceeded wait threshold.

### 4. Results
- The simulation runs for **100 seconds**.
- Performance metrics are collected and **saved as a table in `simulation_results.png`**.

## Key Observations
- More than **4 servers** are needed to keep response time below **500ms**.
- Adding servers **reduces response time and dropped requests**.
- Server utilization **decreases** as more servers are added.
- **Auto-scaling** could optimize server usage dynamically.

## Future Enhancements
- Implement **dynamic auto-scaling** to adjust server count.
- Add **priority-based request handling**.
- Simulate **real-world network latency & failures**.
- Extend simulation with **database query delays**.

## License
This project is licensed under the MIT License. 