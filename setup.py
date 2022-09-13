from setuptools import setup

setup(
    name='langworld_db_data',
    version='0.1.0',
    packages=['tests', 'langworld_db_data', 'langworld_db_data.adders', 'langworld_db_data.writers',
              'langworld_db_data.constants', 'langworld_db_data.filetools', 'langworld_db_data.mdlisters',
              'langworld_db_data.validators', 'langworld_db_data.cldfwriters', 'langworld_db_data.featureprofiletools'],
    url='https://github.com/lemontree210/langworld_db_data/',
    license='CC-BY-4.0',
    author='Dmitry Kolomatskiy',
    author_email='58207913+lemontree210@users.noreply.github.com',
    description='Data files for Jazyki Mira (Languages of the World) database'
)
