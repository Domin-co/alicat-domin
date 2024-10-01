import asyncio
from alicat import MassFlowController

import time


async def get():
    flow_controller: MassFlowController  # Explicit type hint

    async with MassFlowController(address = 'COM3',unit='A') as flow_controller:
        
        await flow_controller.cancel_clear()
        
        await flow_controller.set_totalizer_batch_mass(0.2)
        
        result= await flow_controller.get_totalizer_batch_mass()
        print(f'Totaliser Batch: {result}')
        
        await flow_controller.reset_totaliser()
        
        await flow_controller.cancel_clear()
        
              
                
        await flow_controller.set_flow_setpoint(200)
        
        start_time = time.time()
        
        while time.time() < start_time + 10:
            state= await flow_controller.get_state()
            print(f'State: {state}')
        
       
        
        await flow_controller.zero_flow_setpoint()
        
        
        #result= await flow_controller.get_totalizer_batch_mass()
        #print(f'Totaliser Batch: {result}')


asyncio.run(get())


