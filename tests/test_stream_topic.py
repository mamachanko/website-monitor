from website_monitor.streamtopic import StreamTopic


class TestStreamTopic:
    def test_consumes_messages_published_to_topic(self, stream_topic: StreamTopic):
        stream_topic.publish("test message 1")
        stream_topic.publish("test message 2")

        with stream_topic.consume(group_id="test-consumer") as records:
            assert records == ["test message 1", "test message 2"]

    def test_consumes_nothing_when_topic_is_exhausted(self, stream_topic: StreamTopic):
        with stream_topic.consume(group_id="test-consumer") as records:
            assert records == []

    def test_groups_are_isolated(self, stream_topic: StreamTopic):
        stream_topic.publish("test message 1")
        stream_topic.publish("test message 2")

        with stream_topic.consume(
            group_id="test group 1"
        ) as records_1, stream_topic.consume(group_id="test group 2") as records_2:
            assert records_1 == records_2 == ["test message 1", "test message 2"]
