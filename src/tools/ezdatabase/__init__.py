

# -------------------------------------------------


__package__ = "Database"
__version__ = 1.0
__author__ = "GianptDev"


# -------------------------------------------------


from os import mkdir as make_directory, remove as remove_file, listdir as get_file_list
from os.path import join as join_path, isdir as check_directory, isfile as check_file
from typing import Union
from xml.etree.ElementTree import Element as XmlElement, ElementTree as XmlTree, XMLParser, indent as xml_indent, fromstring as parse_xml
from random import randint
from weakref import ref


# -------------------------------------------------


class Key():


	# -------------------------------------------------

	
	def __init__(self, database: "Database", name: str) -> None:
		
		self._flag_changed: bool = False
		self._removed: bool = False

		self._database = ref(database)
		self._name: str = name

		self._src: Union[str, None] = None
		self._properties: Union[dict[str, any], None] = None
	

	def __repr__(self) -> str:
		return f"<key '{self._name}':'{self._src}'>"


	# -------------------------------------------------


	@property
	def name(self) -> str:
		"""
		The unique name of this key.
		"""

		return self._name
	

	@name.setter
	def name(self, value: str) -> None:
		self.rename(value)


	@property
	def properties(self) -> Union[dict[str, any], None]:
		"""
		The properties of the key, they are loaded or initialized only when required.

		Use the load() method to load the properties.
		"""

		return self._properties
	

	@properties.setter
	def properties(self, value: dict[str, any]) -> None:
		self._properties = value
		self._flag_changed = True
	

	@property
	def src(self) -> Union[str, None]:
		"""
		The source file path wich all the stuff of the key are saved, the path is relative from the database folder.
		"""

		return self._src


	@property
	def removed(self) -> bool:
		"""
		Mark that set the key to be deleted the next time it will be saved.

		The source file will be deleted if it exist and the key is removed from the list inside the database.
		"""

		return self._removed
	

	@removed.setter
	def removed(self, value: bool) -> None:
		self._removed = value


	# -------------------------------------------------


	def rename(self, name: str) -> None:
		"""
		Rename the key with a different name, after rename the key is marked as changed.
		
		Will raise an exception if another key has already that name.
		"""

		for key in self._database()._keys:

			if ((key != self) and (key._name == name)):
				raise Exception(f"Another key is already named '{name}'.")
		
		self._name = name
		self._flag_changed = True
		return True


	def set_property(self, name: str, value: any) -> None:
		"""
		Change or add a property and mark the key as changed, will try to load the source if possible.
		"""

		if (self._properties == None):
			self.load()
		
		self._properties[name] = value
		self._flag_changed = True
	
	
	def remove_property(self, name: str) -> None:
		"""
		Remove a property and mark the key as changed, will try to load the source if possible.
		"""

		if (self._properties == None):
			self.load()

		del self._properties[name]
		self._flag_changed = True
	

	def load(self) -> None:
		"""
		Load the key from his source file and fill the properties, the new set of properties will override the current set.

		If the source does not exist properties will be initialized anyway.
		"""

		src_path = join_path(self._database()._folder, join_path(*self._src.split("/")))
		self._properties = {}

		if (check_file(src_path) == False):
			return
		
		with open(src_path, "r") as file:
			root = parse_xml(file.read())
		
		for element in root:
			
			if (element.tag == "properties"):
				self._properties = {**element.attrib}


	def save(self) -> None:
		"""
		Save the file with all the content of the key and remove the changed mark.

		- The key will not be saved if no changes are marked.
		- The key file will be removed if the remove flag is enabled.
		"""

		# Source file has not be set, generate a new name for it.
		if (self._src == None):

			while(True):
				found = False
				src_id = f"keys/{random_string(8)}.xml"

				for other_key in self._database()._keys:

					if (other_key._src == src_id):
						found = True
						break
				
				if (found == False):
					self._src = src_id
					break

			self._flag_changed = True


		src_path = join_path(self._database()._folder, join_path(*self._src.split("/")))
		
		if (self._removed == True):

			if ((self._src != None) and (check_file(src_path) == True)):
				remove_file(src_path)
			
			self._database()._keys.remove(self)
		
		else:

			if (self._flag_changed == True):
				key_element = XmlElement("key")

				if (self._properties != None):
					key_element.append(XmlElement("properties", self._properties))
				tree = XmlTree(key_element)

				xml_indent(tree, "\t")
				tree.write(src_path)

		self._flag_changed = False


class Database():
	"""
	Database object that handle everything related to databases.
	"""


	# -------------------------------------------------


	def __init__(self, folder: str) -> None:
		
		self._folder: str = folder
		self._keys: list[Key] = []


	def __repr__(self) -> str:
		string = ""

		for key in self._keys:
			string += f"  {key._src} : {key._properties != None} : '{key._name}'\n"
		
		return f"Database\nFolder: '{self._folder}'\n{string}"


	# -------------------------------------------------


	@property
	def folder(self) -> str:
		"""
		The current folder this database is initialized.
		"""

		return self._folder


	@folder.setter
	def folder(self, value: str) -> None:
		self._folder = value


	@property
	def keys(self) -> list[Key]:
		"""
		The list of all keys inside the database.
		"""

		return self._keys


	# -------------------------------------------------


	def add_key(self, name: str) -> Union[Key, None]:
		"""
		Add a new key with the specific name, if another key with the same name already exist the key is not created and None is returned.
		"""

		if (self.get_key(name) != None):
			return None


		key = Key(self, name)
		key.changed = True
		self._keys.append(key)

		return key
	

	def get_key(self, name: str) -> Union[Key, None]:
		"""
		Get the key with the specific name, the key will be obtained even if marked to be removed.
		"""

		for key in self._keys:

			if (key.name == name):
				return key
		
		return None
	

	def exist(self) -> bool:
		"""
		Check if the folder of this database already contain another database or a previus save.
		"""

		return is_database(self._folder)


	def load(self) -> None:
		"""
		Load all database data from a folder.
		"""

		load_database(self, self._folder)

	
	def save(self) -> None:
		"""
		Save the whole database and all his keys in a folder.
		"""

		save_database(self, self._folder)


# -------------------------------------------------


def random_string(lenght: int) -> str:
	"""
	Generate a string of random characters of the alphabet.

	Params:
		lenght (int): Determine the lenght of the final string.
	"""

	string = ""

	for n in range(lenght):

		string += chr(randint(65,90) + 32)

	return string


def is_database(folder: str) -> bool:
	"""
	Check if a folder contain the content of a database.

	Params:
		folder (str): The input folder to check.
	
	Returns:
		True: If the folder exist and contain at least database.xml
		False: If the folder does not exist or not contain databse.xml
	"""

	return (check_directory(folder) and check_file(join_path(folder, "database.xml")))


def load_database(database: Database, folder: str) -> None:
	"""
	Append inside a database all the content of a folder that contain database data.

	If the folder does not contain a database an exception will be raised.

	Params:
		databse (Dabatase): The database to fill.
		folder (str): The folder that contain the database.
	"""

	if (is_database(folder) == False):
		raise Exception(f"The folder '{folder}' does not contain a database.")
	

	database_file = join_path(folder, "database.xml")
	with open(database_file, "r") as file:
		root = parse_xml(file.read())
	
	
	line_count = 0
	for element in root:
		line_count += 1
		
		if (element.tag == "key"):

			if (not "name" in element.attrib):
				raise Exception(f"Attribute 'name' is missing from the key at line '{line_count}'")
			
			if (not "src" in element.attrib):
				raise Exception(f"Attribute 'src' is missing from the key at line '{line_count}'")


			key = Key(database, element.attrib["name"])
			key._src = element.attrib["src"]
			database._keys.append(key)


def save_database(database: Database, folder: str) -> None:
	"""
	Will save all the content of a database inside the input folder.

	If the folder does not exist it will be created.

	Params:
		database (Database): The database to save.
		folder (str): Where to save the database.
	"""

	key_folder = join_path(folder, "keys")

	if (check_directory(folder) == False):
		make_directory(folder)
		make_directory(key_folder)

	elif (check_directory(key_folder) == False):
		make_directory(key_folder)
	

	# Save all keys first, some of them will also remove themself and stuff.
	for key in tuple(database._keys):
		key.save()
	

	database_file = XmlElement("database")

	for key in database._keys:
		key_element = XmlElement("key")
		key_element.attrib = { "name":key._name, "src":key._src }

		database_file.append(key_element)
	

	tree = XmlTree(database_file)
	xml_indent(tree, "\t")
	tree.write(join_path(database._folder, "database.xml"))


# -------------------------------------------------

