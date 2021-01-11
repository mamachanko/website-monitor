from website_monitor import probe_and_publish, consume_and_write
from website_monitor.repository import Repository
from website_monitor.streamtopic import StreamTopic


class TestIntegration:

    def test_probes_get_published_consumed_and_written(self, repository: Repository, stream_topic: StreamTopic):
        assert repository.get_stats() == []
        assert repository.find_all() == []

        probe_and_publish.main()
        probe_and_publish.main()

        consume_and_write.main()

        assert len(repository.find_all()) == 2
        assert len(repository.get_stats()) == 1