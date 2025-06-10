from setuptools import setup

setup(
    name="langworld_db_data",
    version="0.1.0",
    packages=[
        "tests",
        "langworld_db_data",
        "langworld_db_data.tools.features",
        "langworld_db_data.tools.featureprofiles",
        "langworld_db_data.tools.listed_values",
        "langworld_db_data.tools.common",
        "langworld_db_data.tools.common.files",
        "langworld_db_data.tools.common.ids",
        "langworld_db_data.constants",
        "langworld_db_data.validators",
        "langworld_db_data.mdlisters",
        "langworld_db_data.export",
        "langworld_db_data.config",
        "langworld_db_data.xslm_vba",
    ],
    url="https://github.com/Jazyki-Mira/langworld_db_data/",
    license="CC-BY-4.0",
    author="Dmitry Kolomatskiy",
    author_email="58207913+lemontree210@users.noreply.github.com",
    description="Data files for Jazyki Mira (Languages of the World) database",
)
