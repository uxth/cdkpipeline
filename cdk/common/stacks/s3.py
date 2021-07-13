import re

from aws_cdk import aws_s3 as _s3
from aws_cdk import core

from utils.configBuilder import Config


class S3Stack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, config: Config,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        def s3_bucket_name_validator(name: str) -> bool:
            # https://docs.aws.amazon.com/AmazonS3/latest/userguide/BucketRestrictions.html
            pattern = '^([a-z0-9][a-z0-9-]{1,61}[a-z0-9])$'
            success = re.match(pattern, name)
            return success

        self.s3_buckets = []
        for bucket in config.getValue('s3.buckets'):
            bucket_name = bucket['name']
            if s3_bucket_name_validator(bucket_name):
                bucket = _s3.Bucket(self,
                                    id=bucket_name,
                                    versioned=bucket['versioned'])

                self.s3_buckets.append(bucket)
            else:
                raise Exception("Illegal S3 bucket name {}.".format(bucket_name))
