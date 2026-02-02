import glob
import os
import re


def check_occupancy(folder_path):
    # Sort files for deterministic output
    cif_files = sorted(glob.glob(os.path.join(folder_path, "*.cif")))
    no_occupancy_files = []

    for cif_file in cif_files:
        with open(cif_file, "r") as f:
            content = f.read()

        # Remove comments
        content = re.sub(r"#.*", "", content)

        # Check for _atom_site_occupancy
        # We look for the tag. It might be followed by whitespace or newline.
        if "_atom_site_occupancy" not in content:
            no_occupancy_files.append(os.path.basename(cif_file))

    return no_occupancy_files


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(script_dir, "cifs_Li_Ni_O")

    if not os.path.exists(target_dir):
        print(f"Directory not found: {target_dir}")
    else:
        no_occ = check_occupancy(target_dir)
        if no_occ:
            print("CIF files with no occupancy:")
            for f in no_occ:
                print(f)
        else:
            print("All CIF files have occupancy data.")
