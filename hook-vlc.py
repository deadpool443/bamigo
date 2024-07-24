import os
import sys
import vlc

def get_vlc_path():
    return os.path.dirname(vlc.dll._name)

def hook(hook_api):
    vlc_path = get_vlc_path()
    vlc_plugin_path = os.path.join(vlc_path, 'plugins')
    hook_api.add_datas([(vlc_path, '.')])
    hook_api.add_datas([(vlc_plugin_path, 'plugins')])
    os.environ['VLC_PLUGIN_PATH'] = vlc_plugin_path
    if sys.platform.startswith('win'):
        os.add_dll_directory(vlc_path)