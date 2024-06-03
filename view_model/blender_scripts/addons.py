import addon_utils
import bpy

addons_name = list(addon_utils.addons_fake_modules.keys())
exts = [a for a in addons_name if addon_utils.check_extension(a)]

print('BEM-EXTENSIONS: ', exts)