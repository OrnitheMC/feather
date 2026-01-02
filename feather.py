import os
import sys
import subprocess

MAPPINGS_DIR = 'mappings'
GRADLE_TASKS = ['clean', 'enigma', 'enigmaWithoutUnpick', 'build', 'javadoc', 'javadocJar', 'checkMappings',
                'mapMinecraftToIntermediary', 'mapMinecraftToNamed', 'decompileWithCfr', 'decompileWithVineflower',
                'publish', 'loadMappings', 'insertMappings', 'saveMappingsDown', 'saveMappingsUp', 'saveMappings']
GRADLEW = 'gradlew' if os.name == 'nt' else './gradlew'

# some jank to hide versions that are giving problems
UNAVAILABLE_VERSIONS = []
# shortcuts for versions with ugly ids
VERSION_SHORTCUTS = {
    'a1.0.15': 'a1.0.15&server-a0.1.0',
    'server-a0.1.0': 'a1.0.15&server-a0.1.0',
    'a1.0.16': 'a1.0.16&server-a0.1.1-1707',
    'server-a0.1.1': 'a1.0.16&server-a0.1.1-1707',
    'a1.0.16_01': 'a1.0.16_01&server-a0.1.2_01',
    'server-a0.1.2_01': 'a1.0.16_01&server-a0.1.2_01',
    'a1.0.16_02': 'a1.0.16_02&server-a0.1.3',
    'server-a0.1.3': 'a1.0.16_02&server-a0.1.3',
    'a1.0.17_02': 'a1.0.17_02&server-a0.1.4',
    'server-a0.1.4': 'a1.0.17_02&server-a0.1.4',
    'a1.1.1': 'a1.1.1&server-a0.2.1',
    'server-a0.2.1': 'a1.1.1&server-a0.2.1',
    'a1.2.0': 'a1.2.0&server-a0.2.2',
    'server-a0.2.2': 'a1.2.0&server-a0.2.2',
    'a1.2.0_01': 'a1.2.0_01&server-a0.2.2_01',
    'server-a0.2.2_01': 'a1.2.0_01&server-a0.2.2_01',
    'a1.2.1_01': 'a1.2.1_01&server-a0.2.3',
    'server-a0.2.3': 'a1.2.1_01&server-a0.2.3',
    'a1.2.3': 'a1.2.3&server-a0.2.5-0923',
    'server-a0.2.5': 'a1.2.3&server-a0.2.5-0923',
    'a1.2.3_02': 'a1.2.3_02&server-a0.2.5_01',
    'server-a0.2.5_01': 'a1.2.3_02&server-a0.2.5_01',
    'a1.2.3_04': 'a1.2.3_04&server-a0.2.5_02',
    'server-a0.2.5_02': 'a1.2.3_04&server-a0.2.5_02',
    'a1.2.3_05': 'a1.2.3_05&server-a0.2.6',
    'server-a0.2.6': 'a1.2.3_05&server-a0.2.6',
    'a1.2.4_01': 'a1.2.4_01&server-a0.2.6_02',
    'server-a0.2.6_02': 'a1.2.4_01&server-a0.2.6_02',
    'a1.2.5': 'a1.2.5&server-a0.2.7',
    'server-a0.2.7': 'a1.2.5&server-a0.2.7',
    'a1.2.6': 'a1.2.6&server-a0.2.8',
    'server-a0.2.8': 'a1.2.6&server-a0.2.8',
}


def main():
    possible_versions = list(set(find_minecraft_versions()))
    versions = []
    tasks = []
    options = []

    args = sys.argv

    for i in range(1, len(args)):
        arg = args[i]
        parsed_arg = parse_minecraft_version(arg, possible_versions)

        if parsed_arg:
            for version in parsed_arg:
                versions.append(version)
        else:
            if arg in GRADLE_TASKS:
                tasks.append(arg)
            elif arg.startswith('--'):
                options.append(arg)
            else:
                raise Exception('unrecognized arg ' + arg + '!')

    if len(versions) == 0:
        if 'MC_VERSION' in os.environ:
            parsed_arg = parse_minecraft_version(os.environ['MC_VERSION'], possible_versions)

            if parsed_arg:
                for version in parsed_arg:
                    versions.append(version)
            else:
                raise Exception('no minecraft version given!')
        else:
            raise Exception('no minecraft version given!')
    if len(tasks) == 0:
        raise Exception('no gradle tasks given!')

    command = [GRADLEW]
    command.extend(tasks)
    command.extend(options)
    command.append('--stacktrace')

    if len(versions) == 1:
        os.environ['MC_VERSION'] = versions[0]
    else:
        os.environ['MC_VERSIONS'] = ",".join(versions)
    
    subprocess.run(" ".join(command), shell=True, check=True)

def find_minecraft_versions():
    for filename in os.listdir("mappings"):
        if filename.endswith(".tiny"):
            yield filename[:-len(".tiny")]
        elif filename.endswith(".tinydiff"):
            if len(pair := filename[:-len(".tinydiff")].split("#")) == 2:
                yield pair[-1]


def parse_minecraft_version(arg, possible_versions):
    if arg in VERSION_SHORTCUTS.keys():
        return parse_minecraft_version(VERSION_SHORTCUTS[arg], possible_versions)
    versions = []
    if arg in possible_versions:
        versions.append(arg)
    for version in versions:
        if version in UNAVAILABLE_VERSIONS:
            raise Exception('version ' + version + ' is unavailable at the moment!')
    return versions


if __name__ == '__main__':
    main()
