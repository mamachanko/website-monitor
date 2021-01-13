from website_monitor import env
from website_monitor.streamtopic import StreamTopic


class TestStreamTopic:
    def test_consumes_messages_published_to_topic(self, stream_topic: StreamTopic):
        stream_topic.publish("test message 1")
        stream_topic.publish("test message 2")

        (records, commit) = stream_topic.consume(
            group_id=env.require_env("WM_STREAM_CONSUMER_GROUP_ID")
        )
        commit()

        assert records == ["test message 1", "test message 2"]

    def test_consumes_nothing_when_topic_is_exhausted(self, stream_topic: StreamTopic):
        (records, commit) = stream_topic.consume(
            group_id=env.require_env("WM_STREAM_CONSUMER_GROUP_ID")
        )
        commit()

        assert records == []
