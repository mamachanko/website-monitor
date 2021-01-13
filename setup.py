from setuptools import setup

setup(
    name="website_monitor",
    version="0.1",
    py_modules=["website_monitor"],
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
