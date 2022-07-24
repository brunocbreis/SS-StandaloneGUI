import jinja2
from pyperclip import copy
from ss_classes import Canvas
from os import listdir
from os.path import join, isfile


def render_fusion_output(canvas: Canvas, screen_values: list[dict[str,int]]) -> str:
    """Gets a list of screen values rendered by SplitScreener
       and generates code for use in DaVinci Resolve Fusion
    """

    ###### LOAD TEMPLATES ---------------------------------------------
    template_path = 'templates'
    header_file = join(template_path, '1_header.setting')
    canvas_file = join(template_path, '2_generate_canvas.setting')
    screen_file = join(template_path, '3_generate_screen.setting')
    media_out_file = join(template_path, '4_media_out.setting')
    footer_file = join(template_path, '5_footer.setting')


    ######## CREATE HEADER --------------------------------------------
    with open(header_file, 'r') as _:
        header = _.read()
        header += "\n"

    fusion_output = header


    ####### CREATE CANVAS --------------------------------------------
    screen_number = 0
    node_y = 0
    node_output = "SSCanvas1" # The first node's name is also the first output.

    with open(canvas_file, 'r') as template_text:
        template = jinja2.Template(template_text.read())
        render = template.render(
            CANVAS_NAME = node_output,
            CANVAS_WIDTH = canvas.width,
            CANVAS_HEIGHT = canvas.height,
            NODE_Y = node_y
        ) 

    fusion_output += render


    ######## CREATE SCREENS --------------------------------------------
    node_input = node_output
    screen_number += 1
    node_y += 33
    node_output = f"SSMerge{screen_number}"
    screen_name = f"SSScreen{screen_number}"
    mask_name = f"SSMask{screen_number}"

    for screen in screen_values:

        width = screen['Width']
        height = screen['Height']
        center_x = screen['Center.X']
        center_y = screen['Center.Y']
        size = screen['Size']

        with open(screen_file, 'r') as template_text:
            template = jinja2.Template(template_text.read())
            render = template.render(
                INPUT = node_input,
                OUTPUT = node_output,
                SCREEN_NAME = screen_name,
                SCREEN_INDEX = screen_number - 1,
                MASK_NAME = mask_name,
                CANVAS_WIDTH = canvas.width,
                CANVAS_HEIGHT = canvas.height,
                NODE_Y = node_y,
                WIDTH = width,
                HEIGHT = height,
                CENTER_X = center_x,
                CENTER_Y = center_y,
                SIZE = size
            ) + "\n"
        fusion_output += render

        node_input = node_output
        screen_number += 1
        node_output = f"SSMerge{screen_number}"
        screen_name = f"SSScreen{screen_number}"
        mask_name = f"SSMask{screen_number}"
        node_y += 33


    ###### ADD MEDIA OUT ------------------------------------------
    with open(media_out_file, 'r') as template_text:
        template = jinja2.Template(template_text.read())
        render = template.render(
            INPUT = node_input,
            NODE_Y = node_y,
        ) + "\n"
    fusion_output += render


    ####### ADD FOOTER --------------------------------------------
    with open(footer_file, "r") as _:
        footer = "\n"
        footer += _.read()

    fusion_output += footer


    ###### SAVE TO CLIPBOARD --------------------------------------------
    copy(fusion_output)
    print("\nNode tree succesfully copied to clipboard.\n")

    return fusion_output

def save_preset(
        presets_directory: str, 
        fusion_output: str, 
        preset_name: str = "SplitScreenerPreset") -> None:

    presets_directory = presets_directory
    preset_files = [f for f in listdir(presets_directory) if isfile(join(presets_directory, f))]
    preset_file_name = f"{preset_name}.setting"
    i = 0
    while preset_file_name in preset_files:
        i += 1
        preset_file_name = f"{preset_name}_{i}.setting"

    with open(join(presets_directory,preset_file_name), 'w') as new_preset_file:
        new_preset_file.write(fusion_output)