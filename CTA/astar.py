import heapq

class AStarPlanner:
    def __init__(self, map, resolution):
        self.map = map
        self.resolution = resolution
        self.neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]

    def heuristic(self, a, b):
        (x1, y1) = a
        (x2, y2) = b
        return abs(x1 - x2) + abs(y1 - y2)

    def search(self, start, goal):
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while frontier:
            current = heapq.heappop(frontier)[1]

            if current == goal:
                break

            for dx, dy in self.neighbors:
                next = (current[0] + dx, current[1] + dy)

                if not self.is_valid(next):
                    continue

                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goal, next)
                    heapq.heappush(frontier, (priority, next))
                    came_from[next] = current

        path = self.reconstruct_path(came_from, start, goal)
        return path

    def reconstruct_path(self, came_from, start, goal):
        current = goal
        path = [current]
        while current != start:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def is_valid(self, node):
        x, y = node
        if x < 0 or x >= len(self.map[0]) or y < 0 or y >= len(self.map):
            return False
        return self.map[y][x] == 0
