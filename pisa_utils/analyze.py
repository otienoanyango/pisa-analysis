import json
import logging
import os
from datetime import datetime

from pisa_utils.dictionaries import get_assembly_dict, get_bond_dict, get_molecules_dict
from pisa_utils.utils import parse_xml_file

logger = logging.getLogger()


class AnalysePisa:
    """
    This class is responsible for parsing XML files generated by pisa, and
    converting their content to JSON format. It also add UniProt numbering
    using updated mmCIF file
    """

    def __init__(
        self,
        pdb_id,
        assembly_id,
        input_cif,
        input_updated_cif,
        output_json,
        output_xml,
    ):
        self.pdb_id = pdb_id
        self.assembly_code = assembly_id
        self.input_updated_cif = input_updated_cif if input_updated_cif else input_cif
        self.output_json = output_json if output_json else None
        self.output_xml = output_xml
        self.results = {}
        self.interfaces_results = None

    def create_assem_interfaces_dict(self):
        """
        Function writes assembly interfaces dictionaries

        :return: type dict - assembly interfaces dictionary
        """

        start = datetime.now()
        logging.info("creating assembly dictionary")
        print("creating assembly dictionary")

        interfaces_xml_file = os.path.join(self.output_xml, "interfaces.xml")
        assembly_xml_file = os.path.join(self.output_xml, "assembly.xml")
        result = {}
        interfaces_results = {}

        if os.path.exists(interfaces_xml_file) and os.path.exists(assembly_xml_file):
            asroot = parse_xml_file(xml_file=assembly_xml_file)
            root = parse_xml_file(xml_file=interfaces_xml_file)

            if root and asroot:

                try:
                    assembly_status = asroot.find("status").text
                    assemblies = asroot.iter("asu_complex")

                    assem_result = get_assembly_dict(assemblies)

                except Exception as e:
                    logging.error(
                        "invalid assembly dictionary : probably fields not found in xml file"
                    )
                    logging.error(e)

                # Create interfaces dictionaries

                status = root.find("status").text
                num_interfaces = root.find("n_interfaces").text
                # interfaces = root.findall("interface")

                # logging.debug("number of interfaces: {}".format(len(interfaces)))

                result["status"] = status
                result["num_interfaces"] = num_interfaces

                non_ligand_interface_count = 0

                interfaces = root.iter("interface")

                for interface in interfaces:

                    # Interface General information
                    interface_id = interface.find("id").text
                    interface_area = round(float(interface.find("int_area").text), 2)
                    interface_solvation_energy = round(
                        float(interface.find("int_solv_en").text), 2
                    )
                    interface_stabilization_energy = round(
                        float(interface.find("stab_en").text), 2
                    )
                    p_value = round(float(interface.find("pvalue").text), 3)

                    # No. of bonds counted

                    n_h_bonds = int(interface.find("h-bonds/n_bonds").text)
                    n_ss_bonds = int(interface.find("ss-bonds/n_bonds").text)
                    n_covalent_bonds = int(interface.find("cov-bonds/n_bonds").text)
                    n_salt_bridges = int(interface.find("salt-bridges/n_bonds").text)
                    other_contacts = int(interface.find("other-bonds/n_bonds").text)

                    molecules = interface.iter("molecule")
                    (
                        molecules_dicts,
                        interface_residues_count,
                        is_ligand,
                    ) = get_molecules_dict(molecules)

                    if not is_ligand:
                        non_ligand_interface_count += 1

                        # Reading bonds

                        hbonds = interface.find("h-bonds")
                        sbridges = interface.find("salt-bridges")
                        covbonds = interface.find("cov-bonds")
                        ssbonds = interface.find("ss-bonds")
                        othbonds = interface.find("other-bonds")

                        # Writing bonds dictionaries

                        # for hbond in hbonds:
                        hbond_dict = get_bond_dict(
                            hbonds, "H-bond", self.pdb_id, self.input_updated_cif
                        )

                        # for sbridge in sbridges:
                        sbridge_dict = get_bond_dict(
                            sbridges,
                            "salt-bridges",
                            self.pdb_id,
                            self.input_updated_cif,
                        )
                        # for covbond in covbonds:
                        covbond_dict = get_bond_dict(
                            covbonds,
                            "cov-bonds",
                            self.pdb_id,
                            self.input_updated_cif,
                        )
                        # for ssbond in ssbonds:
                        ssbond_dict = get_bond_dict(
                            ssbonds, "ss-bonds", self.pdb_id, self.input_updated_cif
                        )
                        # for othbond in othbonds:
                        othbond_dict = get_bond_dict(
                            othbonds,
                            "other-bond",
                            self.pdb_id,
                            self.input_updated_cif,
                        )

                        interface_dict = {
                            "interface_id": interface_id,
                            "interface_area": interface_area,
                            "solvation_energy": interface_solvation_energy,
                            "stabilization_energy": interface_stabilization_energy,
                            "p_value": p_value,
                            "number_interface_residues": interface_residues_count,
                            "number_hydrogen_bonds": n_h_bonds,
                            "number_covalent_bonds": n_covalent_bonds,
                            "number_disulfide_bonds": n_ss_bonds,
                            "number_salt_bridges": n_salt_bridges,
                            "number_other_bonds": other_contacts,
                            "hydrogen_bonds": hbond_dict,
                            "salt_bridges": sbridge_dict,
                            "disulfide_bonds": ssbond_dict,
                            "covalent_bonds": covbond_dict,
                            "other_bonds": othbond_dict,
                            "molecules": molecules_dicts,
                        }

                        # Append all dictionaries in 'result'

                        result.setdefault("id", []).append(interface_id)
                        result.setdefault("int_area", []).append(interface_area)
                        result.setdefault("interface_dicts", []).append(interface_dict)

                result["non_ligand_interface_count"] = non_ligand_interface_count

        if result and assem_result:

            overall = len(result.get("id", []))
            interface_dicts = result.get("interface_dicts", [])
            assem_dict = {
                "mmsize": assem_result.get("assembly_mmsize"),
                "dissociation_energy": assem_result.get("assembly_diss_energy"),
                "accessible_surface_area": assem_result.get("assembly_asa"),
                "buried_surface_area": assem_result.get("assembly_bsa"),
                "entropy": assem_result.get("assembly_entropy"),
                "dissociation_area": assem_result.get("assembly_diss_area"),
                "solvation_energy_gain": assem_result.get("assembly_int_energy"),
                "formula": assem_result.get("assembly_formula"),
                "composition": assem_result.get("assembly_composition"),
                "interface_count": overall,
                "interfaces": interface_dicts,
            }

            assembly_dictionary = {
                "pdb_id": self.pdb_id,
                "assembly_id": self.assembly_code,
                "pisa_version": "2.0",
                "assembly": assem_dict,
            }

            self.results.setdefault("PISA", assembly_dictionary)
            # print(self.results)

            interfaces_results = self.results

        end = datetime.now()
        logging.info("finished creating assembly dictionary")

        time_taken = end - start
        time_taken_str = str(time_taken)
        logging.info(
            "time taken to create assembly dictionary {}".format(time_taken_str)
        )
        print("Finished creating assembly dictionary in {}".format(time_taken_str))

        # dump to json file
        output_json = os.path.join(
            self.output_json,
            "{}-assembly{}-interfaces.json".format(self.pdb_id, self.assembly_code),
        )

        self.save_to_json(interfaces_results, output_json)

        return interfaces_results

    def create_assembly_dict(self):

        """Function writes simplified assembly dictionary

        :return: type dict - assembly dictionary
        """
        result = {}
        start = datetime.now()
        logging.info("creating simplified assembly dictionary")
        print("creating simplified assembly dictionary")

        assembly_xml_file = os.path.join(self.output_xml, "assembly.xml")
        result = {}

        if os.path.exists(assembly_xml_file):
            asroot = parse_xml_file(xml_file=assembly_xml_file)

        if asroot:

            try:
                assembly_status = asroot.find("status").text
                assemblies = asroot.iter("asu_complex")

                assem_result = get_assembly_dict(assemblies)

            except Exception as e:
                logging.error(
                    "invalid assembly dictionary : probably fields not found in xml file"
                )
                logging.error(e)

            assem_dict = {
                "id": assem_result.get("assembly_id"),
                "size": assem_result.get("assembly_size"),
                "macromolecular_size": assem_result.get("assembly_mmsize"),
                "dissociation_energy": assem_result.get("assembly_diss_energy"),
                "accessible_surface_area": assem_result.get("assembly_asa"),
                "buried_surface_area": assem_result.get("assembly_bsa"),
                "entropy": assem_result.get("assembly_entropy"),
                "dissociation_area": assem_result.get("assembly_diss_area"),
                "solvation_energy_gain": assem_result.get("assembly_int_energy"),
                "number_of_uc": assem_result.get("assembly_n_uc"),
                "number_of_dissociated_elements": assem_result.get("assembly_n_diss"),
                "symmetry_number": assem_result.get("assembly_sym_num"),
                "formula": assem_result.get("assembly_formula"),
                "composition": assem_result.get("assembly_composition"),
            }

            assembly_dictionary = {
                "pdb_id": self.pdb_id,
                "assembly_id": self.assembly_code,
                "pisa_version": "2.0",
                "assembly": assem_dict,
            }

            result.setdefault("PISA", assembly_dictionary)

        end = datetime.now()
        logging.info("finished creating assembly dictionary")

        time_taken = end - start
        time_taken_str = str(time_taken)
        logging.info(
            "time taken to create simplified assembly dictionary {}".format(
                time_taken_str
            )
        )
        print(
            "Finished creating assembly simplified dictionary in {}".format(
                time_taken_str
            )
        )

        output_json = os.path.join(
            self.output_json,
            "{}-assembly{}.json".format(self.pdb_id, self.assembly_code),
        )

        self.save_to_json(result, output_json)

        return result

    def save_to_json(self, result, output_file):
        """
        Dump the data into a JSON file
        :return:
        """

        if result:
            with open(output_file, "w") as out_file:
                json.dump(result, out_file)
                logging.info("saving to JSON successful")

        else:
            logging.warning("saving to JSON failed")
