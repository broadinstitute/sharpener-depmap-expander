
from swagger_server.models.transformer_info import TransformerInfo
from swagger_server.models.parameter import Parameter
from swagger_server.models.transformer_query import TransformerQuery
from swagger_server.models.gene_info import GeneInfo
from swagger_server.models.gene_info import GeneInfoIdentifiers
from swagger_server.models.attribute import Attribute

from typing import List

import json
import requests

NAME = 'DepMap co-fitness correlation'
THRESHOLD = 'correlation threshold'
DIRECTION = 'correlation direction'
CORRELATED_VALUES = 'correlated values'

CORR_URL = 'https://translator.broadinstitute.org/gene_knockout_correlation/correlations/'


def configure():
    """
        Configure transformer
    """
    global CORR_URL

    with open("config.json",'r') as f:
        config = json.loads(f.read())
        if 'correlation_url' in config:
            CORR_URL = config['correlation_url']

    # also configure transformer and parameter names
    expander_info()


def expander_info():
    """
        Return information for this expander
    """
    global NAME, THRESHOLD, DIRECTION, CORRELATED_VALUES

    with open("transformer_info.json",'r') as f:
        info = TransformerInfo.from_dict(json.loads(f.read()))
        NAME = info.name
        THRESHOLD = info.parameters[0].name
        DIRECTION = info.parameters[1].name
        CORRELATED_VALUES = info.parameters[2].name
        return info


def expand(query: TransformerQuery):
    """
        Execute this expander, find all genes correlated to query genes.
    """
    controls = {control.name:control.value for control in query.controls}
    try:
        direction = controls[DIRECTION]
        threshold = float(controls[THRESHOLD])
        if controls[CORRELATED_VALUES] == 'gene knockout':
            gene_list = []
            genes = {}
            for gene in query.genes:
                gene_id = 'NCBIGene:'+entrez_gene_id(gene) if entrez_gene_id(gene) != None else gene.gene_id
                gene.attributes.append(
                    Attribute(
                        name = 'gene-knockout correlation with '+gene_symbol(gene),
                        value = '1.0',
                        source = NAME
                        )
                    )
                gene_list.append(gene)
                genes[gene_id] = gene
            for gene in query.genes:
                expand_gene_knockout(gene, direction, threshold, gene_list, genes)
            return gene_list
        else:
            msg = "invalid correlated values: '"+controls['correlated values']+"'"
            return ({ "status": 400, "title": "Bad Request", "detail": msg, "type": "about:blank" }, 400 )
    except ValueError:
        msg = "invalid correlation threshold: '"+controls['correlation threshold']+"'"
        return ({ "status": 400, "title": "Bad Request", "detail": msg, "type": "about:blank" }, 400 )





def expand_gene_knockout(query_gene: GeneInfo, direction: str, threshold: float, gene_list: List[GeneInfo], genes: dict):
    """
        Add genes with gene-knockout correlation to query gene above the threshold
    """
    gene_id = entrez_gene_id(query_gene)
    if gene_id is not None:
        correlations = requests.get(CORR_URL+gene_id).json()
        for correlation in correlations:
            if above_threshold(direction, correlation['correlation'], threshold):
                gene = get_gene(correlation['entrez_gene_id_2'], gene_list, genes)
                add_correlation(gene, correlation, gene_symbol(query_gene))


def above_threshold(direction: str, correlation_value: float, threshold: float):
    """
        Compare correlation values with a threshold
    """
    if direction == 'correlation':
        return correlation_value > threshold
    if direction == 'anti-correlation':
        return correlation_value < threshold
    if direction == 'both':
        return abs(correlation_value) > abs(threshold)
    return correlation_value > threshold


def get_gene(entrez_gene_id: str, gene_list: List[GeneInfo], genes: dict):
    """
        Find GeneInfo with a given entrez gene id or create a new GeneInfo
    """
    gene_id = 'NCBIGene:'+str(entrez_gene_id)
    if gene_id in genes:
        return genes[gene_id]
    gene = GeneInfo(gene_id = gene_id,
                    attributes = [],
                    identifiers = GeneInfoIdentifiers(entrez = gene_id)
                   )
    gene_list.append(gene)
    genes[gene_id] = gene
    return gene


def add_correlation(gene: GeneInfo, correlation: dict, symbol: str):
    """
        Add correlation information to a GeneInfo
    """
    gene.attributes.append(
        Attribute(
            name = 'gene-knockout correlation with '+symbol,
            value = str(correlation['correlation']),
            source = NAME
        )
    )


def entrez_gene_id(gene: GeneInfo):
    """
        Return value of the entrez_gene_id attribute
    """
    if (gene.identifiers is not None and gene.identifiers.entrez is not None):
        if (gene.identifiers.entrez.startswith('NCBIGene:')):
            return gene.identifiers.entrez[9:]
        else:
            return gene.identifiers.entrez
    return None


def gene_symbol(gene: GeneInfo):
    """
        Return value of the gene_symbol attribute
    """
    for attr in gene.attributes:
        if attr.name == 'gene_symbol':
            return attr.value
    return 'query gene'


# configure transformer
configure()
