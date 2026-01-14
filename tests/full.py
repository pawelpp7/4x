def test_full_colonization_and_development_flow():
    print("="*60)
    print("FULL COLONIZATION & DEVELOPMENT TEST")
    print("="*60)
    
    # --- IMPORTY ---
    try:
        from galaxy.galaxy import Galaxy
        from empire.empire import Empire
        from buildings.SpacePort import SpacePort
        from buildings.PopulationHub import PopulationHub
        from empire.Population import Population
        print("✓ Imports successful")
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

    # --- GALAXY ---
    try:
        galaxy = Galaxy(system_count=1, size=200)
        system = galaxy.systems[0]["system"]
        print(f"✓ Galaxy created with {len(system.planets)} planets")
    except Exception as e:
        print(f"✗ Galaxy creation failed: {e}")
        return False

    # --- EMPIRE ---
    try:
        empire = Empire("Test Empire", (255,255,255), galaxy, is_player=True, energy=200)
        print(f"✓ Empire created: {empire.name}, energy={empire.energy}")
    except Exception as e:
        print(f"✗ Empire creation failed: {e}")
        return False

    # --- PLANETY ---
    try:
        source_planet = system.planets[0]
        target_planet = system.planets[1]
        print(f"✓ Source planet: {id(source_planet)}")
        print(f"✓ Target planet: {id(target_planet)}")
    except Exception as e:
        print(f"✗ Planet selection failed: {e}")
        return False

    # --- RĘCZNA KOLONIZACJA ŹRÓDŁA ---
    print("\n--- SETTING UP SOURCE PLANET ---")
    try:
        source_planet.colonized = True
        source_planet.set_owner(empire)
        source_planet.population = Population(size=10.0)
        empire.planets.append(source_planet)
        
        # daj zasoby
        for r in ["energy", "minerals", "organics", "water", "gases", "rare_elements"]:
            source_planet.storage[r] = 100.0
        
        print(f"✓ Source planet colonized")
        print(f"  - Population: {source_planet.population.size}")
        print(f"  - Resources: energy={source_planet.storage['energy']}, minerals={source_planet.storage['minerals']}")
    except Exception as e:
        print(f"✗ Source planet setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # --- SPACE PORT BUDOWA ---
    print("\n--- BUILDING SPACE PORT ---")
    try:
        spaceport = SpacePort()
        spaceport.owner = empire
        
        # sprawdź czy target jest wolny
        print(f"  Target colonized: {target_planet.colonized}")
        print(f"  Target owner: {target_planet.owner}")
        
        # znajdź wolny hex
        free_hex = next(
            (h for h in target_planet.hex_map.hexes if not h.is_blocked()),
            None
        )
        
        if not free_hex:
            print("✗ No free hex on target planet")
            return False
        
        print(f"  Found free hex: ({free_hex.q}, {free_hex.r})")
        
        # sprawdź zasoby na source
        print(f"  - Resources: energy={source_planet.storage['energy']}, minerals={source_planet.storage['minerals']}")
        print(f"  Source population before: {source_planet.population.size}")
        
        # buduj (NOWA SYGNATURA: planet, hex, source_planet)
        ok, msg = spaceport.build(target_planet, free_hex, source_planet)
        
        if ok:
            print(f"✓ SpacePort build: {msg}")
            print(f"  Target colonized: {target_planet.colonized}")
            print(f"  Target population: {target_planet.population.size if target_planet.population else 'None'}")
            print(f"  Source population after: {source_planet.population.size}")
            
            # sprawdź typ owner
            if target_planet.owner:
                if hasattr(target_planet.owner, 'name'):
                    print(f"  Target owner: {target_planet.owner.name}")
                else:
                    print(f"  ! Target owner is wrong type: {type(target_planet.owner).__name__}")
                    print(f"    Expected Empire, got {type(target_planet.owner)}")
                    return False
            else:
                print(f"  Target owner: None")
                return False
        else:
            print(f"✗ SpacePort build failed: {msg}")
            return False
            
    except Exception as e:
        print(f"✗ SpacePort construction failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # --- DODAJ TARGET DO IMPERIUM (już nie potrzebne - SpacePort to robi) ---
    print("\n--- EMPIRE CHECK ---")
    try:
        print(f"  Empire planets: {len(empire.planets)}")
        if target_planet in empire.planets:
            print(f"  ✓ Target planet is in empire")
        else:
            print(f"  ✗ Target planet NOT in empire (this is a bug)")
            return False
    except Exception as e:
        print(f"✗ Empire check failed: {e}")

    # --- SPRAWDZENIE STANU ---
    print("\n--- COLONY STATE CHECK ---")
    try:
        print(f"  Colonized: {target_planet.colonized}")
        print(f"  Owner: {target_planet.owner.name}")
        print(f"  Population: {target_planet.population.size}")
        print(f"  SpacePort: {target_planet.spaceport.name}")
        print(f"  Storage energy: {target_planet.storage.get('energy', 0)}")
        print(f"  Storage organics: {target_planet.storage.get('organics', 0)}")
        
        if not target_planet.colonized:
            print("✗ Colony not marked as colonized")
            return False
        
        if target_planet.population.size < 1.0:
            print("✗ Colony has no population")
            return False
            
        print("✓ Colony fully established")
        
    except Exception as e:
        print(f"✗ State check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # --- POPULATION HUB ---
    print("\n--- BUILDING POPULATION HUB ---")
    try:
        hub = PopulationHub()
        hub.owner = empire
        
        # znajdź wolny hex (nie SpacePort)
        free_hex = next(
            (h for h in target_planet.hex_map.hexes 
             if not h.is_blocked() and h.can_build(hub, target_planet)),
            None
        )
        
        if not free_hex:
            print("✗ No free hex for Population Hub")
            return False
        
        print(f"  Found free hex: ({free_hex.q}, {free_hex.r})")
        print(f"  Can afford: {hub.can_afford(target_planet)}")
        print(f"  Storage: organics={target_planet.storage['organics']}, minerals={target_planet.storage['minerals']}")
        
        ok, msg = hub.build(target_planet, free_hex)
        
        if ok:
            print(f"✓ Population Hub build: {msg}")
        else:
            print(f"✗ Population Hub build failed: {msg}")
            return False
            
    except Exception as e:
        print(f"✗ Population Hub construction failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # --- ROZWÓJ POPULACJI ---
    print("\n--- POPULATION GROWTH TEST ---")
    try:
        pop_before = target_planet.population.size
        print(f"  Population before: {pop_before:.2f}")
        print(f"  Growth rate: {target_planet.population.growth}")
        
        for i in range(10):
            target_planet.tick()
            if i % 3 == 0:
                print(f"  Tick {i+1}: pop={target_planet.population.size:.2f}")
        
        pop_after = target_planet.population.size
        print(f"  Population after: {pop_after:.2f}")
        
        if pop_after > pop_before:
            print(f"✓ Population grew by {pop_after - pop_before:.2f}")
        else:
            print(f"✗ Population did not grow (before={pop_before:.2f}, after={pop_after:.2f})")
            return False
            
    except Exception as e:
        print(f"✗ Population growth test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "="*60)
    print("✓ ALL TESTS PASSED")
    print("="*60)
    return True


if __name__ == "__main__":
    try:
        success = test_full_colonization_and_development_flow()
        if not success:
            print("\n! Some tests failed")
            input("Press ENTER to exit...")
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press ENTER to exit...")