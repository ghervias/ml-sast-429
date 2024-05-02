# ML-SAST-Prototyp

The ML-SAST-Prototyp is a tool to detect software vulnerabilities. It uses a clustering algorithm to differentiate benign from vulnerable source code. Contrary to other machine-learning tools it does not work on the raw source code to find vulnerabilities but rather on the control-flow graph. The tool contains a novel toolchain to generate the control-flow graph from the source code. This graph is transformed into a machine-learning compatible format and compared against vulnerable source code extracted from the [Juliet Test Suite for C and C++](https://samate.nist.gov/SARD/test-suites/112). 


## Structure
The ML-SAST-Prototyp consists of several components: the actual tool "mlsast", bening and vulnerable paths from the [Juliet Test Suite for C and C++](https://samate.nist.gov/SARD/test-suites/112) "models", an oracle test "evaluation", an example to try out the prototype "example" and a frontend to display detected vulnerabilites "frontend".

## License
The ML-SAST-Prototyp is licensed under the GNU GENERAL PUBLIC LICENSE 3. For more information on the license, see the included license text itself or visit [GNU GENERAL PUBLIC LICENSE](https://www.gnu.org/licenses/gpl-3.0.en.html).
