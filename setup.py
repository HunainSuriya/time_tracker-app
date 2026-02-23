from setuptools import setup, find_packages

setup(
    name='time_tracker_app',
    version='1.0.0',
    description='Time Tracker App for Frappe',
    author='Hunain Suriya',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=['frappe']
)
