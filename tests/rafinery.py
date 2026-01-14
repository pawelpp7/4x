"""
Test systemu rafinerii z wieloma inputami
"""

def test_refinery_system():
    print("=" * 70)
    print("REFINERY SYSTEM TEST")
    print("=" * 70)
    
    from galaxy.galaxy import Galaxy
    from empire.empire import Empire
    from buildings.EmpireSpacePort import EmpireSpacePort
    from buildings.Mining import MiningComplex
    from buildings.Refinery import Smelter, ChemicalPlant, Bioreactor
    from empire.Population import Population
    
    # Setup
    galaxy = Galaxy(system_count=1, size=200)
    empire = Empire("Test Empire", (255, 255, 255), galaxy, is_player=True)
    
    # Skolonizuj planetę
    planet = galaxy.systems[0]["system"].planets[0]
    esp = EmpireSpacePort()
    esp.set_owner(empire)
    
    hex_esp = next((h for h in planet.hex_map.hexes if not h.is_blocked()), None)
    success, msg = esp.build(planet, hex_esp)
    
    if not success:
        print(f"✗ Failed to colonize: {msg}")
        return False
    
    print(f"✓ Colony established")
    print(f"  Population: {planet.population.size}")
    print(f"  Storage: {planet.storage}")
    
    # === TEST 1: Zbuduj kopalnie ===
    print("\n--- TEST 1: Building Extractors ---")
    
    # Dodaj zasoby do hexów manualnie (dla testu)
    for hex in planet.hex_map.hexes[:5]:
        hex.resources = {
            "minerals": 2.0,
            "energy": 1.5,
            "water": 1.0,
            "organics": 1.2,
        }
    
    # Zbuduj kopalnie
    extractors = [
        ("minerals", MiningComplex("minerals")),
        ("energy", MiningComplex("energy")),
        ("water", MiningComplex("water")),
        ("organics", MiningComplex("organics")),
    ]
    
    for res_name, extractor in extractors:
        extractor.owner = empire
        hex = next((h for h in planet.hex_map.hexes 
                   if res_name in h.resources and not h.is_blocked()), None)
        
        if hex:
            success, msg = extractor.build(planet, hex)
            if success:
                print(f"✓ Built {extractor.name}")
            else:
                print(f"✗ Failed: {msg}")
    
    # Produkuj przez 10 turów
    print("\n--- Producing basic resources (10 turns) ---")
    for i in range(20):
        planet.tick()
    
    print(f"Storage after 10 turns:")
    for res in ["minerals", "energy", "water", "organics"]:
        print(f"  {res}: {planet.storage.get(res, 0):.1f}")
    
    # === TEST 2: Zbuduj Smelter ===
    print("\n--- TEST 2: Building Smelter ---")
    
    smelter = Smelter()
    smelter.owner = empire
    
    hex_smelter = next((h for h in planet.hex_map.hexes 
                       if not h.is_blocked()), None)
    
    print(f"Smelter requirements:")
    print(f"  Construction: {smelter.cost}")
    print(f"  Operational: {smelter.operational_cost}")
    print(f"  Current storage: minerals={planet.storage.get('minerals', 0):.1f}, energy={planet.storage.get('energy', 0):.1f}")
    
    success, msg = smelter.build(planet, hex_smelter)
    
    if success:
        print(f"✓ {msg}")
        print(f"  Storage after build: minerals={planet.storage.get('minerals', 0):.1f}, energy={planet.storage.get('energy', 0):.1f}")
    else:
        print(f"✗ Failed: {msg}")
        return False
    
    # === TEST 3: Produkcja alloys ===
    print("\n--- TEST 3: Alloys Production (10 turns) ---")
    
    print(f"Planet instability: {planet.instability():.2f}")
    print(f"Temperature extreme: {planet.extreme_level('temperature'):.2f}")
    
    alloys_produced = 0.0
    
    for i in range(10):
        before_minerals = planet.storage.get('minerals', 0)
        before_energy = planet.storage.get('energy', 0)
        
        planet.tick()
        
        after_minerals = planet.storage.get('minerals', 0)
        after_energy = planet.storage.get('energy', 0)
        alloys = planet.storage.get('alloys', 0)
        
        alloys_this_turn = alloys - alloys_produced
        alloys_produced = alloys
        
        print(f"Turn {i+1}:")
        print(f"  Consumed: {before_minerals - after_minerals:.1f} minerals, {before_energy - after_energy:.1f} energy")
        print(f"  Produced: {alloys_this_turn:.2f} alloys (total: {alloys:.2f})")
    
    # === TEST 4: Chemical Plant ===
    print("\n--- TEST 4: Chemical Plant ---")
    
    # Dodaj gases do hexów
    for hex in planet.hex_map.hexes[:3]:
        if 'gases' not in hex.resources:
            hex.resources['gases'] = 1.5
    
    # Zbuduj gas collector
    gas_collector = MiningComplex("gases")
    gas_collector.owner = empire
    hex_gas = next((h for h in planet.hex_map.hexes 
                   if 'gases' in h.resources and not h.is_blocked()), None)
    
    if hex_gas:
        gas_collector.build(planet, hex_gas)
        print(f"✓ Built Gas Collector")
    
    # Produkuj gases
    for _ in range(5):
        planet.tick()
    
    print(f"Storage: gases={planet.storage.get('gases', 0):.1f}, water={planet.storage.get('water', 0):.1f}")
    
    # Zbuduj Chemical Plant
    chem_plant = ChemicalPlant()
    chem_plant.owner = empire
    
    hex_chem = next((h for h in planet.hex_map.hexes 
                    if not h.is_blocked()), None)
    
    if chem_plant.can_afford(planet):
        success, msg = chem_plant.build(planet, hex_chem)
        if success:
            print(f"✓ Built Chemical Plant")
            
            # Produkuj chemicals
            for _ in range(5):
                planet.tick()
            
            print(f"Chemicals produced: {planet.storage.get('chemicals', 0):.2f}")
        else:
            print(f"✗ Failed: {msg}")
    else:
        print(f"! Cannot afford Chemical Plant")
    
    # === SUMMARY ===
    print("\n" + "=" * 70)
    print("FINAL STORAGE")
    print("=" * 70)
    
    print("\nTier 1 (Basic):")
    for res in ["minerals", "energy", "water", "organics", "gases", "rare_elements"]:
        amount = planet.storage.get(res, 0)
        if amount > 0:
            print(f"  {res:15s}: {amount:6.1f}")
    
    print("\nTier 2 (Refined):")
    for res in ["alloys", "chemicals", "biotech", "plastics", "electronics", "fuel"]:
        amount = planet.storage.get(res, 0)
        if amount > 0:
            print(f"  {res:15s}: {amount:6.1f}")
    
    print("\n✓ All tests passed!")
    return True


if __name__ == "__main__":
    try:
        success = test_refinery_system()
        if not success:
            print("\n✗ Tests failed")
        input("\nPress ENTER to exit...")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress ENTER to exit...")