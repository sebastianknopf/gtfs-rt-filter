"""GTFS-RT Protocol Buffers and canonical protobuf JSON serialization."""
from google.protobuf.json_format import MessageToJson
from google.transit import gtfs_realtime_pb2

def decode(payload: bytes) -> gtfs_realtime_pb2.FeedMessage:
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(payload)
    if not feed.IsInitialized():
        raise ValueError("Upstream feed is missing required GTFS-RT fields")
    return feed

def encode(feed: gtfs_realtime_pb2.FeedMessage, json_output: bool) -> bytes:
    if json_output:
        return (MessageToJson(feed, indent=2, preserving_proto_field_name=False) + "\n").encode("utf-8")
    return feed.SerializeToString()
