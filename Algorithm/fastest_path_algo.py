import math
import numpy as np


class FastestPath:
    def __init__(self):
        self.min_cost = 10000
        self.path = []

    def tsp(self, dist, vis, cur, cnt, n, cost, ans):
        if cnt == n:
            if cost < self.min_cost:
                self.min_cost = cost
                self.path = ans
                return
        for i in range(n):
            if vis[i] == False:
                if cost + dist[cur][i] > self.min_cost:
                    continue
                vis[i] = True
                new_ans = np.zeros(n)
                for k in range(cnt):
                    new_ans[k] = ans[k]
                new_ans[cnt] = i
                self.tsp(dist, vis, i, cnt + 1, n, cost + dist[cur][i], new_ans)
                vis[i] = False

    def plan_path(self, dist, n):
        visited = [False for i in range(n)]
        visited[0] = True
        ans = np.zeros(n)
        self.tsp(dist, visited, 0, 1, n, 0, ans)
        return self.path
