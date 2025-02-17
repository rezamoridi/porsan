from fastapi import APIRouter, File
from typing import Optional
from fastapi import UploadFile
from urllib.parse import quote
from dotenv import load_dotenv
import os, boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from typing import List, Optional


load_dotenv()

LIARA_ENDPOINT = os.getenv("LIARA_ENDPOINT")
LIARA_ACCESS_KEY = os.getenv("LIARA_ACCESS_KEY")
LIARA_SECRET_KEY = os.getenv("LIARA_SECRET_KEY")
LIARA_BUCKET_NAME = os.getenv("LIARA_BUCKET_NAME")

s3 = boto3.client(
    "s3",
    endpoint_url=LIARA_ENDPOINT,
    aws_access_key_id=LIARA_ACCESS_KEY,
    aws_secret_access_key=LIARA_SECRET_KEY,
)




class BucketObj_2:
    """Version2 support multiple image uploading. permalink works as attribute and returns links
    as a list"""

    def __init__(self, files: List[Optional[UploadFile]], save_names: List[str], destination: str, format_: str = "jpg") -> None:
        self.files = files
        self.save_names = save_names
        self.destination = destination
        self.format_ = format_
        self.perma_links = self.generate_perma_links()

    def upload_images(self) -> None:
        for file, save_name in zip(self.files, self.save_names):
            try:
                if not file:
                    raise ValueError(f"File for {save_name} is None")
                s3.upload_fileobj(
                    file.file,
                    LIARA_BUCKET_NAME,
                    f'{self.destination}/{save_name}.{self.format_}'
                )
            except (NoCredentialsError, PartialCredentialsError) as e:
                raise RuntimeError(f"Credential error for file {save_name}: {str(e)}")
            except ValueError as e:
                raise ValueError(f"Error with file {save_name}: {str(e)}")
            except Exception as e:
                raise RuntimeError(f"Failed to upload {save_name}: {str(e)}")

    def generate_perma_links(self) -> List[str]:
        links = []
        for save_name in self.save_names:
            obj_filename_encoded = quote(f'{self.destination}/{save_name}.{self.format_}')
            obj_perma_link = f"https://{LIARA_BUCKET_NAME}.{LIARA_ENDPOINT.replace('https://', '')}/{obj_filename_encoded}"
            links.append(obj_perma_link)
        print("Generated perma_links: ", links)  
        return links


