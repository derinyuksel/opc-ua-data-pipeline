import asyncio
import logging
import random
from asyncua import Server, ua

# 3 variables: Temperature, Pressure, and Status
# We update them every 2 seconds so the rest of the pipeline has data to read

async def main():
    # 1 Initialize the Server
    server = Server()
    await server.init()
    
    # 0.0.0.0 to listen on all network interfaces
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")
    
    server.set_server_name("Simulation Server")

    # Setup the Namespace
    # In OPC-UA, a namespace organizes our tags so they don't clash with system tags.
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    # 3. Create the Machine Object
    objects = server.nodes.objects
    my_machine = await objects.add_object(idx, "SimulatedMachine")

    # 4. Create the Variables (Sensors)
    # We define the variables starting values here.
    
    # Temperature (Float)
    temp_node = await my_machine.add_variable(idx, "Temperature", 25.0)
    
    # Pressure (Float)
    press_node = await my_machine.add_variable(idx, "Pressure", 1013.25)
    
    # Production Status (Boolean: True=Running, False=Stopped)
    status_node = await my_machine.add_variable(idx, "ProductionStatus", True)

    # Set them to read-only for clients (clients can see data, but not change it)
    await temp_node.set_writable(False)
    await press_node.set_writable(False)
    await status_node.set_writable(False)

    print("Server started at opc.tcp://0.0.0.0:4840/freeopcua/server/")
    
    # 5. The Simulation Loop
    async with server:
        while True:
            # Generate fake data to mimic a real machine
            
            # Temperature: Random between 20.0 and 80.0
            new_temp = round(random.uniform(20.0, 80.0), 2)
            await temp_node.write_value(new_temp)
            
            # Pressure: Random between 1000 and 1050
            new_press = round(random.uniform(1000.0, 1050.0), 2)
            await press_node.write_value(new_press)
            
            # Status: 90% chance to be True (Running), 10% chance of Error
            # This helps us test our dashboard alerts later.
            new_status = random.random() > 0.1
            await status_node.write_value(new_status)

            # Log to console so we know it's working
            print(f"Updated: Temp={new_temp}, Press={new_press}, Status={new_status}")
            
            # Wait 2 seconds before next update
            await asyncio.sleep(2)

if __name__ == "__main__":
    # Configure logging to show us errors if something crashes
    logging.basicConfig(level=logging.WARN)
    
    # Run the server
    asyncio.run(main())