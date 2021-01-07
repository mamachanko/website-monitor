
# website availability monitor

## backlog

[ ] integration test

### website checker
[ ] check periodically
[ ] check for http status code
[ ] check for response time
[ ] publish check result
[ ] publish check result to Kafka topic
[ ] stretch: check for regex

### database writer
[ ] consume topic
[ ] consume topic to db

### tooling
[ ] provision instances through script
[ ] provision databases and schemas
[ ] provision topics
[ ] packaging
[ ] monitor stats tool (TAOP histogram)
[ ] query performance   

### documentation
[ ] README
[ ] reasoning
[ ] references
     * https://help.aiven.io/en/articles/489572-getting-started-with-aiven-kafka

## TODOs
[ ] separate requirements files
[ ]Aiven CLI to provision
 * Kafka instance
 * Postgres instance
[ ] test-containers for tests?

## notes for discussion
testcontainers
schema
assume databases and schema exist / are manager elsewhere
ACL
timeouts
logging
