import re


class VersionManager:
    @staticmethod
    def version_tuple(version: str) -> tuple:
        """
        Converts a version string (e.g., "1.2.3") into a tuple of integers.

        Args:
            version (str): The version string (e.g., "1.2.3").

        Returns:
            tuple: A tuple containing the integers extracted from the version string.
        """
        # Use a single regular expression to extract numbers
        version_parts = re.findall(r'\d+', version)
        return tuple(map(int, version_parts))
