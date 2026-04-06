from MemoryHierarchy import MemoryHierarchy

def main():
    """Main function to run the memory hierarchy simulation"""
    # Configuration
    SSD_SIZE = 100
    DRAM_SIZE = 50
    L3_SIZE = 20
    L2_SIZE = 10
    L1_SIZE = 5
    
    # Create memory hierarchy
    memory = MemoryHierarchy(SSD_SIZE, DRAM_SIZE, L3_SIZE, L2_SIZE, L1_SIZE)
    
    # Print configuration
    memory.print_config()
    
    # Preload SSD with instructions 0-99
    memory.preload_ssd(list(range(100)))
    
    # Instruction requests
    requests = [3, 1, 6, 3, 7, 3, 10, 3, 5, 8, 3, 6]
    
    print("\n" + "="*60)
    print("INSTRUCTION ACCESS TRACE")
    print("="*60)
    print(f"Request sequence: {requests}")
    print("="*60)
    
    # Run simulation
    memory.run_simulation(requests)
    
    # Print results
    memory.print_final_state()
    memory.print_stats()
    
    print("\n Simulation complete!")

if __name__ == "__main__":
    main()