import asyncio
import math
import time
import threading
import struct
from typing import List, Optional

# Third-party libraries
from bleak import BleakScanner, BleakClient
import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT, K_SPACE, KEYDOWN

# OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *


DEVICE_NAME = "open-ring"

CHAR_UUID = "0000fe4-0000-1000-8000-00805f9b34fb" 


ACCEL_SENS = 16384.0  
GYRO_SENS  = 131.0     


COMP_ALPHA   = 0.98    
LPF_ALPHA    = 0.3     
GRAVITY      = 9.81
VEL_DAMPING  = 0.98   
POS_SCALE    = 0.1    


class SharedState:

    def __init__(self):
        self.lock = threading.Lock()
        self.running = True
        

        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0


        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0
        

        self.ax_g = 0.0
        self.ay_g = 0.0
        self.az_g = 0.0
        self.gx_dps = 0.0
        self.gy_dps = 0.0
        self.gz_dps = 0.0
        self.initialized = False
    
    def reset_position(self):

        with self.lock:
            self.x = self.y = self.z = 0.0
            self.vx = self.vy = self.vz = 0.0
            print("Position reset.")

class MathUtils:
    @staticmethod
    def low_pass(prev: float, new_val: float, alpha: float) -> float:
        return prev + alpha * (new_val - prev)

    @staticmethod
    def euler_to_rotation_matrix(roll, pitch, yaw):
        """Returns 3x3 rotation matrix for transforming accel vector."""
        cr, sr = math.cos(roll), math.sin(roll)
        cp, sp = math.cos(pitch), math.sin(pitch)
        cy, sy = math.cos(yaw), math.sin(yaw)

        # ZYX rotation sequence
        return [
            [cy * cp,  cy * sp * sr - sy * cr,  cy * sp * cr + sy * sr],
            [sy * cp,  sy * sp * sr + cy * cr,  sy * sp * cr - cy * sr],
            [-sp,      cp * sr,                cp * cr]
        ]

class BLEManager:

    def __init__(self, state: SharedState):
        self.state = state
        self.last_update_time = None

    def notification_handler(self, sender, data: bytearray):
        try:
            # Decode data (Expected format: "ax,ay,az,gx,gy,gz")
            text = data.decode("utf-8", errors='ignore').strip()
            parts = text.split(",")
            
            if len(parts) != 6:
                return 


            raw_vals = [float(x) for x in parts]
            ax_raw, ay_raw, az_raw, gx_raw, gy_raw, gz_raw = raw_vals

            self.process_physics(ax_raw, ay_raw, az_raw, gx_raw, gy_raw, gz_raw)

        except ValueError:
            pass 
        except Exception as e:
            print(f"Data Error: {e}")

    def process_physics(self, ax_r, ay_r, az_r, gx_r, gy_r, gz_r):
        current_time = time.time()
        if self.last_update_time is None:
            self.last_update_time = current_time
            return
        
        dt = current_time - self.last_update_time
        self.last_update_time = current_time
        

        if dt <= 0 or dt > 0.1:
            dt = 0.01

        ax_g_new = ax_r / ACCEL_SENS
        ay_g_new = ay_r / ACCEL_SENS
        az_g_new = az_r / ACCEL_SENS
        gx_dps_new = gx_r / GYRO_SENS
        gy_dps_new = gy_r / GYRO_SENS
        gz_dps_new = gz_r / GYRO_SENS

        with self.state.lock:

            if not self.state.initialized:
                self.state.ax_g, self.state.ay_g, self.state.az_g = ax_g_new, ay_g_new, az_g_new
                self.state.gx_dps, self.state.gy_dps, self.state.gz_dps = gx_dps_new, gy_dps_new, gz_dps_new
                self.state.initialized = True
            else:
                self.state.ax_g = MathUtils.low_pass(self.state.ax_g, ax_g_new, LPF_ALPHA)
                self.state.ay_g = MathUtils.low_pass(self.state.ay_g, ay_g_new, LPF_ALPHA)
                self.state.az_g = MathUtils.low_pass(self.state.az_g, az_g_new, LPF_ALPHA)
                self.state.gx_dps = MathUtils.low_pass(self.state.gx_dps, gx_dps_new, LPF_ALPHA)
                self.state.gy_dps = MathUtils.low_pass(self.state.gy_dps, gy_dps_new, LPF_ALPHA)
                self.state.gz_dps = MathUtils.low_pass(self.state.gz_dps, gz_dps_new, LPF_ALPHA)


            roll_acc = math.atan2(self.state.ay_g, self.state.az_g)
            pitch_acc = math.atan2(-self.state.ax_g, math.sqrt(self.state.ay_g**2 + self.state.az_g**2))


            self.state.roll += math.radians(self.state.gx_dps) * dt
            self.state.pitch += math.radians(self.state.gy_dps) * dt
            self.state.yaw += math.radians(self.state.gz_dps) * dt


            self.state.roll = COMP_ALPHA * self.state.roll + (1.0 - COMP_ALPHA) * roll_acc
            self.state.pitch = COMP_ALPHA * self.state.pitch + (1.0 - COMP_ALPHA) * pitch_acc
            

            R = MathUtils.euler_to_rotation_matrix(self.state.roll, self.state.pitch, self.state.yaw)
            

            acc_local = [self.state.ax_g * GRAVITY, self.state.ay_g * GRAVITY, self.state.az_g * GRAVITY]
            

            acc_world = [
                sum(R[0][i] * acc_local[i] for i in range(3)),
                sum(R[1][i] * acc_local[i] for i in range(3)),
                sum(R[2][i] * acc_local[i] for i in range(3))
            ]

            # Subtract Gravity (Assume World Z is up)
            acc_world[2] -= GRAVITY

            # Thresholding (ignore tiny movements to stop drift)
            if abs(acc_world[0]) < 0.2: acc_world[0] = 0
            if abs(acc_world[1]) < 0.2: acc_world[1] = 0
            if abs(acc_world[2]) < 0.2: acc_world[2] = 0


            self.state.vx += acc_world[0] * dt
            self.state.vy += acc_world[1] * dt
            self.state.vz += acc_world[2] * dt

            self.state.vx *= VEL_DAMPING
            self.state.vy *= VEL_DAMPING
            self.state.vz *= VEL_DAMPING

            self.state.x += self.state.vx * dt
            self.state.y += self.state.vy * dt
            self.state.z += self.state.vz * dt

    async def run(self):
        print(f"Scanning for device with name containing: '{DEVICE_NAME}'...")
        device = await BleakScanner.find_device_by_filter(
            lambda d, ad: d.name and DEVICE_NAME in d.name,
            timeout=10.0
        )

        if not device:
            print("Device not found. Please ensure it is powered on.")
            self.state.running = False
            return

        print(f"Connecting to {device.name}...")
        
        try:
            async with BleakClient(device) as client:
                print(f"Connected. subscribing to {CHAR_UUID}")
                await client.start_notify(CHAR_UUID, self.notification_handler)
                
                while self.state.running:
                    if not client.is_connected:
                        print("Device disconnected unexpectedly.")
                        break
                    await asyncio.sleep(0.5)
                
                await client.stop_notify(CHAR_UUID)
        except Exception as e:
            print(f"Bluetooth Error: {e}")
            self.state.running = False

class Visualizer:
    def __init__(self, state: SharedState):
        self.state = state
        self.display_dim = (800, 600)

    def draw_axis(self):
        glBegin(GL_LINES)
        # X Axis (Red)
        glColor3f(1, 0, 0); glVertex3f(0, 0, 0); glVertex3f(1, 0, 0)
        # Y Axis (Green)
        glColor3f(0, 1, 0); glVertex3f(0, 0, 0); glVertex3f(0, 1, 0)
        # Z Axis (Blue)
        glColor3f(0, 0, 1); glVertex3f(0, 0, 0); glVertex3f(0, 0, 1)
        glEnd()

    def draw_glider(self):
        """Draws a 3D Paper Plane / Dart shape using Triangles."""
        glBegin(GL_TRIANGLES)

        

        glColor3f(0.2, 0.6, 1.0)
        
        # Left Wing Top
        glVertex3f(0.0, 0.0, -1.5)  
        glVertex3f(-1.0, 0.0, 1.0)  
        glVertex3f(0.0, 0.2, 1.0) 
        
        # Right Wing Top
        glVertex3f(0.0, 0.0, -1.5)  
        glVertex3f(1.0, 0.0, 1.0)  
        glVertex3f(0.0, 0.2, 1.0)   


        glColor3f(0.1, 0.4, 0.8)
        

        glVertex3f(0.0, 0.0, -1.5)
        glVertex3f(-1.0, 0.0, 1.0)
        glVertex3f(0.0, -0.2, 1.0)  


        glVertex3f(0.0, 0.0, -1.5)
        glVertex3f(1.0, 0.0, 1.0)
        glVertex3f(0.0, -0.2, 1.0)


        glColor3f(0.6, 0.6, 0.6) 
        glVertex3f(-1.0, 0.0, 1.0)
        glVertex3f(1.0, 0.0, 1.0)
        glVertex3f(0.0, 0.2, 1.0)

        glVertex3f(-1.0, 0.0, 1.0)
        glVertex3f(1.0, 0.0, 1.0)
        glVertex3f(0.0, -0.2, 1.0)

        glEnd()

    def main_loop(self):
        pygame.init()
        pygame.display.set_mode(self.display_dim, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("IMU Visualizer | Press SPACE to Reset Position")

        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (self.display_dim[0] / self.display_dim[1]), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        
        clock = pygame.time.Clock()

        while self.state.running:
 
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.state.running = False
                elif event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        self.state.reset_position()

      
            with self.state.lock:
                roll = self.state.roll
                pitch = self.state.pitch
                yaw = self.state.yaw
                x = self.state.x * POS_SCALE
                y = self.state.y * POS_SCALE
                z = self.state.z * POS_SCALE


            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            
            glTranslatef(0.0, 0.0, -8.0)
            

            glTranslatef(x, y, z)
            

            glRotatef(math.degrees(yaw), 0, 1, 0)   
            glRotatef(math.degrees(pitch), 1, 0, 0) 
            glRotatef(math.degrees(roll), 0, 0, 1) 

            self.draw_axis()
            self.draw_glider()

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    shared_state = SharedState()
    

    ble_manager = BLEManager(shared_state)
    ble_thread = threading.Thread(target=lambda: asyncio.run(ble_manager.run()), daemon=True)
    ble_thread.start()


    viz = Visualizer(shared_state)
    try:
        viz.main_loop()
    except KeyboardInterrupt:
        pass
    finally:
        shared_state.running = False
        print("Exiting...")