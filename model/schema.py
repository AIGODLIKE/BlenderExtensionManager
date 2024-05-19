from pathlib import Path


class ExtensionsTags():
    """https://docs.blender.org/manual/en/dev/extensions/tags.html"""
    addons: list = ['3D View', 'Add Curve', 'Add Mesh', 'Animation', 'Bake', 'Camera', 'Compositing', 'Development',
                    'Game Engine', 'Geometry Nodes', 'Grease Pencil', 'Import-Export', 'Lighting', 'Material',
                    'Modeling',
                    'Mesh', 'Node', 'Object', 'Paint', 'Pipeline', 'Physics', 'Render', 'Rigging', 'Scene', 'Sculpt',
                    'Sequencer', 'System', 'Text Editor', 'Tracking', 'User Interface', 'UV']
    themes: list = ['Dark', 'Light', 'Colorful', 'Inspired By', 'Print', 'Accessibility', 'High Contrast']


class ExtensionsOptional():
    blender_version_max: str = "5.1.0"
    # * "files" (for access of any filesystem operations)
    # * "network" (for internet access)
    # * "clipboard" (to read and/or write the system clipboard)
    # * "camera" (to capture photos and videos)
    # * "microphone" (to capture audio)
    # permissions = ["files", "network"]
    permissions: list = ['files', 'network', 'clipboard', 'camera', 'microphone']
    # copyright = [
    #   "2002-2024 Developer Name",
    #   "1998 Company Name",
    copyright: list[str]
    # bundle 3rd party Python modules. "./wheels/hexdump-3.3-py3-none-any.whl",
    wheels: list[str]
    # platforms = ["windows-amd64", "macos-arm64", "linux-x86_64"]
    # Other supported platforms: "windows-arm64", "macos-x86_64"
    platforms: list[str]


class ExtensionsType():
    addon = 'add-on'
    theme = 'theme'


class Schema():
    """below attr is must have"""
    id: str
    name: str
    version: str
    tagline: str
    maintainer: str
    website: str
    tags: list  # ExtensionsTags
    license: list
    blender_version_min: str = '4.2.0'
    type: str = 'add-on'
    schema_version: str = '1.0.0'

    def __init__(self, data):
        for k, v in data.items():
            if k in self.__annotations__:
                setattr(self, k, v)
            if k in ExtensionsOptional.__annotations__:
                setattr(self, k, v)

    def to_dict(self) -> dict:
        data = {}
        for k, v in self.__annotations__.items():
            data[k] = getattr(self, k)
        # other attr
        for k, v in ExtensionsOptional.__annotations__.items():
            if hasattr(self, k):
                data[k] = getattr(self, k)
        return data

    @staticmethod
    def search_list(data: dict) -> list:
        # remove
        new_data = data
        keys = ['id', 'name', 'tagline', 'maintainer']
        for k in keys:
            if k not in new_data:
                new_data.pop(k)

        return list(new_data.values())

    @staticmethod
    def write(data: dict, directory: Path) -> bool:
        'write_to a blender_manifest.toml file'
        import tomllib
        try:
            with open(directory.joinpath('blender_manifest.toml'), 'w', encoding='utf-8') as f:
                for k, v in data.items():
                    if isinstance(v, str):
                        # name = "addon_name"
                        f.write(f'{k} = "{v}"\n')
                    elif isinstance(v, list):
                        # ['1','2','3',...]
                        wrap_list = [str(f'"{i}"') for i in v]
                        full_str = ', '.join(wrap_list)
                        f.write(f'{k} = [{full_str}]\n')

        except Exception as e:
            return False
        return True

        # # toml
        # toml_str = tomllib
        # with open(directory.joinpath('blender_manifest.toml'), 'w', encoding='utf-8') as f:
        #     f.write(toml_str)
