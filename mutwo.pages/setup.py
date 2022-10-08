from setuptools import setup

setup(
    name="mutwo.pages",
    install_requires=[
        "mutwo.core>=0.62.0, <0.63.0",
        "mutwo.zimmermann>=0.5.0, <0.6.0",
        "Jinja2",
        # "numpy",
    ],
)
