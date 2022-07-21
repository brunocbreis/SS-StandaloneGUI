import jinja2
from pyperclip import copy
from ss_calc import screen_values, canvas
import os.path

###### LOAD TEMPLATES ---------------------------------------------
template_path = 'templates'
header_file = os.path.join(template_path, '1_header.setting')
canvas_file = os.path.join(template_path, '2_generate_canvas.setting')
screen_file = os.path.join(template_path, '3_generate_screen.setting')
media_out_file = os.path.join(template_path, '4_media_out.setting')
footer_file = os.path.join(template_path, '5_footer.setting')

######## CREATE HEADER --------------------------------------------

with open(header_file, 'r') as _:
    header = _.read()
    header += "\n"

FUSION_OUTPUT = header

####### CREATE CANVAS --------------------------------------------

# initialize iterable variables
screen_number = 0
y = 0
output = "SSCanvas1"

with open(canvas_file, 'r') as template_text:
    template = jinja2.Template(template_text.read())
    render = template.render(
        CANVAS_NAME = output,
        CANVAS_WIDTH = canvas.width,
        CANVAS_HEIGHT = canvas.height,
        Y = y
    ) 

FUSION_OUTPUT += render


######## CREATE SCREENS --------------------------------------------

# update Variables for the first time, before looping
input = output
screen_number += 1
y += 33
output = f"SSMerge{screen_number}"
screen_name = f"SSScreen{screen_number}"
mask_name = f"SSMask{screen_number}"


###### LET'S LOOP! --------------------------------------------

REPEATS = len(screen_values)

for i in range(REPEATS):

    width = screen_values[i]['Width']
    height = screen_values[i]['Height']
    center_x = screen_values[i]['Center.X']
    center_y = screen_values[i]['Center.Y']
    size = screen_values[i]['Size']

    with open(screen_file, 'r') as template_text:
        template = jinja2.Template(template_text.read())
        render = template.render(
            INPUT = input,
            OUTPUT = output,
            SCREEN_NAME = screen_name,
            SCREEN_INDEX = i,
            MASK_NAME = mask_name,
            CANVAS_WIDTH = canvas.width,
            CANVAS_HEIGHT = canvas.height,
            Y = y,
            WIDTH = width,
            HEIGHT = height,
            CENTER_X = center_x,
            CENTER_Y = center_y,
            SIZE = size
        ) + "\n"
    FUSION_OUTPUT += render

    input = output
    screen_number += 1
    output = f"SSMerge{screen_number}"
    screen_name = f"SSScreen{screen_number}"
    mask_name = f"SSMask{screen_number}"
    y += 33


###### ADD MEDIA OUT ------------------------------------------

with open(media_out_file, 'r') as template_text:
    template = jinja2.Template(template_text.read())
    render = template.render(
        INPUT = input,
        Y = y,
    ) + "\n"
FUSION_OUTPUT += render

####### ADD FOOTER --------------------------------------------

with open(footer_file, "r") as _:
    footer = "\n"
    footer += _.read()

FUSION_OUTPUT += footer


###### SAVE TO CLIPBOARD --------------------------------------------
copy(FUSION_OUTPUT)

print("Node tree succesfully copied to clipboard.")