

"""
Script to automatically build the packages.

When execute will automatically grab every script inside the nodelib folder of each port
and put them inside a nodelib folder in a zip file.

changelogs are also included.
"""


# TODO: broken


# ---------------------------------------------------------


from os import mkdir as make_directory
from os import listdir as list_directory
from os import chdir as change_work_directory

from os.path import isdir as check_directory
from os.path import join as join_path
from os.path import splitext as split_path

from zipfile import ZipFile


# ---------------------------------------------------------


ignore_files: tuple = (
	".exe", ".obj", ".class",
)

ignore_folders: tuple = (
	"__pycache__",
)


# ---------------------------------------------------------


def main() -> None:
	
	# Check if the output folder exist, if not make a new one.
	if (check_directory("release") == False):
		make_directory("release")

	# Get the nodelib folder inside each port and loop his content.
	for port_directory in list_directory(join_path("tools")):
		output_destination: str = join_path("release", f"{port_directory}.zip")

		# Create a new zip file to fill.
		with ZipFile(output_destination, 'w') as zip_file:

			# The library folder of the port.
			port_content: str = join_path("tools", port_directory)

			for folder_content in list_directory(port_content):
				add_content(zip_file, folder_content, port_content)


# Executed for each directory and each file.
def add_content(zip_file, name: str, path: str) -> None:

	if (check_directory(join_path(path, name)) == True):
		
		if (name in ignore_folders):
			return
		
		path = join_path(path, name)

		for item in list_directory(path):
			add_content(zip_file, item, path)
	
	else:

		if (split_path(name)[-1] in ignore_files):
			return
		
		zip_file.write(
			join_path(path, name),
			join_path("nodeclass", name)
		)
		

# ---------------------------------------------------------


if (__name__ == "__main__"):
	main()


# ---------------------------------------------------------

