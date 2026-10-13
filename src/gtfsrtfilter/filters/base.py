"""Common interface for GTFS-Realtime entity filters."""
from abc import ABC, abstractmethod
from google.transit import gtfs_realtime_pb2

class EntityFilter(ABC):
    @abstractmethod
    def apply(self, feed: gtfs_realtime_pb2.FeedMessage) -> None:
        """Modify the feed in place, removing unmatched entities."""
