import pytest


@pytest.fixture()
def valid_xml_raw_dataset_payload():
    return """
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <dataset>
            <investigation>2022097034</investigation>
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
def valid_xml_raw_dataset_payload_sample_type():
    return """
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <dataset>
            <investigation>2022097034</investigation>
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
                <type>Test Sample</type>
            </sample>
            <datafile>
                <location>/data/bl13/2022097034/mxau_241222.nxs</location>
                <size>942040</size>
            </datafile>
        </dataset>
        """

@pytest.fixture()
def valid_xml_processed_dataset_payload():
    return """
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <dataset>
            <investigation>2022097034</investigation>
            <instrument>bl13</instrument>
            <name>mxau_241222</name>
            <parameter>
                    <name>input_datasets</name>
                    <value>872,312</value>
            </parameter>
            <location>/data/bl13/</location>
            <startDate>2019-08-08T15:57:45.920+02:00</startDate>
            <endDate>2021-05-30T15:19:08.422+02:00</endDate>
            <sample>
                <name>SAMPLE 1</name>
                <type>Test Sample</type>
            </sample>
            <datafile>
                <location>/data/bl13/2022097034/mxau_241222.nxs</location>
                <size>942040</size>
            </datafile>
        </dataset>
        """


@pytest.fixture()
def valid_xml_raw_dataset_investigation_id_payload():
    return """
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <dataset>
            <investigationId>8293</investigationId>
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
                <type>Test Sample</type>
            </sample>
            <datafile>
                <location>/data/bl13/2022097034/mxau_241222.nxs</location>
                <size>942040</size>
            </datafile>
        </dataset>
        """


@pytest.fixture()
def no_datafiles_xml_raw_dataset_payload():
    return """
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <dataset>
            <investigation>2022097034</investigation>
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
        </dataset>
        """


@pytest.fixture()
def valid_xml_raw_dataset_sketchy_datafile_location_payload():
    return """
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <dataset>
            <investigation>2022097034</investigation>
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
            <datafile>
                <location>/etc/paswd</location>
                <size>942040</size>
            </datafile>
            <datafile>
                <location>/tmp/../etc/paswd</location>
                <size>942040</size>
            </datafile>
        </dataset>
        """

@pytest.fixture()
def valid_xml_raw_dataset_sketchy_location_payload():
    return """
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <dataset>
            <investigation>2022097034</investigation>
            <instrument>bl13</instrument>
            <name>mxau_241222</name>
            <parameter>
                    <name>InstrumentXraylens09_lens_material</name>
                    <value> value 1</value>
            </parameter>
            <location>/tmp/../etc/</location>
            <startDate>2019-08-08T15:57:45.920+02:00</startDate>
            <endDate>2021-05-30T15:19:08.422+02:00</endDate>
            <sample>
                <name>SAMPLE 1</name>
            </sample>
        </dataset>
        """

