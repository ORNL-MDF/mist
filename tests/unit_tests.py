import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from md2pdf.core import md2pdf
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
    # PDF creation from markdown_test_SS316L
        current_dir = os.path.dirname(os.path.abspath(__file__))
        md_file_name = "markdown_test_SS316L.md"
        pdf_file_name = "pdf_test_SS316L.pdf"

        # Construct full file paths
        md_file_path = os.path.join(current_dir, 'md_file_name')
        pdf_file_path = os.path.join(current_dir, pdf_file_name)
        with open(md_file_name, "r") as f:
                md_content = f.read()
        # Convert Md to PDF
        md2pdf(pdf_file_path, md_content)

    # PDF creation from markdown_test_AlCu
        current_dir = os.path.dirname(os.path.abspath(__file__))
        md_file_name = "markdown_test_AlCu.md"
        pdf_file_name = "pdf_test_AlCu.pdf"

        md_file_path = os.path.join(current_dir, 'md_file_name')
        pdf_file_path = os.path.join(current_dir, pdf_file_name)
        with open(md_file_name, "r") as f:
                md_content = f.read()
        # Convert Markdown to PDF using md2pdf
        md2pdf(pdf_file_path, md_content)

    def test_write_adamantine(self):
        path_to_example_data = os.path.join(os.path.dirname(__file__), '../examples/SS316L.json')
        mat = mist.core.MaterialInformation(path_to_example_data)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file = "mistinput.info"
        adamantine_file_path = os.path.join(current_dir, 'mistinput.info')

        # Call the function that should create the file
        mat.write_adamantine_input(adamantine_file_path)

        # Assert that the file now exists
        self.assertTrue(os.path.exists(adamantine_file_path), f"File {file} should exist.")

    def test_write_additivefoam(self):
        path_to_example_data = os.path.join(os.path.dirname(__file__), '../examples/SS316L.json')
        mat = mist.core.MaterialInformation(path_to_example_data)
        transport_filepath, thermo_filepath = mat.write_additivefoam_input()

        # Asserts whether the files actually exist
        self.assertTrue(os.path.exists(transport_filepath), f"File {thermo_filepath} should exist.")
        self.assertTrue(os.path.exists(thermo_filepath)), f"File {thermo_filepath} should exist."

    def test_write_3dthesis(self):
        path_to_example_data = os.path.join(os.path.dirname(__file__), '../examples/SS316L.json')
        mat = mist.core.MaterialInformation(path_to_example_data)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        thesis_file_path = os.path.join(current_dir, '3dthesis_input.txt')
        file = "3dthesis_input.txt"
        mat.write_3dthesis_input(thesis_file_path)

        # I may have to do something more sophisticated in case there's roundoff error
        expected_lines = ["Constants\n", "{\n", "\t T_0\t-1\n", "\t T_L\t1730\n", "\t k\t26.901513499999997\n", "\t c\t608.641365\n", "\t p\t7955\n", "}"]

        floating_point_line_numbers = [2, 3, 4, 5]
        relative_tolerance = 1e-5

        with open(thesis_file_path, 'r') as f:
            lines = f.readlines()
            for i in range(0, len(lines)):
                if i in floating_point_line_numbers:
                    expected = float(expected_lines[i].strip().split()[1])
                    test = float(lines[i].strip().split()[1])
                    diff = abs(expected-test)/expected
                    try:
                        assert(diff < relative_tolerance)
                    except:
                        print("Error: difference exceeded the tolerance", diff, relative_tolerance)

                else:
                    assert(lines[i] == expected_lines[i])

if __name__ == '__main__':
    unittest.main()
