#!/usr/bin/env python

from pathlib import Path
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile

def is_software_in_path(software_name):
    return shutil.which(software_name) is not None


def make_smpte_filename_safe(start_time, end_time):
    """
    Convert SMPTE time codes to a filename-safe format.

    Parameters:
    - start_time (str): The starting time in SMPTE format (e.g., "01:23:45").
    - end_time (str): The ending time in SMPTE format (e.g., "02:34:56").

    Returns:
    - str: A filename-safe string representation of the time codes.
    """

    # Remove colons from the start time to make it filename-safe.
    start_time_safe = start_time.replace(':', '')

    # Remove colons from the end time to make it filename-safe.
    end_time_safe = end_time.replace(':', '')

    # Construct the filename by joining the start and end times with a hyphen.
    time_code_filename_safe = f"{start_time_safe}-{end_time_safe}"

    # Return the constructed filename-safe time code string.
    return time_code_filename_safe


def get_video_properties(video):
    """
    Use ffprobe to get all properties of a media file.

    This function runs the ffprobe command-line utility to fetch all properties
    of the media file. The properties are returned as a dictionary.

    Parameters:
        video (str): The filename or path of the video to examine.

    Returns:
        dict: A dictionary containing all properties of the media file.
    """

    # Command list for running ffprobe.
    # '-i' specifies the input video.
    # '-show_format' and '-show_streams' fetch detailed information about the media file.
    # '-v quiet' ensures ffprobe runs without displaying logs.
    # '-print_format json' sets the output format to JSON.
    cmd = [
        'ffprobe', '-i', video,
        '-show_format', '-show_streams',
        '-v', 'quiet',
        '-print_format', 'json'
    ]

    # Run the command and capture the output.
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = result.stdout.decode('utf-8')

    # Parse the JSON output and return as a dictionary.
    properties = json.loads(output)
    return properties


def args_checker(args):
    """
    Checks if arguments are files or folders.

    Returns True if all arguments are either files or folders.
    Returns False if any of the arguments is neither a file nor folder.

    If files/folders are dropped on the script they are added as arguments.
    Args can be...
    Single file:      'C:\\Users\\admin\\Desktop\\sample_video_1.mp4'
    Single folder:    'C:\\Users\\admin\\Desktop\\sample files'
    Multiple files:   '0001.png', '0002.png', '0003.png'...
    Multiple folders: '\\images\\1', '\\images\\2', '\\images\\3'...
    ...or a combination of them
    """

    # Check if any arguments are provided.
    if len(args) > 1:

        # Check if only one argument is provided.
        if len(args) <= 2:

            # Check if the single argument is a file.
            if os.path.isfile(args[1]):
                print("Only a single file provided")
                return True

            # Check if the single argument is a directory.
            elif os.path.isdir(args[1]):
                print("This is a single folder")
                print(args[1])
                return True

        # Handle the case where multiple arguments are provided.
        else:

            # Iterate over each argument starting from the second one.
            for each in args[1:]:

                # Check if the current argument is neither a file nor a folder.
                if not (os.path.isfile(each) or os.path.isdir(each)):
                    print("Multiple args, but some are not files or folders")
                    return False

            # All arguments are either files or folders.
            print("Multiple args, and all are files or folders (or variation)")
            return True

    # No arguments provided.
    else:
        return False


def determine_desktop():
    """
    Determine the desktop folder based on the operating system.

    Returns:
        Path: Path to the desktop folder for the current user.
    """

    # Get the name of the operating system (e.g. 'Windows', 'Darwin', 'Linux').
    system = platform.system()

    # Get the path to the home directory of the current user.
    user_home = Path.home()

    # Use a dictionary to map operating system names to their respective
    # desktop paths. If the OS is not recognized, default to a generic path.
    desktop_paths = {
        'Windows': Path(os.environ['USERPROFILE']) / 'Desktop',
        'Darwin': user_home / 'Desktop',
        'Linux': user_home / 'Desktop'
    }

    return desktop_paths.get(system, user_home / 'Desktop')


def is_image(file_name):
    """
    Check if the file is image based on its extension.

    Parameters:
        file_name (str): The name of the file to check.

    Returns:
        bool: True if the file is an image, False otherwise.
    """

    # Convert the file name to lowercase and check if it ends with any of the
    # specified video file extensions.
    return file_name.lower().endswith(('png'))


def is_video(file_name):
    """
    Check if the file is a video based on its extension.

    Parameters:
        file_name (str): The name of the file to check.

    Returns:
        bool: True if the file is a video, False otherwise.
    """

    # Convert the file name to lowercase and check if it ends with any of the
    # specified video file extensions.
    return file_name.lower().endswith(('mkv', 'mp4', 'webm'))


def is_subtitle(file_name):
    """
    Check if the file is a subtitle based on its extension.

    Parameters:
        file_name (str): The name of the file to check.

    Returns:
        bool: True if the file is a subtitle, False otherwise.
    """

    # Convert the file name to lowercase and check if it ends with any of the
    # specified subtitle file extensions.
    return file_name.lower().endswith(('srt', 'ass'))


def contains_single_video_and_subtitle(files):
    """
    Check if the list contains a single video file and a single subtitle file.

    Parameters:
        files (list): The list of file names to check.

    Returns:
        bool:   True if the list contains a single video and a single subtitle, 
                False otherwise.
    """
    
    video_count = 0
    subtitle_count = 0

    for file_name in files:
        if is_video(file_name):
            video_count += 1
        elif is_subtitle(file_name):
            subtitle_count += 1

    return video_count == 1 and subtitle_count == 1


def find_png_folders(directories):
    """
    Identify and return folders within the given directories that contain PNGs.

    Parameters:
        directories (list): The list of directories to search within.

    Returns:
        list: A list of folder paths that contain PNG files.
    """

    # An empty list to store the paths of folders containing PNG files.
    png_folders = []

    # Iterate over each directory in the list
    for directory in directories:
        # Use os.walk to iterate over all subdirectories and files within.
        for root, _, files in os.walk(directory):

            # Check each file in root to see if it's a PNG image.
            # If any of the files in the directory is a PNG image, add the
            # directory path to the png_folders list.
            if any(is_image(f) for f in files):
                png_folders.append(root)

    # Return the list of folder paths containing PNG files.
    return png_folders


def convert_time_format(time_str):
    """
    Converts time format from hh:mm:ss:xxx to hh:mm:ss.xxx.

    Parameters:
        time_str (str): The time string to convert.

    Returns:
        str: The converted time string or the original time if no conversion
        is needed.
    """

    # Check if the provided time string has 4 segments separated by colons.
    # This would mean it's in the format hh:mm:ss:xxx.
    if len(time_str.split(':')) == 4:

        # Replace the last colon with a period.
        # 'rsplit' splits the string from the right, ensuring only the last
        # colon is replaced.
        return '.'.join(time_str.rsplit(':', 1))

    # If the time string is not in the expected format, return it unchanged.
    return time_str


def extract_frames_with_ffmpeg(video, output_fps, folder="temp_folder",
                               start_time=None, end_time=None, 
                               subtitle_file=None, loglevel="warning"):
    """
    Extract frames from a video using ffmpeg and burn in subtitles if provided.

    Parameters:
        video (str)                     Path to the video file.

        output_fps (int)                Frames per second to extract.

        folder (str, optional)          Folder to save extracted frames.
                                        Default is "temp_folder".

        start_time (str, optional)      Start time 
                                        ('hh: mm : ss' or 'hh : mm : ss.xxx').
                                        Default is None.

        end_time (str, optional)        End time
                                        ('hh : mm : ss' or 'hh : mm : ss.xxx').
                                        Default is None.

        subtitle_file (str, optional)   Path to the subtitle file.
                                        Default is None.

        loglevel (str, optional)        ffmpeg log level. Default is "warning".
    """

    # Check if the specified folder exists. If not, create it.
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Base command for ffmpeg: specifying the log level, input video, desired output fps,
    # and the naming format for the extracted frames.
    cmd = ['ffmpeg', '-loglevel', loglevel, '-i', video]

    # If a start time is provided, format it and add it to the command.
    if start_time:
        start_time = convert_time_format(start_time)
        cmd.extend(['-ss', start_time, '-copyts'])

    # If an end time is provided, format it and add it to the command.
    if end_time:
        end_time = convert_time_format(end_time)
        cmd.extend(['-to', end_time])

    # Construct the filter string
    filter_str = []
    if subtitle_file:
        filter_str.append(f'subtitles={subtitle_file}')
    filter_str.append(f'fps={output_fps},scale=720:-1:flags=lanczos')
    cmd.extend(['-vf', ','.join(filter_str)])

    cmd.append(f'{folder}/frame_%04d.png')

    print("\n\n\n")
    # Execute the ffmpeg command to extract frames.
    subprocess.run(cmd)
    print("\n\n\n")


def convert_to_gif(input_files, output_file, output_width, output_fps,
                   output_quality):
    """
    Use gifski to convert a series of image files to a GIF.

    Parameters:
        input_files (list): List of paths to the input image files.
        output_file (str): Path to the output GIF file.
        output_width (str): Desired width of the output GIF.
        output_fps (str): Desired frames per second for the output GIF.
        output_quality (str): Desired quality for the output GIF.
    """

    # Initialize the command list for gifski.
    # This list contains the executable name, flags, and their values.
    cmd = [
        'gifski',        # The gifski executable.
        '-o',            # Flag to specify the output file.
        output_file,     # Path to the output GIF file.
        '--width',       # Flag to set the width of the output GIF.
        output_width,    # Desired width for the output GIF.
        '--fps',         # Flag to set the frames per second.
        output_fps,      # Desired frames per second.
        '--quality',     # Flag to set the quality of the output GIF.
        output_quality   # Desired quality level.
    ]

    # Extend the command list with the paths of the input image files.
    cmd.extend(input_files)

    # Execute the gifski command to create the GIF.
    subprocess.run(cmd)


def get_input(prompt, validation_function):
    """
    Prompt the user for input and validate it using a provided function.

    This function repeatedly prompts the user for input until the input is
    valid according to the provided validation function or the user provides
    no input.

    Parameters:
        prompt (str): The message displayed to the user.
        validation_function (function): A function that returns True if the
                                        input is valid and False otherwise.

    Returns:
        str or None: User's input if it's valid or None if no input is given.
    """

    # Infinite loop to ask for user input until valid input is given.
    while True:

        # Get input from the user.
        user_input = input(prompt)

        # If the user provides no input, return None.
        if not user_input:
            return None

        # If the user's input passes the validation function, return the input.
        if validation_function(user_input):
            return user_input

        # If the input is invalid, inform the user and prompt again.
        print("Invalid input. Please try again.")


def validate_time_format(time_str):
    """
    Validate if the provided string matches the time format "hh:mm:ss:xxx".

    Parameters:
        time_str (str): The time string to validate.

    Returns:
        bool: True if the string matches the format, False otherwise.
    """

    # Regular expression pattern to match the time format:
    # "hours:minutes:seconds:milliseconds".
    # \d{1,2} matches 1 or 2 digits for hours, minutes, and seconds.
    # \d{1,3} matches 1 to 3 digits for milliseconds.
    pattern = r"(\d{1,2}:\d{1,2}:\d{1,2}:\d{1,3})"

    # Use the fullmatch method to check if the string matches the pattern.
    # Return True if there's a match, otherwise return False.
    return bool(re.fullmatch(pattern, time_str))


def validate_file_name(file_name):
    """
    Validate if the provided file name is not empty and the file exists.

    Parameters:
        file_name (str): The name or path of the file to validate.

    Returns:
        bool: True if the file name is not empty and the file exists, False
        otherwise.
    """

    # Check if the file name string is not empty using bool().
    # Then, use os.path.exists() to check if the file or directory with the
    # given name exists in the file system.
    # The 'and' operator ensures both conditions are met.
    return bool(file_name) and os.path.exists(file_name)


def validate_number(num):
    """
    Validate if the provided input can be converted to an integer and
    lies between 50 and 3840 (inclusive).

    Parameters:
        num (str): The input string to validate.

    Returns:
        bool: True if the input meets the criteria, False otherwise.
    """

    try:
        # Attempt to convert the input string to an integer.
        num = int(num)

        # Check if the converted number lies between 50 and 3840 (inclusive).
        return 50 <= num <= 3840

    # If the conversion to integer fails, a ValueError is raised.
    except ValueError:
        # Return False since the input string is not a valid integer.
        return False


def validate_fps(num):
    """
    Validate if the provided input can be converted to an integer and lies
    between 5 and 60 (inclusive), typically representing frames per second.

    Parameters:
        num (str): The input string to validate.

    Returns:
        bool: True if the input meets the criteria, False otherwise.
    """

    try:
        # Attempt to convert the input string to an integer.
        num = int(num)

        # Check if the converted number lies between 5 and 60 (inclusive).
        # This range is common for validating frames per second (fps) values.
        return 5 <= num <= 60

    # If the conversion to integer fails, a ValueError is raised.
    except ValueError:
        # Return False since the input string is not a valid integer.
        return False


def validate_quality(num):
    """
    Validate if the provided input can be converted to an integer and
    lies between 1 and 100 (inclusive), typically representing a quality
    percentage.

    Parameters:
        num (str): The input string to validate.

    Returns:
        bool: True if the input meets the criteria, False otherwise.
    """

    try:
        # Attempt to convert the input string to an integer.
        num = int(num)

        # Check if the converted number lies between 1 and 100 (inclusive).
        # This range is common for validating quality percentages.
        return 1 <= num <= 100

    # If the conversion to integer fails, a ValueError is raised.
    except ValueError:
        # Return False since the input string is not a valid integer.
        return False


def contains_only_files(paths):
    """
    Check if the provided list contains only file paths.

    Parameters:
        paths (list): List of paths to validate.

    Returns:
        bool: True if all paths are files, False otherwise.
    """

    # Check if the list of paths is empty.
    if not paths:
        # Return False since the list is empty.
        return False

    # Iterate over each path in the list.
    for path in paths:

        # Check if the path does not exist.
        if not os.path.exists(path):
            print("Please provide file(s) or a folder")
            return False  # Path does not exist

        # Check if the path is a directory.
        if os.path.isdir(path):
            print("Directory found...")
            return False  # Found a directory

    # If the loop completes without returning, all paths are files.
    print("All are files")
    return True


def get_start_time():
    """
    Prompt the user for a start time in the format
    "hours:minutes:seconds:milliseconds".

    If the user provides an invalid time format, they will be prompted again.
    If the user leaves the input blank, the function will return None.

    Returns:
        str or None: The user's input if it's valid or None if no input.
    """

    # Use the get_input function to prompt the user for the start time.
    # The prompt message specifies the expected format and informs the user
    # that they can leave it blank to skip trimming.
    # The validate_time_format function is passed as the validation function
    # to ensure the user's input matches the expected time format.
    return get_input(
        "Enter the start time (hours:minutes:seconds:milliseconds) or "
        "leave blank to skip trimming: ",
        validate_time_format
    )


def get_end_time():
    """
    Prompt the user for an end time in the format
    "hours:minutes:seconds:milliseconds".

    If the user provides an invalid time format, they will be prompted again.
    If the user leaves the input blank, the function will return None.

    Returns:
        str or None: The user's input if it's valid or None if no input.
    """

    # Use the get_input function to prompt the user for the end time.
    # The prompt message specifies the expected format.
    # The validate_time_format function is passed as the validation function
    # to ensure the user's input matches the expected time format.
    return get_input(
        "Enter the end time (hours:minutes:seconds:milliseconds): ",
        validate_time_format
    )


def get_output_width(default="512"):
    """
    Prompt the user for the desired output width in pixels.

    If the user provides an invalid number or leaves the input blank,
    the function will return the default width.

    Parameters:
        default (str): The default width value to return if the user
                       provides no input. Default is "512".

    Returns:
        str: The user's input if it's valid or the default width if no input.
    """

    # Use the get_input function to prompt the user for the desired width.
    # The prompt message specifies that the width should be provided in pixels.
    # The validate_number function is passed as the validation function
    # to ensure the user's input is a valid number.
    width = get_input("Width (Resolution in pixels): ", validate_number)

    # Return the user's input if it's valid. If the user provides no input,
    # return the default width.
    return width if width else default


def get_output_fps(default="12"):
    """
    Prompt the user for numbers of frames per second (FPS) for the output file.

    If the user provides an invalid number or leaves the input blank,
    the function will return the default FPS.

    Parameters:
        default (str): The default FPS value to return if the user
                       provides no input. Default is "12".

    Returns:
        str: The user's input if it's valid or the default FPS if no input.
    """

    # Use the get_input function to prompt the user for the desired FPS.
    # The prompt message specifies that the input should represent frames
    # per second for the output file.
    # The validate_fps function is passed as the validation function
    # to ensure the user's input is a valid FPS value.
    fps = get_input("FPS (frames per second for the output file): ",
                    validate_fps)

    # Return the user's input if it's valid. If the user provides no input,
    # return the default FPS.
    return fps if fps else default


def get_output_quality(default="100"):
    """
    Prompt the user for the desired output quality for gifski.

    If the user provides an invalid number or leaves the input blank,
    the function will return the default quality value.

    Parameters:
        default (str): The default quality value to return if the user
                       provides no input. Default is "100".

    Returns:
        str: The user's input if it's valid or the default quality if no input.
    """

    # Use the get_input function to prompt the user for the desired quality.
    # The prompt message specifies that the input should represent the quality
    # value for gifski, which should be in the range of 1-100.
    # The validate_quality function is passed as the validation function
    # to ensure the user's input is a valid quality value.
    quality = get_input("Enter gifski quality (1-100): ", validate_quality)

    # Return the user's input if it's valid. If the user provides no input,
    # return the default quality value.
    return quality if quality else default


# Define the main function which serves as the primary entry point for the
# program. This function will contain the main logic or flow of the program.
def main():

    # If the operating system is windows
    if platform.system() == 'Windows':

        # Check if gifski is available in PATH
        if not is_software_in_path('gifski'):
            print("Gifski could not be found in PATH.")
            print("Please download gifski and remember to add it to PATH.")
            input("Read the documentation for more info...")
            exit()

        # Check if ffmpeg is available in PATH
        if not is_software_in_path('ffmpeg'):
            print("Gifski could not be found in PATH.")
            print("Please download gifski and remember to add it to PATH.")
            input("Read the documentation for more info...")
            exit()

    else:
        print("You are running the script in an operating system that is not "
            "tested. Proceed at your own risk. Make sure ffmpeg and gifski "
            "can be called in the terminal.")

    # Checking if the provided command-line arguments are files or folders.
    if args_checker(sys.argv):

        # Determine the desktop folder based on the operating system.
        desktop = determine_desktop()

        # Set the command-line arguments as source since this script only
        # takes files or folders as arguments.
        source = sys.argv[1:]
    
    else:
        input("No file(s) or folder(s) added...")
        exit()

    # ######################################
    # If the source is a folder
    # ######################################

    directories = []  # Make an empty list to contain directories
    for arg in source:  # For each argument
        if os.path.isdir(arg):  # Check if each arg is a dir
            directories.append(arg)  # Add the dir to the list

    if len(directories) > 0:  # If the list contains more than 0 directories

        output_width = get_output_width()
        output_fps = get_output_fps()
        output_quality = get_output_quality()

        # List of checked folders that contain PNG files
        png_folders = find_png_folders(directories)

        # Now you have a list of folders with PNGs (png_folders)
    try:
        print("List of checked folders that contain PNG image files: ",
              png_folders)
        for png_folder in png_folders:

            # Filter for PNG files
            png_files = []
            for f in os.listdir(png_folder):
                if is_image(f):
                    png_files.append(os.path.join(png_folder, f))

            for each in png_files:
                print(each)

            base_name = os.path.basename(png_folder)
            output_file = os.path.join(desktop, f"{base_name}.gif")

            convert_to_gif(png_files, output_file, output_width,
                           output_fps, output_quality)
    except Exception as e:
        pass

    # ######################################
    # If the source is images
    # ######################################
    try:
        image_files = [f for f in source if is_image(f)]
        if image_files:

            output_width = get_output_width()
            output_fps = get_output_fps()
            output_quality = get_output_quality()

            output_file = os.path.join(desktop, 'output.gif')

            convert_to_gif(image_files, output_file, output_width,
                           output_fps, output_quality)
    except Exception as e:
        pass

    # ######################################
    # If the source are videos
    # ######################################

    subtitle_file = None
    if contains_single_video_and_subtitle(source):
        # Get the first subtitle file from the list
        for file in source:
            if is_subtitle(file):
                subtitle_file = file

    try:
        # Creates a new list called video_files that contains only the items 
        # from source for which the is_video function returns True.
        video_files = [f for f in source if is_video(f)]
        if video_files:

            start_time = None  # For multiple videos don't ask for positions
            end_time = None  # For multiple videos don't ask for positions
            output_width = get_output_width()
            output_fps = get_output_fps()
            output_quality = get_output_quality()

            if len(video_files) == 1:  # If a single file - ask for positions
                start_time = get_start_time()
                end_time = get_end_time() if start_time else None


            for video in video_files:

                with tempfile.TemporaryDirectory() as temp_folder:
                    # If start or end time is provided
                    if start_time is not None:

                        # Construct the file name based on the time code
                        timecode = make_smpte_filename_safe(
                            start_time, end_time)
                        base_name = os.path.basename(video)
                        name_without_ext = os.path.splitext(base_name)[0]
                        output_gif_name = f"{name_without_ext} - {timecode}.gif"

                        if subtitle_file is not None:
                            extract_frames_with_ffmpeg(
                                video, output_fps, temp_folder, start_time, 
                                end_time, subtitle_file)
                        else:
                            extract_frames_with_ffmpeg(
                                video, output_fps, temp_folder, start_time, 
                                end_time)

                    else:

                        # Check if the video (without trimming is longer than
                        # 15 seconds)

                        properties = get_video_properties(video)
                        # Extract the duration from the properties dictionary.
                        duration = float(properties['format']['duration'])
                        print(f"Duration of the video: {duration} seconds")
                        duration = get_video_duration(video)
                        if duration > 15:
                            input(  "\nThe input video is longer than 15 "
                                    "seconds, and no trimming has been made.\n"
                                    "Long GIFs are not recommended.\n"
                                    "Aborting operation...\n\n")
                            exit()

                        else:
                            if subtitle_file is not None:
                                extract_frames_with_ffmpeg(
                                    video, output_fps, temp_folder, 
                                    subtitle_file)
                            else:
                                extract_frames_with_ffmpeg(
                                    video, output_fps, temp_folder)

                            base_name = os.path.basename(video)
                            name_without_ext = os.path.splitext(base_name)[0]
                            output_gif_name = f"{name_without_ext}.gif"

                    # Get the frame files from the temp directory
                    frames = [
                        os.path.join(temp_folder, f)
                        for f in sorted(os.listdir(temp_folder))
                        if is_image(f)
                    ]

                    output_file = os.path.join(desktop, output_gif_name)

                    convert_to_gif(frames, output_file, output_width,
                                   output_fps, output_quality)
    except Exception as e:
        raise

# Check if this script is being run as the main module.
# This condition ensures that the code inside this block is only executed when
# the script is run directly and not when it's imported as a module.
if __name__ == '__main__':

    # Call the main function to execute the primary logic of the script.
    main()

    # Prompt the user to press the Enter key. This is often used to prevent
    # the terminal or command prompt from closing immediately after the script
    # finishes executing, allowing the user to see any output or messages.
    input("Press Enter to exit...")
