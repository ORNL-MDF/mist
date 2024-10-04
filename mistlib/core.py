import json
import pandoc
import os
from enum import Enum


class ValueTypes(Enum):
    SCALAR = 1
    LAURENT_POLYNOMIAL = 2
    TABLE = 3


class Property:
    def __init__(
        self,
        name,
        unit,
        value=None,
        value_laurent_poly=None,
        value_table=None,
        dependent_variable_print_name=None,
        dependent_variable_print_symbol=None,
        dependent_variable_unit=None,
        print_name=None,
        reference=None,
        uncertainty=None,
        print_symbol=None,
    ):

        self.name = name
        self.value = None
        self.value_laurent_poly = None
        self.value_table = None
        self.unit = unit
        self.reference = reference
        self.uncertainty = uncertainty
        self.print_symbol = print_symbol

        # Dependent variable information (for Laurent polynomial and table values)
        self.dependent_variable_print_name = dependent_variable_print_name
        self.dependent_variable_print_symbol = dependent_variable_print_symbol
        self.dependent_variable_unit = dependent_variable_unit

        if print_name == None:
            self.print_name = name
        else:
            self.print_name = print_name

        num_value_definitions = 0
        if value != None:
            self.value_type = ValueTypes.SCALAR
            self.value = value
            num_value_definitions = num_value_definitions + 1
        if value_laurent_poly != None:
            self.value_type = ValueTypes.LAURENT_POLYNOMIAL
            self.value_laurent_poly = value_laurent_poly
            num_value_definitions = num_value_definitions + 1
        if value_table != None:
            self.value_type = ValueTypes.TABLE
            self.value_table = value_table
            num_value_definitions = num_value_definitions + 1
            print("Tabular input values are not currently supported.")
            assert False

        # Check that only one type of value is defined
        assert num_value_definitions < 2

    def evaluate_laurent_polynomial(self, dependent_variable_value):
        sum = 0.0
        for term in self.value_laurent_poly:
            sum = sum + term[0] * dependent_variable_value ** term[1]
        return sum


class SinglePhase:
    def __init__(self, name, print_name=None):

        self.property_names = [
            "eutectic_contact_angle",
            "gibbs_thomson_coeff",
            "liquidus_slope",
            "solubility_limit",
            "solute_diffusivities",
            "solute_misfit_strains",
            "taylor_factor",
            "shear_modulus_base_element",
            "burgers_vector_base_element",
            "poisson_ratio_base_element",
        ]

        self.name = name
        self.print_name = print_name
        self.properties = {}


class MaterialInformation:
    def __init__(self, file=None):

        self.composition_names = ["base_element", "solute_elements"]

        self.thermophysical_property_names = [
            "density",
            "specific_heat_solid",
            "specific_heat_liquid",
            "thermal_conductivity_solid",
            "thermal_conductivity_liquid",
            "dynamic_viscosity",
            "thermal_expansion",
            "latent_heat_fusion",
            "latent_heat_vaporization",
            "emissivity",
            "molecular_mass",
            "liquidus_temperature",
            "log_vapor_pressure",
            "laser_absorption",
            "solidus_eutectic_temperature",
            "hall_petch_coefficient",
            "interface_response_function",
        ]

        self.composition = {}
        self.properties = {}
        self.phase_properties = {}

        if file == None:
            # Set all values to None
            self.name = None
            self.notes = None
            self.composition = None
            self.single_phase_properties = None

            for p in self.thermophysical_property_names:
                self.properties[p] = None

        else:
            # Call the load from file method
            self.load_json(file)

        return

    def load_json(self, file):
        # Load a JSON file
        # Do we want to check for entries that don't match expected entries?
        with open(file, "r") as f:
            data = json.load(f)
            self.name = data["name"]
            self.notes = data["note"]

            if "composition" in data.keys():
                self.composition["base_element"] = self.populate_optional_field(
                    data["composition"], "base_element"
                )
                self.composition["solute_elements"] = self.populate_optional_field(
                    data["composition"], "solute_elements"
                )

                if self.composition["base_element"] in data["composition"].keys():
                    self.composition[self.composition["base_element"]] = (
                        self.json_blob_to_property(
                            data["composition"], self.composition["base_element"]
                        )
                    )

                for solute_element in self.composition["solute_elements"]:
                    if solute_element in data["composition"].keys():
                        self.composition[solute_element] = self.json_blob_to_property(
                            data["composition"], solute_element
                        )

            if "single_phase_properties" in data.keys():
                self.phases = self.populate_optional_field(
                    data["single_phase_properties"], "phases"
                )
                for phase in self.phases:
                    phase_name = phase
                    phase_print_name = data["single_phase_properties"][phase][
                        "print_name"
                    ]
                    single_phase = SinglePhase(phase_name, phase_print_name)
                    for p in single_phase.property_names:
                        if p == "solute_diffusivities" or p == "solute_misfit_strains":
                            # These have an extra level compared to all of the other properties and so it needs to be handled separately
                            if p in data["single_phase_properties"][phase].keys():
                                temp_dict = {}
                                for element in self.composition["solute_elements"]:
                                    temp_val = None
                                    if (
                                        element
                                        in data["single_phase_properties"][phase][
                                            p
                                        ].keys()
                                    ):
                                        temp_val = self.json_blob_to_property(
                                            data["single_phase_properties"][phase][p],
                                            element,
                                        )
                                    temp_dict[element] = temp_val
                                single_phase.properties[p] = temp_dict

                        else:
                            if p in data["single_phase_properties"][phase].keys():
                                single_phase.properties[p] = self.json_blob_to_property(
                                    data["single_phase_properties"][phase], p
                                )

                    self.phase_properties[phase] = single_phase

            if "thermophysical_properties" in data.keys():
                for p in self.thermophysical_property_names:
                    if p in data["thermophysical_properties"].keys():
                        self.properties[p] = self.json_blob_to_property(
                            data["thermophysical_properties"], p
                        )

        return

    def json_blob_to_property(self, json_blob, property_string):
        tree = json_blob[property_string]
        # Mandatory fields
        name = property_string

        # Optional fields
        unit = self.populate_optional_field(tree, "unit")
        value = self.populate_optional_field(tree, "value")
        value_laurent_poly = self.populate_optional_field(tree, "value_laurent_poly")
        value_table = self.populate_optional_field(tree, "value_table")
        dependent_variable_print_name = self.populate_optional_field(
            tree, "dependent_variable_print_name"
        )
        dependent_variable_print_symbol = self.populate_optional_field(
            tree, "dependent_variable_print_symbol"
        )
        dependent_variable_unit = self.populate_optional_field(
            tree, "dependent_variable_unit"
        )
        print_name = self.populate_optional_field(tree, "print_name")
        reference = self.populate_optional_field(tree, "reference")
        uncertainty = self.populate_optional_field(tree, "uncertainty")
        print_symbol = self.populate_optional_field(tree, "print_symbol")

        property = Property(
            name,
            unit,
            value,
            value_laurent_poly,
            value_table,
            dependent_variable_print_name,
            dependent_variable_print_symbol,
            dependent_variable_unit,
            print_name,
            reference,
            uncertainty,
            print_symbol,
        )

        return property

    def populate_optional_field(self, json_blob, field_key):
        val = None
        if field_key in json_blob:
            val = json_blob[field_key]
            if val == "None":
                val = None

        return val

    def latex_laurent_poly(self, value_laurent_poly, dependent_variable_print_symbol):
        latex_str = ""
        for term in value_laurent_poly:
            if term[1] == 0:
                latex_str = latex_str + str(term[0]) + " + "
            elif term[1] == 1:
                latex_str = (
                    latex_str
                    + str(term[0])
                    + " $"
                    + dependent_variable_print_symbol
                    + "$ + "
                )
            else:
                latex_str = (
                    latex_str
                    + str(term[0])
                    + " $"
                    + dependent_variable_print_symbol
                    + "^{"
                    + str(term[1])
                    + "}$ + "
                )

        latex_str = latex_str.rstrip("+ ")

        return latex_str

    def write_json(self, file):
        # Write a JSON file with the current material information
        # TODO
        return

    def write_markdown(self, file, tables=["properties"]):
        # TODO: Add support for the other types of properties

        # Write a Markdown file with the current material information
        with open(file, "w") as f:
            reference_list = []
            num_refs = 0

            f.write("# Material Properties: " + self.name + "\n\n")

            if "composition" in tables:
                f.write("## Composition \n")

                f.write("|Element | Concentration | Units | Data Source | \n")
                f.write("|---------| ----- | ----- | ----------- | \n")

                elements = [self.composition["base_element"]]
                elements.extend(self.composition["solute_elements"])
                for element in elements:
                    print_name_str = element
                    value_str = str(self.composition[element].value)
                    unit_str = self.composition[element].unit

                    next_ref = self.composition[element].reference
                    ref_index = None

                    if next_ref != None:
                        ref_index = -1
                        for idx, ref in enumerate(reference_list):
                            if next_ref == ref:
                                ref_index = idx
                                break

                        if ref_index == -1:
                            ref_index = len(reference_list)
                            reference_list.append(next_ref)

                    ref_str = None
                    if ref_index == None:
                        ref_str = "-"
                    else:
                        ref_str = "[" + str(ref_index + 1) + "]"

                    f.write(
                        "| "
                        + print_name_str
                        + " | "
                        + value_str
                        + " | $"
                        + unit_str
                        + "$ | "
                        + ref_str
                        + " |"
                        + "\n"
                    )

            if "properties" in tables:

                f.write("## Thermophysical Properties \n")

                f.write("|Property | Value | Units | Data Source | \n")
                f.write("|---------| ----- | ----- | ----------- | \n")

                for p in self.thermophysical_property_names:
                    if p in self.properties.keys():
                        next_ref = self.properties[p].reference
                        ref_index = None

                        if next_ref != None:
                            ref_index = -1
                            for idx, ref in enumerate(reference_list):
                                if next_ref == ref:
                                    ref_index = idx
                                    break

                            if ref_index == -1:
                                ref_index = len(reference_list)
                                reference_list.append(next_ref)

                        print_name_str = self.properties[p].print_name

                        value_str = None
                        if self.properties[p].value_type == ValueTypes.SCALAR:
                            value_str = self.replace_none_with_string(
                                self.properties[p].value, "-"
                            )
                        elif (
                            self.properties[p].value_type
                            == ValueTypes.LAURENT_POLYNOMIAL
                        ):
                            value_str = self.latex_laurent_poly(
                                self.properties[p].value_laurent_poly,
                                self.properties[p].dependent_variable_print_symbol,
                            )
                        elif (
                            self.properties[p].value_type
                            == ValueTypes.LAURENT_POLYNOMIAL
                        ):
                            value_str = self.replace_none_with_string(
                                self.properties[p].value_table, "-"
                            )
                        else:
                            value_str = "-"

                        unit_str = self.replace_none_with_string(
                            self.properties[p].unit, "-"
                        )

                        ref_str = None
                        if ref_index == None:
                            ref_str = "-"
                        else:
                            ref_str = "[" + str(ref_index + 1) + "]"

                        f.write(
                            "| "
                            + print_name_str
                            + " | "
                            + value_str
                            + " | $"
                            + unit_str
                            + "$ | "
                            + ref_str
                            + " |"
                            + "\n"
                        )
            f.write("\n")
            if self.notes is not None:
                f.write("## Notes \n")
                f.write(self.notes + "\n")
                f.write("\n")
            f.write("## References \n")
            for idx, ref in enumerate(reference_list):
                ref_str = self.replace_none_with_string(ref, "-")
                f.write("[" + str(idx + 1) + "] " + ref_str + "\n")
                f.write("\n")

        return

    def write_pdf(self, file):
        # Write a PDF file with the current material information
        temp_md_file = "temp.md"
        self.write_markdown(temp_md_file)
        doc = pandoc.read(file=temp_md_file)
        pandoc.write(
            doc, file=file, format="pdf", options=["-V", "geometry:margin=1in"]
        )
        os.remove(temp_md_file)

        return

    def write_adamantine_input(self, file):
        reference_temperature = self.properties[
            "solidus_eutectic_temperature"
        ].value  # For adamantine we assume that all temperature-dependent material properties are evaluated at the solidus temperature
        code_name = "adamantine"

        specific_heat_1 = self.get_property(
            "specific_heat_solid", code_name, reference_temperature
        )
        specific_heat_2 = self.get_property(
            "specific_heat_liquid", code_name, reference_temperature
        )
        thermal_conductivity_1 = self.get_property(
            "thermal_conductivity_solid", code_name, reference_temperature
        )
        density = self.get_property("density", code_name, reference_temperature)
        thermal_conductivity_2 = self.get_property(
            "thermal_conductivity_liquid", code_name, reference_temperature
        )
        emissivity = self.get_property("emissivity", code_name, reference_temperature)

        content = (
            f"materials\n{{"
            f"\n\tn_material 1"
            f"\n\tproperty_format polynomial"
            f"\n\tmaterial_0"
            f"\n\t{{"
            f"\n\t\tsolid"
            f"\n\t\t{{"
            f"\n\t\t\tdensity {density} ;"
            f"\n\t\t\tspecific_heat {specific_heat_1} ;"
            f"\n\t\t\tthermal_conductivity_x {thermal_conductivity_1} ;"
            f"\n\t\t\tthermal_conductivity_z {thermal_conductivity_1} ;"
            f"\n\t\t\temissivity {emissivity} ;"
            f"\n\t\t}}"
            f"\n\t\tliquid"
            f"\n\t\t{{"
            f"\n\t\t\tdensity {density} ;"
            f"\n\t\t\tspecific_heat {specific_heat_2} ;"
            f"\n\t\t\tthermal_conductivity_x {thermal_conductivity_2} ;"
            f"\n\t\t\tthermal_conductivity_z {thermal_conductivity_2} ;"
            f"\n\t\t\temissivity {emissivity} ;"
            f"\n\t\t}}"
            f"\n\tsolidus {self.properties['solidus_eutectic_temperature'].value} ;"
            f"\n\tliquidus {self.properties['liquidus_temperature'].value} ;"
            f"\n\tlatent heat {self.properties['latent_heat_fusion'].value} ;"
            f"\n\t}}"
            f"\n}}"
        )
        with open(file, "w") as f:
            f.write(content)

    def append_file(input_filename, output_filename):
        # Get current directory of the script
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Form paths
        input_file_path = os.path.join(current_dir, input_filename)
        output_file_path = os.path.join(current_dir, output_filename)

        # Read the input file
        with open(input_file_path, "r") as input_file:
            input_content = input_file.read()

        # Append the content to the output file
        with open(output_file_path, "a") as output_file:
            output_file.write(input_content)

        return

    def write_additivefoam_transportProp(self, file="transportProperties"):
        code_name = "AdditiveFOAM"
        comment_block = """/*---------------------------------------------------------------------------
     AdditiveFOAM template input file (compatible with 1.0, OpenFOAM 10)

                      Created with Mist
  ---------------------------------------------------------------------------*/
  FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      transportProperties;
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

    """

        def get_coefficient_string(variable_name, property_name):
            p = self.properties[property_name]
            if p.value_type == ValueTypes.LAURENT_POLYNOMIAL:
                all_coeff = ""
                # Extract up to the third order coefficients for AdditiveFOAM
                for term in p.value_laurent_poly:
                    if len(all_coeff.split("\t")) < 4:
                        all_coeff += f"{term[0]}\t"
                # Fill any missing coefficients
                if len(p.value_laurent_poly) < 3:
                    while len(all_coeff.split("\t")) < 4:
                        all_coeff += "0.0\t"
                return f"\t{variable_name}\t({all_coeff.strip()});\n"
            else:
                print(f"Warning: converting scalar into polynomial.")
                return f"\t{variable_name}\t({p.value}\t0.0\t0.0);\n"

        content = comment_block

        content += "solid\n{\n"
        content += get_coefficient_string("kappa", "thermal_conductivity_solid")
        content += get_coefficient_string("Cp", "specific_heat_solid")

        content += "}\n\nliquid\n{\n"
        content += get_coefficient_string("kappa", "thermal_conductivity_liquid")
        content += get_coefficient_string("Cp", "specific_heat_liquid")

        content += "}\n\npowder\n{\n"
        content += get_coefficient_string("kappa", "thermal_conductivity_solid")
        content += get_coefficient_string("Cp", "specific_heat_solid")
        content += "}\n\n"

        reference_temperature = self.properties["solidus_eutectic_temperature"].value
        density = self.get_property("density", code_name, reference_temperature)
        latent_heat_fusion = self.get_property(
            "latent_heat_fusion", code_name, reference_temperature
        )
        dynamic_viscosity = self.get_property(
            "dynamic_viscosity", code_name, reference_temperature
        )
        thermal_expansion = self.get_property(
            "thermal_expansion", code_name, reference_temperature
        )
        content += f"rho     [1 -3 0 0 0 0 0]    {density};\n"
        content += f"mu      [1 -1 -1  0 0 0 0]  {dynamic_viscosity};\n"
        content += f"beta    [0 0 0 -1 0 0 0]    {thermal_expansion};\n"
        content += f"DAS     [0 1 0 0 0 0 0]     10e-6;\n"
        content += f"Lf      [0  2 -2  0 0 0 0]  {latent_heat_fusion:.2e};\n\n"
        content += f"// ************************************************************************* //"

        with open(file, "w") as f:
            f.write(content)
        return file

    def write_additivefoam_thermoPath(self, file="thermoPath"):
        with open(file, "w") as g:
            eutectic_temp = self.properties["solidus_eutectic_temperature"].value
            liquidus_temp = self.properties["liquidus_temperature"].value
            g.write(
                f"(\n{eutectic_temp:.4f}\t 1.0000 \n{liquidus_temp:.4f}\t 0.0000\n)"
            )
        return file

    def write_additivefoam_input(
        self, transport_file="transportProperties", thermo_file="thermoPath"
    ):
        self.write_additivefoam_transportProp(file=transport_file)
        self.write_additivefoam_thermoPath(file=thermo_file)
        return [transport_file, thermo_file]

    def write_exaca_input(self, file="exaca_material_file.json"):
        data = {}
        eutectic_temp = self.properties["solidus_eutectic_temperature"].value
        liquidus_temp = self.properties["liquidus_temperature"].value
        data["freezing_range"] = liquidus_temp - eutectic_temp
        # Get interface response function as a Laurent polynomial
        irf = self.properties["interface_response_function"].value_laurent_poly
        irf_dict = {}
        for value, order in irf:
            irf_dict[order] = value
        if len(irf) == 4:
            data["function"] = "cubic"
            data["coefficients"] = {
                "A": irf_dict[3],
                "B": irf_dict[2],
                "C": irf_dict[1],
                "D": irf_dict[0],
            }
        elif len(irf) == 3:
            data["function"] = "quadratic"
            data["coefficients"] = {
                "A": irf_dict[2],
                "B": irf_dict[1],
                "C": irf_dict[0],
            }
        else:
            print(
                f"interface_response_function must be polynomial of 3rd order or less for ExaCA input file"
            )
            raise ValueError
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return file

    def write_3dthesis_input(self, file, initial_temperature=None):
        # 3DThesis/autothesis/Condor assumes at "T_0" initial temperature value. Myna populates this from Peregrine. For now we add a placeholder of -1 unless the user specifies an initial temperature.
        if initial_temperature == None:
            initial_temperature = -1

        code_name = "autothesis"
        # For autothesis we assume that all temperature-dependent material properties are evaluated at the solidus temperature
        reference_temperature = self.properties["solidus_eutectic_temperature"].value
        thermal_conductivity = self.get_property(
            "thermal_conductivity_solid", code_name, reference_temperature
        )
        density = self.get_property("density", code_name, reference_temperature)
        specific_heat = self.get_property(
            "specific_heat_solid", code_name, reference_temperature
        )

        content_to_write = (
            "Constants\n"
            "{\n"
            f"\t T_0\t{initial_temperature}\n"
            f"\t T_L\t{self.properties['liquidus_temperature'].value}\n"
            f"\t k\t{thermal_conductivity}\n"
            f"\t c\t{specific_heat}\n"
            f"\t p\t{density}\n"
            "}"
        )
        with open(file, "w") as f:
            f.write(content_to_write)

    def get_property(self, property_name, code_name, reference_temperature):
        prop = None
        p = self.properties[property_name]
        if p.value_type == ValueTypes.SCALAR:
            prop = p.value
        elif p.value_type == ValueTypes.LAURENT_POLYNOMIAL:
            prop = p.evaluate_laurent_polynomial(reference_temperature)
        else:
            print(
                f"Error: {code_name} requires either SCALAR or LAURENT_POLYNOMIAL ValueTypes for {property_name}."
            )
        return prop

    def replace_none_with_string(self, entry, replace_string):
        if entry == None:
            return replace_string
        else:
            return str(entry)

    def validate_completeness(self):
        # Check if the information is complete by a user-specified standard
        # TODO
        return
