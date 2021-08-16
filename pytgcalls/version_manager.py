import re


class VersionManager:
    @staticmethod
    def version_tuple(v):
        list_version = []
        for vmj in v.split('.'):
            list_d = re.findall('[0-9]+', vmj)
            for vmn in list_d:
                list_version.append(int(vmn))
        return tuple(list_version)
