"""
Tutorial 2: Phase analysis with tree search
Dara is equipped with a parallelized tree search algorithm to identify possible phases
present in a given XRD pattern.

In this tutorial, we will try to identify the phases in one experimental solid-state
reaction sample between `GeO2` and `ZnO`.
"""

from pathlib import Path

from dara import search_phases
from dara.cif import Cif
from dara.structure_db import CODDatabase

# Step 1: Prepare reference phases
# Dara pre-builds an index of all the unique and low-energy phases in ICSD and COD
# databases. It also implements a method to download CIF structures from COD data server
# so that there is no need to obtain the offline database.
#
# Before every search, we will need to gather all the reference phases in the chemical
# system for the search algorithm. Dara provides `ICSDDatabase` and `CODDatabase` to do
# the filtering.
#
# In this example, we will use `CODDatabase` to download all the phases in the chemical system of `Li-Ni-O`.

pattern_path = "./data/LNO-6_2025-1014_2.rasx"
chemical_system = "Li-Ni-O"

# The COD database contains methods to filter phases in the chemical system
cod_database = CODDatabase()

# Use a directory name based on the chemical system to avoid mixing phases from different systems
cifs_dir = f"cifs_{chemical_system.replace('-', '_')}"

# gather reference phases and save them to a directory
all_icsd_ids = cod_database.get_cifs_by_chemsys(chemical_system, dest_dir=cifs_dir)

# Since we are using a pre-filterd database (i.e., the COD), the downloaded CIF files will automatically be named according to the
# following convention:
#
# ```
# {composition}_{spacegroup}_(cod|icsd_{id})-{e_hull}.cif
# ```
# Where the `e_hull` is the energy above the convex hull in meV/atom, as determined from
# the Materials Project database for the ground-state entry with matching composition and spacegroup.

# Step 2: Search for phases
# After preparing the reference CIFs, we can start the phase search on a provided XRD pattern.

# gather all the phases in the cifs directory
all_cifs = list(Path(cifs_dir).glob("*.cif"))

search_results = search_phases(
    pattern_path=pattern_path,
    phases=all_cifs,
    wavelength="Co",
    instrument_profile="Aeris-fds-Pixcel1d-Medipix3",
)

# Step 3: Result analysis
# The returned search result will be a list of `SearchResult` object.

# Display search results
print(search_results)

# In this pattern, we only have one solution found with `Rwp = 12.04 %`.
for i in range(len(search_results)):
    print(f"Rwp of solution {i} = {search_results[i].refinement_result.lst_data.rwp} %")

# Each `SearchResult` has a `.visualize()` method to visualize the refined pattern and
# missing/extra peaks in the solution. If there are no missing or extra peaks, this option
# will not appear.
# Get the figure and save it
fig = search_results[0].visualize()

# Save as HTML (interactive, works without additional dependencies)
fig.write_html("phase_search_result.html")
print("Saved interactive figure to phase_search_result.html")

# Optionally save as PNG (requires kaleido: pip install kaleido)
# fig.write_image("phase_search_result.png", width=1200, height=800, scale=2)
# print("Saved figure to phase_search_result.png")

# You can also view all the alternative phases in one solution from `SearchResult.phases` attribute.
print("Phases found in solution 0:")
for i, phases_ in enumerate(search_results[0].phases):
    print(f"    - Phase {i}: {[phase.path.name for phase in phases_]}")

# Step 4: Export refined structures
# The refined structures can be extracted and saved as CIF files
best_result = search_results[0].refinement_result
output_dir = Path("refined_structures")
output_dir.mkdir(exist_ok=True)

print("\nExporting refined structures:")
for phase_name in best_result.lst_data.phases_results.keys():
    try:
        # Get the refined structure
        refined_structure = best_result.export_structure(phase_name)

        # Convert to CIF and save
        refined_cif = Cif.from_structure(refined_structure, filename=phase_name)
        output_path = output_dir / f"{phase_name}_refined.cif"
        refined_cif.to_file(output_path)

        # Get phase info
        phase_info = best_result.lst_data.phases_results[phase_name]
        print(f"  Saved: {output_path}")
        print(
            f"    - Weight fraction: {phase_info.gewicht[0]:.4f} ± {phase_info.gewicht[1]:.4f}"
        )
        print(f"    - R-phase: {phase_info.rphase:.2f}%")
        if phase_info.a:
            print(
                f"    - Lattice parameter a: {phase_info.a[0]:.6f} ± {phase_info.a[1]:.6f} nm"
            )
    except Exception as e:
        print(f"  Warning: Could not export {phase_name}: {e}")

print(f"\nAll refined structures saved to: {output_dir}/")
