"""Pipeline Loader."""
from collections import OrderedDict

import yaml


# @staticmethod
def ordered_load(stream, loader=yaml.SafeLoader, object_pairs_hook=OrderedDict):
    """Load YAML, preserving the ordering of all data."""
    class OrderedLoader(loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)

    return yaml.load(stream, OrderedLoader)  # nosec
