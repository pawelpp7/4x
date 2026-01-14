import logging
from galaxy.galaxy import Galaxy
from empire.empire import Empire
from core.init import init_start_planet

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')

# Keywords to recognize military and other building types by name
MILITARY_KEYWORDS = [
    'Barracks', 'Training Grounds', 'Vehicle Factory', 'Air Base', 'Shipyard',
    'Command Center', 'War Academy', 'Planetary Shield', 'Orbital Defense Platform'
]
REFINERY_KEYWORDS = [
    'Smelter', 'Chemical Plant', 'Bioreactor', 'Polymer Factory', 'Electronics Fab', 'Fuel Refinery'
]
MINING_KEYWORDS = [
    'Extractor', 'Mining Complex', 'Collector'
]
POP_HUB = 'Population Hub'
SPACE_PORT = 'Space Port'


def count_buildings_on_planet(planet):
    counts = {
        'military': 0,
        'refinery': 0,
        'mining': 0,
        'population_hub': 0,
        'space_port': 0,
        'other': 0,
        'total': 0,
    }

    for h in planet.hex_map.hexes:
        if getattr(h, 'building_major', None):
            name = h.building_major.name
            counts['total'] += 1
            if any(k in name for k in MILITARY_KEYWORDS):
                counts['military'] += 1
            elif any(k in name for k in REFINERY_KEYWORDS):
                counts['refinery'] += 1
            elif any(k in name for k in MINING_KEYWORDS):
                counts['mining'] += 1
            elif name == POP_HUB:
                counts['population_hub'] += 1
            elif name == SPACE_PORT:
                counts['space_port'] += 1
            else:
                counts['other'] += 1

        for b in h.buildings_small:
            name = b.name
            counts['total'] += 1
            if any(k in name for k in MILITARY_KEYWORDS):
                counts['military'] += 1
            elif any(k in name for k in REFINERY_KEYWORDS):
                counts['refinery'] += 1
            elif any(k in name for k in MINING_KEYWORDS):
                counts['mining'] += 1
            elif name == POP_HUB:
                counts['population_hub'] += 1
            elif name == SPACE_PORT:
                counts['space_port'] += 1
            else:
                counts['other'] += 1

    return counts


def gather_production(empire):
    totals = {}
    for p in empire.planets:
        prod = p.produce()
        for r, v in prod.items():
            totals[r] = totals.get(r, 0.0) + v
    return totals


def print_turn_report(galaxy, turn):
    logging.info('--- TURN %d REPORT ---', turn)

    for emp in galaxy.empires:
        prod = gather_production(emp)
        building_totals = {
            'military': 0,
            'refinery': 0,
            'mining': 0,
            'population_hub': 0,
            'space_port': 0,
            'other': 0,
            'total': 0,
        }
        for p in emp.planets:
            counts = count_buildings_on_planet(p)
            for k, v in counts.items():
                building_totals[k] = building_totals.get(k, 0) + v

        logging.info('%s: Planets=%d, Cash=%.1f', emp.name, len(emp.planets), emp.cash)
        logging.info('%s: Production this turn: %s', emp.name, prod)
        logging.info('%s: Building counts: %s', emp.name, building_totals)

        # Active transports for empire
        tman = emp.transport_manager
        if tman.transports:
            logging.info('%s: Active transports (%d):', emp.name, len(tman.transports))
            for t in tman.transports:
                src = getattr(t.source, 'name', id(t.source))
                tgt = getattr(t.target, 'name', id(t.target))
                logging.info('  - %s -> %s | type=%s cargo=%s time_left=%s', src, tgt, t.transport_type, t.cargo, t.time_remaining)
        else:
            logging.info('%s: No active transports', emp.name)

        # Per-planet detailed listing (storage, buildings, garrison)
        for p in emp.planets:
            name = getattr(p, 'name', id(p))
            storage = {k: round(v, 1) for k, v in p.storage.items()} if hasattr(p, 'storage') else {}
            buildings = p.buildings_summary()
            garrison = []
            try:
                for u in p.military_manager.garrison:
                    garrison.append(f"{u.name}(HP={u.current_health:.1f},M={u.current_morale:.2f})")
            except Exception:
                pass

            logging.info('  Planet %s: Pop=%.1f, Storage=%s', name, p.population.size if hasattr(p, 'population') else 0.0, storage)
            logging.info('    Buildings (%d): %s', len(buildings), buildings)
            logging.info('    Garrison (%d): %s', len(garrison), garrison)


def run(turns=100, systems=12):
    galaxy = Galaxy(system_count=systems, size=800)

    # Create two AI empires
    e1 = Empire('Red AI', (200, 50, 50), galaxy, is_player=False)
    e2 = Empire('Blue AI', (50, 80, 200), galaxy, is_player=False)
    galaxy.empires.extend([e1, e2])

    # Initialize starting planets
    init_start_planet(e1, galaxy.systems[0])
    init_start_planet(e2, galaxy.systems[1])

    # Give planets readable names
    for entry in galaxy.systems:
        sys_id = entry['id']
        for i, p in enumerate(entry['system'].planets):
            p.name = f'S{sys_id}-P{i}'

    logging.info('Starting AI detailed test for %d turns', turns)

    for t in range(1, turns + 1):
        # Report production before applying tick (shows potential production)
        print_turn_report(galaxy, t)

        # advance simulation
        galaxy.tick()

    logging.info('Final summary after %d turns', turns)
    print_turn_report(galaxy, turns)


if __name__ == '__main__':
    run(turns=100, systems=16)
