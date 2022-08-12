from typing import Dict

from singer import get_logger, metrics, write_record

from .abstracts import FullTableStream, UrlEndpointMixin

LOGGER = get_logger()
from typing import Dict, List, Tuple

from ..helpers import ApiSpec


class Unsubscribers(FullTableStream, UrlEndpointMixin):
    """
    class for products stream
    """

    stream = "unsubscribers"
    tap_stream_id = "unsubscribers"
    key_properties = [
        "id",
    ]
    api_auth_version = ApiSpec.API_V1
    url_endpoint = "https://api.yotpo.com/apps/APP_KEY/unsubscribers"

    def get_records(self):
        extraction_url = self.get_url_endpoint()
        params = ({"page": 1, "count": 1000},)
        while True:
            response = self.client.get(extraction_url, params, {}, self.api_auth_version)
            raw_records = response.get("response", {}).get(self.stream, [])
            if not raw_records:
                break
            params["page"] += 1
            yield from raw_records

    def sync(self, state: Dict, schema: Dict, stream_metadata: Dict, transformer) -> Dict:
        """
        Sync implementation for `unsubscribers` stream
        """
        with metrics.record_counter(self.tap_stream_id) as counter:
            for record in self.get_records():
                transformed_record = transformer.transform(record, schema, stream_metadata)
                write_record(self.tap_stream_id, transformed_record)
                counter.increment()
        return state
