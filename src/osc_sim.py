import yaml
import osc_def
from pathlib import Path

config_path = Path(__file__).parent / "config.yaml"

#print(f"Suche Config unter: {config_path}") # Kleine Hilfe fürs Debugging

with open(config_path, "r") as f:
    config = yaml.safe_load(f)


#print("\n--------------------------------------\n")

# Defining Code Parameter
n = 16384 # number of codeword bits (output)
print("K: number of codeword bits (output Coder):       n = ", n)
k = int(n / 2) # number of information bits (input)
print("N: number of information bits (input Coder):     k = ", k)
code_rate = k / n # r = k/n
print("R: Code rate:                                    r = ", code_rate)
num_bits_per_symbol = 1 # OOK

# Generating input bitstream
# number_of_blocks = 150 # arbitrary choosen
# batch_size = k * number_of_blocks # Number of symbols we want to generate

b = osc_def.bitstream(k, n, batch=150)

# Simulation Loop
results = osc_def.OpticalSatcomChain(b,
                                     config,
                                     "bpsk",
                                     ebn0_min=-1,
                                     ebn0_max=12,
                                     simsteps=54,
                                     ldpc=True,
                                     RS=True)
print("\n\nEND SIMULATION")