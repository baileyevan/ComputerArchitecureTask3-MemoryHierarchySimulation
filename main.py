# memory_hierarchy.py
import random
from collections import OrderedDict
from MemoryLevel import MemoryLevel
from MemoryHierarchy import MemoryHierarchy


def main():
    """Main function to run the memory hierarchy simulation"""
    
    # Configuration
    SSD_SIZE = 100
    DRAM_SIZE = 50
    L3_SIZE = 20
    L2_SIZE = 10
    L1_SIZE = 5
    REPLACEMENT_POLICY = "LRU"  # Options: "FIFO", "LRU", "Random"
    BANDWIDTH = 1  # Instructions per cycle
    
    # Create memory hierarchy
    memory = MemoryHierarchy(SSD_SIZE, DRAM_SIZE, L3_SIZE, L2_SIZE, L1_SIZE,
                             replacement_policy=REPLACEMENT_POLICY,
                             bandwidth=BANDWIDTH)
    
    # Print configuration
    memory.print_configuration()
    
    # Preload SSD with instructions 0-99
    memory.preload_ssd(list(range(100)))
    
    # Instruction access trace
    # Modify this to test different access patterns
    instruction_requests = [3, 1, 6, 3, 7, 3, 10, 3, 5, 8, 3, 6]
    
    print("\n" + "="*50)
    print("INSTRUCTION ACCESS TRACE")
    print("="*50)
    print(f"Requests: {instruction_requests}")
    print("="*50)
    
    # Run the simulation
    memory.run_requests(instruction_requests)
    
    # Print final state and statistics
    memory.print_final_state()
    memory.print_stats()
    
    print("\nSimulation complete!")


if __name__ == "__main__":
    main()