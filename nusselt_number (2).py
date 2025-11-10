import os
import numpy as np

# =============================================================================
# ## USER INPUT: YOU MUST CHANGE THESE THREE VARIABLES ##
# =============================================================================

# 1. Path to your OpenFOAM case directory. 
#    If you place this script inside your case folder, this can just be '.'
case_path = '.' 

# 2. Characteristic Length (L) in meters. 
#    (e.g., pipe diameter, plate length)
L_char = 0.5      # [m] <-- CHANGE THIS

# 3. Thermal Conductivity (k) of the fluid in W/(m·K).
#    (Find this in your 'constant/thermophysicalProperties' file)
k_fluid = 0.025    # [W/(m·K)] <-- CHANGE THIS

# =============================================================================

def parse_h_values(filepath):
    """
    Parses an OpenFOAM boundary field file to extract a list of scalar values.
    """
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return None # File doesn't exist for this timestep

    data_started = False
    h_values = []
    
    for line in lines:
        if line.strip() == '(':
            data_started = True
            continue
        if line.strip() == ')':
            break
        if data_started:
            try:
                h_values.append(float(line.strip()))
            except (ValueError, IndexError):
                continue
                
    return h_values

def main():
    """
    Main function to find time directories and calculate Nusselt number.
    """
    print("--- Starting Nusselt Number Calculation ---")
    print(f"Characteristic Length (L): {L_char} m")
    print(f"Fluid Thermal Conductivity (k): {k_fluid} W/(m·K)")
    print("-" * 50)
    print(f"{'Time [s]':<12} | {'Avg. h [W/m^2K]':<20} | {'Nusselt Number (Nu)':<20}")
    print("-" * 50)

    # Find all directories in the case path that are numbers (timesteps)
    time_dirs = [d for d in os.listdir(case_path) if os.path.isdir(os.path.join(case_path, d)) and d.replace('.','',1).isdigit()]
    
    # Sort time directories numerically
    time_dirs.sort(key=float)

    if not time_dirs:
        print("Error: No time directories found. Make sure 'case_path' is correct.")
        return

    # Loop through each time directory
    for t in time_dirs:
        # Construct the full path to the file
        h_filepath = os.path.join(case_path, t, 'wallHeatTransferCoeff')
        
        if not os.path.exists(h_filepath):
            continue # Skip if the file doesn't exist (e.g., in time '0')

        # Get the list of h values from the file
        h_list = parse_h_values(h_filepath)
        
        if h_list:
            # Calculate the average h for the current timestep
            avg_h = np.mean(h_list)
            
            # Calculate the Nusselt number
            nusselt_number = (avg_h * L_char) / k_fluid
            
            # Print the formatted results
            print(f"{t:<12} | {avg_h:<20.4f} | {nusselt_number:<20.2f}")
            
    print("-" * 50)
    print("--- Calculation Complete ---")


if __name__ == "__main__":
    main()