from libs.job_templates.mongo import MongoAggregatorJob
from libs.utils.common import parse_conf
from libs.program_args.base import args_parser

if __name__ == "__main__":
    args = args_parser.parse_args()

    job = MongoAggregatorJob(
        bootstrap_servers=args.bootstrap_servers,
        topic=args.topic,
        batch_interval=args.batch_interval,
        checkpoint_dir=args.checkpoint_dir,
        sql_file=args.sql_file,
        json_fields_map=parse_conf(args.json_fields_map),
        spark_conf=parse_conf(args.spark_conf),
        kafka_conf=parse_conf(args.kafka_conf),
        writer_conf=parse_conf(args.writer_conf),
        write_method=args.write_method,
        allow_late_for=args.allow_late_for
    )
    job.run()
