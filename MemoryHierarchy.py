from MemoryLevel import MemoryLevel

class MemoryHierarchy:
    def __init__(self, ssd_size, dram_size, l3_size, l2_size, l1_size):
        self.clock = 0
        
        # Create memory levels (largest to smallest)
        self.ssd = MemoryLevel("SSD", ssd_size, latency=10)
        self.dram = MemoryLevel("DRAM", dram_size, latency=5)
        self.l3 = MemoryLevel("L3", l3_size, latency=3)
        self.l2 = MemoryLevel("L2", l2_size, latency=2)
        self.l1 = MemoryLevel("L1", l1_size, latency=1)
        
        # Pending transfers queue
        self.pending_transfers = []
        
    def preload_ssd(self, instructions):
        """Preload SSD with instructions"""
        for instr in instructions:
            if len(self.ssd.storage) < self.ssd.size:
                self.ssd.storage.append(instr)
                self.ssd.storage_set.add(instr)
        print(f"Preloaded {len(self.ssd.storage)} instructions into SSD")
    
    def find_and_move_data(self, data):
        """Find data in hierarchy and schedule its movement to L1"""
        print(f"\n[Cycle {self.clock}] CPU requests instruction {data}")
        
        # Check each level from L1 down to SSD
        if self.l1.check_and_record(data, True):
            print(f"  Data already in L1! No movement needed.")
            return True
        
        if self.l2.check_and_record(data, True):
            print(f"  Found in L2! Moving to L1...")
            self.schedule_movement(data, self.l2, self.l1, self.l2.latency)
            return True
        
        if self.l3.check_and_record(data, True):
            print(f"  Found in L3! Moving to L2 then L1...")
            self.schedule_movement(data, self.l3, self.l2, self.l3.latency)
            self.schedule_movement(data, self.l2, self.l1, self.l2.latency)
            return True
        
        if self.dram.check_and_record(data, True):
            print(f"  Found in DRAM! Moving up through hierarchy...")
            self.schedule_movement(data, self.dram, self.l3, self.dram.latency)
            self.schedule_movement(data, self.l3, self.l2, self.l3.latency)
            self.schedule_movement(data, self.l2, self.l1, self.l2.latency)
            return True
        
        if self.ssd.check_and_record(data, True):
            print(f"  Found in SSD! Moving up through entire hierarchy...")
            # Schedule sequential movements: SSD→DRAM→L3→L2→L1
            self.schedule_movement(data, self.ssd, self.dram, self.ssd.latency)
            self.schedule_movement(data, self.dram, self.l3, self.dram.latency)
            self.schedule_movement(data, self.l3, self.l2, self.l3.latency)
            self.schedule_movement(data, self.l2, self.l1, self.l2.latency)
            return True
        
        print(f"  ERROR: Data {data} not found in hierarchy!")
        return False
    
    def schedule_movement(self, data, source, target, latency):
        """Schedule a data movement between levels"""
        self.pending_transfers.append({
            'data': data,
            'source': source,
            'target': target,
            'remaining': latency,
            'total_latency': latency
        })
        print(f"    Scheduled: {data} from {source.name} → {target.name} (takes {latency} cycles)")
    
    def process_clock_cycle(self):
        """Process one clock cycle - move data one step through pending transfers"""
        self.clock += 1
        print(f"\n=== CLOCK CYCLE {self.clock} ===")
        
        transfers_completed = []
        
        # Decrement remaining cycles for all pending transfers
        for transfer in self.pending_transfers[:]:
            transfer['remaining'] -= 1
            
            if transfer['remaining'] <= 0:
                # Transfer complete!
                transfers_completed.append(transfer)
                self.pending_transfers.remove(transfer)
        
        # Process completed transfers (add data to target)
        for transfer in transfers_completed:
            data = transfer['data']
            source = transfer['source']
            target = transfer['target']
            
            # Add to target level
            if target.add_data(data, source.name):
                pass
        
        return len(transfers_completed)
    
    def run_simulation(self, requests):
        """Run the complete simulation"""
        request_idx = 0
        total_requests = len(requests)
        
        while request_idx < total_requests or self.pending_transfers:
            # Issue new request if no pending transfers (or at start)
            if request_idx < total_requests and (not self.pending_transfers or self.clock == 0):
                self.find_and_move_data(requests[request_idx])
                request_idx += 1
            
            # Process one clock cycle
            if self.pending_transfers or request_idx < total_requests:
                self.process_clock_cycle()
    
    def print_final_state(self):
        """Print final state of all memory levels"""
        print("\n" + "="*60)
        print("FINAL MEMORY STATE")
        print("="*60)
        print(f"L1 Cache: {sorted(self.l1.storage)} (size: {len(self.l1.storage)}/{self.l1.size})")
        print(f"L2 Cache: {sorted(self.l2.storage)} (size: {len(self.l2.storage)}/{self.l2.size})")
        print(f"L3 Cache: {sorted(self.l3.storage)} (size: {len(self.l3.storage)}/{self.l3.size})")
        print(f"DRAM:     {sorted(self.dram.storage)} (size: {len(self.dram.storage)}/{self.dram.size})")
        print(f"SSD:      First 20: {sorted(self.ssd.storage)[:20]}... (total: {len(self.ssd.storage)})")
        print("="*60)
    
    def print_stats(self):
        """Print performance statistics"""
        print("\n" + "="*60)
        print("PERFORMANCE STATISTICS")
        print("="*60)
        
        def calc_hit_rate(level):
            total = level.hits + level.misses
            return (level.hits/total)*100 if total > 0 else 0
        
        print(f"L1 Cache:  Hits={self.l1.hits}, Misses={self.l1.misses}, Hit Rate={calc_hit_rate(self.l1):.1f}%")
        print(f"L2 Cache:  Hits={self.l2.hits}, Misses={self.l2.misses}, Hit Rate={calc_hit_rate(self.l2):.1f}%")
        print(f"L3 Cache:  Hits={self.l3.hits}, Misses={self.l3.misses}, Hit Rate={calc_hit_rate(self.l3):.1f}%")
        print(f"DRAM:      Hits={self.dram.hits}, Misses={self.dram.misses}")
        print(f"SSD:       Hits={self.ssd.hits}, Misses={self.ssd.misses}")
        print("="*60)
    
    def print_config(self):
        """Print configuration"""
        print("\n" + "="*60)
        print("MEMORY HIERARCHY CONFIGURATION")
        print("="*60)
        print(f"SSD:  {self.ssd.size} instructions (Latency: {self.ssd.latency} cycles)")
        print(f"DRAM: {self.dram.size} instructions (Latency: {self.dram.latency} cycles)")
        print(f"L3:   {self.l3.size} instructions (Latency: {self.l3.latency} cycles)")
        print(f"L2:   {self.l2.size} instructions (Latency: {self.l2.latency} cycles)")
        print(f"L1:   {self.l1.size} instructions (Latency: {self.l1.latency} cycles)")
        print(f"Policy: {self.l1.policy}")
        print("="*60)