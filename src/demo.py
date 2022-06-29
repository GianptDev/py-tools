

from tools.ezdatabase import Database
from tools.translationtool import TranslationTool



def main() -> None:
	
	data = Database("test\\database")

	if (data.load() == False):
		data.save()
	
	for n in range(16):
		data.add_key(str(n + 1))

	print(repr(data))



if (__name__ == "__main__"):
	main()

