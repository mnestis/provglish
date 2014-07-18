from distutils.core import setup

setup(
	name="Provglish",
	version="0.2.0",
	author="Darren Richardson",
	packages=["provglish","provglish.tests"],
	package_data={"provglish":["prov.owl",]},
	scripts=["bin/prov-o-query","bin/prov2ce"],
	license="LICENSE.txt",
	description="Converting PROV to Controlled English",
	long_desciption=open("README.md").read(),
	install_requires=[
		"rdflib >= 4.1.2",
		"inflect >= 0.2.4",
	],
	requires=[
		"rdflib (>=4.1.2)",
		"inflect (>=0.2.4)",
	],
)
