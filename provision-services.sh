avn service create stream --service-type kafka --plan startup-2 --cloud google-europe-west3
avn service create database --service-type pg --plan hobbyist --cloud google-europe-west3
avn service list --format '{service_name}' | xargs -n1 avn service get --format '{state}'

avn service topic-create stream website_check --partitions 1 --replication 2
avn service topic-create stream website_check_test --partitions 1 --replication 2

