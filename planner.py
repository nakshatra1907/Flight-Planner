from flight import Flight

class Heap:
    def __init__(self, init_array=[]):
        self.heap = init_array
        n = len(init_array)
        for i in range(n // 2 - 1, -1, -1):
            self.downheap(i)

    def downheap(self, index):
        n = len(self.heap)
        walk = index
        left_child_index = 2 * index + 1
        right_child_index = 2 * index + 2

        if left_child_index < n and self.heap[left_child_index] < self.heap[walk]:
            walk = left_child_index
        if right_child_index < n and self.heap[right_child_index] < self.heap[walk]:
            walk = right_child_index
        if walk != index:
            self.heap[walk], self.heap[index] = self.heap[index], self.heap[walk]
            self.downheap(walk)

    def upheap(self, index):
        parent_index = (index - 1) // 2
        while index > 0 and self.heap[index] < self.heap[parent_index]:
            self.heap[index], self.heap[parent_index] = self.heap[parent_index], self.heap[index]
            index = parent_index
            parent_index = (index - 1) // 2

    def insert(self, value):
        self.heap.append(value)
        self.upheap(len(self.heap) - 1)

    def extract(self):
        if self.size() == 0:
            return None
        root = self.top()
        last = self.heap.pop()
        if self.size() > 0:
            self.heap[0] = last
            self.downheap(0)
        return root

    def top(self):
        if self.size() == 0:
            return None
        return self.heap[0]

    def size(self):
        return len(self.heap)


class Queue:
    def __init__(self):
        self.queue = []
        self.front = 0

    def append(self, item):
        self.queue.append(item)

    def pop(self):
        if self.front < len(self.queue):
            item = self.queue[self.front]
            self.front += 1
            return item
        else:
            raise IndexError("pop from empty queue")

    def is_empty(self):
        return self.front == len(self.queue)


class RouteNode:
    def __init__(self, flight, previous=None):
        self.flight = flight
        self.previous = previous
        if previous is not None:
            self.size = self.previous.size + 1
        else:
            self.size = 1

    def to_list(self):
        route = []
        current = self
        while current:
            route.append(current.flight)
            current = current.previous
        route.reverse()
        return route


class Planner:
    def __init__(self, flights):
        """The Planner

        Args:
            flights (List[Flight]): A list of information of all the flights (objects of class Flight)
        """
        max_city = max(max(flight.end_city for flight in flights), max(flight.start_city for flight in flights))
        self.graph = [[] for i in range(max_city + 1)]
        for flight in flights:
            self.graph[flight.start_city].append(flight)
        pass

    def least_flights_earliest_route(self, start_city, end_city, t1, t2):
        """
        Return List[Flight]: A route from start_city to end_city, which departs after t1 (>= t1) and
        arrives before t2 (<=) satisfying:
        The route has the least number of flights, and within routes with same number of flights,
        arrives the earliest
        """
        q = Queue()
        visited = [float("inf")] * len(self.graph)
        q.append((start_city, None, t1))
        visited[start_city] = t1
        ans = None
        n = 1e11
        t=1e11
        if start_city==end_city:
            return []
        while not q.is_empty():
            current_city, current_route_node, current_time = q.pop()
            if current_city == end_city:
                if current_route_node.size < n:
                    t=current_time
                    n = current_route_node.size
                    ans = current_route_node
                elif current_route_node.size == n:
                    if current_time<t:
                        t=current_time
                        ans = current_route_node
                continue
            for flight in self.graph[current_city]:
                if not current_route_node:
                    valid_departure = flight.departure_time >= current_time
                else:
                    valid_departure = flight.departure_time >= current_time + 20

                if (valid_departure and flight.arrival_time <= t2 and flight.arrival_time < visited[flight.end_city]):
                    visited[flight.end_city] = flight.arrival_time
                    new_route_node = RouteNode(flight, current_route_node)
                    q.append((flight.end_city, new_route_node, flight.arrival_time))
        if ans is None:
            return []
        return ans.to_list()

        pass

    def cheapest_route(self, start_city, end_city, t1, t2):
        """
        Return List[Flight]: A route from start_city to end_city, which departs after t1 (>= t1) and
        arrives before t2 (<=) satisfying:
        The route is a cheapest route
        """
        heap = Heap()
        heap.insert((0, start_city, t1, None))
        visited = [float('inf')] * len(self.graph)
        ans = None
        fare = 1e11
        if start_city == end_city:
            return []
        while heap.size():
            total_fare, current_city, current_time, current_route_node = heap.extract()
            if current_city == end_city:
                if total_fare < fare:
                    ans = current_route_node
                    fare = total_fare
                continue

            if total_fare >= visited[current_city]:
                continue
            visited[current_city] = total_fare

            for flight in self.graph[current_city]:
                if not current_route_node:
                    valid_departure = flight.departure_time >= current_time
                else:
                    valid_departure = flight.departure_time >= current_time + 20
                if valid_departure and flight.arrival_time <= t2:
                    new_fare = total_fare + flight.fare
                    new_route_node = RouteNode(flight, current_route_node)
                    heap.insert((new_fare, flight.end_city, flight.arrival_time, new_route_node))
        if ans is None:
            return []
        return ans.to_list()

        pass

    def least_flights_cheapest_route(self, start_city, end_city, t1, t2):
        """
        Return List[Flight]: A route from start_city to end_city, which departs after t1 (>= t1) and
        arrives before t2 (<=) satisfying:
        The route has the least number of flights, and within routes with same number of flights,
        is the cheapest
        """
        q = Queue()
        visited = [float("inf")] * len(self.graph)
        q.append((start_city, t1, 0, None))
        visited[start_city] = 0
        ans = None
        fare = 1e11
        n = 1e11
        if start_city==end_city:
            return []

        while not q.is_empty():
            current_city, current_time, current_fare, current_route_node = q.pop()
            if current_city == end_city:
                if current_route_node.size < n:
                    fare = current_fare
                    n = current_route_node.size
                    ans = current_route_node
                elif current_route_node.size == n:
                    if current_fare < fare:
                        fare = current_fare
                        ans = current_route_node
                continue
            for flight in self.graph[current_city]:
                if not current_route_node:
                    valid_departure = flight.departure_time >= current_time
                else:
                    valid_departure = flight.departure_time >= current_time + 20

                if (valid_departure and flight.arrival_time <= t2 and flight.fare + current_fare < visited[
                    flight.end_city]):
                    visited[flight.end_city] = flight.fare + current_fare
                    new_route_node = RouteNode(flight, current_route_node)
                    q.append((flight.end_city, flight.arrival_time, flight.fare + current_fare, new_route_node))
        if ans is None:
            return []
        return ans.to_list()
    
    
    
    
    
    
    
    
    
