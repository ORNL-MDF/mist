import json
import pandoc
import os
from enum import Enum

def hello_world(string_to_print):
    print(string_to_print)

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



        

class MaterialInformation:
    def __init__(self, file=None):

        self.property_list = ['density', 'specific_heat_solid', 'specific_heat_liquid', 'thermal_conductivity_solid', 'thermal_conductivity_liquid', 'dynamic_viscosity', 'thermal_expansion', 'latent_heat_fusion', 'latent_heat_vaporization', 'emissivity', 'molecular_mass',  'liquidus_temperature', 'log_vapor_pressure', 'laser_absorption']

        self.properties = {}

        if (file == None):
            # Set all values to None
            self.name = None
            self.notes = None

            for p in self.property_list:
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

            for p in self.property_list:
                self.properties[p] = self.json_blob_to_property(data, p)
            
        return
    
    def json_blob_to_property(self, json_blob, property_string):
        tree = json_blob[property_string]
        # Mandatory fields
        name = property_string
        unit = self.populate_optional_field(tree, 'unit')

        # Optional fields
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

    def write_markdown(self, file):
        # Write a Markdown file with the current material information
        with open(file, 'w') as f:
            reference_list = []

            f.write("# Material Property Information: " + self.name + '\n\n')
            f.write("## Property Table \n")

            f.write("|Property | Value | Units | Data Source | \n")
            f.write("|---------| ----- | ----- | ----------- | \n")

            num_refs = 0
            for p in self.property_list:
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

            f.write("NOTE: " + self.notes + "\n")
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
    
    def replace_none_with_string(self, entry, replace_string):
        if entry == None:
            return replace_string
        else:
            return str(entry)
        

    def validate_completeness(self):
        # Check if the information is complete by a user-specified standard
        # TODO
        return
        

