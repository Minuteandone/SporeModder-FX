"""
Name registry system for DBPF files - matches the Java implementation's HashManager.

This module provides name lookup functionality using registry files:
- reg_file.txt: Maps file/instance names to their FNV hashes
- reg_type.txt: Maps type names (extensions) to their hashes
- reg_property.txt: Maps property names to their hashes
"""

import os
from typing import Dict, Optional, Tuple


class NameRegistry:
    """A registry that maps between hash values and string names."""

    def __init__(self):
        """Initialize an empty registry."""
        self.hashes: Dict[str, int] = {}  # Map from name to hash
        self.names: Dict[int, str] = {}   # Map from hash to name

    def add(self, name: str, hash_value: int) -> None:
        """Add a name-hash pair to the registry."""
        name_lower = name.lower()
        self.hashes[name_lower] = hash_value
        self.names[hash_value] = name

    def get_name(self, hash_value: int) -> Optional[str]:
        """Get the name for a given hash, or None if not found."""
        return self.names.get(hash_value)

    def get_hash(self, name: str) -> Optional[int]:
        """Get the hash for a given name, or None if not found."""
        return self.hashes.get(name.lower())

    def read_file(self, filepath: str) -> bool:
        """
        Read a registry file. Returns True if successful.
        
        Format: Each line is either:
        - name
        - name\thash (name followed by tab and hex hash like 0x12345678)
        - name~\thash (alias format - name ending with ~ and hash)
        """
        if not os.path.exists(filepath):
            return False

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    if '\t' in line:
                        # Format: name\thash
                        parts = line.split('\t')
                        name = parts[0].strip()
                        try:
                            # Parse hex hash (e.g., "0x12345678")
                            hash_str = parts[1].strip()
                            if hash_str.startswith('0x') or hash_str.startswith('0X'):
                                hash_value = int(hash_str, 16)
                            else:
                                hash_value = int(hash_str, 16)
                            self.add(name, hash_value)
                        except (ValueError, IndexError):
                            # Skip lines with invalid hash format
                            continue
                    else:
                        # Format: just a name (no hash specified)
                        # These will be hashed with FNV if needed
                        pass

            return True
        except Exception as e:
            print(f"Error reading registry file {filepath}: {e}")
            return False


class HashManager:
    """
    Manages hash operations and name registries, matching the Java implementation.
    Uses FNV-1a hashing for generating hashes from names.
    """

    # FNV-1a constants for 32-bit hash
    FNV_32_PRIME = 0x01000193
    FNV_32_OFFSET_BASIS = 0x811c9dc5

    def __init__(self, base_path: str = "."):
        """
        Initialize the hash manager with registry files from the base path.

        Args:
            base_path: Path to the directory containing registry files
        """
        self.base_path = base_path
        self.file_registry = NameRegistry()      # reg_file.txt
        self.type_registry = NameRegistry()      # reg_type.txt
        self.property_registry = NameRegistry()  # reg_property.txt
        self.project_registry = NameRegistry()   # Dynamic project registry

        # Load registry files
        self._load_registries()

    def _load_registries(self) -> None:
        """Load all registry files."""
        self.file_registry.read_file(os.path.join(self.base_path, "reg_file.txt"))
        self.type_registry.read_file(os.path.join(self.base_path, "reg_type.txt"))
        self.property_registry.read_file(os.path.join(self.base_path, "reg_property.txt"))

    @staticmethod
    def fnv_hash(text: str) -> int:
        """
        Calculate FNV-1a hash for a string (32-bit).

        Args:
            text: The string to hash

        Returns:
            The FNV hash as a 32-bit unsigned integer
        """
        if text is None:
            return -1

        hash_value = HashManager.FNV_32_OFFSET_BASIS
        for char in text:
            hash_value ^= ord(char)
            hash_value = (hash_value * HashManager.FNV_32_PRIME) & 0xffffffff

        return hash_value

    def get_file_name(self, hash_value: int) -> str:
        """
        Get the file/instance name for a hash from registry files.

        If not found in registry, returns hexadecimal representation.
        Matches Java's getFileName() method.
        """
        # Try file registry first, then project registry
        name = self.file_registry.get_name(hash_value)
        if name:
            return name

        name = self.project_registry.get_name(hash_value)
        if name:
            return name

        # Fall back to hex representation
        return f"0x{hash_value:08X}"

    def get_type_name(self, hash_value: int) -> str:
        """
        Get the type (extension) name for a hash from reg_type.txt.

        If not found in registry, returns hexadecimal representation.
        Matches Java's getTypeName() method.
        """
        name = self.type_registry.get_name(hash_value)
        if name:
            return name

        name = self.project_registry.get_name(hash_value)
        if name:
            return name

        # Fall back to hex representation
        return f"0x{hash_value:08X}"

    def get_property_name(self, hash_value: int) -> str:
        """
        Get the property name for a hash from reg_property.txt.

        If not found in registry, returns hexadecimal representation.
        Matches Java's getPropName() method.
        """
        name = self.property_registry.get_name(hash_value)
        if name:
            return name

        name = self.project_registry.get_name(hash_value)
        if name:
            return name

        # Fall back to hex representation
        return f"0x{hash_value:08X}"

    def get_file_hash(self, name: str) -> int:
        """
        Get the hash for a file/instance name.

        Supports:
        - Direct name lookup from registry
        - FNV hash calculation if not found
        - Hexadecimal format (0xXXXXXXXX or #XXXXXXXX)

        Matches Java's getFileHash() method.
        """
        if name is None:
            return -1

        # Check if it's a hex literal
        if name.startswith("0x") or name.startswith("0X"):
            try:
                return int(name[2:], 16) & 0xffffffff
            except ValueError:
                pass

        if name.startswith("#"):
            try:
                return int(name[1:], 16) & 0xffffffff
            except ValueError:
                pass

        # Check if it's an alias (ends with ~)
        if name.endswith("~"):
            name_lower = name.lower()
            hash_value = self.file_registry.get_hash(name_lower)
            if hash_value is not None:
                return hash_value
            # If not found, calculate FNV hash
            return self.fnv_hash(name_lower)

        # Calculate FNV hash for regular names
        return self.fnv_hash(name)

    def get_type_hash(self, name: str) -> int:
        """
        Get the hash for a type (extension) name.

        Similar to get_file_hash but uses type registry.
        Matches Java's getTypeHash() method.
        """
        if name is None:
            return -1

        # Check if it's a hex literal
        if name.startswith("0x") or name.startswith("0X"):
            try:
                return int(name[2:], 16) & 0xffffffff
            except ValueError:
                pass

        if name.startswith("#"):
            try:
                return int(name[1:], 16) & 0xffffffff
            except ValueError:
                pass

        # Check registry first
        hash_value = self.type_registry.get_hash(name.lower())
        if hash_value is not None:
            return hash_value

        # Fall back to FNV hash
        return self.fnv_hash(name)

    def hex_to_string_uc(self, hash_value: int) -> str:
        """Convert a hash to uppercase hex string format like '0x12345678'."""
        return f"0x{hash_value:08X}"

    def add_name(self, name: str, hash_value: int, registry_type: str = "file") -> None:
        """
        Add a name to a registry.

        Args:
            name: The name to add
            hash_value: The hash value
            registry_type: Type of registry ('file', 'type', 'property', or 'project')
        """
        if registry_type == "file":
            self.file_registry.add(name, hash_value)
        elif registry_type == "type":
            self.type_registry.add(name, hash_value)
        elif registry_type == "property":
            self.property_registry.add(name, hash_value)
        elif registry_type == "project":
            self.project_registry.add(name, hash_value)


# Global instance of HashManager
_hash_manager = None


def get_hash_manager(base_path: str = ".") -> HashManager:
    """Get or create the global HashManager instance."""
    global _hash_manager
    if _hash_manager is None:
        _hash_manager = HashManager(base_path)
    return _hash_manager


def get_file_name(hash_value: int) -> str:
    """Get the file name for a hash."""
    return get_hash_manager().get_file_name(hash_value)


def get_type_name(hash_value: int) -> str:
    """Get the type name for a hash."""
    return get_hash_manager().get_type_name(hash_value)


def get_property_name(hash_value: int) -> str:
    """Get the property name for a hash."""
    return get_hash_manager().get_property_name(hash_value)


def fnv_hash(text: str) -> int:
    """Calculate FNV-1a hash for a string."""
    return HashManager.fnv_hash(text)
