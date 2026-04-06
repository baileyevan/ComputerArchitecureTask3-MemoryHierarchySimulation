import random
from collections import OrderedDict

class MemoryLevel:
    def __init__(self, name, size, latency=1, bandwidth=1):
        self.name = name
        self.size = size
        self.latency = latency  # cycles per transfer
        self.bandwidth = bandwidth  # instructions per cycle
        self.storage = []  # list of instructions
        self.storage_set = set()  # for O(1) lookup
        self.hits = 0
        self.misses = 0
        self.policy = "FIFO"  # Default replacement policy
        self.pending_transfers = []  # (data, source, target, remaining_cycles)
        
    def read(self, data):
        if data in self.storage_set:
            self.hits += 1
            # Update LRU order if using LRU
            if self.policy == "LRU" and hasattr(self, 'lru_order'):
                if data in self.lru_order:
                    self.lru_order.move_to_end(data)
            return True
        else:
            self.misses += 1
            return False
    
    def add_data(self, data, source=None):
        """Add data to this level (instant, for setup)"""
        if data not in self.storage_set:
            if len(self.storage) >= self.size:
                self.evict()
            self.storage.append(data)
            self.storage_set.add(data)
            if self.policy == "LRU":
                if not hasattr(self, 'lru_order'):
                    self.lru_order = OrderedDict()
                self.lru_order[data] = True
            if source:
                print(f"  {source} → {self.name}: {data}")
            else:
                print(f"  Added {data} to {self.name}")
    
    def evict(self):
        if self.policy == "FIFO":
            removed = self.storage.pop(0)
        elif self.policy == "LRU":
            removed, _ = self.lru_order.popitem(last=False)
            self.storage.remove(removed)
        elif self.policy == "Random":
            idx = random.randint(0, len(self.storage) - 1)
            removed = self.storage.pop(idx)
        
        self.storage_set.remove(removed)
        if self.policy == "LRU" and hasattr(self, 'lru_order') and removed in self.lru_order:
            del self.lru_order[removed]
        print(f"  Evicted {removed} from {self.name}")
        return removed
    
    def schedule_transfer(self, data, target, source_name, cycles):
        """Schedule a multi-cycle transfer"""
        self.pending_transfers.append({
            'data': data,
            'target': target,
            'source_name': source_name,
            'remaining': cycles
        })
    
    def update_transfers(self):
        """Update pending transfers, return completed ones"""
        completed = []
        for transfer in self.pending_transfers[:]:
            transfer['remaining'] -= 1
            if transfer['remaining'] <= 0:
                completed.append(transfer)
                self.pending_transfers.remove(transfer)
        return completed
