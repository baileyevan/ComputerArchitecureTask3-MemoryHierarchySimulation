

def fetch(data, L1, L2, L3, dram, ssd):
    print(f"\nCPU requests {data}")

    if L1.read(data):
        return

    if L2.read(data):
        L1.write(data, "L2")
        return
    
    if L3.read(data):
        L2.write(data, "L3")
        L1.write(data, "L2")
        return

    if dram.read(data):
        L3.write(data, "DRAM")
        L2.write(data, "L3")
        L1.write(data, "L2")
        return

    if ssd.read(data):
        dram.write(data, "SSD")
        L3.write(data, "DRAM")
        L2.write(data, "L3")
        L1.write(data, "L2")
        return