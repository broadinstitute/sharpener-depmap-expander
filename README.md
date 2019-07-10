# sharpener-depmap-expander

Gene-list expander based on DepMap gene-knockdown correlations

Transform query example:

```
{
  "genes": [
    {
      "gene_id": "NCBIGene:100",
      "attributes": [
        {
          "name": "entrez_gene_id",
          "value": "100",
          "source": "query gene"
        },
        {
          "name": "gene_symbol",
          "value": "ADA",
          "source": "query gene"
        }
      ]
    },
    {
      "gene_id": "NCBIGene:2036",
      "attributes": [
        {
          "name": "entrez_gene_id",
          "value": "2036",
          "source": "query gene"
        },
        {
          "name": "gene_symbol",
          "value": "EPB41L1",
          "source": "query gene"
        }
      ]
    }
  ],
  "controls": [
    {
      "name": "correlation threshold",
      "value": "0.25"
    },
    {
      "name": "correlated values",
      "value": "gene knockout"
    }
  ]
}
```