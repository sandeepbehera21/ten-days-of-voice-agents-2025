import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.gamemaster_tools import WorldState

def test_world_state_initialization():
    world = WorldState()
    state = world.get_state()
    assert state["character"]["name"] == "Traveler"
    assert "Old Map" in state["character"]["inventory"]
    assert state["location"]["name"] == "The Crossroads"

def test_inventory_management():
    world = WorldState()
    
    # Add item
    msg = world.add_inventory_item("Magic Sword")
    assert "Magic Sword" in world.state["character"]["inventory"]
    assert "Added Magic Sword" in msg
    
    # Remove item
    msg = world.remove_inventory_item("Rusty Dagger")
    assert "Rusty Dagger" not in world.state["character"]["inventory"]
    assert "Removed Rusty Dagger" in msg
    
    # Remove non-existent item
    msg = world.remove_inventory_item("NonExistentItem")
    assert "not found" in msg

def test_dice_roll():
    world = WorldState()
    roll = world.roll_dice(20)
    assert 1 <= roll <= 20
    
    roll = world.roll_dice(6)
    assert 1 <= roll <= 6

def test_update_location():
    world = WorldState()
    world.update_location("Cave", "A dark cave", ["Out"])
    assert world.state["location"]["name"] == "Cave"
    assert world.state["location"]["description"] == "A dark cave"
