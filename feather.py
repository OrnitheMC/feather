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
#    'a1.0.5': 'a1.0.5-2149',
#    'a1.0.13_01': 'a1.0.13_01-1444',
#    'a1.0.14': 'a1.0.14-1659',
#    'a1.1.0': 'a1.1.0-131933',
#    'a1.2.3_01': 'a1.2.3_01-0958',
#    'server-a0.2.5': 'server-a0.2.5-1004',
    'a1.0.15': 'a1.0.15~server-a0.1.0',
    'server-a0.1.0': 'a1.0.15~server-a0.1.0',
    'a1.0.16': 'a1.0.16~server-a0.1.1-1707',
    'server-a0.1.1': 'a1.0.16~server-a0.1.1-1707',
    'a1.0.16_01': 'a1.0.16_01~server-a0.1.2_01',
    'server-a0.1.2_01': 'a1.0.16_01~server-a0.1.2_01',
    'a1.0.16_02': 'a1.0.16_02~server-a0.1.3',
    'server-a0.1.3': 'a1.0.16_02~server-a0.1.3',
    'a1.0.17_02': 'a1.0.17_02~server-a0.1.4',
    'server-a0.1.4': 'a1.0.17_02~server-a0.1.4',
    'a1.1.1': 'a1.1.1~server-a0.2.1',
    'server-a0.2.1': 'a1.1.1~server-a0.2.1',
    'a1.2.0': 'a1.2.0~server-a0.2.2',
    'server-a0.2.2': 'a1.2.0~server-a0.2.2',
    'a1.2.0_01': 'a1.2.0_01~server-a0.2.2_01',
    'server-a0.2.2_01': 'a1.2.0_01~server-a0.2.2_01',
    'a1.2.1_01': 'a1.2.1_01~server-a0.2.3',
    'server-a0.2.3': 'a1.2.1_01~server-a0.2.3',
    'a1.2.3': 'a1.2.3~server-a0.2.5-0923',
    'server-a0.2.5': 'a1.2.3~server-a0.2.5-0923',
    'a1.2.3_02': 'a1.2.3_02~server-a0.2.5_01',
    'server-a0.2.5_01': 'a1.2.3_02~server-a0.2.5_01',
    'a1.2.3_04': 'a1.2.3_04~server-a0.2.5_02',
    'server-a0.2.5_02': 'a1.2.3_04~server-a0.2.5_02',
    'a1.2.3_05': 'a1.2.3_05~server-a0.2.6',
    'server-a0.2.6': 'a1.2.3_05~server-a0.2.6',
    'a1.2.4_01': 'a1.2.4_01~server-a0.2.6_02',
    'server-a0.2.6_02': 'a1.2.4_01~server-a0.2.6_02',
    'a1.2.5': 'a1.2.5~server-a0.2.7',
    'server-a0.2.7': 'a1.2.5~server-a0.2.7',
    'a1.2.6': 'a1.2.6~server-a0.2.8',
    'server-a0.2.8': 'a1.2.6~server-a0.2.8',
    'b1.1': 'b1.1-1245',
    'b1.1-client': 'b1.1-1255',
    'b1.3-client': 'b1.3-1750-client',
    'b1.3-server': 'b1.3-1731-server',
    'b1.4': 'b1.4-1507',
    'b1.4-client': 'b1.4-1634',
    'b1.8-pre1-client': 'b1.8-pre1-201109081459',
    'b1.8-pre1': 'b1.8-pre1-201109091357',
    'b1.9-pre3': 'b1.9-pre3-201110061350',
    'b1.9-pre3-client': 'b1.9-pre3-201110061402',
    'b1.9-pre4': 'b1.9-pre4-201110131434',
    'b1.9-pre4-server': 'b1.9-pre4-201110131440',
    '12w05a': '12w05a-1442',
    '1.0': '1.0.0',
    '1.3': '1.3-pre-07261249',
    '1.4': '1.4-pre',
    '1.4.1': '1.4.1-pre-10231538',
    '1.4.3': '1.4.3-pre',
    '13w03a': '13w03a-1647',
    '13w05a': '13w05a-1538',
    '13w06a': '13w06a-1636',
    '13w16a': '13w16a-04192037',
    '13w16b': '13w16b-04232151',
    '13w23b': '13w23b-06080101',
    '1.6': '1.6-pre-06251516',
    '1.6.2': '1.6.2-091847',
    '1.6.3': '1.6.3-pre-171231',
    '13w36a': '13w36a-09051446',
    '13w36b': '13w36b-09061310',
    '13w41b': '13w41b-1523',
    '1.7': '1.7-pre',
    '1.7.1': '1.7.1-pre',
    '1.7.3': '1.7.3-pre',
    '1.7.7': '1.7.7-101331',
    '14w04b': '14w04b-1554',
    '14w27b': '14w27b-07021646',
    '14w34c': '14w34c-08191549',
    '16w50a': '16w50a-1438',
    '1.12-pre3': '1.12-pre3-1409',
    '2point0_red': 'af-2013-red',
    '2point0_blue': 'af-2013-blue',
    '2point0_purple': 'af-2013-purple',
    '15w14a': 'af-2015',
    '1.RV-Pre1': 'af-2016'
}


def main():
    possible_versions = list(set(find_minecraft_versions()))
    versions = []
    tasks = []

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
