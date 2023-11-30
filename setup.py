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
    ],
    entry_points={
        'jupyter_serverproxy_servers': [
            'vkdclient = vkd_client:setup_vkdclient',
        ],
        'console_scripts': [
            'vkd = vkd_client.cli:main'
        ]
    },
    package_data={
        '': ['icons/*'],
    },
)