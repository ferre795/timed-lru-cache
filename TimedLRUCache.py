import time
import threading
from enum import Enum

class CacheReturnState(Enum):
    HIT = "HIT"
    MISS = "MISS" 

class Node:
    def __init__(self, key, value, expires_at):
        self.key = key
        self.value = value
        self.expires_at = expires_at
        self.prev = None
        self.next = None    

class TimedLRUCache:
    def __init__(self, capacity: int, ttl: int, clock = time.monotonic):
        self.cache: dict[object, Node] = {}
        self.capacity = capacity
        self.ttl = ttl
        self.clock = clock

        self.lock = threading.Lock()

        self.hits = 0
        self.misses = 0
        self.removals = 0  
        self.expirations = 0
        self.get_ops = 0
        self.set_ops = 0


        self.head = Node(None, None, float("inf"))
        self.tail = Node(None, None, float("inf"))
        self.head.next = self.tail
        self.tail.prev = self.head

    def current_time(self) -> float: 
        return self.clock()
    
    def add_to_front(self, node: Node):
        node.prev = self.head
        second = self.head.next
        second.prev = node
        node.next = self.head.next
        self.head.next = node
        
    def remove_node(self, node: Node):
        node.prev.next = node.next
        if node.next:
            node.next.prev = node.prev
        node.prev = node.next = None

    def move_to_front(self, node: Node):
        self.remove_node(node)
        self.add_to_front(node)
    
    def popLRU(self) -> Node | None:
        lru = self.tail.prev
        if lru is self.head:
            return None
        self.remove_node(lru)
        return lru
        
    
    def get(self, key: int):
        with self.lock:
            self.get_ops += 1
            node = self.cache.get(key)
            if node is None:
                self.misses += 1
                return None, CacheReturnState.MISS.value

            now = self.current_time()
            if now >= node.expires_at:
                self.remove_node(node)
                del self.cache[key]
                self.misses += 1
                self.expirations += 1
                return None, CacheReturnState.MISS.value

            self.move_to_front(node)
            self.hits += 1
            return node.value, CacheReturnState.HIT.value

    def set(self, key: int, value: int):
        with self.lock:
            self.set_ops += 1
            now = self.current_time()
            expiry = now + self.ttl

            node = self.cache.get(key)
            if node:
                node.value = value
                node.expires_at  = expiry
                self.move_to_front(node)
            else:
                node = Node(key, value, expiry)
                self.cache[key] = node
                self.add_to_front(node)

                while len(self.cache) > self.capacity:
                    removed = self.popLRU()
                    if removed is None:
                        break
                    
                    if self.current_time() >= removed.expires_at:
                        self.expirations += 1
                    else:
                        self.removals += 1

                    del self.cache[removed.key]
    
    def stats(self) -> dict:
        with self.lock:
            return {
                "size": len(self.cache),
                "capacity": self.capacity,
                "hits": self.hits,
                "misses": self.misses,
                "removals": self.removals,
                "expirations": self.expirations,
                "get_ops": self.get_ops,
                "set_ops": self.set_ops
            }
        

    def reset_stats(self):
        with self.lock:
            self.hits = 0
            self.misses = 0
            self.removals = 0  
            self.expirations = 0
            self.get_ops = 0
            self.set_ops = 0



            


