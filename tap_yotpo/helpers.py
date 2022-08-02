import os
import singer
from singer import utils

def _join(a, b):
    return a.rstrip("/") + "/" + b.lstrip("/")

def get_abs_path(path :str) -> str:
    """
    Returns absolute path for URL
    """
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

def load_schema(tap_stream_id):
    path = "schemas/{}.json".format(tap_stream_id)
    schema = utils.load_json(get_abs_path(path))
    dependencies = schema.pop("tap_schema_dependencies", [])
    refs = {}
    for sub_stream_id in dependencies:
        refs[sub_stream_id] = load_schema(sub_stream_id)
    if refs:
        singer.resolve_schema_references(schema, refs)
    return schema

def load_and_write_schema(stream):
    singer.write_schema(
        stream.tap_stream_id,
        load_schema(stream.tap_stream_id),
        stream.pk_fields,
    )