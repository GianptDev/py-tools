

from tools.ezdatabase import Database, load_database
from tools.translationtool import TranslationTool



def main() -> None:
	
	data = Database("test\\database")

	if (data.exist() == True):
		data.load()

	for n in range(16):
		key = data.add_key(str(n))
		
		if (key == None):
			key = data.get_key(str(n))
			print(key.properties)
			continue

		key.properties = {
			"amogus":"123",
			"amogi":"123"
		}
	
	if (data.get_key("amogus") == None):
		data.get_key("1").rename("amogus")
	data.get_key("1").set_property("test", "amog")
	data.get_key("2").removed = True

	data.save()
	

	print(repr(data))



if (__name__ == "__main__"):
	main()

