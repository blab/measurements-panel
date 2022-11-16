# Joint visualization of seasonal influenza serology and phylogeny to inform vaccine composition

**Jover Lee<sup>1,6</sup>, James Hadfield<sup>1,6</sup>, Allison Black<sup>2</sup>, Thomas R. Sibley<sup>1</sup>, Richard A. Neher<sup>3,4</sup>, Trevor Bedford<sup>1,5</sup>, John Huddleston<sup>1</sup>**

<sup>1</sup>Vaccine and Infectious Disease Division, Fred Hutchinson Cancer Center, Seattle, WA, USA
<sup>2</sup>Chan Zuckerberg Initiative, CA, San Francisco, CA, USA
<sup>3</sup>Biozentrum, Universität Basel, Switzerland
<sup>4</sup>Swiss Institute of Bioinformatics, Switzerland
<sup>5</sup>Howard Hughes Medical Institute, Seattle, WA, USA
<sup>6</sup>These authors contributed equally to this work and share first authorship

Seasonal influenza vaccines must be updated regularly to account for mutations that allow influenza viruses to escape our existing immunity. A successful vaccine should represent the genetic diversity of recently circulating viruses and induce antibodies that effectively prevent infection by those recent viruses. Thus, linking the genetic composition of circulating viruses and the serological experimental results measuring antibody efficacy is crucial to the vaccine design decision. Historically, genetic and serological data have been presented separately in the form of static visualizations of phylogenetic trees and tabular serological results to identify vaccine candidates. To simplify this decision-making process, we have created an interactive tool for visualizing serological data that has been integrated into Nextstrain’s real-time phylogenetic visualization framework, Auspice. We show how the combined interactive visualizations may be used by decision-makers to explore the relationships between complex data sets for both prospective vaccine virus selection and retrospectively exploring the performance of vaccine viruses.

## Explore the data on Nextstrain

[Explore the measurements panel and its corresponding data on Nextstrain](https://nextstrain.org/community/blab/measurements-panel/flu/seasonal/h3n2/ha?p=grid).

## Run the Nextstrain analysis

Follow [the data curation guide](data/README.md), to prepare the data required to run this workflow.
[Install Miniconda](https://docs.conda.io/en/latest/miniconda.html) and then [install Mamba](https://mamba.readthedocs.io/en/latest/installation.html#installation) into your base conda environment as shown below.

``` bash
conda install mamba -n base -c conda-forge
```

Create a new conda environment with [Snakemake](https://snakemake.readthedocs.io/) installed.

``` bash
mamba create -n snakemake -c conda-forge -c bioconda snakemake
```

Activate the conda environment with Snakemake.

``` bash
conda activate snakemake
```

Run the workflow in "dry-run" mode to see all the steps and ensure that the files you need from the data curation guide exist.

``` bash
snakemake -n -p
```

Run the workflow.

``` bash
snakemake -p --cores all --use-conda --conda-frontend mamba
```

Open a file explorer window for the `auspice/` directory, select all of the files in the directory, and drag those files on to https://auspice.us/.
Explore the measurements panel, tree, and more.

## Build manuscript

``` bash
cd manuscript
./build.sh
```
