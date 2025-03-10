
"""

This file will create synthetic data from inputted strings.
It creates variations of a sentence using a list of nouns and verbs.

"""

import glob
import os
import sys
from PIL import Image
import json
import random

# Variables created for functions
cwd = os.path.dirname(os.path.abspath(__file__))
processed_path = sys.argv[1].strip() + "/"
char_list = [[] for i in range(5000000)]

# Takes a PIL image (im1, img2) and attaches img2 to the right of img1
def get_concat_h(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst

# Takes a PIL image (im1, img2) and attaches img2 to the bottom of img1
def get_concat_v(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst

# Creates the list of characters from the folder "character_images"
# These images need to have the letter on the 6th letter which I put "char-" before.
# Needed since starting a file name with '.' or ' ' creates slight issues
def create_char_list():
    supported_file_extensions = ["jpg", "jpeg", "png", "tif", "tiff"]
    img_files = []
    for ext in supported_file_extensions:
        img_files += glob.glob(
            cwd + f"/data/character_images/*.{ext}", recursive=True)

    # print(cwd)
    for file_path in img_files:
        file_char = os.path.basename(file_path)[5]
        char_place = get_place_from_char(file_char)
        # print(file_path)
        # print(char_place)
        # print(file_char)

        char_list[char_place].append(Image.open(file_path))

# Gets the list position for the specified character
def get_place_from_char(char: str):
    char_place = ord(char)
    if 91 > char_place > 64:  # Upper case letters
        return char_place - 65
    elif 123 > char_place > 96:  # Lower case letters
        return char_place - 96 + 26
    elif char_place == 32:  # The ' ' white space
        return 53
    elif char_place == 46:  # The '.' period
        return 54
    else:
        return -1

# Returns an image of the character
def get_char_as_image(char: str, handwriting_type: int = 0):
    # print(char_list[get_place_from_char(char)][handwriting_type])
    return char_list[get_place_from_char(char)][handwriting_type]

# Creates a full image from the complete text desired to become synthetic data
def create_image_from_string(sentence: str):
    if sentence is None or len(sentence) == 0:
        return None
    characters = [char for char in sentence.upper()]
    length = len(sentence) * 36 if len(sentence) * 36 < 1500 else 1500
    width = 0

    return_image = None
    row_image = Image.new(mode="RGB", size=(0, 64))

    return_string = ""

    while len(characters) > 0:
        char = characters.pop(0)
        if char == "\n":
            continue
        if char == ' ':
            place = 0
            place_width = 0
            char_check = '_'
            while char_check != ' ' and place + 1 < len(characters):
                char_check = characters[place]
                if char_check == "\n":
                    place += 1
                    continue
                place_width += get_char_as_image(char_check).width
                place += 1
            if place_width + row_image.width > 1500:
                if return_image is None:
                    return_image = Image.new(mode="RGB", size=(length, 0))

                return_image = get_concat_v(return_image, row_image)
                row_image = Image.new(mode="RGB", size=(0, 64))
                width = 0

                char = characters.pop(0)
                return_string += '\n'

        char_img = get_char_as_image(char)
        return_string += char
        if char_img is None:
            continue

        if width + char_img.width > 1500:
            if return_image is None:
                return_image = Image.new(mode="RGB", size=(length, 0))

            return_image = get_concat_v(return_image, row_image)
            row_image = Image.new(mode="RGB", size=(0, 64))
            width = 0
        width += char_img.width
        row_image = get_concat_h(row_image, char_img)

    if return_image is None:
        return_image = Image.new(mode="RGB", size=(length, 0))
    return_image = get_concat_v(return_image, row_image)
    return return_image

# Opening JSON file
f = open('/train/tesstrain/word_bank.json')
# returns JSON object as
# a dictionary
word_data = json.load(f)

#Select a sample for words
w_sample = 10

word_data['verbs'] = random.sample(word_data['verbs'], w_sample)
word_data['nouns'] = random.sample(word_data['nouns'], w_sample)
word_data['preposition'] = random.sample(word_data['preposition'], 5)
word_data['places'] = random.sample(word_data['places'], 5)
create_char_list()
list_of_string_pairs = []

# Create new string with a certain pattern
def create_simple_string(n: int, v: int, pr: int, pl: int):
    return f"the {word_data['nouns'][n]} {word_data['verbs'][v]} {word_data['preposition'][pr]} the {word_data['places'][pl]}."

# Loops through every variation of nouns/verbs randomly selected and creates a string from them
for i in range(len(word_data['nouns'])):
    for j in range(len(word_data['verbs'])):
        for k in range(len(word_data['preposition'])):
            for l in range(len(word_data['places'])):
                list_of_string_pairs.append((str(i) + "imga-" + str(j) + "-" + str(k) + "-" + str(l),
                                             create_simple_string(i, j, k, l)))

# Create images of data added to list_of_string_pairs
for file_name, text_data in list_of_string_pairs:

    syn_image = create_image_from_string(text_data)

    syn_image.save(processed_path + file_name + ".png")
    with open(processed_path + file_name + ".gt.txt", 'w') as f:
        f.write(text_data)