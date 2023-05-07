import datetime
import re
from google.cloud import storage
from google.oauth2 import service_account
from great_expectations.render.renderer import SlackRenderer

def generate_download_signed_url_v4(bucket_name, blob_name):
    """Generates a v4 signed URL for downloading a blob.

    Note that this method requires a service account key file. You can not use
    this if you are using Application Default Credentials from Google Compute
    Engine or from the Google Cloud SDK.
    """
    # bucket_name = 'your-bucket-name'
    # blob_name = 'your-object-name'
    credentials = service_account.Credentials.from_service_account_file('/Users/olusegun/Vendease/product_cleanup/gscript/deep-contact-361614-7b0b5fdd8c5d.json')
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(minutes=30),
        # Allow GET requests using this URL.
        method="GET",
    )
    return url


class CustomSlackRenderer(SlackRenderer):
    def _get_report_element(self, docs_link: str):
        # docs link to local site unchanged
        if not docs_link.startswith("https://storage.googleapis.com"):
            return super()._get_report_element(docs_link)
        
        pattern = re.compile(r"^https:\/\/(?:storage\.cloud\.google\.com|storage\.googleapis\.com)\/(?P<bucket_name>[^\/]*)\/(?P<object_name>.*)")
        match = pattern.match(docs_link)
        bucket_name = match.group('bucket_name')
        object_name = match.group('object_name')
        # generate presigned url

        presigned_url = generate_download_signed_url_v4(bucket_name,object_name)
        return super()._get_report_element(presigned_url)

