#import drug_functions
#import model_functions
import sys
import json
import subprocess
import os
import uuid

# Example sequences (commented out):
# NNRTI and NRTI
# SEQ = 'PISPIETVPVKLKPGMDGPRVKQWPLTEEKIKALMEICTEMEKEGKISKIGPENPYNTPVFAIKKKDSDKWRKLVDFRELNKRTQDFWEVQLGIPHPAGLKQKKSVTVLDVGDAYFSVPLDKDFRKYTAFTIPSINNETPGIRYQYNVLPQGWKGSPAIFQCSMTKILEPFRKQNPDLVIYQYMDDLYVGSDLEIGQHRTKIEELREHLLRWGFTTPDKKHQKEPPFLWMGYELHPDKWT'
# PI
# SEQ = 'PQITLWQRPLVTIKIGGQLKEALLDTGADDTVLEEMNLPGRWKPKMIGGIGGFIKVRQYDQILIEICGHKAIGTVLVGPTPVNIIGRNLLTQIGCTLNF'

def get_bin_seq_from(seq: str, peps: dict) -> dict:
    """
    Generates a binary sequence representation based on peptide presence.
    
    Args:
        seq (str): Input protein sequence
        peps (dict): Dictionary of peptides to check for presence in sequence
    
    Returns:
        dict: Binary list where 1 indicates peptide presence, 0 indicates absence
    """
    bin_seq = []
    for pep in peps:
        bin_seq.append(1 if seq.find(str(pep)) >= 0 else 0)
    return bin_seq

# Generate unique ID for temporary files
id_uniq = uuid.uuid4().hex

# Change to working directory - NOTE: Update path to your target directory
os.chdir('D:\\Dir\\')  # TODO: Replace with actual target directory

pipes = []

# Check if command line arguments are provided
if len(sys.argv) > 2:
    dr_type = sys.argv[1]  # Drug type (PI, RTI, or IN)
    seq = sys.argv[2]      # Protein sequence

    # Define drug names for each type
    name_drug = {}
    name_drug["PI"] = ["FPV", "ATV", "DRV", "IDV", "NFV", "TPV", "ATV"]  # Protease Inhibitors
    name_drug["RTI"] = ["3TC", "AZT", "D4T", "ABC"]  # Reverse Transcriptase Inhibitors
    name_drug["IN"] = ["EVG", "RAL"]  # Integrase Inhibitors
    
    res_fin = {}  # Dictionary to store final results
    
    # Process if drug type is valid
    if dr_type in name_drug:
        for drug in name_drug[dr_type]:
            # Define directory and file paths
            dir_all = "D:\\Dir\\" + drug + "\\"
            file_res = "D:\\Dir\\" + id_uniq + "_" + drug + ".csv"
            pept_file = dir_all + 'finger.txt'
            
            # Read peptide list from file
            pept_list = []
            with open(pept_file) as f:
                for line in f:
                    pept_list.append(line.strip())
            
            # Generate binary fingerprint for sequence
            res_finger = get_bin_seq_from(seq, pept_list)
            
            # Write results to temporary CSV file
            with open(file_res, "w+") as f:
                i_max = len(pept_list)
                str_up = ""  # Header line with peptide names
                str_down = ""  # Data line with binary values
                for i in range(i_max):
                    str_up += pept_list[i] + ','
                    str_down += str(res_finger[i]) + ','
                f.write(str_up[:-1] + '\n')  # Write header (remove trailing comma)
                f.write(str_down[:-1])       # Write data (remove trailing comma)

            # Launch child process for prediction
            child = os.path.join(os.path.dirname(__file__), "./child1.py")
            command = [sys.executable, child]
            pipe = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            pipes.append(pipe)
            
            # Send parameters to child process
            pipe.stdin.write(drug.encode("utf8") + b"\n")
            pipe.stdin.write(id_uniq.encode("utf8") + b"\n")
            pipe.stdin.close()

        # Collect results from child processes
        while pipes:
            pipe = pipes.pop()
            out = pipe.communicate()
            str_out = out[0].decode('cp1251')  # Decode output
            drug, fin = str_out.strip().split(';')  # Parse drug name and result
            res_fin[drug] = fin

        # Clean up temporary files
        for drug in name_drug[dr_type]:
            file_res = "D:\\Dir\\" + id_uniq + "_" + drug + ".csv"
            file_res2 = "D:\\Dir\\" + id_uniq + "_" + drug + "_predicted.csv"
            if os.path.exists(file_res2):
                os.remove(file_res2)
            if os.path.exists(file_res):
                os.remove(file_res)

# Output final results as JSON
print(json.dumps(res_fin))