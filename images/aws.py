import boto3
from django.conf import settings

s3_client = boto3.client("s3")


def generate_thumbnail_url(resource, thumbnail_height):
    """Invoke AWS Lambda for thumbnail generation of an image stored in S3 Bucket and retrieve resource URL.

    Args:
        resource (str): path for a resource in S3 Bucket
        thumbnail_height (int): height of the thumbnail

    Returns:
        str: URL for the generated thumbnail
    """
    resource_key = f"{resource}@{thumbnail_height}"
    params = {
        "Bucket": settings.AWS_THUMBNAIL_ACCESS_POINT_ARN,
        "Key": resource_key,
    }

    return s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params=params,
    )
