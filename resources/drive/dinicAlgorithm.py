import numpy as np
from collections import deque
import pandas as pd
import time
import os

class DinicMatrix:
    def __init__(self, num_vertices):
        self.num_vertices = num_vertices
        self.capacity = np.zeros((num_vertices, num_vertices), dtype=np.int64)
        self.flow = np.zeros((num_vertices, num_vertices), dtype=np.int64)
        self.level = []
        self.ptr = []

    def add_edge(self, u, v, cap):
        if u < 0 or v < 0 or u >= self.num_vertices or v >= self.num_vertices:
            raise ValueError("Vertex index out of range")
        if cap < 0:
            raise ValueError("Capacity must be non-negative")
        self.capacity[u][v] = cap

    def bfs(self, source, sink):
        self.level = [-1] * self.num_vertices
        self.level[source] = 0
        q = deque([source])
        
        while q:
            u = q.popleft()
            for v in range(self.num_vertices):
                if self.level[v] < 0 and self.flow[u][v] < self.capacity[u][v]:
                    self.level[v] = self.level[u] + 1
                    q.append(v)
                    
        return self.level[sink] >= 0

    def dfs(self, u, sink, flow):
        if u == sink:
            return flow
            
        while self.ptr[u] < self.num_vertices:
            v = self.ptr[u]
            if self.level[v] == self.level[u] + 1 and self.flow[u][v] < self.capacity[u][v]:
                curr_flow = min(flow, self.capacity[u][v] - self.flow[u][v])
                temp_flow = self.dfs(v, sink, curr_flow)
                
                if temp_flow > 0:
                    self.flow[u][v] += temp_flow
                    self.flow[v][u] -= temp_flow
                    return temp_flow
                    
            self.ptr[u] += 1
        return 0

    def max_flow(self, source, sink):
        if source < 0 or sink < 0 or source >= self.num_vertices or sink >= self.num_vertices:
            raise ValueError("Source or sink vertex index out of range")
            
        total_flow = 0
        while self.bfs(source, sink):
            self.ptr = [0] * self.num_vertices
            while True:
                flow = self.dfs(source, sink, float('inf'))
                if flow == 0:
                    break
                total_flow += flow
        return total_flow

def get_dinic_result(source, destination):
    try:
        start_time = time.time()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, 'results.csv')
        data = pd.read_csv(csv_path)
        graph = DinicMatrix(num_vertices=230)
        for i in range(data.shape[0]):
            graph.add_edge(data.iloc[i, 0], data.iloc[i, 1], int(data.iloc[i, -1]))
            
        
        max_flow_value = graph.max_flow(source,destination)
        
        print(f"Execution time: {time.time() - start_time}  seconds")
        
        final_matrix = []
        for i in range(graph.num_vertices):
            for j in range(graph.num_vertices):
                if graph.flow[i][j] > 0:  
                    final_matrix.append({
                        'source': i,
                        'destination': j,
                        'flow': int(graph.flow[i][j])
                    })
        
        return final_matrix
        
    except FileNotFoundError as e:
        print(f"\nFile not found error: {str(e)}")
        return None
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        return None

def run_test():    
    try:
        result = get_dinic_result(0,229)
        # print(f"Final result: {result}")
    except Exception as e:
        print(f"Test failed: {str(e)}")

if __name__ == "__main__":
    run_test()