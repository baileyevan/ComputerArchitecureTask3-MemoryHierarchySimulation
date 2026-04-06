class MemoryLevel:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.storage = []
        self.hits = 0
        self.misses = 0

    def read(self, data):
        if data in self.storage:
            self.hits += 1
            print(f"{self.name}: HIT for {data}")
            return True
        else:
            self.misses += 1
            print(f"{self.name}: MISS for {data}")
            return False

    def write(self, data, source=None):
        if data not in self.storage:
            if len(self.storage) >= self.size:
                self.evict()
            self.storage.append(data)
            if source:
                print(f"Moved {data} from {source} → {self.name}")
            else:
                print(f"Added {data} to {self.name}")
    
    def evict(self):
        removed = self.storage.pop(0) 
        print(f"Evicted {removed} from {self.name}")