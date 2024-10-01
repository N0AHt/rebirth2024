from setuptools import setup, find_packages

# Function to read requirements from requirements.txt
def parse_requirements(filename):
    with open(filename) as f:
        return f.read().splitlines()
    

setup(
    name = 'rebirth',
    version = '0.1',
    packages = find_packages(),
    include_package_data = True,
    install_requires = parse_requirements('requirements.txt')
)