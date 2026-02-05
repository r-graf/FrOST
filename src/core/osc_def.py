import os
if os.getenv("CUDA_VISIBLE_DEVICES") is None:
    gpu_num = 0 # Use "" to use the CPU
    os.environ["CUDA_VISIBLE_DEVICES"] = f"{gpu_num}"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Import Sionna
try:
    import sionna.phy
except ImportError as e:
    import sys
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
import math as math
import reedsolo as rs

print("\n--------------------------------------\n")
print("BEGIN TOOL")

def OpticalSatcomChain(bitstream, modulation="o3k", uncoded=True, ldpc=True, graphic=True, n=16384 ,k=8192, RS = True, ebn0_min=0., ebn0_max=12., simsteps=12):
    
    b = bitstream
    print("Bitstream:", b)

    ###############
    ### UNCODED ###
    ###############

    # Modulation incl. average power = 1
    print("\nModulation:    ", modulation)
    if modulation == "o3k":
        constellation = sionna.phy.mapping.Constellation("custom", 1, points=[0 , 2])
    elif modulation == "bpsk":
        constellation = sionna.phy.mapping.Constellation("custom", 1, points=[-1 , 1])
    else:
        print("FATAL: UNDEFINED MODULATION SCHEME")
        return
    print("Constellation: ", constellation.points.numpy())
    mapper = sionna.phy.mapping.Mapper(constellation=constellation)
    modulated_bitstream = mapper(bitstream)
    #print("modulated_fec_bitstream:", modulated_bitstream)
    # PLACEHOLDER FSO CHANNEL FROM TIME SERIES

    awgn = sionna.phy.channel.AWGN()
    
    # Simulation Loop for different Eb/N0
    # Simulation Loop parameter
    EBNO_MIN = ebn0_min
    EBNO_MAX = ebn0_max
    sim_steps = simsteps
    # Loop for plotting
    EbNo_dB_range = np.linspace(EBNO_MIN, EBNO_MAX, sim_steps)
    itr = len(EbNo_dB_range)
    ber_uncoded = []
    ber_math = []

    if uncoded == True:
        # Loop
        for snr in range(0, itr):
            # Channel
            ebno_db = EbNo_dB_range[snr]
            no_db = sionna.phy.utils.ebnodb2no(ebno_db=ebno_db, num_bits_per_symbol=1, coderate=.5) * .5 # noise has variance no/2 per real dimension
            #print("no_db =", no_db)
            noised_modulated_bitstream = awgn(modulated_bitstream, no_db)
            #print("noised_modulated_bitstream", noised_modulated_bitstream) 

            # Demodulation
            demapper = sionna.phy.mapping.Demapper("app", constellation=constellation, hard_out=True)
            noised_bitstream = demapper(noised_modulated_bitstream, no_db)
            #print(u_d)

            # Decoding

            # BER Calculation
            ebno_lin = 10 ** (-ebno_db/20)
            theoretical_ber = 0.5 * math.erfc(math.sqrt(10 ** (ebno_db / 10)))
            sionna_ber = sionna.phy.utils.compute_ber(bitstream, noised_bitstream)
            #print("sionna_ber",sionna_ber.numpy())
            ber_uncoded.append(sionna_ber.numpy())
            ber_math.append(theoretical_ber)
            print("\nResults: Eb/N0 = ", ebno_db, "dB,   n0 = ", no_db.numpy(), "dB" )
            print("Math.     BER  = ", theoretical_ber)
            print("uncoded:  BER  = ", ber_uncoded[snr])

        plt.plot(EbNo_dB_range, ber_uncoded, 'g', label="uncoded")
        plt.plot(EbNo_dB_range, ber_math, 'rx', label="Theory")

    ##############
    ###  LDPC  ###
    ##############

    if ldpc == True:
        # LDPC Coding

        print("\nModulation:    ", modulation)
        if modulation == "o3k":
            constellation = sionna.phy.mapping.Constellation("custom", 1, points=[0 , 2])
        elif modulation == "bpsk":
            constellation = sionna.phy.mapping.Constellation("custom", 1, points=[-1 , 1])
        else:
            print("FATAL: UNDEFINED MODULATION SCHEME")
            return
        
        mapper = sionna.phy.mapping.Mapper(constellation=constellation)
                
        demapper = sionna.phy.mapping.Demapper("app", constellation=constellation)

        ldpc_coder = sionna.phy.fec.ldpc.encoding.LDPC5GEncoder(k,n)
        ldpc_b = ldpc_coder(b)
        #print("ldpc_b", ldpc_b)

        # Mapping
        ldpc_mapped = mapper(ldpc_b)
        #print("ldpc_mapped", ldpc_mapped)

        # FSo Channel Channel

        # AWGN
        ber_ldpc = []
        for snr in range(0, itr):
            ebno_db = EbNo_dB_range[snr]
            no_db = sionna.phy.utils.ebnodb2no(ebno_db=ebno_db, num_bits_per_symbol=1, coderate=.5) # noise has variance no/2 per real dimension
            ldpc_noised_mapped = awgn(ldpc_mapped, no_db)
            #print("ldpc_noised_mapped", ldpc_noised_mapped)

            # Demapping
            ldpc_noised_demapped = demapper(ldpc_noised_mapped, no_db)
            #print("ldpc_noised_demapped", ldpc_noised_demapped)

            # Decoding
            ldpc_decoder = sionna.phy.fec.ldpc.decoding.LDPC5GDecoder(ldpc_coder)
            ldpc_noised_decoded = ldpc_decoder(ldpc_noised_demapped)
            #print("ldpc_noised_decoded", ldpc_noised_decoded)
            
            # BER Calculation
            sionna_ber = sionna.phy.utils.compute_ber(bitstream, ldpc_noised_decoded)
            #print("sionna_ber",sionna_ber.numpy())
            ber_ldpc.append(sionna_ber.numpy())
            print("\nResults: Eb/N0 =", ebno_db, "dB,   n0 = ", no_db.numpy(), "dB" )
            print("LDPC:     BER  = ", ber_ldpc[snr])
            if sionna_ber == 0:
                ber_ldpc.extend([sionna_ber.numpy()] * (itr - snr - 1))
                break
        plt.plot(EbNo_dB_range, ber_ldpc, 'b-s', label="LDPC")

    ###################
    ### RS(255,223) ###
    ###################
    
    if RS == True:
        RS_N = 255
        RS_K = 223
        BITS_PER_BYTE = 8
        SIM_LOOP = 1000
        ber_rs = []

        msg = np.random.bytes(RS_K)
        rs_encoder = rs.RSCodec(RS_N - RS_K)
        codeword = rs_encoder.encode(msg)  # 255 bytes

        bits = np.unpackbits(np.frombuffer(codeword, dtype=np.uint8))
        tf_bits = tf.constant(bits, dtype=tf.int32)
        tx = mapper(tf.reshape(tf_bits, (1, -1)))

        for snr in range(0, itr):
            total_bits_uncoded = 0
            total_bits_rs = 0
            bit_errs_rs = 0
            ebno_db = EbNo_dB_range[snr]
            no_rs = sionna.phy.utils.ebnodb2no(ebno_db=ebno_db, num_bits_per_symbol=1, coderate=(RS_K/RS_N))

            for iter in range(SIM_LOOP):
                rx = awgn(tx, no_rs)

                demapper = sionna.phy.mapping.Demapper("app", constellation=constellation, hard_out=True)
                demapped_bits_rs = demapper(rx, no_rs).numpy().astype(np.uint8)[0]

                # BER (uncoded before RS decoding)
                # bit_errs_uncoded += np.sum(bits != demapped_bits_rs)
                total_bits_uncoded += len(bits)

                # RS decode
                rx_bytes = np.packbits(demapped_bits_rs)
                try:
                    decoded_msg, _, _ = rs_encoder.decode(rx_bytes)
                    ref_bits = np.unpackbits(np.frombuffer(msg, dtype=np.uint8))
                    dec_bits = np.unpackbits(np.frombuffer(decoded_msg, dtype=np.uint8))
                    bit_errs = np.sum(ref_bits != dec_bits)
                    bit_errs_rs += bit_errs
                    #print("Bit Error: ", bit_errs)
                except rs.ReedSolomonError:
                    bit_errs_rs += RS_K * BITS_PER_BYTE   # uncorrectable
                    #print("uncorrectable")
                total_bits_rs += RS_K * BITS_PER_BYTE
            # Loop End

            ber_rs.append(bit_errs_rs / total_bits_rs)
            print("\nResults: Eb/N0 =", ebno_db, "dB,   n0 = ", no_db.numpy(), "dB" )
            print("RS:       BER  = ", ber_rs[snr], "at ", total_bits_rs, "Bits and with Bit Errors: ", bit_errs_rs)
            if ber_rs[snr] == 0:
                ber_rs.extend([ber_rs[snr]] * (itr - snr - 1))
                break

        plt.plot(EbNo_dB_range, ber_rs, 'm-.', label="RS(255,223)")

    results = list(zip(EbNo_dB_range, ber_math, ber_uncoded))

    if graphic == True:
        
        plt.xscale('linear')
        plt.yscale('log')
        plt.xlabel('EbNo(dB)')
        plt.ylabel('BER')
        plt.grid(True)
        if modulation == "o3k":
            plt.title('O3K Modulation')
        elif modulation == "bpsk":
            plt.title('BPSK Modulation')
        plt.legend()
        plt.show()

    return results




def bitstream(k, n, batch=150, num_bits_per_symbol=1):
    # Generating input bitstream
    binary_source = sionna.phy.mapping.BinarySource()
    b = binary_source([batch, k]) # binary input stream
    #b = tf.reshape(b, [number_of_blocks, k])
    
    return b
