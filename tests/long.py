from buildings.SpacePort import SpacePort


def test_longterm_ai_gameplay(turns=100):
    """Test długoterminowej rozgrywki AI vs AI"""
    
    print("="*70)
    print(f"LONG-TERM AI GAMEPLAY TEST ({turns} TURNS)")
    print("="*70)
    
    from galaxy.galaxy import Galaxy
    from empire.empire import Empire
    from buildings.EmpireSpacePort import EmpireSpacePort
    
    # === SETUP ===
    print("\n--- SETUP ---")
    galaxy = Galaxy(system_count=10, size=800)
    
    # Empire 1
    empire1 = Empire("AI Empire Alpha", (80, 200, 120), galaxy, is_player=False)
    start1 = galaxy.systems[0]["system"].planets[0]
    init_empire_start(empire1, start1)
    
    # Empire 2
    empire2 = Empire("AI Empire Beta", (200, 80, 180), galaxy, is_player=False)
    start2 = galaxy.systems[1]["system"].planets[0]
    init_empire_start(empire2, start2)
    
    galaxy.empires = [empire1, empire2]
    
    print(f"✓ {empire1.name} starts at system 0")
    print(f"✓ {empire2.name} starts at system 1")
    
    # === SIMULATION ===
    print("\n--- RUNNING SIMULATION ---")
    print("Turn | E1 Planets | E1 Pop | E1 Energy | E2 Planets | E2 Pop | E2 Energy")
    print("-" * 70)
    
    stats = []
    
    for turn in range(turns):
        galaxy.tick()
        
        e1_pop = sum(p.population.size for p in empire1.planets if p.population)
        e2_pop = sum(p.population.size for p in empire2.planets if p.population)
        
        e1_buildings = sum(p.total_buildings() for p in empire1.planets)
        e2_buildings = sum(p.total_buildings() for p in empire2.planets)
        
        e1_storage = empire_storage_sum(empire1)
        e2_storage = empire_storage_sum(empire2)

        stats.append({
            'turn': turn,
            'e1_planets': len(empire1.planets),
            'e1_pop': e1_pop,
            'e1_energy': empire1.energy,
            'e1_buildings': e1_buildings,
            'e1_storage': e1_storage,

            'e2_planets': len(empire2.planets),
            'e2_pop': e2_pop,
            'e2_energy': empire2.energy,
            'e2_buildings': e2_buildings,
            'e2_storage': e2_storage,
        })

        
        # Raport co 10 turów
        report_interval = max(10, turns // 10)
        if turn % report_interval == 0:
            print(
                f"{turn:4d} | "
                f"{len(empire1.planets):10d} | "
                f"{e1_pop:6.1f} | "
                f"{empire1.energy:9.1f} | "
                f"{len(empire2.planets):10d} | "
                f"{e2_pop:6.1f} | "
                f"{empire2.energy:9.1f}"
            )
    
    # === FINAL STATS ===
    print("\n" + "="*70)
    print("FINAL STATISTICS")
    print("="*70)
    
    final = stats[-1]
    
    print(f"\n{empire1.name}:")
    print(f"  Planets: {final['e1_planets']}")
    print(f"  Total Population: {final['e1_pop']:.1f}")
    print(f"  Energy: {final['e1_energy']:.1f}")
    print(f"  Buildings: {final['e1_buildings']}")
    
    print(f"\n{empire2.name}:")
    print(f"  Planets: {final['e2_planets']}")
    print(f"  Total Population: {final['e2_pop']:.1f}")
    print(f"  Energy: {final['e2_energy']:.1f}")
    print(f"  Buildings: {final['e2_buildings']}")
    
    # === VALIDATION ===
    print("\n--- VALIDATION ---")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Oba imperia powinny mieć planety
    tests_total += 1
    if final['e1_planets'] > 0 and final['e2_planets'] > 0:
        print("✓ Both empires have planets")
        tests_passed += 1
    else:
        print("✗ At least one empire has no planets")
    
    # Test 2: Populacja powinna rosnąć
    tests_total += 1
    if final['e1_pop'] > 5 and final['e2_pop'] > 5:
        print("✓ Population growth working")
        tests_passed += 1
    else:
        print("✗ Population not growing properly")
    
    # Test 3: Przynajmniej jedno imperium powinno skolonizować >1 planety
    tests_total += 1
    if final['e1_planets'] > 1 or final['e2_planets'] > 1:
        print("✓ At least one empire expanded")
        tests_passed += 1
    else:
        print("✗ No empire expanded beyond starting planet")
    
    # Test 4: Budynki zostały zbudowane
    tests_total += 1
    total_buildings = sum(p.total_buildings() for p in empire1.planets + empire2.planets)
    if total_buildings > 10:
        print(f"✓ Buildings constructed ({total_buildings} total)")
        tests_passed += 1
    else:
        print(f"✗ Too few buildings ({total_buildings} total)")
    
    # Test 5: Energia nie powinna być < -100 (kryzys energetyczny)
    tests_total += 1
    if final['e1_energy'] > -100 and final['e2_energy'] > -100:
        print("✓ No severe energy crisis")
        tests_passed += 1
    else:
        print("✗ Severe energy crisis detected")
    
    # === GROWTH ANALYSIS ===
    print("\n--- GROWTH ANALYSIS ---")
    
    # Porównaj turę 10 vs ostatnią
    turn10 = stats[min(10, len(stats)-1)]
    turn_final = stats[-1]
    
    e1_planet_growth = turn_final['e1_planets'] - turn10['e1_planets']
    e1_pop_growth = turn_final['e1_pop'] - turn10['e1_pop']
    
    e2_planet_growth = turn_final['e2_planets'] - turn10['e2_planets']
    e2_pop_growth = turn_final['e2_pop'] - turn10['e2_pop']
    
    print(f"\n{empire1.name} (Turn 10 → {turns}):")
    print(f"  Planets: +{e1_planet_growth}")
    print(f"  Population: +{e1_pop_growth:.1f}")
    
    print(f"\n{empire2.name} (Turn 10 → {turns}):")
    print(f"  Planets: +{e2_planet_growth}")
    print(f"  Population: +{e2_pop_growth:.1f}")
    
    # === GRAPHS ===
    print("\n--- GENERATING CHARTS ---")
    try:
        create_charts(stats, empire1.name, empire2.name, turns)
        print("✓ Charts saved to 'ai_test_charts.html'")
    except Exception as e:
        print(f"! Chart generation failed: {e}")
    
    # === SUMMARY ===
    print("\n" + "="*70)
    print(f"TESTS PASSED: {tests_passed}/{tests_total}")
    print("="*70)
    
    if tests_passed == tests_total:
        print("✓ ALL TESTS PASSED - AI is working correctly!")
        return True
    else:
        print(f"✗ {tests_total - tests_passed} TESTS FAILED")
        return False


# Dodaj na początku longterm.py dla lepszego debugowania

def init_empire_start(empire, planet):
    """Inicjalizuje imperium na planecie startowej z debugowaniem"""
    from buildings.EmpireSpacePort import EmpireSpacePort
    from empire.Population import Population
    
    print(f"\n=== Initializing {empire.name} ===")
    print(f"  Planet ID: {id(planet)}")
    
    esp = EmpireSpacePort()
    esp.owner = empire
    
    # Znajdź wolny hex
    free_hex = next(
        (h for h in planet.hex_map.hexes if not h.is_blocked()),
        None
    )
    
    if not free_hex:
        raise RuntimeError("No valid hex for starting planet")
    
    print(f"  Building on hex: ({free_hex.q}, {free_hex.r})")
    
    success, msg = esp.build(planet, free_hex)
    
    if not success:
        raise RuntimeError(f"Failed to initialize empire: {msg}")
    
    print(f"  ✓ {msg}")
    print(f"  Planet colonized: {planet.colonized}")
    print(f"  Planet owner: {planet.owner.name if planet.owner else 'None'}")
    print(f"  Planet population: {planet.population.size if planet.population else 'None'}")
    print(f"  Empire planets: {len(empire.planets)}")
    
    # Dodaj początkowe zasoby
    for res in planet.storage.keys():
        planet.storage[res] = 50.0
    
    print(f"  Starting resources: {sum(planet.storage.values()):.0f} total")
    print()


# Dodaj też debug do AI tick w SimpleAI:

def tick(self):
    """Główna pętla AI - wykonuje akcje co kilka ticków"""
    self.cooldown -= 1
    self.colonization_cooldown -= 1
    
    if self.cooldown > 0:
        return
    
    self.cooldown = 3
    
    # DEBUG: Co 50 turów pokaż status
    if self.galaxy.turn % 50 == 0:
        print(f"\n[AI {self.empire.name}] Turn {self.galaxy.turn} Status:")
        print(f"  Planets: {len(self.empire.planets)}")
        print(f"  Colonization cooldown: {self.colonization_cooldown}")
        
        for i, p in enumerate(self.empire.planets):
            print(f"  Planet {i}: pop={p.population.size:.1f}, "
                  f"energy={p.storage.get('energy', 0):.0f}, "
                  f"minerals={p.storage.get('minerals', 0):.0f}")

    # 1️⃣ PRIORYTET: KOLONIZACJA
    if self.colonization_cooldown <= 0 and len(self.empire.planets) < 15:
        print(f"[AI {self.empire.name}] Attempting colonization...")
        if self.try_colonize():
            self.colonization_cooldown = 10
            return
        else:
            print(f"[AI {self.empire.name}] Colonization failed - will retry in 10 turns")
            self.colonization_cooldown = 10  # Również ustaw cooldown na failure

    # 2️⃣ Rozwój
    if self.empire.planets:
        planet = self.pick_development_planet()
        if planet:
            self.develop_planet(planet)


# W try_colonize dodaj więcej debugowania:

def try_colonize(self):
    """Próbuje skolonizować nową planetę"""
    
    if not self.empire.planets:
        print(f"  No planets to colonize from")
        return False
    
    # 1️⃣ Znajdź valid source planets
    valid_sources = []
    for p in self.empire.planets:
        if not p.colonized or not p.population:
            print(f"  Planet {id(p)} not colonized or no population")
            continue
        
        energy = p.storage.get('energy', 0)
        minerals = p.storage.get('minerals', 0)
        pop = p.population.size
        
        print(f"  Checking planet {id(p)}: energy={energy:.1f}, minerals={minerals:.1f}, pop={pop:.1f}")
        
        if energy >= 12 and minerals >= 7 and pop >= 1.5:
            valid_sources.append(p)
            print(f"    ✓ Valid source!")
        else:
            print(f"    ✗ Insufficient resources")
    
    if not valid_sources:
        print(f"  No valid source planets found")
        return False
    
    source = max(valid_sources, 
                key=lambda p: p.storage.get('energy', 0) + p.storage.get('minerals', 0))
    
    print(f"  Selected source: {id(source)}")
    
    # 2️⃣ Znajdź target
    target = self.find_colonization_target(source)
    if not target:
        print(f"  No colonization target found")
        return False
    
    print(f"  Selected target: {id(target)}")
    
    # 3️⃣ Znajdź wolny hex
    free_hex = next(
        (h for h in target.hex_map.hexes if not h.is_blocked()),
        None
    )
    if not free_hex:
        print(f"  No free hex on target")
        return False
    
    print(f"  Building on hex: ({free_hex.q}, {free_hex.r})")
    
    # 4️⃣ Zbuduj SpacePort
    spaceport = SpacePort()
    spaceport.owner = self.empire
    
    print(f"  Calling SpacePort.build()")
    print(f"    Source energy before: {source.storage.get('energy', 0):.1f}")
    print(f"    Source minerals before: {source.storage.get('minerals', 0):.1f}")
    print(f"    Source pop before: {source.population.size:.1f}")
    
    success, msg = spaceport.build(target, free_hex, source)
    
    if success:
        print(f"  ✓ SUCCESS: {msg}")
        print(f"    Source energy after: {source.storage.get('energy', 0):.1f}")
        print(f"    Source pop after: {source.population.size:.1f}")
        print(f"    Target colonized: {target.colonized}")
        print(f"    Target pop: {target.population.size:.1f}")
        return True
    else:
        print(f"  ✗ FAILED: {msg}")
    
    return False


def create_charts(stats, empire1_name, empire2_name, turns):
    """Tworzy interaktywne wykresy HTML"""
    
    turns_data = [s['turn'] for s in stats]
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AI Test Results - {turns} Turns</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #1a1a1a;
            color: #fff;
        }}
        h1, h2 {{
            color: #4a9eff;
        }}
        .chart {{
            margin: 20px 0;
            background: #2a2a2a;
            padding: 20px;
            border-radius: 8px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-box {{
            background: #2a2a2a;
            padding: 15px;
            border-radius: 8px;
        }}
        .warning {{
            background: #663300;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <h1>AI Long-term Test Results</h1>
    <p>Total turns: {turns}</p>
    
    <div class="stats">
        <div class="stat-box">
            <h3>{empire1_name}</h3>
            <p>Final Planets: {stats[-1]['e1_planets']}</p>
            <p>Final Population: {stats[-1]['e1_pop']:.1f}</p>
            <p>Final Energy: {stats[-1]['e1_energy']:.1f}</p>
            <p>Final Buildings: {stats[-1]['e1_buildings']}</p>
        </div>
        <div class="stat-box">
            <h3>{empire2_name}</h3>
            <p>Final Planets: {stats[-1]['e2_planets']}</p>
            <p>Final Population: {stats[-1]['e2_pop']:.1f}</p>
            <p>Final Energy: {stats[-1]['e2_energy']:.1f}</p>
            <p>Final Buildings: {stats[-1]['e2_buildings']}</p>
        </div>
    </div>
"""

    # Sprawdź czy jest runaway growth
    pop_ratio = stats[-1]['e1_pop'] / max(1, stats[-1]['e2_pop'])
    if pop_ratio > 10 or pop_ratio < 0.1:
        html += f"""
    <div class="warning">
        <h3>⚠️ BALANCE WARNING</h3>
        <p>Extreme population imbalance detected! Ratio: {pop_ratio:.1f}:1</p>
        <p>This indicates runaway growth mechanics that need balancing.</p>
    </div>
"""

    # Population chart
    html += """
    <div class="chart">
        <h2>Population Over Time</h2>
        <div id="popChart"></div>
    </div>
    
    <script>
    var popData = [
        {
            x: """ + str(turns_data) + """,
            y: """ + str([s['e1_pop'] for s in stats]) + """,
            name: '""" + empire1_name + """',
            type: 'scatter',
            line: {color: '#50c878'}
        },
        {
            x: """ + str(turns_data) + """,
            y: """ + str([s['e2_pop'] for s in stats]) + """,
            name: '""" + empire2_name + """',
            type: 'scatter',
            line: {color: '#c850b4'}
        }
    ];
    
    var popLayout = {
        title: 'Population Growth',
        xaxis: {title: 'Turn', color: '#ccc', gridcolor: '#444'},
        yaxis: {title: 'Population', color: '#ccc', gridcolor: '#444'},
        paper_bgcolor: '#2a2a2a',
        plot_bgcolor: '#1a1a1a',
        font: {color: '#ccc'}
    };
    
    Plotly.newPlot('popChart', popData, popLayout);
    </script>
"""

    # Planets chart
    html += """
    <div class="chart">
        <h2>Territory Expansion</h2>
        <div id="planetChart"></div>
    </div>
    
    <script>
    var planetData = [
        {
            x: """ + str(turns_data) + """,
            y: """ + str([s['e1_planets'] for s in stats]) + """,
            name: '""" + empire1_name + """',
            type: 'scatter',
            line: {color: '#50c878'}
        },
        {
            x: """ + str(turns_data) + """,
            y: """ + str([s['e2_planets'] for s in stats]) + """,
            name: '""" + empire2_name + """',
            type: 'scatter',
            line: {color: '#c850b4'}
        }
    ];
    
    var planetLayout = {
        title: 'Colonized Planets',
        xaxis: {title: 'Turn', color: '#ccc', gridcolor: '#444'},
        yaxis: {title: 'Planets', color: '#ccc', gridcolor: '#444'},
        paper_bgcolor: '#2a2a2a',
        plot_bgcolor: '#1a1a1a',
        font: {color: '#ccc'}
    };
    
    Plotly.newPlot('planetChart', planetData, planetLayout);
    </script>
"""

    # Energy chart
    html += """
    <div class="chart">
        <h2>Energy Balance</h2>
        <div id="energyChart"></div>
    </div>
    
    <script>
    var energyData = [
        {
            x: """ + str(turns_data) + """,
            y: """ + str([s['e1_energy'] for s in stats]) + """,
            name: '""" + empire1_name + """',
            type: 'scatter',
            line: {color: '#50c878'}
        },
        {
            x: """ + str(turns_data) + """,
            y: """ + str([s['e2_energy'] for s in stats]) + """,
            name: '""" + empire2_name + """',
            type: 'scatter',
            line: {color: '#c850b4'}
        }
    ];
    
    var energyLayout = {
        title: 'Energy Reserves',
        xaxis: {title: 'Turn', color: '#ccc', gridcolor: '#444'},
        yaxis: {title: 'Energy', color: '#ccc', gridcolor: '#444'},
        paper_bgcolor: '#2a2a2a',
        plot_bgcolor: '#1a1a1a',
        font: {color: '#ccc'}
    };
    
    Plotly.newPlot('energyChart', energyData, energyLayout);
    </script>
"""
    # Total storage chart
    html += """
    <div class="chart">
        <h2>Total Stored Resources</h2>
        <div id="storageChart"></div>
    </div>

    <script>
    var storageData = [
        {
            x: """ + str(turns_data) + """,
            y: """ + str([
                sum(s['e1_storage'].values()) for s in stats
            ]) + """,
            name: '""" + empire1_name + """',
            type: 'scatter'
        },
        {
            x: """ + str(turns_data) + """,
            y: """ + str([
                sum(s['e2_storage'].values()) for s in stats
            ]) + """,
            name: '""" + empire2_name + """',
            type: 'scatter'
        }
    ];

    var storageLayout = {
        title: 'Total Stored Resources',
        xaxis: {title: 'Turn'},
        yaxis: {title: 'Storage'},
        paper_bgcolor: '#2a2a2a',
        plot_bgcolor: '#1a1a1a',
        font: {color: '#ccc'}
    };

    Plotly.newPlot('storageChart', storageData, storageLayout);
    </script>
    """


    # Buildings chart
    html += """
    <div class="chart">
        <h2>Infrastructure Development</h2>
        <div id="buildingChart"></div>
    </div>
    
    <script>
    var buildingData = [
        {
            x: """ + str(turns_data) + """,
            y: """ + str([s['e1_buildings'] for s in stats]) + """,
            name: '""" + empire1_name + """',
            type: 'scatter',
            line: {color: '#50c878'}
        },
        {
            x: """ + str(turns_data) + """,
            y: """ + str([s['e2_buildings'] for s in stats]) + """,
            name: '""" + empire2_name + """',
            type: 'scatter',
            line: {color: '#c850b4'}
        }
    ];
    
    var buildingLayout = {
        title: 'Total Buildings',
        xaxis: {title: 'Turn', color: '#ccc', gridcolor: '#444'},
        yaxis: {title: 'Buildings', color: '#ccc', gridcolor: '#444'},
        paper_bgcolor: '#2a2a2a',
        plot_bgcolor: '#1a1a1a',
        font: {color: '#ccc'}
    };
    
    Plotly.newPlot('buildingChart', buildingData, buildingLayout);
    </script>
"""

    html += """
</body>
</html>
"""
    
    with open('ai_test_charts.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    import webbrowser
    import os
    webbrowser.open('file://' + os.path.abspath('ai_test_charts.html'))
def empire_storage_sum(empire):
    total = {}
    for p in empire.planets:
        for res, val in p.storage.items():
            total[res] = total.get(res, 0) + val
    return total


if __name__ == "__main__":
    import sys
    
    turns = 1000
    if len(sys.argv) > 1:
        try:
            turns = int(sys.argv[1])
        except:
            print("Usage: python longterm.py [turns]")
            turns = 100
    
    try:
        success = test_longterm_ai_gameplay(turns)
        print("\n")
        if success:
            print("🎉 Simulation completed successfully!")
        else:
            print("⚠️  Simulation completed with warnings")
        input("Press ENTER to exit...")
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press ENTER to exit...")