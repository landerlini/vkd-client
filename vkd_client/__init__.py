"""
Return config on servers to start for vkd client

See https://jupyter-server-proxy.readthedocs.io/en/latest/server-process.html
for more information.
"""


def setup_vkdclient():
    return {
        'timeout': 20,
        'port': 8000,
        'new_browser_tab': False,
        'launcher_entry': {
            'title': 'VK dispatcher',
            #'icon_path': os.path.join(os.path.dirname(os.path.abspath(__file__)),
            #                          'icons', 'vscode.svg')
        }
    }