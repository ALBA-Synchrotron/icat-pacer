import os
from time import sleep

from helpers.integrations.icat.extended_client import ICATClient

ICAT_SERVER_URL: str = os.getenv("ICAT_SERVER_URL", "")
ICAT_SERVER_AUTH_METHOD: str = os.getenv("ICAT_SERVER_AUTH_METHOD", "db")
ICAT_SERVER_USERNAME: str = os.getenv("ICAT_SERVER_USERNAME", "")
ICAT_SERVER_PASSWORD: str = os.getenv("ICAT_SERVER_PASSWORD", "")

INVESTIGATION_NAMES: list[str] = ['20250330138',
                                  '20250370028',
                                  '20250370093',
                                  '20250370101',
                                  '20250370149',
                                  '20250370155',
                                  '20250370181',
                                  '20250370250',
                                  '20250370287',
                                  '20250370289',
                                  '20250370339',
                                  '20250370341',
                                  '20250370342',
                                  '20250370404',
                                  '20250370421',
                                  '20250370458',
                                  '20250370468',
                                  '20250370472',
                                  '20250370474',
                                  '20250370499',
                                  '20250370519',
                                  '20260380023',
                                  '20260380029',
                                  '20260380030',
                                  '20260380031',
                                  '20260380058',
                                  '20260380062',
                                  '20260380117',
                                  '20260380151',
                                  '20260380167',
                                  '20260380184',
                                  '20260400010',
                                  '20260400113',
                                  '20260400164',
                                  '20260400177',
                                  '20260400205',
                                  '20260400334',
                                  '20260400347',
                                  '20260400415',
                                  '20260400433',
                                  '20260400482',
                                  '20260400484',
                                  '20260400515']

def clear_investigation_data(client: ICATClient, investigation) -> None:
    try:
        for i in investigation.datasets:
            client.delete(i)

        for i in investigation.samples:
            client.delete(i)

        for i in investigation.parameters:
            if i.type.name in ('__volume', '__fileCount', '__sampleCount', '__datasetCount', '__acquisitionVolume',
                               '__acquisitionFileCount', '__acquisitionDatasetCount', '__processedDatasetCount',
                               '__processedFileCount', '__processedVolume'):
                i.stringValue = "0"
                i.numericValue = 0
                getattr(i, "investigation")
                i.update()

        investigation.fileCount = 0
        investigation.fileSize = 0
        getattr(investigation, "facility")
        getattr(investigation, "type")
        client.update(investigation)

        sleep(10)
    except:
        print(f"Error emptying investigation name={investigation.name}")

if __name__ == "__main__":
    client: ICATClient = ICATClient(url=ICAT_SERVER_URL, auth_plugin=ICAT_SERVER_AUTH_METHOD,
                                    username=ICAT_SERVER_USERNAME, password=ICAT_SERVER_PASSWORD)

    print(f"Total of {len(INVESTIGATION_NAMES)} investigations to empty")

    for index, investigation_name in enumerate(INVESTIGATION_NAMES):
        print(f"Emptying investigation {index+1}/{len(INVESTIGATION_NAMES)}: {investigation_name}")
        investigation = client.search("Investigation", conditions={"name__eq": investigation_name})

        if investigation:
            if isinstance(investigation, list):
                for i in investigation:
                    clear_investigation_data(client, i)
            else:
                clear_investigation_data(client, investigation)



