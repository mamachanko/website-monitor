from setuptools import setup, find_packages

setup(
    name="wm",
    version="0.0.6",
    py_modules=["website_monitor"],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "kafka-python==2.0.2",
        "psycopg2==2.8.6",
        "requests==2.25.1",
        "click==7.1.2",
    ],
    entry_points="""
        [console_scripts]
        wm=website_monitor.cli:wm
    """,
)
