from dara.cif import Cif
from dara.structure_db import CODDatabase


def structures_from_chemsys(chemsys: str, max_ids: int = 10):
    db = CODDatabase()
    cod_ids = db.get_cifs_by_chemsys(chemsys, copy_files=False)

    # Option A: local COD copy present
    if db.local_copy_found:
        structs = []
        for cod_id in cod_ids[:max_ids]:
            cif_path = db.get_file_path(cod_id)
            cif = Cif.from_file(cif_path)
            structs.append(cif.to_structure())
        return structs

    # Option B: no local copy; download CIFs directly
    cifs = db.download_structures(cod_ids[:max_ids], save=False)
    return [cif.to_structure() for cif in cifs]


def structures_from_formula(formula: str, max_ids: int = 10):
    db = CODDatabase()
    cod_ids = db.get_cifs_by_formulas([formula], copy_files=False)

    if db.local_copy_found:
        return [
            Cif.from_file(db.get_file_path(cod_id)).to_structure()
            for cod_id in cod_ids[:max_ids]
        ]

    cifs = db.download_structures(cod_ids[:max_ids], save=False)
    return [cif.to_structure() for cif in cifs]


# Examples
fe_o_structures = structures_from_chemsys("Fe-O")
# fe2o3_structures = structures_from_formula("Fe2O3")
