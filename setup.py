from setuptools import setup
from setuptools.command.install import install

class setup_nltk(install):
	def run(self):
		install.run(self)
		import nltk	
		print "  Downloading all the NLTK files. This may take some time..."
                nltk.downloader.download("all")
                print "    Done."

setup(
	name="Provglish",
	version="0.3.2",
	author="Darren Richardson",
	packages=["provglish","provglish.tests"],
	package_data={"provglish":["prov.owl",]},
	scripts=["bin/prov-o-query","bin/prov2ce"],
	license="LICENSE.txt",
	description="Converting PROV to Controlled English",
	long_description=open("README.md").read(),
	cmdclass={"install": setup_nltk},
	install_requires=[
		"rdflib >= 4.1.2",
		"inflect >= 0.2.4",
		"nltk >= 2.7.6",
	],
	requires=[
		"rdflib (>=4.1.2)",
		"inflect (>=0.2.4)",
		"nltk (>=2.7.6)",
	],
)
