# Usage

After the ml-sast prototype has been installed, following the steps
outlined in the [Installation guide](Installation.md), this guide
provides the necessary steps to analyze your own source code for
potential security vulnerabilities.

## Project directory

The project directory needs to contain the following four items:
1. A directory `code`, which contains the source code that should be
   analyzed 
2. A build script `build.sh` - that defines how the source code is
   compiled
3. A main function, that calls all the exposed APIs of the source code
4. The file `config.yaml`, that define the analysis steps and analysis
   parameters

An example of this setup is given by the `example` project to provide
you a starting point to define and configure the analysis steps to
your needs.

### Code - Directory

This directory contains the source code that should be analyzed.

### build.sh

This scripts defines how the source code is compiled. As the build
system is based on Ubuntu 20.04, needed dependencies for the
compilation of the source code can be installed with the help of `apt`
or `apt-get`.

### config.yaml

This is the main configuration file for the tool that must be
provided with every software project to be analyzed. It configures the
individual analysis phases and the order in which the tool is supposed
to execute them. At the top level, the `config.yaml` is a dictionary,
where key corresponds to a phase, with the exception of the first
key: `general`. All other phases use their exact class names that are
defined by the python modules found in `mlsast/logic/steps`.
Internally the tool maps these names onto the corresponding classes
and executes them in the order (top to bottom) that the
`config.yaml`-file dictates. Listed below are all phases that the tool
is shipped with and their configuration parameters.

#### general

| key      | type   | usage                                                                   |
|----------|--------|-------------------------------------------------------------------------|
| project  | string | The name of the project to analyze (merely for documentation purposes). |
| source   | string | File path to the source code to be analyzed.                            |
| loglevel | string | The log level (DEBUG or INFO or WARNING or ERROR).                      |

##### Example

```
general:
  project: "example"  
  source: ./code  
  loglevel: DEBUG  
```

#### svf

| key     | type   | usage                                                                        |
|---------|--------|------------------------------------------------------------------------------|
| binray  | string | The binary that results from the compilation defined in the build.sh script. |
| delete  | bool   | If true, the docker container of this phase will be removed after execution. |
| graphs  | list   | The internal graph representations that SVF must build for the analysis:     |
| ↳ tldg  | string | The top level dependency graph (LLVM-IR SSA w/o points-to information).      |
| ↳ svfg  | string | The sparse value flow graph (data dependencies considering points-to info).  |
| ↳ icfg  | string | The interprocedural control flow graph (required).                           |
| ↳ ptacg | string | The call graph (includes points-to information, required for icfg).          |
| options | dict   | Additonal options for SVF¹.                                                  |


¹) The number of threads for the parallel execution of the points to analysis may be provided here,
   using the `versioning_threads` key and supplying the number of threads an integer value.
   Moreover, the preciseness of the points-to analysis may be set here as well, through the key:
   `precise_analysis`. The value should be set to `precise` (recommended). Omitting this key
   altogether will result in the imprecise Andersen's points-to analysis to be used.

##### Example

```
svf:
  graphs:
    - tldg
    - icfg
    - svfg
    - ptacg
  options:
    versioning_threads: 7
    precise_analysis: true
  binary: entrypoint
  delete: true
```

#### neo4j

| key                    | type   | usage                                                      |
|------------------------|--------|------------------------------------------------------------|
| delete                 | bool   | Removes Neo4j docker container after execution.            |
| memory                 | dict   | Memory settings for the Neo4j database.                    |
| ↳ auto                 | dict   | Neo4j will automatically determine the best configuration. |
| ↳ heap.initial\_size²  | dict   | Initial heap size in MB (m) or GB (g).                     |
| ↳ heap.max\_size²      | dict   | Maximum heap space in MB (m) or GB (g).                    |
| ↳ pagecache.size²      | dict   | Available page cache size in MB (m) or GB (g).             |
| ↳ off\_heap.max\_size² | dict   | Maximum off heap size in MB (m) or GB (g).                 |
| prepare                | string | Preparation query to be executed before the actual query   |
| query                  | string | Query used to extract proogram data from the neo4j DB.     |

²) Must be prefixed with `dbms.memory.`, please also refer to the official Neo4j documentation
   for more information: [Link](https://neo4j.com/docs/operations-manual/4.4/).

##### Example

```
neo4j:
  delete: true
  memory:
    dbms.memory.heap.initial_size: 5100m
    dbms.memory.heap.max_size: 5100m
    dbms.memory.pagecache.size: 2900m
    dbms.memory.off_heap.max_size: 4000m
prepare: |
         // INIT DATABASE
         CALL mlsast.prepare.generateLabels();
         CALL mlsast.prepare.generateIndeces();
         CALL mlsast.prepare.connectGraphs();
         CALL mlsast.prepare.makeRelationships();
         CALL mlsast.prepare.setIcfgProps();
         CALL mlsast.prepare.buildIcfgPhis();
query: |
       // Get list of procedures in program.
       CALL mlsast.util.listProcedures()
       YIELD str AS f

       // Find call sites for procedures.
       WITH f
       MATCH (n:FunEntryICFGNode {func_name: f})

       // Find exit nodes for same procedures.
       WITH f, n
       MATCH (m:FunExitICFGNode {func_name: f})

       // Find unique paths between call sites and exit points.
       WITH f, n, collect(m) AS exits
         CALL apoc.path.expandConfig(n, {
             relationshipFilter: "icfg>",
             terminatorNodes: exits,
             uniqueness: "NODE_LEVEL",
             maxLevel: 75
         })

         YIELD path

       // Return name of the procedure (f) and the associated paths (path).
       RETURN f, path;
```

#### distance

| key                 | type   | usage                                                         |
|---------------------|--------|---------------------------------------------------------------|
| model\_path         | string | The model to be used for the distance analysis.               |
| node\_property      | string | Data used for the embedding (node\_type or ir\_opcode).       |
| threshold\_factor   | int    | Factor by which to alter the detection threshold.             |
| centroids           | string | Paths on which the models should be initialized (good or bad). |
| clustering\_type    | string | Clustering algorithm used to generate the centroids (kmeans). |
| expected\_clusters  | int    | Expected clusters for each defect class (recommended: 8).     |
| threshold\_scaling  | int    | Factor to scale the detection threshold.                      |
| include\_models³ ⁴  | list   | Defect classes that should be included in the analysis.       |
| exclude\_models⁴    | list   | Defect classes by CWE that should be excluded in the analysis. |
| source\_code\_delta | int    | Reported lines before and after defective code lines.         |

³) Set to `all` if all models should be included.

⁴) For the supplied model that was generated on the basis of the Juliet test suite, this would be
   the corresponding CWE-Class, e.g., CWE-690

##### Example

```
distance:
  model_path: models/juliet.zip
  node_property: node_type
  threshold_factor: 1
  centroids: bad  
  clustering_type: kmeans
  expected_clusters: 8
  threshold_scaling: 1
  include_models: all
    - CWE-122
    - CWE-690
  exclude_models:
    - CWE-606
  source_code_delta: 4
```

### main-function

To buid the interprocedural control flow graph (ICFG) of a program, the tool
requires a single entrypoint into the program. Normally, the main procedure of
any program serves as such entrypoint. However, in some cases there is no main
procedure available, e.g., due to the software being a library. In this case, it
is necessary to manually devise a main procedure that calls every other
procedure that should be respected when generating the ICFG. It is not necessary
that the resulting program is executable as long as it is compilable. This means
especially that bogus parameters may be passed to the library procedure calls,
as long as they respect the procedures signature (e.g., null pointers instead of
valid pointers).

## Run ml-sast prototype

```shell 
python3 -m mlsast -p example/
```

Running the ml-sast prototype for the first time, takes some extra
time, as some docker images need to be downloaded and others need to
be build.

## Visualize results

To visualize the results of the ml-sast prototype a small frontend
has been implemented. This can be started by issuing the following
command:

```shell
cd frontend
python3 -m frontend --report ../example/report.json --models ../models/juliet.zip
```

### Optional options:
The frontend can also be started with two optional options, to filter the detected paths. With the first option ("-x") the reports can be filtered to match a defined regular expressions. With the help of the second option ("-b") the results for the specified models are excluded. Using these two options would result in the following command:
```shell
python3 -m frontend --report ../example/report.json --models ../models/juliet.zip -x "^CWE\d{2,3}_.*_\d+" -b CWE-426
```
Starting the frontend with these options, only loads paths in which the function name of the first node matches the specified regex. The second option removes results concerning the specified model.

## Oracle Tests

As described in the [study](https://www.bsi.bund.de/DE/Service-Navi/Publikationen/Studien/ML-SAST/ml-sast_node.html), 
the prototype was evaluated on real-world software defects. The software
defects were extracted by Fan et al. and published in the 
[study](https://dl.acm.org/doi/abs/10.1145/3379597.3387501). The
commit-hashes that fix these software defects are included with the
prototype along with several scripts to download the software projects
in the version prior to these fixes. These scripts are located in the
directory 'evaluation'. 

To download the software defects run the following commands:
```shell
cd evaluation
bash build.sh && bash build_miniupnp_special_cases.sh && bash build_openjpeg_special_cases.sh
```

After downloading the software projects in the various versions you can
evaluate the prototype on each defect by running the command:
```shell
cd evaluation
bash run_prototype_on_oracle_tests.sh
```

When the prototype has analyzed each version of the different software
projects, you can filter the reports using the python script
'evaluate-oracle-tests.py':
```shell
cd evaluation
python3 evaluate-oracle-tests.py
```
After running this script only reports that match the defects
in filename and line numbers are kept and stored in each directory
under the name 'filtered_report.json'. These filtered reports can then be
visualized with the frontend, which comes with the prototype, and
manually checked if the prototype correctly detected the defects. To do this
change into the directory frontend and issue for example the following command:
```shell
cd frontend
python3 -m frontend --report ../evaluation/results/lib/miniupnp/79cca974a4c2ab1199786732a67ff6d898051b78/1.0/filtered_report.json --models ../models/juliet.zip
```
