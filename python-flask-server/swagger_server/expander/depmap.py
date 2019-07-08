
from swagger_server.models.transformer_info import TransformerInfo
from swagger_server.models.transformer_info import Parameter

def expander_info():
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

