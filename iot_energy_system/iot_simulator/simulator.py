"""
IoT Energy Meter Simulator
Simulates multiple energy meters generating real-time sensor data.
"""

import requests
import random
import time
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnergyMeterSimulator:
    """Simulates IoT energy meter devices."""
    
    def __init__(self, api_url, num_devices=3):
        self.api_url = api_url
        self.num_devices = num_devices
        self.devices = []
        self.running = False
        
    def initialize_devices(self):
        """Create devices in the backend."""
        logger.info(f"Initializing {self.num_devices} devices...")
        
        for i in range(1, self.num_devices + 1):
            device_data = {
                'device_id': f'EMeter-{i:03d}',
                'name': f'Energy Meter {i}',
                'location': f'Building-{(i-1)//3 + 1}, Floor-{((i-1)%3) + 1}',
                'device_type': 'combined',
                'status': 'active',
                'description': f'IoT Energy Meter #{i}'
            }
            
            try:
                # Check if device exists
                response = requests.get(
                    f"{self.api_url}/devices/",
                    params={'device_id': device_data['device_id']}
                )
                
                if response.status_code == 200 and response.json().get('results'):
                    logger.info(f"Device {device_data['device_id']} already exists")
                    self.devices.append(device_data)
                else:
                    # Create new device
                    response = requests.post(
                        f"{self.api_url}/devices/",
                        json=device_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if response.status_code in [200, 201]:
                        logger.info(f"Created device: {device_data['device_id']}")
                        self.devices.append(device_data)
                    else:
                        logger.error(f"Failed to create device: {response.text}")
                        
            except Exception as e:
                logger.error(f"Error initializing device: {e}")
                # Add device to list anyway for simulation
                self.devices.append(device_data)
    
    def get_period_type(self):
        """Determine if current time is day, night, or holiday."""
        now = datetime.now()
        hour = now.hour
        
        # Check if weekend (holiday)
        if now.weekday() >= 5:  # Saturday or Sunday
            return 'holiday'
        
        # Check time of day
        if 6 <= hour < 18:
            return 'day'
        else:
            return 'night'
    
    def generate_sensor_data(self, device_id):
        """Generate realistic sensor readings."""
        
        period = self.get_period_type()
        
        # Base values vary by period
        if period == 'day':
            base_voltage = 230 + random.uniform(-5, 5)
            base_current = random.uniform(10, 50)
            base_temp = random.uniform(25, 35)
        elif period == 'night':
            base_voltage = 230 + random.uniform(-3, 3)
            base_current = random.uniform(5, 20)
            base_temp = random.uniform(20, 28)
        else:  # holiday
            base_voltage = 230 + random.uniform(-2, 2)
            base_current = random.uniform(3, 15)
            base_temp = random.uniform(22, 30)
        
        # Calculate power and energy
        voltage = round(base_voltage, 2)
        current = round(base_current, 2)
        power = round(voltage * current, 2)
        energy_kwh = round(power / 1000 * (10 / 3600), 4)  # 10 seconds worth
        
        # Environmental parameters
        temperature = round(base_temp + random.uniform(-2, 2), 2)
        humidity = round(random.uniform(40, 80), 2)
        
        reading = {
            'device_id': device_id,
            'timestamp': datetime.now().isoformat(),
            'voltage': voltage,
            'current': current,
            'power': power,
            'energy_kwh': energy_kwh,
            'temperature': temperature,
            'humidity': humidity,
            'period_type': period
        }
        
        return reading
    
    def send_reading(self, reading):
        """Send reading to backend API."""
        try:
            response = requests.post(
                f"{self.api_url}/readings/",
                json=reading,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code in [200, 201]:
                logger.info(
                    f"✓ {reading['device_id']}: "
                    f"P={reading['power']}W, T={reading['temperature']}°C, "
                    f"H={reading['humidity']}%, Period={reading['period_type']}"
                )
                return True
            else:
                logger.error(f"Failed to send reading: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error sending reading: {e}")
            return False
    
    def start_simulation(self, interval=10):
        """Start continuous data generation."""
        logger.info(f"Starting simulation with {len(self.devices)} devices...")
        logger.info(f"Pushing data every {interval} seconds")
        logger.info("Press Ctrl+C to stop\n")
        
        self.running = True
        
        try:
            while self.running:
                for device in self.devices:
                    reading = self.generate_sensor_data(device['device_id'])
                    self.send_reading(reading)
                
                logger.info(f"--- Waiting {interval} seconds ---\n")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("\n\nSimulation stopped by user")
            self.running = False
        except Exception as e:
            logger.error(f"Simulation error: {e}")
            self.running = False


def main():
    """Main entry point for the simulator."""
    
    # Configuration
    API_URL = "http://localhost:8000/api"
    NUM_DEVICES = 5
    INTERVAL = 10  # seconds
    
    print("=" * 60)
    print("IoT Energy Meter Simulator")
    print("=" * 60)
    print(f"Backend API: {API_URL}")
    print(f"Number of devices: {NUM_DEVICES}")
    print(f"Data push interval: {INTERVAL} seconds")
    print("=" * 60)
    print()
    
    # Create simulator instance
    simulator = EnergyMeterSimulator(API_URL, NUM_DEVICES)
    
    # Initialize devices
    simulator.initialize_devices()
    
    # Start simulation
    simulator.start_simulation(INTERVAL)


if __name__ == '__main__':
    main()
