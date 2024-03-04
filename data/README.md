# Data curation

All data for this manuscript come from [the GitHub repository](https://github.com/trvrb/flux/tree/master/data) for [Bedford et al. 2014](https://bedford.io/papers/bedford-flux/).
Some sequence data originate from INSDC-based databases (e.g., Influenza Research Database or IRD), so we have included these open data and their accessions here.
Some sequence data originate from [GISAID](https://gisaid.org), so we cannot repost these data here.
Instead, we share the sequence accessions and the steps to download and prepare these data.

## Data copied from Bedford et al. 2014

The files [`H3N2_seq_data.tsv`](https://github.com/trvrb/flux/blob/39e14083dd2ce119b81b0fd777551120ea6c8837/data/H3N2_seq_data.tsv) and [`H3N2_HI_data.tsv`](https://github.com/trvrb/flux/blob/39e14083dd2ce119b81b0fd777551120ea6c8837/data/H3N2_HI_data.tsv) here are copies of the corresponding files in the Bedford et al. GitHub repository.

## Data copied from INSDC databases

We include all data that Bedford et al. 2014 sourced from the Influenza Research Database (IRD) here in the file `IRD.fasta`.
We downloaded these data from the [Influenza Virus Resource](https://www.ncbi.nlm.nih.gov/genomes/FLU/Database/nph-select.cgi?go=database) which provides an interface to search by accession.
We include the corresponding accessions used to obtain these data in `IRD_accessions.txt`.
We created this accessions list from the Bedford et al. sequence table with the following command using [tsv-utils](https://opensource.ebay.com/tsv-utils/).

```bash
tsv-filter -H --str-eq database:IRD H3N2_seq_data.tsv \
  | tsv-select -H -f accession \
  | sed 1d > IRD_accessions.txt
```

We searched by accession on [Influenza Virus Resource](https://www.ncbi.nlm.nih.gov/genomes/FLU/Database/nph-select.cgi?go=database).
Search results included a duplicate copy of a vaccine strain with “Vac” in the “VacStr” column which we omitted from the download.
We customized the FASTA defline to `>{strain}|{accession}|{year}-{month}-{day}` and downloaded FASTA as `IRD.fasta`.

Note that one accession, `CY116571`, does not have a match in the Influenza Virus Resource.
This accession corresponds to the strain A/Auckland/4382/1982 which was [later reclassified as a strain from a mixed infection](https://www.ncbi.nlm.nih.gov/nuccore/CY112369.1).
We omitted this sequence from the subsequent analyses.

## Download sequences and metadata from GISAID

Download the remaining data from Bedford et al. from GISAID.
The following steps assume you already have an account with GISAID.
If you do not, [register for a GISAID account](https://gisaid.org/register/).

  1. Navigate to [GISAID](https://gisaid.org) and login.
  2. Select the "EpiFlu" tab from the main navigation bar.
  3. Open the file `GISAID_accessions.txt` and, working in batches, copy and paste ids for one batch into the "Search patterns" field of the EpiFlu page.
  4. Select "Search".
  5. Select all results by clicking checkbox in the top left of search results.
  6. Select "Download".
  7. Select "Sequences (DNA) as FASTA".
  8. Select "HA" from the "DNA" section.
  9. Set the FASTA header string to `Isolate name|Isolate ID|Collection date|Originating lab`.
  10. Check the box next to "Replace spaces with underscores in FASTA header"
  11. Select "Download".
  12. Save file as `GISAID_batch_{batch_number}.fasta`.
  13. Repeat steps 3-12 for the remaining batches.

The resulting FASTA files will contain more sequences than accessions you searched for, since GISAID returns all versions of sequences for a given isolate accession.
Concatenate all of the batches and remove duplicate sequences with [seqkit](https://bioinf.shenwei.me/seqkit/).

``` bash
cat GISAID_batch_* | seqkit rmdup --by-name > GISAID.fasta
```

## Combine data from INSDC and GISAID databases

Concatenate data from GISAID and IRD.

```bash
cat GISAID.fasta IRD.fasta > raw_h3n2_ha.fasta
```

These sequences contain metadata in their deflines that we need to parse out into a separate FASTA and TSV files.

```
augur parse \
  --sequences raw_h3n2_ha.fasta \
  --output-sequences parsed_h3n2_ha_sequences.fasta \
  --output-metadata parsed_h3n2_ha_metadata.tsv \
  --fields strain accession date authors \
  --fix-dates monthfirst
```

Augur cannot properly parse all of the dates.
Specifically, A/HongKong/1/1968 has a malformed date in its IRD record (`NON--`) and A/Bilthoven/2668/1970 is missing a date in its GISAID record (``), so we need to replace these date strings with the appropriate ambiguous dates for each strain.

``` bash
csvtk -t replace \
  -f date \
  -p "(NON--)" \
  -r "1968-XX-XX" \
  parsed_h3n2_ha_metadata.tsv | \
    csvtk -t replace \
      -f date \
      -p "(^$)" \
      -r "1970-XX-XX" > parsed_h3n2_ha_metadata_with_corrected_dates.tsv
```

Sequence names from Bedford et al. 2014 do not always match names from these databases, so we need to rename the sequences to match the Bedford et al. names.
To rename sequences, we first join the database metadata with the sequence table from Bedford et al. on `accession` using tsv-utils.
After the join, we rename and reorder the "strain" columns with [csvtk](https://bioinf.shenwei.me/csvtk/) such that the Bedford et al. strain name appears as `strain` in the first column.

``` bash
tsv-join \
  --header \
  --filter-file H3N2_seq_data.tsv \
  --key-fields accession \
  --append-fields strain \
  -p bedford_ parsed_h3n2_ha_metadata_with_corrected_dates.tsv \
    | csvtk -t rename -f strain,bedford_strain -n database_strain,strain \
    | csvtk -t cut -f 5,1,2,3,4 > h3n2_ha_metadata.tsv
```

The resulting TSV file has `strain` (from Bedford et al), `database_strain` (from database downloads), `accession`, and `date`.
Create a mapping of database strain name to Bedford et al. strain name.

``` bash
csvtk -t cut -f 2,1 h3n2_ha_metadata.tsv > database_to_bedford_strain.tsv
```

Rename sequences with the mapping of strain names.

``` bash
seqkit replace \
  -p '(.+)' \
  -r '{kv}' \
  -k database_to_bedford_strain.tsv \
  parsed_h3n2_ha_sequences.fasta > h3n2_ha_sequences.fasta
```

The resulting files `h3n2_ha_sequences.fasta` and `h3n2_ha_metadata.tsv` are the starting points for the analyses in this paper.
Each file should contain 401 records.
