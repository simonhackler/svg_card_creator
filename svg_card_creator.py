import os
import yaml
import shutil
import xml.etree.ElementTree as ET
import subprocess


def get_all_yaml_files_dir_and_subdirs(dir_path):
    yaml_files_dir_and_subdirs = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".yaml"):
                yaml_files_dir_and_subdirs.append(os.path.join(root, file))
    return yaml_files_dir_and_subdirs

def create_cards_from_yaml_files(data_parent_dir, card_model, destination_path, get_template_path_from_card):
    check_if_folder_exists_and_create_if_not(folder_path=destination_path+"/cards")
    yaml_files_dir_and_subdirs = get_all_yaml_files_dir_and_subdirs(data_parent_dir)
    card_data_and_image = []
    for yaml_file in yaml_files_dir_and_subdirs:
        card_data_and_image.append(create_cards_from_yaml_file(yaml_file, card_model, destination_path, get_template_path_from_card))
    return card_data_and_image

def create_cards_from_yaml_file(yaml_file, card_model, destination_path, get_template_path_from_card):
    card_data_and_image = []
    with open(yaml_file, 'r') as stream:
        try:
            #data = yaml.safe_load(stream)
            data = yaml.full_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
        if data is not None:
            for card in data:
                card_data_and_image.append(create_card_data_and_image(card, card_model, destination_path, get_template_path_from_card))
    return card_data_and_image

def check_if_folder_exists_and_create_if_not(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def create_card_data_and_image(card, card_model, destination_path, get_template_path_from_card):
    if "CardType" not in card:
        print(card["Name"])
        return None
    print(card["Name"] + " is being generated")
    destination_path_card_type = destination_path + "/cards/" + card["CardType"]
    check_if_folder_exists_and_create_if_not(destination_path_card_type) 

    filename = destination_path_card_type + "/" + card["Name"]
    filenamePNG = filename + ".png"
    filenameSVG = filename + ".svg"
    template_path = get_template_path_from_card(card)
    template_path = os.path.abspath(path=template_path)
    shutil.copyfile(template_path, filenameSVG)

    tree = ET.parse(filenameSVG)
    change_svg_to_data(tree, card, card_model)
    tree.write(filenameSVG)

    subprocess.check_output(['inkscape', filenameSVG, '-o', filenamePNG])
    if "AmountInDeck" in card:
        for i in range(2, card["AmountInDeck"] + 1):
            filenameCopy = filename + "_" + str(i) + ".png"
            subprocess.check_output(['cp', filenamePNG, filenameCopy])
    return (card, filenamePNG)

def change_svg_to_data(tree, card, card_model):
    root = tree.getroot()
    for element in root.iter():
        if "id" in element.attrib:
            for card_id in card_model[card["CardType"]].keys():
                if element.attrib["id"] == card_id:
                    card_model[card["CardType"]][card_id](element, card)


def createCardsFromFile(yaml_path, destination_path, changeSvg, return_template):
    images = []
    yaml_path = os.path.abspath(yaml_path)
    destination_path = os.path.abspath(destination_path)+ "/"
    with open(yaml_path) as file:
        yaml_data = yaml.full_load(file)
        for card in yaml_data:
            filename =  destination_path + card['Name']
            filenamePNG = filename + ".png"
            filenameSVG = filename + ".svg"
            images.append(filenamePNG)

            template_path = return_template(card)
            template_path = os.path.abspath(template_path)
            shutil.copyfile(template_path, filenameSVG)

            tree = ET.parse(filenameSVG)

            changeSvg(tree, card)
            tree.write(filenameSVG)
            subprocess.check_output(['inkscape', filenameSVG, '-o', filenamePNG])
            if "AmountInDeck" in card:
                for i in range(2, card["AmountInDeck"] + 1):
                    filenameCopy = filename + "_" + str(i) + ".png"
                    subprocess.check_output(['cp', filenamePNG, filenameCopy])
                    images.append(filenameCopy)
        return images

def createGrid(images, filename):
    for i in range(len(images) // 10 + 1):
        x = i * 10
        if len(images[x:x+10]) <= 0:
            continue
        subprocess.check_output(['convert'] + images[x:x+10]  + ['+append', './tts/grid-' + filename + str(i) + '.png'])
    subprocess.check_output(['touch'] + ['./tts/' + filename + '-full-grid.png'])
    subprocess.check_output(['rm'] + ['./tts/' + filename + '-full-grid.png'])
    subprocess.check_output(['convert', './tts/*' + filename + '*.png',  '-append', './tts/' + filename + '-full-grid.png'])
    for i in range(len(images) // 10 + 1):
        x = i * 10
        if len(images[x:x+10]) <= 0:
            continue
        subprocess.check_output(['rm'] + ['./tts/grid-' + filename + str(i) + '.png'])

def add_svg_text_element_bold(parent, text):
    element = ET.SubElement(parent, 'text')
    element.set('style', 'font-weight: bold;')
    element.text = text
