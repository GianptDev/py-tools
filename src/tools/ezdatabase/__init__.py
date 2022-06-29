

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


class Database():
	"""
	Database object that handle everything related to databases.
	"""


	# -------------------------------------------------


	class Key():


		# -------------------------------------------------

		
		def __init__(self, database: "Database", src: str, name: str) -> None:
			

			self.changed: bool = False
			"""
			Mark that the content of the current key has changed and should be saved.
			"""
			
			self.remove: bool = False
			"""
			Mark the key to be removed, when saving it will erase the file instead if it exist.
			"""
			
			self._database = ref(database)
			self._src: str = src
			self._name: str = name
			self._description: Union[str, None] = None
			self._properties: dict[str, any] = {}

			self.load(join_path(database._folder, "keys"))
		

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
		def description(self) -> Union[str, None]:
			"""
			The description of this key.
			"""

			return self._description
		

		@description.setter
		def description(self, value: Union[str, None]) -> None:
			self._description = value
			self.changed = True
		

		@property
		def properties(self) -> dict[str, any]:
			"""
			The properties of this key.
			"""

			return self._properties
		

		@properties.setter
		def properties(self, value: dict[str, any]) -> None:
			self._properties = value
			self.changed = True
		

		@property
		def src(self) -> str:
			"""
			An unique id for the key used internally inside the database.
			"""

			return self._src

		
		# -------------------------------------------------


		def _to_xml(self) -> XmlElement:
			root = XmlElement("key")

			if (self._description != None):
				description = XmlElement("description")
				description.text = self._description
				root.append(description)
			
			if (len(self._properties) > 0):
				properties = XmlElement("properties")
				properties.attrib = self._properties
				root.append(properties)
			
			return root


		def _from_xml(self, root: XmlElement) -> None:

			for element in root:

				if (element.tag == "description"):
					self._description = element.text
					self.changed = True
				
				elif (element.tag == "properties"):
					self._properties = {**self._properties, **element.attrib}
					self.changed = True
			


		# -------------------------------------------------


		def rename(self, name: str) -> None:

			for key in self._database().keys:

				if ((key != self) and (key._name == name)):
					raise Exception(f"Another key is named '{name}'.")
			
			self._name = name
			self.changed = True


		def set_property(self, name: str, value: any) -> None:
			"""
			Change or add a property and mark the key as changed.
			"""
			
			self._properties[name] = value
			self.changed = True
		
		
		def remove_property(self, name: str) -> None:
			"""
			Remove a property and mark the key as changed.
			"""
			
			del self._properties[name]
			self.changed = True
		

		def load(self, path: str) -> None:
			
			src_path = join_path(path, "%s.xml" % self._src)

			if (check_file(src_path) == False):
				return
			
			with open(src_path, "r") as file:
				element = parse_xml(file.read())
			
			self._from_xml(element)

		
		def save(self, path: str) -> None:
			"""
			Save the file with all the content of the key and remove the changed mark.
			"""

			src_path = join_path(path, "%s.xml" % self._src)
			
			if (self.remove == True):

				if (check_file(src_path) == True):
					remove_file(src_path)
			
			else:
				
				if (self.changed == True):
					tree = XmlTree(self._to_xml())
					xml_indent(tree, "\t")
					tree.write(src_path)

			self.changed = False


	# -------------------------------------------------


	def __init__(self, folder: str) -> None:
		

		self._folder: str = folder


		self.keys: list[__class__.Key] = []
		"""
		List of all keys inside the database.
		"""


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


	# -------------------------------------------------



	def _src(self) -> str:

		while(True):
			src = ""

			for n in range(8):
				src += chr(randint(97,122))

			found = False

			for other_key in self.keys:
				
				if (other_key._src == src):
					found = True
					break
			
			if (found == False):
				break

		return src


	def _add_key(self, key: "Database.Key") -> None:
		"""
		Called every time a new key need to be added, it must add the new key in the list.

		- virtual
		"""

		key.rename(key._name)
		self.keys.append(key)


	# -------------------------------------------------


	def add_key(self, name: str) -> Union["Database.Key", None]:
		"""
		Add a new key with the specific name, if another key with the same name already exist the key is not created and None is returned.
		"""

		if (self.get_key(name) != None):
			return None

		key = self.__class__.Key(self, self._src(), name)
		key.changed = True

		self._add_key(key)
		return key
	
	
	def remove_key(self, name: str) -> bool:
		"""
		Remove the key with the specific name.
		"""

		index = 0
		found = False

		for key in self.keys:

			if (key.name == name):
				found = True
				break
			
			index += 1
		
		if (found == False):
			return False
		
		del self.keys[index]
		return True
	
	
	def get_key(self, name: str) -> Union["Database.Key", None]:
		"""
		Get the key with the specific name, the key will be obtained even if marked to be removed.
		"""

		for key in self.keys:

			if (key.name == name):
				return key
		
		return None
	
	
	def is_changed(self) -> bool:
		"""
		Check if a key or something in the database has changed.
		"""

		for key in self.keys:

			if (key.changed == True):
				return True
		
		return False
	
	
	def save(self) -> None:
		"""
		Save the database and all keys.
		"""

		key_folder = join_path(self._folder, "keys")

		if (check_directory(self._folder) == False):
			make_directory(self._folder)
			make_directory(key_folder)

		elif (check_directory(key_folder) == False):
			make_directory(key_folder)
		
		database = XmlElement("database")
		database_keys = XmlElement("keys")
		database.append(database_keys)

		for key in self.keys:
			key_element = XmlElement("key")
			key_element.attrib = {
				"name":key._name,
				"src":key._src
			}

			database_keys.append(key_element)
		
		tree = XmlTree(database)
		xml_indent(tree, "\t")
		tree.write(join_path(self._folder, "database.xml"))
		
		for key in self.keys:
			key.save(key_folder)
	
	
	def load(self) -> None:

		if (check_directory(self._folder) == False):
			return
		
		database = join_path(self._folder, "database.xml")

		if (check_file(database) == False):
			print(f"Nothing to load from 'database.xml' in '{self._folder}'.")
			return


		with open(database, "r") as file:
			root = parse_xml(file.read())
		

		for element in root:

			if (element.tag == "keys"):
				
				for key_element in element:

					if (key_element.tag == "key"):

						if (not "name" in key_element.attrib):
							raise Exception(f"Attribute 'name' missing in key defined in '{database}'.")
						
						if (not "src" in key_element.attrib):
							raise Exception(f"Attribute 'src' missing in key defined in '{database}'.")
						
						key = self.__class__.Key(self, key_element.attrib["src"], key_element.attrib["name"])
						self._add_key(key)


# -------------------------------------------------

