import os.path
from setuptools import setup, find_packages


# single source of truth for package version
version_ns = {}
with open(os.path.join('portal', 'version.py')) as f:
    exec(f.read(), version_ns)

install_requires = []
with open('requirements.txt') as reqs:
    for line in reqs.readlines():
        req = line.strip()
        if not req or req.startswith('#'):
            continue
        install_requires.append(req)


setup(name='',
      version=version_ns['__version__'],
      description='',
      long_description=open('README.md').read(),
      author='',
      author_email='',
      url='https://github.com/fair-research/fair-research-data-portal',
      packages=find_packages(),
      install_requires=install_requires,
      dependency_links=[
          'git+git@github.com:globusonline/django-globus-portal-framework.git'
          '#egg=globus_portal_framework'],
      include_package_data=True,
      keywords=['portal', 'globus', 'search', 'django'],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      )
