import setuptools

setuptools.setup(
    name="vkd-client",
    version='v0.1',
    url="https://github.com/landerlini/vkd-client.git",
    author="Lucio Anderlini based on Project Jupyter Contributors",
    description="A client for Virtual Kubelet Dispatcher",
    packages=setuptools.find_packages(),
	keywords=['Jupyter', 'vk-dispatcher'],
	classifiers=['Framework :: Jupyter'],
    install_requires=[
        'jupyter-server-proxy',
        'requests',
        'pyyaml',
        'cyclopts',
        'pandas',
        'jinja2',
        'pydantic',
    ],
    entry_points={
        'jupyter_serverproxy_servers': [
            'vkdclient = vkd_client:setup_vkdclient',
        ],
        'console_scripts': [
            'vkd = vkd_client.__main__:main'
        ]
    },
    # package_data={
    #     '': ['icons/*', 'vkd_client/templates/*.yaml'],
    # },
    # data_files=[
    #     ('vkd_client/templates', ['vkd_client/templates/jobs.yaml']),
    # ]
)