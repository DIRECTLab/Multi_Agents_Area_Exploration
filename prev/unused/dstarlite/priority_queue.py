import heapq


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def add_node(self, item, priority):
        # print('priority:', priority)
        # print('node:', item.position, item.rhs_value, item.g_value)
        heapq.heappush(self.elements, (priority, item))

    def get_node(self):
        item = heapq.heappop(self.elements)
        return item[1]

    def get_first_priority(self):
        return heapq.nsmallest(1, self.elements)[0][0]

    def erase_node(self, node):
        self.elements = [item for item in self.elements if item[1] != node]
        heapq.heapify(self.elements)

    def __iter__(self):
        for key, node in self.elements:
            yield node
