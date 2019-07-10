
from swagger_server.models.transformer_info import TransformerInfo
from swagger_server.models.parameter import Parameter
from swagger_server.models.transformer_query import TransformerQuery
from swagger_server.models.gene_info import GeneInfo
from swagger_server.models.attribute import Attribute

import requests


def expander_info():
    """
        Return information for this expander
    """
    return TransformerInfo(
        name = 'DepMap correlation expander',
        function = 'expander',
        parameters = [
            Parameter(
                name = 'correlation threshold',
                type = 'double',
                default = '0.5'
            ),
            Parameter(
                name = 'correlated values',
                type = 'string',
                default = 'gene knockout',
                allowed_values = ['gene knockout']
            )
        ]
    )


def expand(query: TransformerQuery):
    """
        Execute this expander, find all genes correlated to query genes.
    """
    controls = {control.name:control.value for control in query.controls}
    try:
        threshold = float(controls['correlation threshold'])
        if controls['correlated values'] == 'gene knockout':
            genes = {gene.gene_id:gene for gene in query.genes}
            for gene in query.genes:
                genes = expand_gene_knockout(gene, threshold, genes)
            return list(genes.values())
        else:
            msg = "invalid correlated values: '"+controls['correlated values']+"'"
            return ({ "status": 400, "title": "Bad Request", "detail": msg, "type": "about:blank" }, 400 )
    except ValueError:
        msg = "invalid correlation threshold: '"+controls['correlation threshold']+"'"
        return ({ "status": 400, "title": "Bad Request", "detail": msg, "type": "about:blank" }, 400 )


CORR_URL = 'https://indigo.ncats.io/gene_knockout_correlation/correlations/{}'


def expand_gene_knockout(gene: GeneInfo, threshold: float, genes: dict):
    """
        Add genes with gene-knockout correlation to query gene above the threshold
    """
    gene_id = entrez_gene_id(gene)
    if gene_id != None:
        correlations = requests.get(CORR_URL.format(gene_id)).json()
        for correlation in correlations:
            if correlation['correlation'] > threshold:
                genes = add_correlation(genes, correlation, gene_symbol(gene))
    return genes


def add_correlation(genes:dict, correlation: dict, symbol: str):
    """
        Add correlation information to genes dictionary
    """
    entrez_gene_id = correlation['entrez_gene_id_2']
    gene_id = 'NCBIGene:'+str(entrez_gene_id)
    if gene_id in genes:
        gene = genes[gene_id]
        gene.attributes.append(
            Attribute(
                name = 'gene-knockout correlation with '+symbol,
                value = str(correlation['correlation']),
                source = 'DepMap gene-knockout correlation'
            )
        )
    else:
        gene = GeneInfo(
            gene_id = gene_id,
            attributes = [
                Attribute(
                    name = 'entrez_gene_id',
                    value = str(entrez_gene_id),
                    source = 'DepMap gene-knockout correlation'
                ),
                Attribute(
                    name = 'gene-knockout correlation with '+symbol,
                    value = str(correlation['correlation']),
                    source = 'DepMap gene-knockout correlation'
                )
            ]
        )
        genes[gene_id] = gene
    return genes


def entrez_gene_id(gene: GeneInfo):
    """
        Return value of the entrez_gene_id attribute
    """
    for attr in gene.attributes:
        if attr.name == 'entrez_gene_id':
            return attr.value
    return None


def gene_symbol(gene: GeneInfo):
    """
        Return value of the gene_symbol attribute
    """
    for attr in gene.attributes:
        if attr.name == 'gene_symbol':
            return attr.value
    return 'query gene'

