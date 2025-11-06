# services/storage/s3.py
import boto3
from typing import Optional, Dict, Tuple
from core.config import settings

class S3Storage:
    def __init__(self):
        self.client = boto3.client("s3", region_name=settings.aws_region)
        self.bucket = settings.aws_s3_bucket

    def presign_upload(self, key: str, content_type: Optional[str], expires: int) -> Tuple[str, Dict]:
        fields = {}
        conditions = []
        if content_type:
            fields["Content-Type"] = content_type
            conditions.append({"Content-Type": content_type})
        resp = self.client.generate_presigned_post(
            Bucket=self.bucket,
            Key=key,
            Fields=fields,
            Conditions=conditions,
            ExpiresIn=expires,
        )
        return resp["url"], resp["fields"]

    def presign_download(self, key: str, expires: int) -> str:
        return self.client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires,
        )

    def delete_object(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)