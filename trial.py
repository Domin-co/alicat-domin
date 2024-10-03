import asyncio
from alicat import MassFlowController, FrameParameters, Command 

from enum import Enum
import time

from typing import List, Optional

address='COM3'
unit='A'

enable=[FrameParameters.TOTALIZER_BATCH_REMAINING, FrameParameters.VALVE_DRIVE]
disable=[FrameParameters.DENSITY, FrameParameters.VOLUMETRIC_FLOW_RATE,FrameParameters.STP_VOLUMETRIC_FLOW_RATE]


async def setup_totaliser():
    flow_controller: MassFlowController  # Explicit type hint
    async with MassFlowController(address=address, unit=unit) as flow_controller:
        
        print("Setting up totaliser...")
        print("Setting device Metrics...")
        await flow_controller.set_data_frame(enable=enable, disable=disable)
        await flow_controller.get_data_frame_metrics()
        print("Enabled Metrics:")
        for stat in flow_controller.enabled_metrics:
            print(stat)
        print("Setting Gas to Nitrogen...")   
        await flow_controller.send_command(Command.SET_GAS,8) #8 for Nitrogen
        line = await flow_controller.send_command(Command.GET_GAS)
        response_parts = line.split()
        gas_id = response_parts[-1]
        assert gas_id == '8', f'Expected 8, got {line}'
        print("Gas set to Nitrogen")
        print("Totaliser Setup Complete")
            
            
            
async def tare_totaliser():
    flow_controller: MassFlowController  # Explicit type hint
    async with MassFlowController(address=address, unit=unit) as flow_controller:
        await flow_controller.get_data_frame_metrics()
        await flow_controller.send_command(Command.RESET_TOTALIZER)
        print("Taring totaliser...")
        print("WARNING: Remove inlet pressure and open outlet fittings before proceeding")
        #time.sleep(1)
        
        print("Setting bathc mass to zero")
        await flow_controller.send_command(Command.SET_TOTALIZER_BATCH,0)
        
        print("Valve is held open to clear leak critical zone ")
        await flow_controller.send_command(Command.HOLD_VALVE_OPEN)
        #time.sleep(1)
        
        print("Taring mass flowrate please wait...")
        await flow_controller.tare_mass_flowrate()
        print("Taring complete")
        
        print("Valve set to closed")
        await flow_controller.send_command(Command.HOLD_VALVE_CLOSED)
        
        print("Resetting totaliser...")
        await flow_controller.send_command(Command.RESET_TOTALIZER)
        
        start_time = time.time()
        while time.time() < start_time + 5:
            line=await flow_controller.get_state()
            print(f'Mass Flow Rate: {line.get(FrameParameters.MASS_FLOW_RATE.name)}')
            print(f'Valve Drive: {line.get(FrameParameters.VALVE_DRIVE.name)}')
           
        
        
async def test_batch(batch_mass: float = 0.1):
    flow_controller: MassFlowController  # Explicit type hint
    async with MassFlowController(address=address, unit=unit) as flow_controller:
        await flow_controller.get_data_frame_metrics()
        await flow_controller.send_command(Command.CANCEL_CLEAR_VALVE)
        await flow_controller.send_command(Command.SET_TOTALIZER_BATCH,batch_mass)
        
        result = await flow_controller.send_command(Command.GET_TOTALIZER_BATCH)
        print(f'Totaliser Batch: {result}')
        
        
        
        await flow_controller.send_command(Command.RESET_TOTALIZER)
        
        await flow_controller.send_command(Command.CANCEL_CLEAR_VALVE)
        
        await flow_controller.send_command(Command.SET_MASS_FLOW_SETPOINT,500)
        
        start_time = time.time()
        
        while time.time() < start_time + 10:
            state = await flow_controller.get_state()
             
            print(f'Mass Flow Rate: {state.get(FrameParameters.MASS_FLOW_RATE.name)}, '
                f'Valve Drive: {state.get(FrameParameters.VALVE_DRIVE.name)}, '
                f'Total Mass: {state.get(FrameParameters.TOTAL_MASS.name)}, '
                f'Totaliser Batch Remaining: {state.get(FrameParameters.TOTALIZER_BATCH_REMAINING.name)}')
    
            if state.get(FrameParameters.TOTALIZER_BATCH_REMAINING.name) == '0.0g':
                time.sleep(1)
                state = await flow_controller.get_state()
                measured_mass = state.get(FrameParameters.TOTAL_MASS.name)
                print(f'Batch of {measured_mass} out of {batch_mass}g complete')
                break
        
        await flow_controller.send_command(Command.SET_MASS_FLOW_SETPOINT,0)

#asyncio.run(setup_totaliser())
#asyncio.run(tare_totaliser())
asyncio.run(test_batch())


