"""
Example demonstrating how to retrieve connected TAP devices before establishing connections.
This addresses the issue where the SDK couldn't establish connections with already connected TAPs.

This example works on both Windows and Unix platforms.
"""

import asyncio
import platform
import time


def OnConnect(identifier, name, fw):
    print(f"{identifier} - Connected. Name: {name}, FW Version: {fw}")


def OnDisconnect(identifier):
    print(f"{identifier} - Disconnected")


def OnTapped(identifier, tapcode):
    print(f"{identifier} - Tapped: {tapcode}")


async def demonstrate_list_connected_taps():
    """
    Demonstrate how to list connected TAP devices before running the SDK.
    This helps with debugging connection issues and ensures the SDK can work
    with already connected devices.
    """
    current_platform = platform.system()
    print(f"Running on {current_platform}")
    print("=" * 50)
    
    # Import the SDK (this will automatically choose the right backend)
    from tapsdk import TapSDK, TapInputMode
    
    # Create SDK instance
    if current_platform in ["Darwin", "Linux"]:
        # Unix platforms use async event loop
        loop = asyncio.get_event_loop()
        client = TapSDK(loop=loop)
    else:
        # Windows platform
        client = TapSDK()
    
    print("Checking for connected TAP devices...")
    
    try:
        # List connected TAPs before running the SDK
        connected_taps = await client.list_connected_taps()
        
        if connected_taps:
            print(f"Found {len(connected_taps)} connected TAP device(s):")
            for i, tap in enumerate(connected_taps):
                print(f"  {i+1}. {tap}")
        else:
            print("No connected TAP devices found.")
            print("Make sure your TAP device is:")
            print("  1. Powered on")
            print("  2. Paired with your system")
            print("  3. Connected via Bluetooth")
            return
            
    except Exception as e:
        print(f"Error retrieving connected TAPs: {e}")
        print("This might indicate a compatibility issue with the TAPManager version.")
        # Continue anyway, as the SDK might still work
    
    print("\nStarting SDK...")
    
    # Register event handlers
    if hasattr(client, 'register_connection_events'):
        if asyncio.iscoroutinefunction(client.register_connection_events):
            await client.register_connection_events(OnConnect)
        else:
            client.register_connection_events(OnConnect)
    
    if hasattr(client, 'register_disconnection_events'):
        if asyncio.iscoroutinefunction(client.register_disconnection_events):
            await client.register_disconnection_events(OnDisconnect)
        else:
            client.register_disconnection_events(OnDisconnect)
    
    if hasattr(client, 'register_tap_events'):
        if asyncio.iscoroutinefunction(client.register_tap_events):
            await client.register_tap_events(OnTapped)
        else:
            client.register_tap_events(OnTapped)
    
    # Run the SDK
    if asyncio.iscoroutinefunction(client.run):
        await client.run()
    else:
        client.run()
    
    print("SDK started successfully!")
    print("Try tapping on your TAP device...")
    
    # Set controller mode
    if hasattr(client, 'set_input_mode'):
        if asyncio.iscoroutinefunction(client.set_input_mode):
            await client.set_input_mode(TapInputMode("controller"))
        else:
            client.set_input_mode(TapInputMode("controller"))
    
    # Wait a bit to receive events
    print("Listening for TAP events for 10 seconds...")
    await asyncio.sleep(10)
    
    print("Example completed!")


if __name__ == "__main__":
    if platform.system() in ["Darwin", "Linux"]:
        # Unix platforms
        loop = asyncio.get_event_loop()
        loop.run_until_complete(demonstrate_list_connected_taps())
    else:
        # Windows platform - create event loop
        asyncio.run(demonstrate_list_connected_taps())