"""Test podstawowej funkcjonalności jednostek"""

def test_unit_creation():
    print("=== Test 1: Tworzenie jednostek ===")
    
    from military.units import Infantry, Tank
    
    infantry = Infantry()
    print(f"Infantry: ATK={infantry.stats.attack}, DEF={infantry.stats.defense}, HP={infantry.stats.health}")
    
    tank = Tank()
    print(f"Tank: ATK={tank.stats.attack}, DEF={tank.stats.defense}, HP={tank.stats.health}")
    
    assert infantry.stats.attack == 10.0
    assert tank.stats.defense == 20.0
    
    print("✓ Test passed!\n")

def test_production_queue():
    print("=== Test 2: Kolejka produkcji ===")
    
    from military.units import Infantry, ProductionQueue
    from planet.planet import Planet
    from empire.empire import Empire
    from galaxy.galaxy import Galaxy
    
    galaxy = Galaxy(system_count=5, size=500)
    empire = Empire("Test", (100, 100, 100), galaxy)
    
    planet = Planet()
    planet.colonized = True
    planet.owner = empire
    planet.production_speed = 1.0
    
    queue = ProductionQueue()
    queue.add_to_queue(Infantry)
    
    print(f"Dodano do kolejki: {queue.queue[0]['unit_class'].__name__}")
    print(f"Czas produkcji: {queue.queue[0]['time_total']} tur")
    
    # Symuluj 3 tury
    for i in range(3):
        completed = queue.tick(planet)
        print(f"Tura {i+1}: progress={queue.queue[0]['progress'] if queue.queue else 'DONE'}")
        
        if completed:
            print(f"Ukończono: {completed[0].name}")
            break
    
    assert len(completed) == 1
    print("✓ Test passed!\n")

if __name__ == "__main__":
    test_unit_creation()
    test_production_queue()
    print("=== Wszystkie testy bazowe przeszły! ===")