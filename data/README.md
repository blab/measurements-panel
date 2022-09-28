# Data curation

All data for this manuscript come from [the GitHub repository](https://github.com/trvrb/flux/tree/master/data) for [Bedford et al. 2014](https://bedford.io/papers/bedford-flux/).
We use sequence data from [GISAID](https://gisaid.org), so we cannot repost these data here.
Instead, we share the sequence accessions and the steps to download and prepare these data.

## Data copied from Bedford et al. 2014

The files [`H3N2_seq_data.tsv`](https://github.com/trvrb/flux/blob/39e14083dd2ce119b81b0fd777551120ea6c8837/data/H3N2_seq_data.tsv) and [`H3N2_HI_data.tsv`](https://github.com/trvrb/flux/blob/39e14083dd2ce119b81b0fd777551120ea6c8837/data/H3N2_HI_data.tsv) here are copies of the corresponding files in the Bedford et al. GitHub repository.

## Download sequences and metadata from GISAID

The following steps assume you already have an account with GISAID.
If you do not, [register for a GISAID account](https://gisaid.org/register/).

  1. Navigate to [GISAID](https://gisaid.org) and login.
  2. Select the "EpiFlu" tab from the main navigation bar.
  3. Copy and paste ids for a batch in one of the files named like `epi_ids_batch_1.txt` in this directory into the "Search patterns" field of the EpiFlu page.
  4. Select "Search"
  5. Select all results by clicking checkbox in the top left of search results
  6. Select "Download"
  7. Select "Sequences (DNA) as FASTA"
  8. Select "HA" from the "DNA" section
  9. Set the FASTA header string to `Isolate name|Isolate ID | DNA Accession no. | DNA INSDC | Collection date`
  10. Select "Download"
  11. Save file as `batch_{batch_number}.fasta`
  12. Repeat steps 3-11 for each batch.
  13. Concatenate the batch FASTA files into `raw_h3n2_ha.fasta`

The resulting FASTA file will contain more sequences than EPI ids you searched for, since GISAID returns all versions of sequences for a given strain name that matches any EPI id.
Next, filter the raw FASTA file by EPI id from the complete list in this directory.

```python
import Bio.SeqIO

# Load GISAID segment sequence ids (e.g., EPI103357).
with open("epi_ids.txt", "r") as handle:
    epi_ids = [line.strip() for line in handle]

# Remove leading "EPI" string from each id (e.g., 103357).
epi_numbers = [epi_id[3:] for epi_id in epi_ids]

# Filter records.
records = []
sequences = Bio.SeqIO.parse("raw_h3n2_ha.fasta", "fasta")
for sequence in sequences:
    # Search sequence record's EPI id in known list.
    if sequence.name.split("|")[2] in epi_numbers:
        records.append(sequence)

# Save filtered records.
Bio.SeqIO.write(records, "h3n2_ha.fasta", "fasta")
```

The resulting FASTA file `h3n2_ha.fasta` is the starting point for the workflow.
