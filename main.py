from MemoryLevel import MemoryLevel
from readWriteLogic import fetch


def printState(L1, L2, L3, dram, ssd):
    print("\nFinal Memory State:")
    print(f"L1 Cache: {L1.storage}")
    print(f"L2 Cache: {L2.storage}")
    print(f"L3 Cache: {L3.storage}")
    print(f"DRAM: {dram.storage}")
    print(f"SSD: {ssd.storage}")

def printStats(L1, L2, L3, dram, ssd):
    print("\nCache Performance Stats:")
    print(f"L1 Cache: {L1.hits} hits, {L1.misses} misses")
    print(f"L2 Cache: {L2.hits} hits, {L2.misses} misses")
    print(f"L3 Cache: {L3.hits} hits, {L3.misses} misses")
    print(f"DRAM: {dram.hits} hits, {dram.misses} misses")
    print(f"SSD: {ssd.hits} hits, {ssd.misses} misses")

def main():

    """Setup"""
    ssd = MemoryLevel("SSD", 100)
    dram = MemoryLevel("DRAM", 50)
    L3 = MemoryLevel("L3", 20)
    L2 = MemoryLevel("L2", 10)
    L1 = MemoryLevel("L1", 5)

    hierarchy = [L1, L2, L3, dram, ssd]

    """Preloading data into memory levels"""
    ssd.storage = [i for i in range(100)]

    #each number is a instruction being requested
    requests = [3, 1, 6, 3]

    clock = 0
    for req in requests:
        clock += 1
        print(f"\n--- Clock Cycle {clock} ---")
        fetch(req, L1, L2, L3, dram, ssd)


    """"Final State and Stats"""
    printState(L1, L2, L3, dram, ssd)
    printStats(L1, L2, L3, dram, ssd)
    """END OF MAIN"""    
    pass


if __name__ == "__main__":
    main()