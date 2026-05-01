import os
import sys

import yaml
import osc_def
from pathlib import Path

config_path = Path(__file__).parent / "config.yaml"

print(f"Suche Config unter: {config_path}") # Kleine Hilfe fürs Debugging

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

if os.getenv("CUDA_VISIBLE_DEVICES") is None:
    gpu_num = 0 # Use "" to use the CPU
    os.environ["CUDA_VISIBLE_DEVICES"] = f"{gpu_num}"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Import Sionna
try:
    import sionna.phy
except ImportError as e:
    if 'google.colab' in sys.modules:
       # Install Sionna in Google Colab
       print("Installing Sionna and restarting the runtime. Please run the cell again.")
       os.system("pip install sionna")
       os.kill(os.getpid(), 5)
    else:
       raise e

# IPython "magic function" for inline plots
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np

print("\n--------------------------------------\n")

# Defining Code Parameter
n = 16384 # number of codeword bits (output)
print("number of codeword bits (output):       n = ", n)
k = int(n / 2) # number of information bits (input)
print("number of information bits (input):     k = ", k)
code_rate = k / n # r = k/n
print("Code rate:                              r = ", code_rate)
num_bits_per_symbol = 1 # OOK

# Generating input bitstream
#number_of_blocks = 150 # arbitrary choosen
#batch_size = k * number_of_blocks # Number of symbols we want to generate
#binary_source = sionna.phy.mapping.BinarySource()
#b = binary_source([batch_size, num_bits_per_symbol]) # binary input stream
#b = tf.reshape(b, [number_of_blocks, k])

b = osc_def.bitstream(k, n, batch=1000)

# Simulation
results = osc_def.OpticalSatcomChain(b, config, "bpsk", ebn0_min=-1, ebn0_max=12, simsteps=27, ldpc=False, RS=False)
#osc_sim.OpticalSatcomChain(b, "o3k")
#print("\nSimulation result vector: \n",results)
print("\n\nEND SIMULATION")