import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import mistlib as mist

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
        # Create from the SS316L JSON file
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

        # Create from the AlCu JSON file
        path_to_example_data = os.path.join(os.path.dirname(__file__), '../examples/AlCu.json')
        mat = mist.core.MaterialInformation(path_to_example_data)

        assert(mat.name == "AlCu")
        properties = mat.properties
        phase_properties = mat.phase_properties

        assert(mat.composition['base_element'] == "Al")
        assert(mat.composition['solute_elements'] == ["Cu"])

        assert(properties['solidus_eutectic_temperature'].name == "solidus_eutectic_temperature")
        assert(abs(properties['solidus_eutectic_temperature'].value - 821.15) < 1.0e-13)
        assert(properties['solidus_eutectic_temperature'].unit == "K")
        assert(properties['solidus_eutectic_temperature'].reference == "O. Sinninger, M. Peters, P.W. Voorhees, Two-Phase Eutectic Growth in Al-Cu and Al-Cu-Ag, Metallurgical and Materials Transactions A, Vol. 49A, pp. 1692-1707, 2018.") 
        assert(properties['solidus_eutectic_temperature'].uncertainty == None)
        assert(properties['solidus_eutectic_temperature'].print_symbol == "T_{s}")

        assert(phase_properties['liquid'].name == 'liquid')
        solute_diffusivities = phase_properties['liquid'].properties['solute_diffusivities']
        assert(abs(solute_diffusivities["Cu"].value - 2.4e-9) < 1.0e-13)

        assert(abs(phase_properties['alpha'].properties['gibbs_thomson_coeff'].value - 2.4e-7) < 1.0e-13)
        
        assert(abs(phase_properties['theta'].properties['solubility_limit'].value - 31.9) < 1.0e-13)

        # Create from the AlCu_test_in JSON file
        path_to_example_data = os.path.join(os.path.dirname(__file__), 'AlCu_test_in.json')
        mat = mist.core.MaterialInformation(path_to_example_data)
        assert(mat.name == "AlCu")

        comp = mat.composition
        assert(comp['base_element'] == "Al")
        assert(comp['solute_elements'] == ['Cu'])
        assert(abs(comp['Al'].value - 91.0) < 1.0e-13)
        assert(abs(comp['Cu'].value - 9.0) < 1.0e-13)

    def test_write_markdown(self):
        path_to_example_data = os.path.join(os.path.dirname(__file__), '../examples/SS316L.json')
        mat = mist.core.MaterialInformation(path_to_example_data)
        
        file = "markdown_test_SS316L.md"
        mat.write_markdown(file)

        path_to_example_data = os.path.join(os.path.dirname(__file__), 'AlCu_test_in.json')
        mat = mist.core.MaterialInformation(path_to_example_data)
        
        file = "markdown_test_AlCu.md"
        mat.write_markdown(file, ['properties', 'composition'])

    def test_write_pdf(self):
        path_to_example_data = os.path.join(os.path.dirname(__file__), '../examples/SS316L.json')
        mat = mist.core.MaterialInformation(path_to_example_data)
        
        file = "pdf_test_SS316L.pdf"
        mat.write_pdf(file)

    def test_write_3dthesis(self):
        path_to_example_data = os.path.join(os.path.dirname(__file__), '../examples/SS316L.json')
        mat = mist.core.MaterialInformation(path_to_example_data)
        
        file = "3dthesis_input.txt"
        mat.write_3dthesis_input(file)

        # I may have to do something more sophisticated in case there's roundoff error
        expected_lines = ["Constants\n", "{\n", "\t T_0\t-1\n", "\t T_L\t1730\n", "\t k\t26.901513499999997\n", "\t c\t608.641365\n", "\t p\t7955\n", "}"]

        with open(file, 'r') as f:
            lines = f.readlines()
            assert(lines == expected_lines)





if __name__ == '__main__':
    unittest.main()