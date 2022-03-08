from setuptools import setup, find_packages

setup(
    name="dict_graph",
    version="0.1.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=["click", "matplotlib"],
    entry_points={"console_scripts": ["draw_dict = draw_dict:cli"]},
)
