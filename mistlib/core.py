import json
import pandoc
import os
from enum import Enum

class ValueTypes(Enum):
    SCALAR = 1
    LAURENT_POLYNOMIAL = 2
    TABLE = 3

class Property:
    def __init__(self, name, unit, value = None, value_laurent_poly = None, value_table = None, dependent_variable_print_name = None, dependent_variable_print_symbol = None, dependent_variable_unit = None, print_name = None, reference = None, uncertainty = None, print_symbol = None):

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
        if (value != None):
            self.value_type = ValueTypes.SCALAR
            self.value = value
            num_value_definitions = num_value_definitions + 1
        if (value_laurent_poly != None):
            self.value_type = ValueTypes.LAURENT_POLYNOMIAL
            self.value_laurent_poly = value_laurent_poly
            num_value_definitions = num_value_definitions + 1
        if (value_table != None):
            self.value_type = ValueTypes.TABLE
            self.value_table = value_table
            num_value_definitions = num_value_definitions + 1
            print("Tabular input values are not currently supported.")
            assert(False)

        # Check that only one type of value is defined
        assert(num_value_definitions < 2)

    def evaluate_laurent_polynomial(self, dependent_variable_value):
        sum = 0.0
        for term in self.value_laurent_poly:
            sum = sum + term[0] * dependent_variable_value**term[1]
        return sum

class SinglePhase:
    def __init__(self, name, print_name = None):

        self.property_names = ['eutectic_contact_angle', 'gibbs_thomson_coeff', 'liquidus_slope','solubility_limit', 'solute_diffusivities', 'solute_misfit_strains', 'taylor_factor', 'shear_modulus_base_element', 'burgers_vector_base_element', 'poisson_ratio_base_element']

        self.name = name
        self.print_name = print_name
        self.properties = {}       

class MaterialInformation:
    def __init__(self, file=None):

        self.composition_names = ['base_element', 'solute_elements']
        
        self.thermophysical_property_names = ['density', 'specific_heat_solid', 'specific_heat_liquid', 'thermal_conductivity_solid', 'thermal_conductivity_liquid', 'dynamic_viscosity', 'thermal_expansion', 'latent_heat_fusion', 'latent_heat_vaporization', 'emissivity', 'molecular_mass',  'liquidus_temperature', 'log_vapor_pressure', 'laser_absorption', 'solidus_eutectic_temperature', 'hall_petch_coefficient']

        self.composition = {}
        self.properties = {}
        self.phase_properties = {}

        if (file == None):
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
        with open(file, 'r') as f:
            data = json.load(f)
            self.name = data['name']
            self.notes = data['note']

            if ("composition" in data.keys()):
                self.composition['base_element'] = self.populate_optional_field(data["composition"], 'base_element')
                self.composition['solute_elements'] = self.populate_optional_field(data["composition"], 'solute_elements')
              
                if (self.composition['base_element'] in data["composition"].keys()):
                    self.composition[self.composition['base_element']] = self.json_blob_to_property(data["composition"], self.composition['base_element'])
                
                for solute_element in self.composition['solute_elements']:
                    if (solute_element in data["composition"].keys()):
                        self.composition[solute_element] = self.json_blob_to_property(data["composition"], solute_element)

            if ("single_phase_properties" in data.keys()):
                self.phases = self.populate_optional_field(data["single_phase_properties"], 'phases')
                for phase in self.phases:
                    phase_name = phase
                    phase_print_name = data["single_phase_properties"][phase]['print_name']
                    single_phase = SinglePhase(phase_name, phase_print_name)
                    for p in single_phase.property_names:
                        if (p == "solute_diffusivities" or p == "solute_misfit_strains"):
                            # These have an extra level compared to all of the other properties and so it needs to be handled seperately
                            if (p in data["single_phase_properties"][phase].keys()):
                                temp_dict = {}
                                for element in self.composition['solute_elements']:
                                    temp_val = None
                                    if (element in data["single_phase_properties"][phase][p].keys()):
                                        temp_val = self.json_blob_to_property(data["single_phase_properties"][phase][p], element)
                                    temp_dict[element] = temp_val
                                single_phase.properties[p] = temp_dict   
                                    
                        else:
                            if (p in data["single_phase_properties"][phase].keys()):
                                single_phase.properties[p] = self.json_blob_to_property(data["single_phase_properties"][phase], p)

                    self.phase_properties[phase] = single_phase

            if ("thermophysical_properties" in data.keys()):
                for p in self.thermophysical_property_names:
                    if (p in data["thermophysical_properties"].keys()):
                        self.properties[p] = self.json_blob_to_property(data["thermophysical_properties"], p)
            
        return
    
    def json_blob_to_property(self, json_blob, property_string):
        tree = json_blob[property_string]
        # Mandatory fields
        name = property_string

        # Optional fields
        unit = self.populate_optional_field(tree, 'unit')
        value = self.populate_optional_field(tree, 'value')
        value_laurent_poly = self.populate_optional_field(tree, 'value_laurent_poly')
        value_table = self.populate_optional_field(tree, 'value_table')
        dependent_variable_print_name = self.populate_optional_field(tree, 'dependent_variable_print_name')
        dependent_variable_print_symbol = self.populate_optional_field(tree, 'dependent_variable_print_symbol')
        dependent_variable_unit = self.populate_optional_field(tree, 'dependent_variable_unit')
        print_name = self.populate_optional_field(tree, 'print_name')
        reference = self.populate_optional_field(tree, 'reference')
        uncertainty = self.populate_optional_field(tree, 'uncertainty')
        print_symbol = self.populate_optional_field(tree, 'print_symbol')

        property = Property(name, unit, value, value_laurent_poly, value_table, dependent_variable_print_name, dependent_variable_print_symbol, dependent_variable_unit, print_name, reference, uncertainty, print_symbol)

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
            if (term[1] == 0):
                latex_str = latex_str + str(term[0]) + " + "
            elif (term[1] == 1):
                latex_str = latex_str + str(term[0]) + " $" + dependent_variable_print_symbol + "$ + "
            else:
                latex_str = latex_str + str(term[0]) + " $" + dependent_variable_print_symbol + "^{" + str(term[1]) + "}$ + "
        
        latex_str = latex_str.rstrip("+ ")

        return latex_str

    def write_json(self, file):
        # Write a JSON file with the current material information
        # TODO
        return

    def write_markdown(self, file, tables=['properties']):
        # TODO: Add support for the other types of properties
        
        # Write a Markdown file with the current material information
        with open(file, 'w') as f:
            reference_list = []
            num_refs = 0

            f.write("# Material Properties: " + self.name + '\n\n')

            if ('composition' in tables):
                f.write("## Composition \n")

                f.write("|Element | Concentration | Units | Data Source | \n")
                f.write("|---------| ----- | ----- | ----------- | \n")
                
                elements = [self.composition['base_element']]
                elements.extend(self.composition['solute_elements'])
                for element in elements:
                    print_name_str = element
                    value_str = str(self.composition[element].value)
                    unit_str = self.composition[element].unit

                    next_ref = self.composition[element].reference
                    ref_index = None
                
                    if (next_ref != None):
                        ref_index = -1
                        for idx, ref in enumerate(reference_list):
                            if next_ref == ref:
                                ref_index = idx
                                break
                    
                        if ref_index == -1:
                            ref_index = len(reference_list)
                            reference_list.append(next_ref)

                    ref_str = None
                    if (ref_index == None):
                        ref_str = '-'
                    else:
                        ref_str = "[" + str(ref_index+1) + "]"

                    f.write("| " + print_name_str + " | " + value_str + " | $" + unit_str + "$ | " + ref_str + " |" + "\n")

            if ('properties' in tables):
                
                f.write("## Thermophysical Properties \n")

                f.write("|Property | Value | Units | Data Source | \n")
                f.write("|---------| ----- | ----- | ----------- | \n")

                for p in self.thermophysical_property_names:
                    if (p in self.properties.keys()):
                        next_ref = self.properties[p].reference
                        ref_index = None
                    
                        if (next_ref != None):
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
                        if (self.properties[p].value_type == ValueTypes.SCALAR):
                            value_str =  self.replace_none_with_string(self.properties[p].value, '-')
                        elif (self.properties[p].value_type == ValueTypes.LAURENT_POLYNOMIAL):
                            value_str =  self.latex_laurent_poly(self.properties[p].value_laurent_poly, self.properties[p].dependent_variable_print_symbol)
                        elif (self.properties[p].value_type == ValueTypes.LAURENT_POLYNOMIAL):
                            value_str =  self.replace_none_with_string(self.properties[p].value_table, '-')
                        else:
                            value_str = '-'

                        unit_str = self.replace_none_with_string(self.properties[p].unit, '-')

                        ref_str = None
                        if (ref_index == None):
                            ref_str = '-'
                        else:
                            ref_str = "[" + str(ref_index+1) + "]"

                        f.write("| " + print_name_str + " | " + value_str + " | $" + unit_str + "$ | " + ref_str + " |" + "\n")
            f.write("\n")
            if (self.notes is not None):
                f.write("## Notes \n")
                f.write(self.notes + "\n")
                f.write("\n")
            f.write("## References \n")
            for idx, ref in enumerate(reference_list):
                ref_str = self.replace_none_with_string(ref, '-')
                f.write("["+ str(idx+1) +"] " + ref_str + "\n")
                f.write("\n")
        
        return
        
    def write_pdf(self, file):
        # Write a PDF file with the current material information
        temp_md_file = "temp.md"
        self.write_markdown(temp_md_file)
        doc = pandoc.read(file=temp_md_file)
        pandoc.write(doc, file=file, format='pdf', options=['-V', 'geometry:margin=1in'])
        os.remove(temp_md_file)

        return
    
    def write_adamantine_input(self, file):
        reference_temperature = self.properties["solidus_eutectic_temperature"].value # For adamantine we assume that all temperature-dependent material properties are evaluated at the solidus temperature

        p = self.properties["specific_heat_solid"]
        if (p.value_type == ValueTypes.SCALAR):
                specific_heat_1 = p.value
        elif (p.value_type == ValueTypes.LAURENT_POLYNOMIAL):
                specific_heat_1 = p.evaluate_laurent_polynomial(reference_temperature)
        else:
                print("Error: adamantine requires either SCALAR or LAURENT_POLYNOMIAL ValueTypes.")

        p = self.properties["specific_heat_liquid"]
        if (p.value_type == ValueTypes.SCALAR):
                specific_heat_2 = p.value
        elif (p.value_type == ValueTypes.LAURENT_POLYNOMIAL):
                specific_heat_2 = p.evaluate_laurent_polynomial(reference_temperature)
        else:
                print("Error: adamantine requires either SCALAR or LAURENT_POLYNOMIAL ValueTypes.")

        p = self.properties["thermal_conductivity_solid"]
        if (p.value_type == ValueTypes.SCALAR):
                thermal_conductivity_1 = p.value
        elif (p.value_type == ValueTypes.LAURENT_POLYNOMIAL):
                thermal_conductivity_1 = p.evaluate_laurent_polynomial(reference_temperature)
        else:
                print("Error: adamantine requires either SCALAR or LAURENT_POLYNOMIAL ValueTypes.")

        density = None
        p = self.properties["density"]
        if p.value_type == ValueTypes.SCALAR:
                density = p.value
        elif p.value_type == ValueTypes.LAURENT_POLYNOMIAL:
                density = p.evaluate_laurent_polynomial(reference_temperature)
        else:
                print("Error: adamantine requires either SCALAR or LAURENT_POLYNOMIAL ValueTypes.")

        thermal_conductivity = None
        p = self.properties["thermal_conductivity_liquid"]
        if p.value_type == ValueTypes.SCALAR:
                thermal_conductivity_2 = p.value
        elif p.value_type == ValueTypes.LAURENT_POLYNOMIAL:
                thermal_conductivity_2 = p.evaluate_laurent_polynomial(reference_temperature)
        else:
                print("Error: adamantine requires either SCALAR or LAURENT_POLYNOMIAL ValueTypes.")

        emissivity = None
        p = self.properties["emissivity"]
        if p.value_type == ValueTypes.SCALAR:
                emissivity = p.value
        elif p.value_type == ValueTypes.LAURENT_POLYNOMIAL:
                emissivity = p.evaluate_laurent_polynomials(reference_temperature)
        else:
                print("Error: adamantine requires either SCALAR or LAURENT_POLYNOMIAL ValueTypes.")

        with open(file, 'w') as f:
                f.write("materials\n{")
                f.write(f"\n\tn_material 1\n")
                f.write("\n\tproperty_format polynomial\n")  # This may need to be dynamic
                f.write("\n\tmaterial_0\n\t{\n")
                f.write("\t\tsolid\n\t\t{\n")
                f.write(f"\t\t\tdensity {density} ;\n") 
                f.write(f"\t\t\tspecific_heat {specific_heat_1} ;\n")  
                f.write(f"\t\t\tthermal_conductivity_x {thermal_conductivity_1} ;\n") 
                f.write(f"\t\t\tthermal_conductivity_z {thermal_conductivity_1} ;\n")
                f.write(f"\t\t\temissivity {emissivity} ; \n")
                f.write("\t\t}\n")
                f.write("\t\tliquid\n\t\t{\n")
                f.write(f"\t\t\tdensity {density} ;\n")
                f.write(f"\t\t\tspecific_heat {specific_heat_1} ;\n")
                f.write(f"\t\t\tthermal_conductivity_x {thermal_conductivity_2} ;\n")
                f.write(f"\t\t\tthermal_conductivity_z {thermal_conductivity_2} ;\n")
                f.write(f"\t\t\temissivity {emissivity} ; \n")
                f.write("\t\t}\n")
                f.write(f"\tsolidus {self.properties['solidus_eutectic_temperature'].value} ;\n")
                f.write(f"\tliquidus {self.properties['liquidus_temperature'].value} ;\n")
                f.write(f"\tlatent heat {self.properties['latent_heat_fusion'].value} ;\n\t\t}}\n}}")
       
        return    

    def append_file(input_filename, output_filename):
        # Get current directory of the script
            current_dir = os.path.dirname(os.path.abspath(__file__))

            # Form paths
            input_file_path = os.path.join(current_dir, input_filename)
            output_file_path = os.path.join(current_dir, output_filename)

            # Read the input file
            with open(input_file_path, 'r') as input_file:
                input_content = input_file.read()

            # Append the content to the output file
            with open(output_file_path, 'a') as output_file:
                output_file.write(input_content)
    
            return
    
    def write_additivefoam_input(self, file):
        specific_heat_1 = None
        specific_heat_2 = None
        # Reference temperature based on a property from self.properties
        comment_block = """/*---------------------------------------------------------------------------
     AdditiveFOAM template input file (compatible with 1.0, OpenFOAM 10)

                      Created for simulation with Myna
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

        reference_temperature = self.properties["solidus_eutectic_temperature"].value
        p=(self.properties["thermal_conductivity_solid"].value_laurent_poly)
        labeled_values = {}
        for idx, pair in enumerate(p, 1):
            label = f"thermal_cond_S{idx}" 
            first_value = pair[0]
            labeled_values[label] = first_value
       
        a = []
        for label, value in labeled_values.items():
            a.append(value)
            print(f"{value}")
        p=(self.properties["thermal_conductivity_liquid"].value_laurent_poly)
        first_values = [pair[0] for pair in p]
        labeled_values = {}
        for idx, pair in enumerate(p, 1):
            label = f"thermal_cond_S{idx}" 
            first_value = pair[0]
            labeled_values[label] = first_value
        
        b = []
        for label, value in labeled_values.items():
            b.append(value)
            print(f"{value}")

        p = self.properties["specific_heat_solid"]
        if (p.value_type == ValueTypes.SCALAR):
                specific_heat_1 = p.value
        elif (p.value_type == ValueTypes.LAURENT_POLYNOMIAL):
                specific_heat_1 = p.evaluate_laurent_polynomial(reference_temperature)
        else:
                print("Error: ValueType not supported")

        p = self.properties["specific_heat_liquid"]
        if (p.value_type == ValueTypes.SCALAR):
                specific_heat_2 = p.value
        elif (p.value_type == ValueTypes.LAURENT_POLYNOMIAL):
                specific_heat_2 = p.evaluate_laurent_polynomial(reference_temperature)
        else:
                print("Error: ValueType not supported")
        
        with open(file, "w") as f:
            f.write(comment_block)
            f.write("solid\n{\n")
            f.write(f"\tkappa\t ({a[0]} {a[1]} 0.0);\n") 
            f.write(f"\tCp\t\t ({specific_heat_1} 0.0 0.0);\n")
            f.write("}\n\n")
            
            f.write("liquid\n{\n")
            f.write(f"\tkappa\t ({b[0]} {b[1]} 0.0);\n") 
            f.write(f"\tCp\t\t ({specific_heat_2} 0.0 0.0);\n")
            f.write("}\n")

    def write_3dthesis_input(self, file, initial_temperature=None):
         # 3DThesis/autothesis/Condor assumes at "T_0" initial temperature value. Myna populates this from Peregrine. For now we add a placeholder of -1 unless the user specifies an intial temperature.
        if (initial_temperature == None):
            initial_temperature = -1

         # For autothesis we assume that all temperature-dependent material properties are evaluated at the solidus temperature
        reference_temperature = self.properties["solidus_eutectic_temperature"].value

        thermal_conductivity = None
        p = self.properties["thermal_conductivity_solid"]
        if (p.value_type == ValueTypes.SCALAR):
            thermal_conductivity = p.value
        elif (p.value_type == ValueTypes.LAURENT_POLYNOMIAL):
             thermal_conductivity = p.evaluate_laurent_polynomial(reference_temperature)
        else:
            print("Error: autothesis requires either SCALAR or LAURENT_POLYNOMIAL ValueTypes")

        specific_heat = None
        p = self.properties["specific_heat_solid"]
        if (p.value_type == ValueTypes.SCALAR):
            specific_heat = p.value
        elif (p.value_type == ValueTypes.LAURENT_POLYNOMIAL):
             specific_heat = p.evaluate_laurent_polynomial(reference_temperature)
        else:
            print("Error: autothesis requires either SCALAR or LAURENT_POLYNOMIAL ValueTypes")

        density = None
        p = self.properties["density"]
        if (p.value_type == ValueTypes.SCALAR):
            density = p.value
        elif (p.value_type == ValueTypes.LAURENT_POLYNOMIAL):
             density = p.evaluate_laurent_polynomial(reference_temperature)
        else:
            print("Error: autothesis requires either SCALAR or LAURENT_POLYNOMIAL ValueTypes")

        with open(file, 'w') as f:
              f.write("Constants\n")
              f.write("{\n")
              f.write("\t T_0\t" + str(initial_temperature) + "\n")
              f.write("\t T_L\t" + str(self.properties["liquidus_temperature"].value) + "\n")
              f.write("\t k\t" + str(thermal_conductivity) + "\n")
              f.write("\t c\t" + str(specific_heat) + "\n")
              f.write("\t p\t" + str(density) + "\n")
              f.write("}")


    def replace_none_with_string(self, entry, replace_string):
        if entry == None:
            return replace_string
        else:
            return str(entry)
       
        
    def validate_completeness(self):
        # Check if the information is complete by a user-specified standard
        # TODO
        return
    
    
        

