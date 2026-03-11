import pytest


@pytest.fixture()
def xml_message_missing_investigation():
    return """
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <dataset>
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
def xml_message_missing_instrument():
    return """
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <dataset>
            <investigation>2022097034</investigation>
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
def xml_message_missing_name():
    return """
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <dataset>
            <investigation>2022097034</investigation>
            <instrument>bl13</instrument>
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
def xml_message_missing_location():
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
def xml_message_missing_start_date():
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
def xml_message_missing_end_date():
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
def xml_message_missing_param_value():
    return """
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <dataset>
            <investigation>2022097034</investigation>
            <instrument>bl13</instrument>
            <name>mxau_241222</name>
            <parameter>
                    <name>InstrumentXraylens09_lens_material</name>
                    <value></value>
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
def xml_message_missing_param_name():
    return """
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <dataset>
            <investigation>2022097034</investigation>
            <instrument>bl13</instrument>
            <name>mxau_241222</name>
            <parameter>
                    <name></name>
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
def xml_message_empty_datafile_location():
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
                <location></location>
                <size>942040</size>
            </datafile>
        </dataset>
        """

@pytest.fixture()
def xml_message_empty_sample_name():
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
                <name></name>
                <type>Test Sample</type>
            </sample>
            <datafile>
                <location>asd</location>
                <size>942040</size>
            </datafile>
        </dataset>
        """

@pytest.fixture()
def xml_message_too_many_datafiles():
    return f"""
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
            {'''
            <datafile>
                <location>/data/bl13/2022097034/mxau_241222.nxs</location>
                <size>942040</size>
            </datafile>'''*30002}
        </dataset>
        """

@pytest.fixture()
def xml_message_duplicate_parameters():
    return f"""
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <dataset>
            <investigation>2022097034</investigation>
            <instrument>bl13</instrument>
            <name>mxau_241222</name>
            <parameter>
                    <name>InstrumentXraylens09_lens_material</name>
                    <value> value 1</value>
            </parameter>
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