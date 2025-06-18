import xml.etree.ElementTree as ET
from xml.dom import minidom

from kombu.serialization import register


# Encoder: Converts a Python object (e.g., a dictionary) to an XML string
def xml_encoder(data):
    """
    Encodes a Python dictionary into an XML string.
    This is a basic example; you'll likely need to adapt it
    to your specific XML structure.
    """
    if not isinstance(data, dict):
        raise TypeError("XML encoder expects a dictionary as input.")

    # Create the root element
    root = ET.Element(data.get('root_tag', 'message'))

    # Add attributes to the root (example)
    if 'attributes' in data:
        for key, value in data['attributes'].items():
            root.set(key, str(value))

    # Add child elements based on dictionary keys
    for key, value in data.items():
        if key not in ['root_tag', 'attributes']:  # Skip special keys
            element = ET.SubElement(root, key)
            if isinstance(value, dict):
                # Handle nested dictionaries (recursive call or specific logic)
                for sub_key, sub_value in value.items():
                    sub_element = ET.SubElement(element, sub_key)
                    sub_element.text = str(sub_value)
            elif isinstance(value, list):
                # Handle lists by creating multiple elements
                for item in value:
                    item_element = ET.SubElement(element, 'item')
                    if isinstance(item, dict):
                        for sub_key, sub_value in item.items():
                            sub_sub_element = ET.SubElement(item_element, sub_key)
                            sub_sub_element.text = str(sub_value)
                    else:
                        item_element.text = str(item)
            else:
                element.text = str(value)

    # Convert the ElementTree to a string
    xml_string = ET.tostring(root, encoding='utf-8', xml_declaration=True).decode('utf-8')

    # Optional: Pretty print for better readability (remove in production for performance)
    try:
        dom = minidom.parseString(xml_string)
        xml_string = dom.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")
    except Exception as e:
        print(f"Warning: Could not pretty print XML: {e}")

    return xml_string


# Decoder: Converts an XML string to a Python object (e.g., a dictionary)
def xml_decoder(data):
    """
    Decodes an XML string into a Python dictionary.
    This is a basic example; you'll likely need to adapt it
    to your specific XML structure.
    """

    if not isinstance(data, (str, bytes)):
        raise TypeError("XML decoder expects a string or bytes as input.")

    if isinstance(data, bytes):
        data = data.decode('utf-8')

    root = ET.fromstring(data)

    # Extract root tag and attributes
    result = {
        'root_tag': root.tag,
        'attributes': root.attrib
    }

    # Extract child elements
    for child in root:
        if len(child) > 0:  # Has nested children
            nested_data = {}
            for sub_child in child:
                nested_data[sub_child.tag] = sub_child.text
            if child.tag in result.keys():
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(nested_data)
            else:
                result[child.tag] = nested_data
        else:  # Simple text content
            result[child.tag] = child.text

    return result


def register_xml() -> None:
    """
    Note: The decoding output of this serializer can be found in message.payload.
    """
    register(
        'xml',
        xml_encoder,
        xml_decoder,
        content_type='application/xml',
        content_encoding='utf-8'
    )
    print("XML serializer 'xml' registered with Kombu.")
