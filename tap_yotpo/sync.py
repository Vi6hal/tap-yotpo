"""tap-yotpo sync."""
import singer

from . import streams

LOGGER = singer.get_logger()


def sync(client, catalog: singer.Catalog, state):
    """performs sync for selected streams."""
    with singer.Transformer() as transformer:
        for stream in catalog.get_selected_streams(state):
            tap_stream_id = stream.tap_stream_id
            stream_schema = stream.schema.to_dict()
            stream_metadata = singer.metadata.to_map(stream.metadata)
            stream_obj = streams.STREAMS[tap_stream_id](client)
            LOGGER.info("Starting sync for stream: %s", tap_stream_id)
            state = singer.set_currently_syncing(state, tap_stream_id)
            singer.write_state(state)
            singer.write_schema(tap_stream_id, stream_schema, stream_obj.key_properties, stream.replication_key)
            state = stream_obj.sync(
                state=state, schema=stream_schema, stream_metadata=stream_metadata, transformer=transformer
            )
            singer.write_state(state)

    state = singer.set_currently_syncing(state, None)
    singer.write_state(state)
