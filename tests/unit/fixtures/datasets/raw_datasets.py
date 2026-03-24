import os
import random
import re
import shutil
import tempfile
from pathlib import Path
import xml.etree.ElementTree as ET
import pytest


@pytest.fixture
def json_dataset_non_existent_instrument():
    return {
        "investigation": "2022097034-non-existent",
        "instrument": "bl9999",
        "name": "mxau_241222",
        "parameters": [
            {
                "name": "parameter_1",
                "value": "872,312"
            }
        ],
        "location": "/data/bl13/",
        "start_date": "2019-08-08T15:57:45.920+02:00",
        "end_date": "2021-05-30T15:19:08.422+02:00",
        "sample": {
            "name": "SAMPLE 1"
        },
        "datafiles": [
            {
                "location": "/data/bl13/2022097034/mxau_241222.nxs",
                "size": 942040
            }
        ]
    }


@pytest.fixture()
def xml_dataset_non_existent_instrument():
    return """
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <dataset>
            <investigation>2022097034-non-existent</investigation>
            <instrument>bl9999</instrument>
            <name>mxau_241222</name>
            <parameter>
                    <name>InstrumentXraylens09_lens_material</name>
                    <value> value 1</value>
            </parameter>
            <location>/data/bl13/</location>
            <startDate>2019-08-08T15:57:45.920+02:00</startDate>
            <endDate>2021-05-30T15:19:08.422+02:00</endDate>
            <sample>
                <name>SAMPLE 1</name>
            </sample>
            <datafile>
                <location>/data/bl13/2022097034/mxau_241222.nxs</location>
                <size>942040</size>
            </datafile>
        </dataset>
        """


@pytest.fixture
def json_dataset_non_existent_investigation():
    return {
        "investigation": "2022097034-non-existent",
        "instrument": "bl13",
        "name": "mxau_241222",
        "parameters": [
            {
                "name": "parameter_1",
                "value": "872,312"
            }
        ],
        "location": "/data/bl13/",
        "start_date": "2019-08-08T15:57:45.920+02:00",
        "end_date": "2021-05-30T15:19:08.422+02:00",
        "sample": {
            "name": "SAMPLE 1"
        },
        "datafiles": [
            {
                "location": "/data/bl13/2022097034/mxau_241222.nxs",
                "size": 942040
            }
        ]
    }


@pytest.fixture()
def xml_dataset_non_existent_investigation():
    return """
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <dataset>
            <investigation>2022097034-non-existent</investigation>
            <instrument>bl13</instrument>
            <name>mxau_241222</name>
            <parameter>
                    <name>InstrumentXraylens09_lens_material</name>
                    <value> value 1</value>
            </parameter>
            <location>/data/bl13/</location>
            <startDate>2019-08-08T15:57:45.920+02:00</startDate>
            <endDate>2021-05-30T15:19:08.422+02:00</endDate>
            <sample>
                <name>SAMPLE 1</name>
            </sample>
            <datafile>
                <location>/data/bl13/2022097034/mxau_241222.nxs</location>
                <size>942040</size>
            </datafile>
        </dataset>
        """


@pytest.fixture()
def ingestion_files_for_testing():
    created_files: dict = {}

    with tempfile.TemporaryDirectory(prefix="dataset_unittest_") as tmp:
        dataset_location = Path(tmp)

        for i in range(10):
            size = random.randint(1024, 100 * 1024)
            file = dataset_location / f"file_{i}.dat"

            file.write_bytes(os.urandom(size))
            created_files[file] = size

        for i in range(10):
            size = random.randint(1024, 100 * 1024)
            file = dataset_location / f"extra_file_{i}.dat"

            file.write_bytes(os.urandom(size))

        gallery_folder = dataset_location / "gallery"
        gallery_folder.mkdir(exist_ok=True)

        assets_folder = Path(__file__).resolve().parents[1] / "assets"
        for img in ["image1.png", "image2.png", "image3.png"]:
            shutil.copy(assets_folder / img, gallery_folder / img)

        yield dataset_location, created_files


@pytest.fixture
def json_raw_dataset(ingestion_files_for_testing, test_investigation, test_parameter_types, random_str):
    dataset_location, created_files = ingestion_files_for_testing
    return {
        "investigation": test_investigation.name,
        "instrument": test_investigation.investigationInstruments[0].instrument.name,
        "name": f"mxau_241222_json_{random_str()}",
        "parameters": [
            {
                "name": f"{v.name}",
                "value": f"value_{i}"
            } for i, v in enumerate(test_parameter_types)
        ],
        "location": str(dataset_location),
        "start_date": "2025-09-23T10:00:45.920+02:00",
        "end_date": "2025-09-23T10:19:08.422+02:00",
        "sample": {
            "name": "SAMPLE 1"
        },
        "datafiles": [
            {
                "location": str(i),
                "size": created_files[i]
            } for i in created_files
        ]
    }


@pytest.fixture()
def xml_raw_dataset(ingestion_files_for_testing, test_investigation, test_parameter_types, random_str):
    dataset_location, created_files = ingestion_files_for_testing
    datafile_elements = "\n".join(
        f"""
        <datafile>
            <location>{str(i)}</location>
            <size>{created_files[i]}</size>
        </datafile>
        """ for i in created_files
    )
    parameter_elements = "\n".join(f"""
                <parameter>
                    <name>{v.name}</name>
                    <value>value_{i}</value>
                </parameter>""" for i, v in enumerate(test_parameter_types))
    return f"""
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <dataset>
            <investigation>{test_investigation.name}</investigation>
            <instrument>{test_investigation.investigationInstruments[0].instrument.name}</instrument>
            <name>mxau_241222_xml_{random_str()}</name>
            {parameter_elements}
            <location>{str(dataset_location)}</location>
            <startDate>2025-09-23T10:00:45.920+02:00</startDate>
            <endDate>2025-09-23T10:19:08.422+02:00</endDate>
            <sample> 
                <name>SAMPLE 1</name>
            </sample>
            {datafile_elements}
        </dataset>
        """


@pytest.fixture()
def xml_raw_dataset_investigation_instrument_mismatch(xml_raw_dataset, test_investigation, random_instrument_2):
    return xml_raw_dataset.replace(test_investigation.investigationInstruments[0].instrument.name,
                                   random_instrument_2.name)


@pytest.fixture()
def json_raw_dataset_investigation_instrument_mismatch(json_raw_dataset, random_instrument_2):
    json_raw_dataset["instrument"] = random_instrument_2.name
    return json_raw_dataset


@pytest.fixture()
def xml_raw_dataset_investigation_overlapping_sessions(xml_raw_dataset, test_investigation_overlapping_1,
                                                       test_investigation_overlapping_2):
    new_investigation = f"<investigation>{test_investigation_overlapping_1.name}</investigation>"
    ret = re.sub(r"<investigation>.*?</investigation>", new_investigation, xml_raw_dataset, flags=re.DOTALL)
    return ret


@pytest.fixture()
def json_raw_dataset_investigation_overlapping_sessions(json_raw_dataset, test_investigation_overlapping_1,
                                                        test_investigation_overlapping_2):
    json_raw_dataset["investigation"] = test_investigation_overlapping_1.name
    return json_raw_dataset


@pytest.fixture()
def xml_raw_dataset_investigation_instrument_mismatch_investigation_id(xml_raw_dataset, test_investigation,
                                                                       random_instrument_2):
    ret = xml_raw_dataset.replace(test_investigation.investigationInstruments[0].instrument.name,
                                  random_instrument_2.name)
    new_investigation_id = f"<investigationId>{test_investigation.id}</investigationId><investigation>{test_investigation.name}</investigation>"
    new_name = f"xml_dataset_instr_mistmatch_but_investigation_id"
    ret = re.sub(r"<investigation>.*?</investigation>", new_investigation_id, ret, flags=re.DOTALL)

    root = ET.fromstring(ret.strip())

    for parent in root.iter():
        if parent.tag != "parameter":
            for name in parent.findall("name"):
                name.text = new_name

    return ET.tostring(root, encoding="unicode")


@pytest.fixture()
def json_raw_dataset_investigation_instrument_mismatch_investigation_id(json_raw_dataset, random_instrument_2,
                                                                        test_investigation):
    json_raw_dataset["instrument"] = random_instrument_2.name
    json_raw_dataset["investigation_id"] = test_investigation.id
    json_raw_dataset["name"] = f"{json_raw_dataset["name"]}_with_investigation_id"
    return json_raw_dataset


@pytest.fixture()
def xml_raw_dataset_invalid_sample_type(xml_raw_dataset):
    new_sample = "<sample><name>sample 1</name><type>completely_invalid_type</type></sample>"
    xml_string = re.sub(r"<sample>.*?</sample>", new_sample, xml_raw_dataset, flags=re.DOTALL)
    return xml_string


@pytest.fixture()
def json_raw_dataset_invalid_sample_type(json_raw_dataset):
    json_raw_dataset["sample"]["type"] = "completely_invalid_type"
    return json_raw_dataset
