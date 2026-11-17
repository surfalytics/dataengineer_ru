from systems.parse import parse  # pip install systems==0.1.0

SPEC = """
HiringRate(10)
ProductEngineers(1000)
[PotentialHires] > ProductEngineers @ HiringRate
[PotentialServices] > RequestedServices(10) @ ProductEngineers / 10
RequestedServices > InflightServices(0, 10) @ Leak(1.0)
InflightServices > PortNameAssigned @ Leak(1.0)
PortNameAssigned > PuppetGenerated @ Leak(0.8)
PortNameAssigned > RequestedServices @ Leak(0.2)
PuppetGenerated > PuppetConfigMerged @ Leak(0.8)
PuppetGenerated > InflightServices @ Leak(0.2)
PuppetConfigMerged > ServerCapacityAllocated @ Leak(0.8)
PuppetConfigMerged > PuppetGenerated @ Leak(0.2)
"""

last = parse(SPEC).run(rounds=50)[-1]
print("очередь заявок:", last["RequestedServices"])
print("сервисов выдано:", last["ServerCapacityAllocated"])
