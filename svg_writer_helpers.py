import os

def set_svg_element_text_to_property(property):
    return lambda element, card: set_svg_element_text(element, card[property])

def set_svg_element_text(element, text):
    element[0].text = text

def set_svg_element_image(element, card):
    if "TexturePath" in card:
        element.attrib["{http://www.w3.org/1999/xlink}href"] = os.path.abspath(card["TexturePath"])
    else:
        element.set("style", "display:none;")