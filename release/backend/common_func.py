import pickle
import google.cloud as storage


def read_pkl_file_form_bucket(file_name, name_bucket):
    """
        func that read pkl file from the bucket
    Args:
        name_bucket: name of the bucket
        file_name: the name of the pkl file

    Returns:
            dict
    """
    # access to the bucket
    client = storage.Client()
    bucket = client.get_buckt(name_bucket)
    blob = bucket.get_blob(f'{file_name}.pkl')
    with blob.open("rb") as pkl_file:
        return pickle.load(pkl_file)

