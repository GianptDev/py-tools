

# -------------------------------------------------


from csv import reader


# -------------------------------------------------


__author__ = "GianptDev"
__version__ = 1.0


# -------------------------------------------------

# TODO: Extra testing and implement that new feature.


class TranslationTool:
	"""
	Utility to load and manage translations from csv files.
	
	To use it you first store the path of all files that store translations, then you set the locale you wish and use the `load_strings` method.
	
	All translations are stored inside a dictionary that hold the key and the translated string, to get the translated string use the `translate` method.
	"""
	
	
	# -------------------------------------------------
	

	def __init__(self, locale: str = "en") -> None:
		self._locales: tuple = ()
		self._strings: dict = {}
		self._locale: str = locale
	

	# -------------------------------------------------


	@property
	def locales(self) -> "tuple":
		"""
		The list of files wich strings will be loaded, the header of each file must contain a "key" and all locales.
		"""
		
		return self._locales
	
	
	@locales.setter
	def locales(self, locales: "tuple") -> None:
		self._locales = locales
	
	
	@property
	def strings(self) -> "dict":
		"""
		All strings of the current language from all locales.
		
		The content is structured like this:
		- `<key name>:<translated string>`
		"""
		
		return self._strings
	
	
	@strings.setter
	def strings(self, strings: "dict") -> None:
		self._strings = strings
	
	
	@property
	def locale(self) -> "str":
		"""
		The current selected locale, when changed make sure to execute load_strings to update the current set of trasnlations.
		"""
		
		return self._locale
	
	
	@locale.setter
	def locale(self, locale: "str") -> None:
		self._locale = locale


	# -------------------------------------------------


	def add_locale(self, path: "str") -> None:
		"""
		Add a new file to the list of locale files, make sure the file exist and is a csv.
		"""
		
		self._locales = (*self._locales, path,)
	

	def remove_locale(self, path: "str") -> None:
		"""
		Remove a file from the list of locale files.
		"""
		
		self._locales = tuple([s for s in self._locales if s != path])


	def load_strings(self, default_locale: "str" = "en") -> None:
		"""
		Open all locale files and load strings for the current language, every empty string are ignored.
		
		If a string for the current language does not exist or is empty you can choose another language to replace the string.
		
		If the header of the file does not contain the "key" keyword an error is raised, because under that name all string keys are defined.
		"""
		
		self._strings.clear()

		for _locale in self._locales:

			key_index: int = -1
			locale_index: int = -1
			default_index: int = -1
			line_count: int = 0

			with open(_locale, "r") as file:
				content = reader(file)
				
				for row in content:
					
					if (line_count == 0):
						row_count: int = 0
						
						for string in row:
							
							if (string == "key"):
								key_index = row_count
							elif (string == self._locale):
								locale_index = row_count
							elif (string == default_locale):
								default_index = row_count
							
							row_count += 1
					
					else:
						
						if (key_index < 0):
							raise Exception("Failed to find the 'key' section in the file.")
						
						
						if ((locale_index >= 0) and (row[locale_index] != "")):
							self._strings[row[key_index]] = row[locale_index]
						elif ((default_index >= 0) and (row[default_index] != "")):
							self._strings[row[key_index]] = row[default_index]
					
					line_count += 1


	# -------------------------------------------------
	

	def translate(self, key: "str") -> "str":
		"""
		Get the translated version of the key.
		
		If the key does not exist it will return the key.
		"""
		
		return self._strings.get(key, key)
		


# -------------------------------------------------


if (__name__ == "__main__"):
	t = TranslationTool()

	t.add_locale("test.csv")

	t.strings["test"] = "thing"

	print(t.translate("test"))

