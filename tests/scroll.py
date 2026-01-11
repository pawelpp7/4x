# tests/test_scroll.py
"""Test scrollowania build menu"""

def test_scroll_state():
    print("=== Test: Build Menu Scroll State ===")
    
    from render.build_menu import BuildMenuState, handle_build_menu_scroll
    
    state = BuildMenuState()
    print(f"Initial scroll: {state.scroll}")
    print(f"Initial max_scroll: {state.max_scroll}")
    
    # Symuluj max_scroll (normalnie obliczany w draw funkcji)
    state.max_scroll = 500
    
    # Scroll w dół (ujemny delta)
    handle_build_menu_scroll(state, -1)  # Scroll down
    print(f"After scroll down: {state.scroll}")
    assert state.scroll == 50, f"Expected 50, got {state.scroll}"
    
    # Scroll w górę (pozytywny delta)
    handle_build_menu_scroll(state, 1)  # Scroll up
    print(f"After scroll up: {state.scroll}")
    assert state.scroll == 0, f"Expected 0, got {state.scroll}"
    
    # Scroll poza max
    state.scroll = 600
    handle_build_menu_scroll(state, -1)
    print(f"Clamped to max: {state.scroll}")
    assert state.scroll == state.max_scroll, "Should clamp to max"
    
    print("✓ Scroll state works correctly!")

if __name__ == "__main__":
    test_scroll_state()
    print("\n✓✓✓ All tests passed! ✓✓✓")