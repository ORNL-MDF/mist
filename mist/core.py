import json
import pandoc
import os

def hello_world(string_to_print):
    print(string_to_print)

class Property:
    def __init__(self, name, value, unit, print_name = None, reference = None, uncertainty = None, print_symbol = None):
        self.name = name
        self.value = value
        self.unit = unit
        self.reference = reference
        self.uncertainty = uncertainty
        self.print_symbol = print_symbol

        if print_name == None:
            self.print_name = name
        else:
            self.print_name = print_name

class MaterialInformation:
    def __init__(self, file=None):

        self.property_list = ['density', 'liquidus_temperature']

        self.properties = {}

        if (file == None):
            # Set all values to None
            self.name = None

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

            for p in self.property_list:
                self.properties[p] = self.json_blob_to_property(data, p)
            
        return
    
    def json_blob_to_property(self, json_blob, property_string):
        tree = json_blob[property_string]
        # Mandatory fields
        name = property_string
        value = tree['value']
        unit = tree['unit']

        # Optional fields
        print_name = self.populate_optional_field(tree, 'print_name')
        reference = self.populate_optional_field(tree, 'reference')
        uncertainty = self.populate_optional_field(tree, 'uncertainty')
        print_symbol = self.populate_optional_field(tree, 'print_symbol')

        property = Property(name, value, unit, print_name, reference, uncertainty, print_symbol)

        return property
    
    def populate_optional_field(self, json_blob, field_key):
        val = None
        if field_key in json_blob:
            val = json_blob[field_key]
            if val == "None":
                val = None

        return val

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

            for p in self.property_list:
                next_ref = self.properties[p].reference
                ref_index = -1
                for idx, ref in enumerate(reference_list):
                    if next_ref == ref:
                        ref_index = idx
                        break
                
                if ref_index == -1:
                    ref_index = len(reference_list)
                    reference_list.append(next_ref)

                f.write("| " + self.properties[p].print_name + " | " + str(self.properties[p].value) + " | $" + self.properties[p].unit + "$ | " + " [" + str(ref_index+1) + "] |" + "\n")

            f.write("\n")
            f.write("## References \n")
            for idx, ref in enumerate(reference_list):
                f.write("["+ str(idx+1) +"] " + ref + "\n")

        
        return
        
    def write_pdf(self, file):
        # Write a PDF file with the current material information
        temp_md_file = "temp.md"
        pdf_file = "test.pdf"
        self.write_markdown(temp_md_file)
        doc = pandoc.read(file=temp_md_file)
        pandoc.write(doc, file=pdf_file, format='pdf', options=['-V', 'geometry:margin=1in'])
        os.remove(temp_md_file)

        return
    
    def validate_completeness(self):
        # Check if the information is complete by a user-specified standard
        # TODO
        return
        

