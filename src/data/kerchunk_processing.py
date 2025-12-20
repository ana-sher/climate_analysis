import hashlib
import json
import os
from pathlib import Path

import earthaccess
import fsspec
from earthaccess import DataGranule
from fsspec import AbstractFileSystem


def lambda_handler(event, context):
    bucket = os.environ.get('S3_BUCKET')
    if not bucket:
        raise ValueError("Missing required environment variable S3_BUCKET")
    collection_short_name = event.get("collection")
    if not collection_short_name:
        raise ValueError("Missing required event parameter collection")

    try:
        create_kerchunk_for_collection(collection_short_name, bucket, **event.get("search_filters", {}))
    except Exception as e:
        return {"statusCode": 500, "message": str(e)}

    return {
        "statusCode": 200,
        "message": f"Created kerchunk ref file for collection {collection_short_name}"
    }


def create_kerchunk_for_collection(collection_short_name: str, bucket: str, **search_kwargs) -> None:
    earthaccess.login()
    results = earthaccess.search_data(
        short_name=collection_short_name,
        **search_kwargs
    )

    create_kerchunk_ref(search_kwargs, results, bucket)


def create_kerchunk_ref(search_kwargs: dict, results: list[DataGranule], bucket: str,
                        local_pat_root: Path = None) -> dict:
    if not results:
        return {}
    outfile = f"s3://{bucket}/kerchunk_refs/{results[0]['meta']['collection-concept-id']}/{_dict_hash(search_kwargs)}.json"
    kerchunk_local_dir = local_pat_root / "kerchunk_refs" if local_pat_root else Path("/kerchunk_refs")
    fs: AbstractFileSystem = fsspec.filesystem("s3")
    file_exist = fs.exists(outfile)

    kerchunk_refs_out = {}

    if not file_exist:
        earthaccess.open_virtual_mfdataset(results, access="indirect", concat_dim="sounding_id",
                                           coords="minimal", compat="override", combine_attrs="override",
                                           reference_dir=kerchunk_local_dir)
        with open(kerchunk_local_dir / Path(f"{results[0]['meta']['collection-concept-id']}-root.json"), "r") as f:
            kerchunk_refs_out = json.load(f)

        with fs.open(outfile, "w") as f:
            json.dump(kerchunk_refs_out, f)
    else:
        with fs.open(outfile, "r") as f:
            kerchunk_refs_out = json.load(f)
    return kerchunk_refs_out


def _dict_hash(dictionary: dict[str, any]) -> str:
    """MD5 hash of a dictionary."""
    dhash = hashlib.md5()
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()
