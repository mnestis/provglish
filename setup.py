import setuptools
from setuptools import setup, find_packages
from setuptools.command.install import install as _install

class post_install(_install):
	def run(self):
		import nltk	
		print "  Downloading all the NLTK files. This may take some time..."
                nltk.downloader.download("maxent_treebank_pos_tagger")
                nltk.downloader.download("averaged_perceptron_tagger")
                print "    Done."

setup(
	name="provglish",
	version="0.4.0",
	author="Darren Richardson",
	packages=find_packages(exclude=["*.tests"]),
	package_data={"provglish":["prov.owl",]},
	scripts=["bin/prov-o-query","bin/prov2ce", "bin/prov2provglish"],
	license="LICENSE.txt",
	description="Converting PROV to Controlled English",
	long_description=open("README.md").read(),
	install_requires=[
		"rdflib >= 4.1.2",
		"inflect >= 0.2.4",
		"nltk >= 2.7.6",
		"nlgserv == 0.2.3",
                "numpy >= 1.8.2",
	],
	requires=[
		"rdflib (>=4.1.2)",
		"inflect (>=0.2.4)",
		"nltk (>=2.7.6)",
		"nlgserv (==0.2.3)",
                "numpy (>=1.8.2)",
	],
        cmdclass={"post_install": post_install},
)
