import bpy
import json

repos = list(bpy.context.preferences.extensions.repos)
repos_list = [
    {
        'name': r.name,
        'id': r.module,
        'enabled': r.enabled,
        'directory': r.directory,
        'use_custom_directory': r.use_custom_directory,
        'use_remote_url': r.use_remote_url,
        'remote_url': r.remote_url,
        'custom_directory': r.custom_directory,
    }
    for r in repos]

repos_str = json.dumps(repos_list)

print('BEM-REPOS: ',repos_str)