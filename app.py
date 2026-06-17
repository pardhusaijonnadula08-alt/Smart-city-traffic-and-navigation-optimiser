import heapq

class CityMap:
    def __init__(self):
        # Adjacency list: { intersection: { neighbor: base_travel_time } }
        self.graph = {}
        # Stores live traffic multipliers: { (u, v): multiplier }
        self.traffic_conditions = {}

    def add_intersection(self, name):
        """Adds a new intersection/node to the city map."""
        if name not in self.graph:
            self.graph[name] = {}

    def add_road(self, u, v, base_time):
        """Adds a two-way road between intersection u and v with a base travel time."""
        self.add_intersection(u)
        self.add_intersection(v)
        self.graph[u][v] = base_time
        self.graph[v][u] = base_time  # Two-way street

    def update_traffic(self, u, v, congestion_multiplier):
        """
        Updates traffic conditions on a road.
        1.0 = Normal traffic
        2.5 = Heavy traffic (takes 2.5x longer)
        """
        if u in self.graph and v in self.graph[u]:
            self.traffic_conditions[(u, v)] = congestion_multiplier
            self.traffic_conditions[(v, u)] = congestion_multiplier
            print(f"[TRAFFIC UPDATE] Congestion on road {u} <-> {v} is now {congestion_multiplier}x!")
        else:
            print(f"[ERROR] Road between {u} and {v} does not exist.")

    def get_edge_weight(self, u, v, is_emergency=False):
        """Calculates the actual travel time factoring in traffic and emergency status."""
        base_time = self.graph[u][v]
        multiplier = self.traffic_conditions.get((u, v), 1.0)
        
        if is_emergency:
            # Emergency vehicles bypass standard traffic delays (multiplier treated as 1.0)
            # and get a 20% speed boost on the open road due to sirens clearing paths
            return base_time * 0.8
        else:
            return base_time * multiplier

    def find_optimal_route(self, start, destination, is_emergency=False):
        """
        Dijkstra's Algorithm Implementation.
        Finds the fastest route from start to destination.
        """
        if start not in self.graph or destination not in self.graph:
            return None, float('inf')

        # Priority Queue stores tuples of: (cumulative_time, current_node)
        priority_queue = [(0, start)]
        
        # Track the absolute shortest time to reach each intersection
        shortest_times = {node: float('inf') for node in self.graph}
        shortest_times[start] = 0
        
        # Track parent pointers to reconstruct the final driving path
        previous_nodes = {node: None for node in self.graph}

        while priority_queue:
            current_time, current_node = heapq.heappop(priority_queue)

            # If we reached our destination, we can stop early
            if current_node == destination:
                break

            # If we found a longer path to an already processed node, skip it
            if current_time > shortest_times[current_node]:
                continue

            # Check all neighboring intersections
            for neighbor in self.graph[current_node]:
                weight = self.get_edge_weight(current_node, neighbor, is_emergency)
                time_to_neighbor = current_time + weight

                # If this new path is faster, record it!
                if time_to_neighbor < shortest_times[neighbor]:
                    shortest_times[neighbor] = time_to_neighbor
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(priority_queue, (time_to_neighbor, neighbor))

        # Reconstruct the path from destination back to start
        path = []
        curr = destination
        while curr is not None:
            path.append(curr)
            curr = previous_nodes[curr]
        path.reverse()  # Reverse to get start -> destination order

        # If the destination is unreachable
        if shortest_times[destination] == float('inf'):
            return None, float('inf')

        return path, shortest_times[destination]


# =====================================================================
# SIMULATION / TESTING UTILITY
# =====================================================================
if __name__ == "__main__":
    # 1. Initialize our Smart City Engine
    city = CityMap()

    # 2. Build a city network layout
    # Nodes: Suburbs, Main Street, Uptown, Midtown, Downtown, Highway Link
    city.add_road("Suburbs", "Main_Street", base_time=10)
    city.add_road("Suburbs", "Highway_Link", base_time=5)
    city.add_road("Main_Street", "Midtown", base_time=8)
    city.add_road("Highway_Link", "Uptown", base_time=12)
    city.add_road("Midtown", "Downtown", base_time=6)
    city.add_road("Uptown", "Downtown", base_time=10)
    city.add_road("Main_Street", "Uptown", base_time=3)

    print("--- SCENARIO 1: Normal Morning Commute (Standard Civilian) ---")
    path, total_time = city.find_optimal_route("Suburbs", "Downtown", is_emergency=False)
    print(f"Optimal Civilian Path: {' -> '.join(path)}")
    print(f"Estimated Travel Time: {total_time:.1f} minutes\n")

    print("--- SCENARIO 2: Major Accident & Traffic Spike ---")
    # A massive accident happens on Main Street connecting to Midtown
    city.update_traffic("Main_Street", "Midtown", congestion_multiplier=5.0)
    
    # Recalculate route for a standard driver
    path, total_time = city.find_optimal_route("Suburbs", "Downtown", is_emergency=False)
    print(f"New Civilian Path: {' -> '.join(path)}")
    print(f"Adjusted Travel Time: {total_time:.1f} minutes\n")

    print("--- SCENARIO 3: Emergency Vehicle Dispatch (Ambulance) ---")
    # Dispatch an ambulance along the exact same route during the traffic crisis
    amb_path, amb_time = city.find_optimal_route("Suburbs", "Downtown", is_emergency=True)
    print(f"Ambulance Override Path: {' -> '.join(amb_path)}")
    print(f"Emergency Arrival Time: {amb_time:.1f} minutes\n")

import streamlit as st
import heapq
import networkx as nx
import matplotlib.pyplot as plt

# =====================================================================
# BACKEND ENGINE (CityMap Class)
# =====================================================================
class CityMap:
    def __init__(self):
        self.graph = {}
        self.traffic_conditions = {}

    def add_intersection(self, name):
        if name not in self.graph:
            self.graph[name] = {}

    def add_road(self, u, v, base_time):
        self.add_intersection(u)
        self.add_intersection(v)
        self.graph[u][v] = base_time
        self.graph[v][u] = base_time

    def update_traffic(self, u, v, congestion_multiplier):
        if u in self.graph and v in self.graph[u]:
            self.traffic_conditions[(u, v)] = congestion_multiplier
            self.traffic_conditions[(v, u)] = congestion_multiplier

    def get_edge_weight(self, u, v, is_emergency=False):
        base_time = self.graph[u][v]
        multiplier = self.traffic_conditions.get((u, v), 1.0)
        if is_emergency:
            return base_time * 0.8  # Bypasses traffic + 20% speed boost
        return base_time * multiplier

    def find_optimal_route(self, start, destination, is_emergency=False):
        if start not in self.graph or destination not in self.graph:
            return None, float('inf')

        priority_queue = [(0, start)]
        shortest_times = {node: float('inf') for node in self.graph}
        shortest_times[start] = 0
        previous_nodes = {node: None for node in self.graph}

        while priority_queue:
            current_time, current_node = heapq.heappop(priority_queue)

            if current_node == destination:
                break

            if current_time > shortest_times[current_node]:
                continue

            for neighbor in self.graph[current_node]:
                weight = self.get_edge_weight(current_node, neighbor, is_emergency)
                time_to_neighbor = current_time + weight

                if time_to_neighbor < shortest_times[neighbor]:
                    shortest_times[neighbor] = time_to_neighbor
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(priority_queue, (time_to_neighbor, neighbor))

        path = []
        curr = destination
        while curr is not None:
            path.append(curr)
            curr = previous_nodes[curr]
        path.reverse()

        if shortest_times[destination] == float('inf'):
            return None, float('inf')

        return path, shortest_times[destination]

# =====================================================================
# FRONTEND INTERFACE (Streamlit Application)
# =====================================================================

# Initialize the city network map session state so it doesn't reset on click
if 'city' not in st.session_state:
    city = CityMap()
    city.add_road("Suburbs", "Main_Street", base_time=10)
    city.add_road("Suburbs", "Highway_Link", base_time=5)
    city.add_road("Main_Street", "Midtown", base_time=8)
    city.add_road("Highway_Link", "Uptown", base_time=12)
    city.add_road("Midtown", "Downtown", base_time=6)
    city.add_road("Uptown", "Downtown", base_time=10)
    city.add_road("Main_Street", "Uptown", base_time=3)
    st.session_state.city = city

city = st.session_state.city

# Title Block
st.set_page_config(layout="wide")
st.title("🌐 Smart City Traffic & Navigation Optimizer")
st.markdown("A real-time backend engine visualizing shortest path variants using Dijkstra's Algorithm.")
st.markdown("---")

# Layout Splitting: Sidebar Controls vs Main View
sidebar = st.sidebar
sidebar.header("🛠️ Simulation Controls")

# 1. Navigation Panel
sidebar.subheader("1. Route Planning")
nodes_list = sorted(list(city.graph.keys()))
start_node = sidebar.selectbox("Departure Point", nodes_list, index=0)
end_node = sidebar.selectbox("Destination Point", nodes_list, index=len(nodes_list)-1)
vehicle_type = sidebar.radio("Vehicle Classification", ["Standard Civilian Vehicle", "Emergency Vehicle (Ambulance)"])
is_emergency = (vehicle_type == "Emergency Vehicle (Ambulance)")

# 2. Traffic Controller Panel
sidebar.subheader("2. Live Traffic Modifier")
all_edges = []
for u in city.graph:
    for v in city.graph[u]:
        if (v, u) not in all_edges:
            all_edges.append((u, v))

selected_edge = sidebar.selectbox("Select Target Road Segment", all_edges, format_func=lambda x: f"{x[0]} ↔️ {x[1]}")
congestion_level = sidebar.slider("Congestion Multiplier", min_value=1.0, max_value=10.0, value=1.0, step=0.5)

if sidebar.button("Apply Traffic Spike"):
    city.update_traffic(selected_edge[0], selected_edge[1], congestion_level)
    st.toast(f"Traffic updated for {selected_edge[0]}-{selected_edge[1]}!", icon="🚨")

# MAIN FRAME - Logic Processing
path, total_time = city.find_optimal_route(start_node, end_node, is_emergency)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📊 Execution Diagnostics")
    if path:
        st.success(f"**Optimal Route Identified!**")
        st.metric(label="Calculated Runtime Duration", value=f"{total_time:.1f} Mins")
        st.markdown("**Turn-by-Turn Navigation Strategy:**")
        st.write(" ➔ ".join([f"`{node}`" for node in path]))
    else:
        st.error("Destination route completely unreachable due to server-side disconnects.")

with col2:
    st.subheader("🗺️ Live Topology Graph Matrix")
    
    # Render map using NetworkX and Matplotlib
    G = nx.Graph()
    for u in city.graph:
        for v in city.graph[u]:
            G.add_edge(u, v, weight=city.get_edge_weight(u, v, is_emergency))
            
    pos = nx.spring_layout(G, seed=42) # Consistent layout structure
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Highlighting the path nodes and edges
    path_edges = []
    if path:
        path_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
        
    # Draw standard structural elements
    nx.draw_networkx_nodes(G, pos, node_color="#2b5c8f", node_size=800, ax=ax)
    nx.draw_networkx_labels(G, pos, font_color="white", font_size=9, font_weight="bold", ax=ax)
    
    # Regular roads vs Active Route segments colors
    nx.draw_networkx_edges(G, pos, edgelist=[e for e in G.edges() if e not in path_edges and (e[1], e[0]) not in path_edges], edge_color="#b2bec3", width=2, ax=ax)
    if path_edges:
        route_color = "#e74c3c" if is_emergency else "#2ecc71"
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color=route_color, width=5, ax=ax)

    # Adding edge weights as labels
    edge_labels = {}
    for u, v in G.edges():
        weight = city.get_edge_weight(u, v, is_emergency)
        edge_labels[(u, v)] = f"{weight:.1f}m"
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax)
    
    plt.axis("off")
    st.pyplot(fig)