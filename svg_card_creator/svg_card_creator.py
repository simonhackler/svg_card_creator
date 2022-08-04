import os
import yaml
import shutil
import xml.etree.ElementTree as ET
import subprocess

def hello():
    print("hello")

def createCardsFromFile(yaml_path, destination_path, changeSvg, returnTemplate):
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

            template_path = returnTemplate(card)
            template_path = os.path.abspath(template_path)
            shutil.copyfile(template_path, filenameSVG)

            tree = ET.parse(filenameSVG)


            changeSvg(tree, card)
            #root = tree.getroot()
            #for element in root.iter():
            #    changeSvg(element, card)
            tree.write(filenameSVG)
            subprocess.check_output(['inkscape', filenameSVG, '-o', filenamePNG])
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
