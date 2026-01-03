"""
CMakeLists.txt Parser for C++ Analysis
Extracts compilation settings from CMake to configure Clang analysis accurately.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set


class CMakeParser:
    """Parser for CMakeLists.txt files."""
    
    def __init__(self, cmake_path: Path):
        """
        Initialize CMake parser.
        
        Args:
            cmake_path: Path to CMakeLists.txt file
        """
        self.cmake_path = Path(cmake_path).resolve()
        self.source_dir = self.cmake_path.parent
        self.settings = {}
        
        if self.cmake_path.exists():
            self._parse()
    
    def _parse(self):
        """Parse CMakeLists.txt file."""
        content = self.cmake_path.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
        
        self.settings = {
            'include_dirs': [],
            'definitions': [],
            'cxx_standard': '17',
            'source_files': [],
            'header_files': [],
            'link_directories': [],
            'link_libraries': []
        }
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                i += 1
                continue
            
            # Parse include_directories
            if 'include_directories' in line.lower():
                self._parse_include_directories(line, i, lines)
            
            # Parse add_definitions
            elif 'add_definitions' in line.lower():
                self._parse_definitions(line)
            
            # Parse CMAKE_CXX_STANDARD
            elif 'CMAKE_CXX_STANDARD' in line:
                self._parse_cxx_standard(line)
            
            # Parse set(SOURCES ...)
            elif re.search(r'set\s*\(\s*SOURCES', line, re.IGNORECASE):
                self._parse_file_list(line, i, lines, 'source_files')
            
            # Parse set(HEADERS ...)
            elif re.search(r'set\s*\(\s*HEADERS', line, re.IGNORECASE):
                self._parse_file_list(line, i, lines, 'header_files')
            
            # Parse target_include_directories
            elif 'target_include_directories' in line.lower():
                self._parse_target_include_directories(line)
            
            # Parse target_compile_definitions
            elif 'target_compile_definitions' in line.lower():
                self._parse_target_compile_definitions(line)
            
            i += 1
    
    def _parse_include_directories(self, line: str, line_num: int, all_lines: List[str]):
        """Parse include_directories() command."""
        # Extract arguments
        match = re.search(r'include_directories\s*\((.*?)\)', line, re.IGNORECASE)
        if match:
            args = match.group(1).split()
            for arg in args:
                dir_path = self._resolve_path(arg)
                if dir_path and dir_path.exists():
                    self.settings['include_dirs'].append(str(dir_path))
    
    def _parse_definitions(self, line: str):
        """Parse add_definitions() command."""
        match = re.search(r'add_definitions\s*\((.*?)\)', line, re.IGNORECASE)
        if match:
            args = match.group(1).split()
            for arg in args:
                if arg.startswith('-D'):
                    def_name = arg[2:]
                    # Handle -DVAR=value
                    if '=' in def_name:
                        def_name = def_name.split('=')[0]
                    self.settings['definitions'].append(def_name)
    
    def _parse_cxx_standard(self, line: str):
        """Parse CMAKE_CXX_STANDARD setting."""
        match = re.search(r'CMAKE_CXX_STANDARD\s+(\d+)', line)
        if match:
            self.settings['cxx_standard'] = match.group(1)
    
    def _parse_file_list(self, line: str, start_line: int, all_lines: List[str], key: str):
        """Parse set(SOURCES ...) or set(HEADERS ...) command."""
        i = start_line + 1
        while i < len(all_lines):
            file_line = all_lines[i].strip()
            if file_line.startswith(')'):
                break
            if file_line and not file_line.startswith('#'):
                file_path = self._resolve_path(file_line)
                if file_path and file_path.exists():
                    self.settings[key].append(str(file_path))
            i += 1
    
    def _parse_target_include_directories(self, line: str):
        """Parse target_include_directories() command."""
        # Extract PRIVATE, PUBLIC, INTERFACE directories
        match = re.search(r'target_include_directories\s*\([^)]+\)', line, re.IGNORECASE)
        if match:
            # Extract directory arguments (skip target name and scope keywords)
            parts = line.split()
            for part in parts:
                if part not in ['target_include_directories', '(', 'PRIVATE', 'PUBLIC', 'INTERFACE', ')']:
                    dir_path = self._resolve_path(part)
                    if dir_path and dir_path.exists():
                        self.settings['include_dirs'].append(str(dir_path))
    
    def _parse_target_compile_definitions(self, line: str):
        """Parse target_compile_definitions() command."""
        match = re.search(r'target_compile_definitions\s*\([^)]+\)', line, re.IGNORECASE)
        if match:
            parts = line.split()
            for part in parts:
                if part.startswith('-D') or (not part.startswith('target_compile_definitions') 
                                            and part not in ['(', 'PRIVATE', 'PUBLIC', 'INTERFACE', ')']):
                    if part.startswith('-D'):
                        def_name = part[2:]
                        if '=' in def_name:
                            def_name = def_name.split('=')[0]
                        self.settings['definitions'].append(def_name)
    
    def _resolve_path(self, path_str: str) -> Optional[Path]:
        """Resolve CMake variable references in paths."""
        # Replace CMake variables
        path_str = path_str.replace('${CMAKE_SOURCE_DIR}', str(self.source_dir))
        path_str = path_str.replace('${CMAKE_CURRENT_SOURCE_DIR}', str(self.source_dir))
        path_str = path_str.replace('${CMAKE_CURRENT_LIST_DIR}', str(self.source_dir))
        
        # Handle relative paths
        if not os.path.isabs(path_str):
            path_str = str(self.source_dir / path_str)
        
        return Path(path_str)
    
    def get_compile_args(self, source_file: Path) -> List[str]:
        """
        Get Clang compile arguments for a source file.
        
        Args:
            source_file: Path to source file to analyze
            
        Returns:
            List of compile arguments
        """
        compile_args = []
        
        # C++ standard
        std = self.settings.get('cxx_standard', '17')
        compile_args.append(f'-std=c++{std}')
        
        # Add standard C++ include paths (try common locations)
        standard_include_paths = self._find_standard_include_paths()
        for include_path in standard_include_paths:
            compile_args.append(f'-I{include_path}')
        
        # Include directories from CMake
        for include_dir in self.settings.get('include_dirs', []):
            compile_args.append(f'-I{include_dir}')
        
        # Add source file directory
        compile_args.append(f'-I{source_file.parent}')
        
        # Add source directory
        compile_args.append(f'-I{self.source_dir}')
        
        # Definitions
        for definition in self.settings.get('definitions', []):
            compile_args.append(f'-D{definition}')
        
        return compile_args
    
    def _find_standard_include_paths(self) -> List[str]:
        """Find standard C++ include paths."""
        import sys
        import subprocess
        
        include_paths = []
        
        # Try to get include paths from Clang
        try:
            result = subprocess.run(
                ['clang++', '-E', '-x', 'c++', '-', '-v'],
                input='',
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            # Parse output for include paths
            in_include_section = False
            for line in result.stderr.split('\n'):
                if '#include <...>' in line or 'End of search list' in line:
                    in_include_section = True
                    continue
                if in_include_section and line.strip().startswith('/') or line.strip().startswith('C:'):
                    path = line.strip()
                    if os.path.exists(path):
                        include_paths.append(path)
        except:
            pass
        
        # Fallback: try common Windows paths
        if sys.platform == 'win32':
            common_paths = [
                r'C:\Program Files\LLVM\include\c++\v1',
                r'C:\Program Files (x86)\LLVM\include\c++\v1',
                r'C:\Program Files\Microsoft Visual Studio\*\VC\Tools\MSVC\*\include',
                r'C:\Program Files (x86)\Microsoft Visual Studio\*\VC\Tools\MSVC\*\include',
            ]
            for pattern in common_paths:
                import glob
                matches = glob.glob(pattern)
                include_paths.extend(matches)
        
        return include_paths
    
    def get_all_source_files(self) -> List[Path]:
        """Get all source files listed in CMakeLists.txt."""
        files = []
        for file_path in self.settings.get('source_files', []):
            files.append(Path(file_path))
        return files
    
    def get_all_header_files(self) -> List[Path]:
        """Get all header files listed in CMakeLists.txt."""
        files = []
        for file_path in self.settings.get('header_files', []):
            files.append(Path(file_path))
        return files


def parse_cmake_for_analysis(cmake_path: Path, source_file: Path) -> List[str]:
    """
    Convenience function to parse CMake and get compile args.
    
    Args:
        cmake_path: Path to CMakeLists.txt
        source_file: Path to source file to analyze
        
    Returns:
        List of compile arguments
    """
    parser = CMakeParser(cmake_path)
    return parser.get_compile_args(source_file)

