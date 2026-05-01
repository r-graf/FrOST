import yaml
import osc_def
from pathlib import Path

config_path = Path(__file__).parent / "config.yaml"

print(f"Suche Config unter: {config_path}") # Kleine Hilfe fürs Debugging

with open(config_path, "r") as f:
    config = yaml.safe_load(f)


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
# number_of_blocks = 150 # arbitrary choosen
# batch_size = k * number_of_blocks # Number of symbols we want to generate

b = osc_def.bitstream(k, n, batch=1000)

# Simulation Loop
results = osc_def.OpticalSatcomChain(b,
                                     config,
                                     "bpsk",
                                     ebn0_min=-1,
                                     ebn0_max=12,
                                     simsteps=27,
                                     ldpc=False,
                                     RS=False)
print("\n\nEND SIMULATION")