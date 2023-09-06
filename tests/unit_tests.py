import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#import mist
import unittest

#from mist.core import hello_world
import mist

class TestSuite(unittest.TestCase):
    """Test cases."""

    def test_property_creation(self):
        # Manual creation
        prop = mist.core.Property("density", "kg/m^3", 2.0)
        assert(prop.name == "density")
        assert(abs(prop.value - 2.0) < 1.0e-13)
        assert(prop.unit == "kg/m^3")
        assert(prop.reference == None) 
        assert(prop.uncertainty == None)
        assert(prop.print_symbol == None)

        prop = mist.core.Property("density", "kg/m^3", 2.0, uncertainty = 1.5)
        assert(prop.name == "density")
        assert(abs(prop.value - 2.0) < 1.0e-13)
        assert(prop.unit == "kg/m^3")
        assert(prop.reference == None) 
        assert(abs(prop.uncertainty - 1.5) < 1.0e-13)
        assert(prop.print_symbol == None)

    def test_material_information_creation(self):
        # Create from a JSON file
        path_to_example_data = os.path.join(os.path.dirname(__file__), '../examples/SS316L.json')
        mat = mist.core.MaterialInformation(path_to_example_data)

        assert(mat.name == "SS316L")
        properties = mat.properties
        assert(properties['density'].name == "density")
        assert(abs(properties['density'].value - 7955.0) < 1.0e-13)
        assert(properties['density'].unit == "kg/m^3")
        assert(properties['density'].reference == "C.S. Kim, Thermophysical properties of stainless steels, Argonne National Laboratory, Argonne, Illinois, 1975.") 
        assert(properties['density'].uncertainty == None)
        assert(properties['density'].print_symbol == "\\rho")

        assert(properties['liquidus_temperature'].name == "liquidus_temperature")
        assert(abs(properties['liquidus_temperature'].value - 1730.0) < 1.0e-13)
        assert(properties['liquidus_temperature'].unit == "K")
        assert(properties['liquidus_temperature'].reference == "C.S. Kim, Thermophysical properties of stainless steels, Argonne National Laboratory, Argonne, Illinois, 1975.") 
        assert(properties['liquidus_temperature'].uncertainty == None)
        assert(properties['liquidus_temperature'].print_symbol == "T_{l}")

    def test_write_markdown(self):
        path_to_example_data = os.path.join(os.path.dirname(__file__), '../examples/SS316L.json')
        mat = mist.core.MaterialInformation(path_to_example_data)
        
        file = "markdown_test.md"
        mat.write_markdown(file)

    def test_write_pdf(self):
        path_to_example_data = os.path.join(os.path.dirname(__file__), '../examples/SS316L.json')
        mat = mist.core.MaterialInformation(path_to_example_data)
        
        file = "markdown_test.md"
        mat.write_pdf(file)



if __name__ == '__main__':
    unittest.main()