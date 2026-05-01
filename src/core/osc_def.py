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
import matplotlib.ticker as ticker
import tensorflow as tf
import numpy as np
import math as math
import reedsolo as rs
from scipy.special import erf

print("\n--------------------------------------\n")
print("BEGIN TOOL")

def get_fso_link_offset(config):
    """
    Berechnet den Offset zwischen Eb/N0 (dB) und der Sendeleistung P_tx (dBm).
    Basierend auf den physikalischen Parametern aus deinem Test-Skript.
    """
    # --- Parameter (Diese könntest du später auch als Argumente übergeben) ---
    # L_km = 2.0
    # visibility_km = 4.0
    # wavelength_nm = 1550.0
    # rx_aperture_cm = 10.0
    # theta_mrad = 1.5
    # R_resp = 0.9          # Responsivity
    # data_rate = 1e9       # 1 Gbps
    # T_kelvin = 300
    # R_load = 50
    # kB = 1.38e-23
    # q_charge = 1.602e-19

    lp = config['link_params']
    L_km = lp['L_km']
    visibility_km = lp['visibility_km']
    wavelength_nm = lp['wavelength_nm']
    theta_mrad = lp['theta_mrad']

    rp = config['receiver_params']
    rx_aperture_cm = rp['rx_aperture_cm']
    R_resp = rp['R_resp']
    data_rate = rp['data_rate']
    T_kelvin = rp['T_kelvin']
    R_load = rp['R_load']

    c = config['constants']
    kB = c['kB']
    q_charge = c['q_charge']

    # 1. Geometrische Verluste
    w_L = (theta_mrad / 2000.0) * (L_km * 1000)
    rx_radius_m = (rx_aperture_cm / 100.0) / 2.0
    v = (np.sqrt(np.pi) * rx_radius_m) / (np.sqrt(2) * w_L)
    h_geo = erf(v)**2

    # 2. Atmosphärische Verluste (Kim Modell)
    q = 0.585 * (visibility_km**(1/3)) if visibility_km <= 6 else 1.3
    sigma_atm = (3.91 / visibility_km) * ((wavelength_nm / 550.0)**(-q))
    h_atm = np.exp(-sigma_atm * L_km)

    # 3. Rauschen (Thermal Noise Dominant)
    # Wir nehmen an, dass das Rauschen konstant ist (Worst Case für den Offset)
    sigma_sq_thermal = (4 * kB * T_kelvin * data_rate) / R_load
    
    # 4. Der "Brückenschlag"
    # P_rx = P_tx * h_geo * h_atm
    # I_sig = P_rx * R_resp
    # SNR = (I_sig^2) / sigma_sq_total
    # Wir setzen P_tx = 1W (30 dBm) als Referenz und schauen, welches Eb/N0 dabei rauskommt.
    p_tx_ref_dbm = 30.0
    p_tx_ref_w = 1.0
    p_rx = p_tx_ref_w * h_geo * h_atm
    i_sig = p_rx * R_resp
    snr_lin = (i_sig**2) / sigma_sq_thermal
    ebn0_db_ref = 10 * np.log10(snr_lin) # Bei OOK/BPSK (1 Bit/Symbol) ist EbN0 approx SNR

    # Offset: P_tx_dBm = EbN0_dB + Offset
    offset = p_tx_ref_dbm - ebn0_db_ref
    print("\n--- LINK BUDGET VERIFIKATION ---")
    print(f"Linklänge:               {L_km} km")
    print(f"Visibilität:             {visibility_km} km")
    print(f"Divergenzwinkel:         {theta_mrad} mrad")
    print(f"Geometrischer Verlust:   {10 * np.log10(h_geo):.2f} dB")
    print(f"Atmosphärischer Verlust: {10 * np.log10(h_atm):.2f} dB")
    print(f"Totaler Kanal-Verlust:   {10 * np.log10(h_geo * h_atm):.2f} dB")
    print(f"Thermische Rauschleistung: {sigma_sq_thermal:.2e} A^2")
    print(f"Signalstrom bei 30 dBm:    {i_sig:.2e} A")
    print(f"Resultierendes Eb/N0:    {ebn0_db_ref:.2f} dB")
    print("--------------------------------\n")
    return offset

def OpticalSatcomChain(bitstream, config, modulation="o3k", uncoded=True, ldpc=True, graphic=True, n=16384 ,k=8192, RS = True, ebn0_min=0., ebn0_max=12., simsteps=12):
    
    b = bitstream
    print("Bitstream:", b)

    if graphic == True:
        fig, ax1 = plt.subplots(figsize=(10, 6))

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
    # PLACEHOLDER FSO CHANNEL FROM TIME SERIES ULTRAAIR

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

        if graphic == True:
            ax1.plot(EbNo_dB_range, ber_uncoded, 'g', label="Uncoded")
            ax1.plot(EbNo_dB_range, ber_math, 'rx', label="Theoretical Uncoded")

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
        
        if graphic == True:
            ax1.plot(EbNo_dB_range, ber_ldpc, 'b-s', label="LDPC")

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

        if graphic == True:
            ax1.plot(EbNo_dB_range, ber_rs, 'm-.', label="RS(255,223)")

    results = list(zip(EbNo_dB_range, ber_math, ber_uncoded))

    if graphic == True:
        ax1.set_xlim([ebn0_min, ebn0_max])
        ax1.set_yscale('log')
        ax1.set_xlabel('Eb/N0 (dB)')
        ax1.set_ylabel('BER')
        ax1.grid(True, which="both", ls="-", color='0.85') # Macht das Grid schöner
        
        if modulation == "o3k":
            ax1.set_title('O3K Modulation Performance')
        elif modulation == "bpsk":
            ax1.set_title('BPSK Modulation Performance')
            
        ax1.legend()

        # Obere Achse (Sendeleistung) berechnen und anfügen
        offset = get_fso_link_offset(config)
        distance = config['link_params']['L_km']
        ax2 = ax1.twiny()
        ax2.set_xlim([ebn0_min + offset, ebn0_max + offset])
        ax2.set_xlabel(f'Benötigte Sendeleistung $P_{{tx}}$ (dBm) bei L={distance}km, Visibility={config["link_params"]["visibility_km"]}km und Divergenzwinkel={config["link_params"]["theta_mrad"]}mrad', color='tab:blue')
        ax2.tick_params(axis='x', colors='tab:blue')

        ax2.xaxis.set_major_locator(ticker.MultipleLocator(2))
        ax2.xaxis.set_minor_locator(ticker.MultipleLocator(1))

        plt.tight_layout()
        plt.show()

    return results

def bitstream(k, n, batch=150, num_bits_per_symbol=1):
    # Generating input bitstream
    binary_source = sionna.phy.mapping.BinarySource()
    b = binary_source([batch, k]) # binary input stream
    #b = tf.reshape(b, [number_of_blocks, k])
    
    return b