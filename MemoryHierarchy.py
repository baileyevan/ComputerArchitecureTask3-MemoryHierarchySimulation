from MemoryLevel import MemoryLevel
import random
from collections import OrderedDict

class MemoryHierarchy:
    def __init__(self, ssd_size, dram_size, l3_size, l2_size, l1_size, 
                 replacement_policy="FIFO", bandwidth=1):
        
        self.clock = 0
        self.bandwidth = bandwidth
        
        # Create memory levels with latencies
        self.ssd = MemoryLevel("SSD", ssd_size, latency=10, bandwidth=bandwidth)
        self.dram = MemoryLevel("DRAM", dram_size, latency=5, bandwidth=bandwidth)
        self.l3 = MemoryLevel("L3", l3_size, latency=3, bandwidth=bandwidth)
        self.l2 = MemoryLevel("L2", l2_size, latency=2, bandwidth=bandwidth)
        self.l1 = MemoryLevel("L1", l1_size, latency=1, bandwidth=bandwidth)
        
        # Set replacement policy
        for level in [self.l1, self.l2, self.l3]:
            level.policy = replacement_policy
        
        self.hierarchy = [self.l1, self.l2, self.l3, self.dram, self.ssd]
        self.pending_operations = []  # (data, current_level_idx, target_level_idx)
        
    def configure(self, ssd_size=None, dram_size=None, l3_size=None, l2_size=None, l1_size=None):
        """Allow runtime reconfiguration"""
        if ssd_size: self.ssd.size = ssd_size
        if dram_size: self.dram.size = dram_size
        if l3_size: self.l3.size = l3_size
        if l2_size: self.l2.size = l2_size
        if l1_size: self.l1.size = l1_size
    
    def preload_ssd(self, instructions):
        """Preload SSD with instructions"""
        for instr in instructions:
            if len(self.ssd.storage) < self.ssd.size:
                self.ssd.add_data(instr)
    
    def find_data_location(self, data):
        """Find which level contains the data"""
        if data in self.l1.storage_set:
            return self.l1, 0
        if data in self.l2.storage_set:
            return self.l2, 1
        if data in self.l3.storage_set:
            return self.l3, 2
        if data in self.dram.storage_set:
            return self.dram, 3
        if data in self.ssd.storage_set:
            return self.ssd, 4
        return None, -1
    
    def move_data_up(self, data, source_level, target_level, source_idx, target_idx):
        """Move data up the hierarchy with latency"""
        # Schedule transfers through intermediate levels
        current = source_idx
        while current > target_idx:
            # Move from current level to next higher level
            if current == 4:  # SSD to DRAM
                next_level = self.dram
                next_idx = 3
                latency = self.ssd.latency
            elif current == 3:  # DRAM to L3
                next_level = self.l3
                next_idx = 2
                latency = self.dram.latency
            elif current == 2:  # L3 to L2
                next_level = self.l2
                next_idx = 1
                latency = self.l3.latency
            elif current == 1:  # L2 to L1
                next_level = self.l1
                next_idx = 0
                latency = self.l2.latency
            
            # Schedule the transfer
            cycles_needed = (latency + self.bandwidth - 1) // self.bandwidth
            self.pending_operations.append({
                'data': data,
                'from_level': current,
                'to_level': next_idx,
                'remaining_cycles': cycles_needed,
                'source_obj': self.get_level_by_idx(current),
                'target_obj': next_level
            })
            current = next_idx
        
        return True
    
    def get_level_by_idx(self, idx):
        """Get memory level object by index"""
        return [self.l1, self.l2, self.l3, self.dram, self.ssd][idx]
    
    def fetch_instruction(self, instruction):
        """Request an instruction (read operation)"""
        print(f"\n[Cycle {self.clock}] CPU requests instruction {instruction}")
        
        # Find where the data is
        location, idx = self.find_data_location(instruction)
        
        if location:
            # Data found at some level
            print(f"  {location.name}: HIT for {instruction}")
            location.hits += 1
            
            # If not in L1, need to move it up
            if idx > 0:
                self.move_data_up(instruction, location, self.l1, idx, 0)
        else:
            # Data not found anywhere (shouldn't happen if SSD is preloaded)
            print(f"  ERROR: Instruction {instruction} not found in hierarchy!")
    
    def update_pending_operations(self):
        """Process pending transfers with clock cycles"""
        completed = []
        
        for op in self.pending_operations[:]:
            op['remaining_cycles'] -= 1
            
            if op['remaining_cycles'] <= 0:
                # Transfer complete
                completed.append(op)
                self.pending_operations.remove(op)
                
                # Add data to target level
                op['target_obj'].add_data(op['data'], op['source_obj'].name)
        
        return completed
    
    def run_clock_cycle(self):
        """Advance the simulation by one clock cycle"""
        self.clock += 1
        print(f"\n=== CLOCK CYCLE {self.clock} ===")
        
        # Process pending transfers
        completed = self.update_pending_operations()
        
        # Report completed transfers
        for op in completed:
            print(f"  Transfer complete: {op['data']} now in {op['target_obj'].name}")
        
        return completed
    
    def run_requests(self, requests):
        """Run a sequence of instruction requests"""
        request_queue = list(requests)
        request_idx = 0
        
        while request_idx < len(request_queue) or self.pending_operations:
            # Issue new request if no pending operations or at start of cycle
            if request_idx < len(request_queue) and len(self.pending_operations) < self.bandwidth * 2:
                self.fetch_instruction(request_queue[request_idx])
                request_idx += 1
            
            # Advance clock
            self.run_clock_cycle()
            
            # Small delay for readability
            # input("Press Enter to continue...")
    
    def print_configuration(self):
        """Print memory hierarchy configuration"""
        print("\n" + "="*50)
        print("MEMORY HIERARCHY CONFIGURATION")
        print("="*50)
        print(f"SSD:  {self.ssd.size} instructions (Latency: {self.ssd.latency} cycles)")
        print(f"DRAM: {self.dram.size} instructions (Latency: {self.dram.latency} cycles)")
        print(f"L3:   {self.l3.size} instructions (Latency: {self.l3.latency} cycles)")
        print(f"L2:   {self.l2.size} instructions (Latency: {self.l2.latency} cycles)")
        print(f"L1:   {self.l1.size} instructions (Latency: {self.l1.latency} cycles)")
        print(f"Bandwidth: {self.bandwidth} instruction(s) per cycle")
        print(f"Replacement Policy: {self.l1.policy}")
        print("="*50)
    
    def print_final_state(self):
        """Print final state of all memory levels"""
        print("\n" + "="*50)
        print("FINAL MEMORY STATE")
        print("="*50)
        print(f"L1 Cache: {sorted(self.l1.storage)}")
        print(f"L2 Cache: {sorted(self.l2.storage)}")
        print(f"L3 Cache: {sorted(self.l3.storage)}")
        print(f"DRAM:     {sorted(self.dram.storage)}")
        print(f"SSD:      {sorted(self.ssd.storage)}")
        print("="*50)
    
    def print_stats(self):
        """Print cache performance statistics"""
        print("\n" + "="*50)
        print("PERFORMANCE STATISTICS")
        print("="*50)
        print(f"L1 Cache: {self.l1.hits} hits, {self.l1.misses} misses, "
              f"Hit Rate: {self.get_hit_rate(self.l1):.2%}")
        print(f"L2 Cache: {self.l2.hits} hits, {self.l2.misses} misses, "
              f"Hit Rate: {self.get_hit_rate(self.l2):.2%}")
        print(f"L3 Cache: {self.l3.hits} hits, {self.l3.misses} misses, "
              f"Hit Rate: {self.get_hit_rate(self.l3):.2%}")
        print(f"DRAM:     {self.dram.hits} hits, {self.dram.misses} misses")
        print(f"SSD:      {self.ssd.hits} hits, {self.ssd.misses} misses")
        print("="*50)
    
    def get_hit_rate(self, level):
        total = level.hits + level.misses
        return level.hits / total if total > 0 else 0
    
    def print_movement_trace(self, instruction):
        """Print data movement trace for an instruction"""
        pass  # Implemented in fetch_instruction
