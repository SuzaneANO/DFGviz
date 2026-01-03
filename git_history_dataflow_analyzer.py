"""
Git History Dataflow Analyzer with Safety Guarantees

This module analyzes git history for dataflow changes while ensuring:
1. NEVER modifies git history (commits, branches, tags)
2. NEVER modifies the working directory
3. NEVER modifies HEAD or branch pointers
4. Uses ONLY read-only git operations (git show, git log, git ls-files, git rev-parse)
5. All file operations happen in temporary directories
6. Proper exception handling with guaranteed cleanup
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Callable
import traceback

# Import dataflow analysis modules
try:
    from scalpel_complete_dataflow import run_complete_dataflow_analysis
except ImportError:
    print("Warning: scalpel_complete_dataflow not found", file=sys.stderr)
    run_complete_dataflow_analysis = None

try:
    from clang_complete_dataflow import analyze_cpp_file, CLANG_AVAILABLE
    # Check if Clang is actually available (not just imported)
    if CLANG_AVAILABLE:
        CLANG_ANALYZER_AVAILABLE = True
    else:
        CLANG_ANALYZER_AVAILABLE = False
        analyze_cpp_file = None
except ImportError:
    print("Warning: clang_complete_dataflow not found. C++ analysis will be unavailable.", file=sys.stderr)
    analyze_cpp_file = None
    CLANG_ANALYZER_AVAILABLE = False
except Exception as e:
    print(f"Warning: C++ analyzer initialization failed: {e}", file=sys.stderr)
    analyze_cpp_file = None
    CLANG_ANALYZER_AVAILABLE = False

try:
    from generate_interactive_dataflow import generate_interactive_svg
except ImportError:
    print("Warning: generate_interactive_dataflow not found", file=sys.stderr)
    generate_interactive_svg = None


class SafeGitHistoryAnalyzer:
    """
    Git history analyzer that uses ONLY read-only git operations.
    
    This class guarantees that:
    - Git history is NEVER modified (no commits, rebases, resets, etc.)
    - Working directory is NEVER modified
    - HEAD and branch pointers are NEVER modified
    - Only read-only operations are used: git show, git log, git ls-files, git rev-parse
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        if not (self.repo_path / '.git').exists():
            raise ValueError(f"Not a git repository: {self.repo_path}")
        self.commit_data = {}
        
    def get_file_content_at_commit(self, commit_hash: str, file_path: str) -> Optional[str]:
        """
        Safely get file content at a specific commit using read-only git show.
        
        This is a READ-ONLY operation that does NOT modify:
        - Git history
        - Working directory
        - HEAD or branch pointers
        - Any repository state
        """
        try:
            result = subprocess.run(
                ['git', 'show', f'{commit_hash}:{file_path}'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return None
    
    def analyze_commit_safely(self, commit_hash: str, target_files: List[str], 
                              progress_callback: Optional[Callable] = None) -> Optional[Dict]:
        """
        Analyze a commit safely using ONLY read-only git operations.
        
        This method:
        - Uses read-only git show to get file contents (does NOT modify repo)
        - Creates files in a temporary directory (outside the git repo)
        - Never touches the git repository or working directory
        - Guarantees git history remains unchanged
        """
        if progress_callback:
            progress_callback(f"Analyzing commit {commit_hash[:8]}...")
            
        # Use read-only git show to get file contents
        temp_dir = None
        try:
            temp_dir = tempfile.mkdtemp(prefix=f'git_analysis_{commit_hash[:8]}_')
            temp_files = []
            
            for file_path in target_files:
                # Get relative path from repo root
                rel_path = os.path.relpath(file_path, self.repo_path)
                if rel_path.startswith('..'):
                    # File is outside repo, skip
                    continue
                    
                content = self.get_file_content_at_commit(commit_hash, rel_path)
                if content is not None:
                    # Create file in temp directory
                    temp_file_path = Path(temp_dir) / rel_path
                    temp_file_path.parent.mkdir(parents=True, exist_ok=True)
                    temp_file_path.write_text(content, encoding='utf-8')
                    temp_files.append(str(temp_file_path))
            
            if not temp_files:
                if progress_callback:
                    progress_callback(f"No files found in commit {commit_hash[:8]}")
                return None
            
            # Run dataflow analysis on temp files
            if run_complete_dataflow_analysis:
                try:
                    result = run_complete_dataflow_analysis(
                        temp_files,
                        generate_html=False,
                        force=True,
                        start_server=False,  # Disable server startup in GUI mode
                        target_function=None  # Analyze all functions, not filtered to one
                    )
                    # Verify result has expected structure
                    if result and isinstance(result, dict):
                        # Ensure it has at least a variables key (even if empty)
                        if 'variables' not in result:
                            result['variables'] = {}
                        if 'metadata' not in result:
                            result['metadata'] = {}
                        return result
                    else:
                        if progress_callback:
                            progress_callback(f"Analysis returned invalid result for commit {commit_hash[:8]}")
                        return None
                except Exception as e:
                    if progress_callback:
                        progress_callback(f"Error during analysis for commit {commit_hash[:8]}: {e}")
                    print(f"Error analyzing commit {commit_hash}: {e}", file=sys.stderr)
                    traceback.print_exc()
                    return None
            else:
                if progress_callback:
                    progress_callback(f"Analysis module not available for commit {commit_hash[:8]}")
                return None
                
        except Exception as e:
            print(f"Error analyzing commit {commit_hash}: {e}", file=sys.stderr)
            traceback.print_exc()
            return None
        finally:
            # Always clean up temp directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    print(f"Warning: Could not clean up temp directory {temp_dir}: {e}", file=sys.stderr)
    
    def analyze_all_commits(self, target_files: List[str], 
                           progress_callback: Optional[Callable] = None) -> Dict[str, Dict]:
        """
        Analyze all commits safely using ONLY read-only git operations.
        
        This method does NOT modify the git repository in any way.
        All operations use read-only git commands (git log, git show).
        """
        # Get list of commits using read-only git log
        try:
            result = subprocess.run(
                ['git', 'log', '--oneline', '--all'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            commit_lines = result.stdout.strip().split('\n')
            commits = [line.split()[0] for line in commit_lines if line.strip()]
        except subprocess.CalledProcessError as e:
            print(f"Error getting commit list: {e}", file=sys.stderr)
            return {}
        
        # Analyze commits using only read-only operations
        # No need for GitStatePreserver since we never modify the repo
        results = {}
        total = len(commits)
        
        for i, commit_hash in enumerate(commits):
            if progress_callback:
                progress_callback(f"Processing commit {i+1}/{total}: {commit_hash[:8]}")
            
            result = self.analyze_commit_safely(commit_hash, target_files, progress_callback)
            # Store result if it's a valid dict with expected structure
            if result is not None and isinstance(result, dict):
                # Check if result has actual data (not just empty dict)
                if result.get('variables') or result.get('metadata'):
                    results[commit_hash] = result
                else:
                    # Empty result - log but don't store (or store with a flag)
                    if progress_callback:
                        progress_callback(f"Commit {commit_hash[:8]} has no dataflow data")
            # Don't store None results - they indicate errors or missing files
                
        return results


def find_git_repo_root(file_path: str) -> Optional[str]:
    """Find the git repository root containing the given file"""
    path = Path(file_path).resolve()
    
    # If it's a file, start from its parent directory
    if path.is_file():
        path = path.parent
    
    # Walk up the directory tree to find .git
    while path != path.parent:
        if (path / '.git').exists():
            return str(path)
        path = path.parent
    
    return None


def launch_tkinter_gui(repo_path: str, target_files: Optional[List[str]] = None):
    """Launch Tkinter GUI for git history dataflow analysis"""
    try:
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox, scrolledtext
        import threading
        import json
        import webbrowser
        import http.server
        import socketserver
    except ImportError as e:
        print(f"Error importing tkinter: {e}", file=sys.stderr)
        print("Tkinter may not be installed. On Linux, install python3-tk", file=sys.stderr)
        return
    
    # Check trial period
    try:
        from usage_limiter import is_trial_expired, get_trial_status_message, get_remaining_days
        if is_trial_expired():
            root = tk.Tk()
            root.withdraw()  # Hide main window
            messagebox.showerror("Trial Expired", get_trial_status_message())
            root.destroy()
            return
    except ImportError:
        # If usage_limiter not available, continue without trial check
        pass
    
    class GitHistoryDataflowGUI:
        def __init__(self, root, repo_path: str, initial_files: Optional[List[str]] = None):
            self.root = root
            self.repo_path = Path(repo_path).resolve()
            self.analyzer = None  # Will be created lazily when needed
            self.results = {}
            self.is_analyzing = False
            
            # Try to initialize analyzer, but don't fail if repo is invalid
            try:
                if (self.repo_path / '.git').exists():
                    self.analyzer = SafeGitHistoryAnalyzer(str(self.repo_path))
            except Exception as e:
                # Repo might be invalid, but we'll let user browse for a valid one
                pass
            
            root.title("DFGviz - DataFlow Graph Visualizer")
            root.geometry("1000x700")
            
            # Create main frame
            main_frame = ttk.Frame(root, padding="10")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            root.columnconfigure(0, weight=1)
            root.rowconfigure(0, weight=1)
            main_frame.columnconfigure(1, weight=1)
            main_frame.rowconfigure(2, weight=1)
            
            # Repository path
            ttk.Label(main_frame, text="Repository:").grid(row=0, column=0, sticky=tk.W, pady=5)
            self.repo_var = tk.StringVar(value=str(self.repo_path))
            ttk.Entry(main_frame, textvariable=self.repo_var, width=60).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
            ttk.Button(main_frame, text="Browse", command=self.browse_repo).grid(row=0, column=2, padx=5)
            
            # Language selection
            ttk.Label(main_frame, text="Language:").grid(row=1, column=0, sticky=tk.W, pady=5)
            self.language_var = tk.StringVar(value="Python")
            language_frame = ttk.Frame(main_frame)
            language_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5)
            ttk.Radiobutton(language_frame, text="Python", variable=self.language_var, value="Python", 
                          command=self.on_language_change).pack(side=tk.LEFT, padx=5)
            cpp_radio = ttk.Radiobutton(language_frame, text="C++", variable=self.language_var, value="C++",
                                       command=self.on_language_change)
            cpp_radio.pack(side=tk.LEFT, padx=5)
            if not CLANG_ANALYZER_AVAILABLE:
                cpp_radio.config(state=tk.DISABLED)
                # Try to get more specific error message
                try:
                    from clang_complete_dataflow import CLANG_AVAILABLE
                    if not CLANG_AVAILABLE:
                        ttk.Label(language_frame, text="(Install Clang/LLVM)", foreground="gray").pack(side=tk.LEFT, padx=5)
                    else:
                        ttk.Label(language_frame, text="(C++ analyzer not available)", foreground="gray").pack(side=tk.LEFT, padx=5)
                except:
                    ttk.Label(language_frame, text="(C++ analyzer not available)", foreground="gray").pack(side=tk.LEFT, padx=5)
            
            # Files to analyze
            ttk.Label(main_frame, text="Files to analyze:").grid(row=2, column=0, sticky=tk.W, pady=5)
            files_frame = ttk.Frame(main_frame)
            files_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5)
            files_frame.columnconfigure(0, weight=1)
            
            self.files_listbox = tk.Listbox(files_frame, height=4)
            self.files_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
            
            files_buttons = ttk.Frame(files_frame)
            files_buttons.grid(row=0, column=1, sticky=tk.W)
            ttk.Button(files_buttons, text="Add Files", command=self.add_files).grid(row=0, column=0, pady=2)
            ttk.Button(files_buttons, text="Add File", command=self.add_file).grid(row=1, column=0, pady=2)
            ttk.Button(files_buttons, text="Remove", command=self.remove_file).grid(row=2, column=0, pady=2)
            ttk.Button(files_buttons, text="Remove All", command=self.remove_all_files).grid(row=3, column=0, pady=2)
            ttk.Button(files_buttons, text="Auto-detect", command=self.auto_detect_files).grid(row=4, column=0, pady=2)
            
            # Function to analyze (optional)
            ttk.Label(main_frame, text="Function (optional):").grid(row=3, column=0, sticky=tk.W, pady=5)
            function_frame = ttk.Frame(main_frame)
            function_frame.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5)
            function_frame.columnconfigure(0, weight=1)
            
            self.function_var = tk.StringVar()
            function_entry = ttk.Entry(function_frame, textvariable=self.function_var, width=40)
            function_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
            ttk.Label(function_frame, text="Leave empty to analyze all functions").grid(row=0, column=1, sticky=tk.W)
            
            # Function auto-detect button
            ttk.Button(function_frame, text="Detect Functions", command=self.detect_functions).grid(row=1, column=0, sticky=tk.W, pady=2)
            
            # Progress bar (above notebook)
            progress_bar_frame = ttk.Frame(main_frame)
            progress_bar_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
            progress_bar_frame.columnconfigure(0, weight=1)
            
            ttk.Label(progress_bar_frame, text="Progress:").grid(row=0, column=0, sticky=tk.W)
            self.progress_var = tk.DoubleVar()
            self.progress_bar = ttk.Progressbar(progress_bar_frame, variable=self.progress_var, maximum=100, length=400, mode='determinate')
            self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
            self.progress_label = ttk.Label(progress_bar_frame, text="Ready")
            self.progress_label.grid(row=1, column=1, padx=5)
            
            # Progress and results area
            notebook = ttk.Notebook(main_frame)
            notebook.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
            
            # Progress tab
            progress_frame = ttk.Frame(notebook, padding="10")
            notebook.add(progress_frame, text="Progress")
            self.progress_text = scrolledtext.ScrolledText(progress_frame, height=15, wrap=tk.WORD, font=('Consolas', 9))
            self.progress_text.pack(fill=tk.BOTH, expand=True)
            
            # Configure text colors
            self.progress_text.tag_config("info", foreground="blue")
            self.progress_text.tag_config("success", foreground="green")
            self.progress_text.tag_config("warning", foreground="orange")
            self.progress_text.tag_config("error", foreground="red")
            self.progress_text.tag_config("debug", foreground="gray")
            self.progress_text.tag_config("normal", foreground="black")
            
            # Results tab
            results_frame = ttk.Frame(notebook, padding="10")
            notebook.add(results_frame, text="Results")
            self.results_text = scrolledtext.ScrolledText(results_frame, height=15, wrap=tk.WORD)
            self.results_text.pack(fill=tk.BOTH, expand=True)
            
            # Commits tab
            commits_frame = ttk.Frame(notebook, padding="10")
            notebook.add(commits_frame, text="Commits")
            commits_list_frame = ttk.Frame(commits_frame)
            commits_list_frame.pack(fill=tk.BOTH, expand=True)
            
            self.commits_listbox = tk.Listbox(commits_list_frame, height=10)
            self.commits_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.commits_listbox.bind('<<ListboxSelect>>', self.on_commit_select)
            
            commits_scrollbar = ttk.Scrollbar(commits_list_frame, orient=tk.VERTICAL, command=self.commits_listbox.yview)
            commits_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.commits_listbox.config(yscrollcommand=commits_scrollbar.set)
            
            # Control buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.grid(row=6, column=0, columnspan=3, pady=10)
            
            self.analyze_button = ttk.Button(button_frame, text="Analyze", command=self.start_analysis)
            self.analyze_button.pack(side=tk.LEFT, padx=5)
            
            ttk.Button(button_frame, text="Clear Results", command=self.clear_results).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Export Results", command=self.export_results).pack(side=tk.LEFT, padx=5)
            self.generate_html_button = ttk.Button(button_frame, text="Generate HTML Graphs", command=self.generate_html_graphs)
            self.generate_html_button.pack(side=tk.LEFT, padx=5)
            self.serve_html_button = ttk.Button(button_frame, text="Serve HTML Files", command=self.serve_html_files)
            self.serve_html_button.pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Quit", command=root.quit).pack(side=tk.LEFT, padx=5)
            
            # Track server state
            self.server_thread = None
            self.server_process = None
            self.server_port = None
            self.html_output_dir = None
            
            # Initialize files (after all widgets are created)
            if initial_files:
                for f in initial_files:
                    self.files_listbox.insert(tk.END, f)
            else:
                # Try to auto-detect files, but don't fail if repo is invalid
                try:
                    self.auto_detect_files()
                except Exception as e:
                    # progress_text exists now, so we can log the error
                    self.log(f"Could not auto-detect files: {e}")
            
            # Show trial status if applicable
            try:
                from usage_limiter import get_remaining_days, get_days_since_installation, TRIAL_PERIOD_DAYS
                remaining = get_remaining_days()
                days_used = get_days_since_installation()
                if remaining > 0:
                    self.log(f"Trial: {remaining} days remaining ({days_used}/{TRIAL_PERIOD_DAYS} days used)", "info")
                else:
                    self.log("Trial period expired - please purchase a license", "error")
            except ImportError:
                pass
            
            self.log("GUI initialized", "success")
            self.log(f"Repository: {self.repo_path}", "info")
            if CLANG_ANALYZER_AVAILABLE:
                self.log("C++ analyzer available", "success")
            else:
                self.log("C++ analyzer not available - install Clang to enable C++ support", "warning")
            self.load_commits()
        
        def on_language_change(self):
            """Handle language selection change"""
            language = self.language_var.get()
            self.log(f"Language changed to: {language}", "info")
            # Clear file list when language changes
            self.files_listbox.delete(0, tk.END)
            # Optionally auto-detect files for the new language
            # (User can also manually click "Auto-detect" if they prefer)
            try:
                if self.repo_path.exists() and (self.repo_path / '.git').exists():
                    # Auto-detect files for the new language
                    self.auto_detect_files()
            except Exception:
                # Silently fail - user can manually click Auto-detect if needed
                pass
        
        def log(self, message: str, level: str = "normal"):
            """Add message to progress log with color coding
            
            Args:
                message: The log message
                level: One of "info", "success", "warning", "error", "debug", "normal"
            """
            # Determine tag based on message content if level not specified
            if level == "normal":
                message_lower = message.lower()
                if "error" in message_lower or "failed" in message_lower or "exception" in message_lower:
                    level = "error"
                elif "warning" in message_lower or "warn" in message_lower:
                    level = "warning"
                elif "complete" in message_lower or "success" in message_lower or "[ok]" in message_lower:
                    level = "success"
                elif "debug" in message_lower or "[debug]" in message_lower:
                    level = "debug"
                elif "info" in message_lower or "[info]" in message_lower or "starting" in message_lower:
                    level = "info"
            
            # Insert message with appropriate tag
            start_pos = self.progress_text.index(tk.END)
            self.progress_text.insert(tk.END, f"{message}\n", level)
            self.progress_text.see(tk.END)
            self.root.update_idletasks()
        
        def _ensure_analyzer(self, silent: bool = False) -> bool:
            """Ensure analyzer is initialized. Returns True if successful, False otherwise.
            
            Args:
                silent: If True, don't show error messageboxes (for startup)
            """
            if self.analyzer is not None:
                return True
            
            # Try to initialize analyzer
            try:
                if (self.repo_path / '.git').exists():
                    self.analyzer = SafeGitHistoryAnalyzer(str(self.repo_path))
                    return True
                else:
                    if not silent:
                        messagebox.showerror("Error", f"Not a git repository: {self.repo_path}\nPlease select a valid git repository using the Browse button.")
                    else:
                        self.log(f"Not a git repository: {self.repo_path}. Please select a valid repository.", "warning")
                    return False
            except Exception as e:
                if not silent:
                    messagebox.showerror("Error", f"Failed to initialize git repository: {e}\nPlease select a valid git repository using the Browse button.")
                else:
                    self.log(f"Could not initialize git repository: {e}. Please select a valid repository.", "warning")
                return False
        
        def browse_repo(self):
            """Browse for repository directory"""
            path = filedialog.askdirectory(title="Select Git Repository", initialdir=str(self.repo_path))
            if path:
                try:
                    self.repo_path = Path(path).resolve()
                    self.repo_var.set(str(self.repo_path))
                    self.analyzer = SafeGitHistoryAnalyzer(str(self.repo_path))
                    self.log(f"Repository changed to: {self.repo_path}", "info")
                    self.load_commits()
                except Exception as e:
                    messagebox.showerror("Error", f"Invalid repository: {e}")
        
        def add_file(self):
            """Add a single file to analyze"""
            if not self.repo_path.exists():
                messagebox.showerror("Error", "Please select a valid repository first")
                return
            
            language = self.language_var.get()
            if language == "Python":
                filetypes = [("Python files", "*.py"), ("All files", "*.*")]
            else:  # C++
                filetypes = [
                    ("C++ files", "*.cpp *.h *.hpp *.cc *.cxx"),
                    ("C++ source", "*.cpp"),
                    ("C++ headers", "*.h *.hpp"),
                    ("All files", "*.*")
                ]
            
            file_path = filedialog.askopenfilename(
                title="Select File to Analyze",
                initialdir=str(self.repo_path),
                filetypes=filetypes
            )
            if file_path:
                rel_path = os.path.relpath(file_path, self.repo_path)
                if rel_path.startswith('..'):
                    messagebox.showerror("Error", "File must be within the repository")
                else:
                    self.files_listbox.insert(tk.END, file_path)
        
        def add_files(self):
            """Add multiple files to analyze"""
            if not self.repo_path.exists():
                messagebox.showerror("Error", "Please select a valid repository first")
                return
            
            language = self.language_var.get()
            if language == "Python":
                filetypes = [("Python files", "*.py"), ("All files", "*.*")]
            else:  # C++
                filetypes = [
                    ("C++ files", "*.cpp *.h *.hpp *.cc *.cxx"),
                    ("C++ source", "*.cpp"),
                    ("C++ headers", "*.h *.hpp"),
                    ("All files", "*.*")
                ]
            
            file_paths = filedialog.askopenfilenames(
                title="Select Files to Analyze",
                initialdir=str(self.repo_path),
                filetypes=filetypes
            )
            if file_paths:
                added_count = 0
                for file_path in file_paths:
                    rel_path = os.path.relpath(file_path, self.repo_path)
                    if rel_path.startswith('..'):
                        messagebox.showwarning("Warning", f"File {os.path.basename(file_path)} is outside repository, skipping")
                    else:
                        # Check if already in list
                        existing = self.files_listbox.get(0, tk.END)
                        if file_path not in existing:
                            self.files_listbox.insert(tk.END, file_path)
                            added_count += 1
                if added_count > 0:
                    self.log(f"Added {added_count} file(s)", "success")
        
        def detect_functions(self):
            """Detect functions in selected files and populate dropdown"""
            target_files = self.get_target_files()
            if not target_files:
                messagebox.showwarning("Warning", "Please select at least one file first")
                return
            
            language = self.language_var.get()
            
            try:
                if language == "Python":
                    # Run quick analysis to detect functions
                    if run_complete_dataflow_analysis:
                        self.log("Detecting functions in selected files...")
                        result = run_complete_dataflow_analysis(
                            target_files=target_files,
                            generate_html=False,
                            force=False,
                            target_function=None,
                            start_server=False
                        )
                        
                        if result and 'metadata' in result:
                            defined_functions = result.get('metadata', {}).get('functions', [])
                            if not defined_functions:
                                # Try alternative key
                                defined_functions = result.get('metadata', {}).get('defined_functions', [])
                            
                            if defined_functions:
                                # Create a popup window to select function
                                func_window = tk.Toplevel(self.root)
                                func_window.title("Select Function")
                                func_window.geometry("400x300")
                                
                                ttk.Label(func_window, text="Select a function:").pack(pady=5)
                                
                                func_listbox = tk.Listbox(func_window, height=10)
                                func_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
                                
                                for func in sorted(defined_functions):
                                    func_listbox.insert(tk.END, func)
                                
                                def select_function():
                                    selection = func_listbox.curselection()
                                    if selection:
                                        selected_func = func_listbox.get(selection[0])
                                        self.function_var.set(selected_func)
                                        func_window.destroy()
                                        self.log(f"Selected function: {selected_func}")
                                
                                ttk.Button(func_window, text="Select", command=select_function).pack(pady=5)
                                ttk.Button(func_window, text="Cancel", command=func_window.destroy).pack(pady=2)
                                
                                self.log(f"Found {len(defined_functions)} function(s)", "success")
                            else:
                                messagebox.showinfo("Info", "No functions found in selected files")
                                self.log("No functions detected", "warning")
                        else:
                            messagebox.showerror("Error", "Could not analyze files to detect functions")
                    else:
                        messagebox.showerror("Error", "Scalpel analysis module not available")
                else:  # C++
                    if analyze_cpp_file:
                        self.log("Detecting functions in C++ files...")
                        # Analyze first file to get functions
                        if target_files:
                            result = analyze_cpp_file(
                                filepath=target_files[0],
                                generate_html=False,
                                start_server=False
                            )
                            
                            if result and 'metadata' in result:
                                defined_functions = result.get('metadata', {}).get('functions', [])
                                
                                if defined_functions:
                                    # Create a popup window to select function
                                    func_window = tk.Toplevel(self.root)
                                    func_window.title("Select Function")
                                    func_window.geometry("400x300")
                                    
                                    ttk.Label(func_window, text="Select a function:").pack(pady=5)
                                    
                                    func_listbox = tk.Listbox(func_window, height=10)
                                    func_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
                                    
                                    for func in sorted(defined_functions):
                                        func_listbox.insert(tk.END, func)
                                    
                                    def select_function():
                                        selection = func_listbox.curselection()
                                        if selection:
                                            selected_func = func_listbox.get(selection[0])
                                            self.function_var.set(selected_func)
                                            func_window.destroy()
                                            self.log(f"Selected function: {selected_func}")
                                    
                                    ttk.Button(func_window, text="Select", command=select_function).pack(pady=5)
                                    ttk.Button(func_window, text="Cancel", command=func_window.destroy).pack(pady=2)
                                    
                                    self.log(f"Found {len(defined_functions)} function(s)", "success")
                                else:
                                    messagebox.showinfo("Info", "No functions found in selected files")
                                    self.log("No functions detected", "warning")
                            else:
                                messagebox.showerror("Error", "Could not analyze C++ files to detect functions")
                        else:
                            messagebox.showerror("Error", "No files selected")
                    else:
                        messagebox.showerror("Error", "Clang analysis module not available")
            except Exception as e:
                messagebox.showerror("Error", f"Error detecting functions: {e}")
                self.log(f"Error detecting functions: {e}", "error")
        
        def remove_file(self):
            """Remove selected file from list"""
            selection = self.files_listbox.curselection()
            if selection:
                self.files_listbox.delete(selection[0])
        
        def remove_all_files(self):
            """Remove all files from list"""
            if self.files_listbox.size() > 0:
                self.files_listbox.delete(0, tk.END)
                self.log("Removed all files from list", "info")
        
        def auto_detect_files(self):
            """Auto-detect files in repository based on selected language"""
            if not self._ensure_analyzer():
                return
            
            language = self.language_var.get()
            try:
                if language == "Python":
                    result = subprocess.run(
                        ['git', 'ls-files', '*.py'],
                        cwd=str(self.repo_path),
                        capture_output=True,
                        text=True,
                        check=True,
                        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                    )
                    files = [os.path.join(str(self.repo_path), f) for f in result.stdout.strip().split('\n') if f]
                    file_type = "Python"
                else:  # C++
                    # First, try to find and parse CMakeLists.txt
                    cmake_path = self.repo_path / "CMakeLists.txt"
                    files = []
                    cmake_used = False
                    
                    if cmake_path.exists():
                        try:
                            # Try to import CMake parser
                            try:
                                from cmake_parser import CMakeParser
                                parser = CMakeParser(cmake_path)
                                
                                # Get source files from CMake
                                source_files = parser.get_all_source_files()
                                header_files = parser.get_all_header_files()
                                
                                # Combine source and header files
                                cmake_files = source_files + header_files
                                
                                # Convert to absolute paths and verify they exist
                                for file_path in cmake_files:
                                    abs_path = Path(file_path)
                                    if not abs_path.is_absolute():
                                        abs_path = self.repo_path / abs_path
                                    
                                    if abs_path.exists():
                                        files.append(str(abs_path))
                                
                                if files:
                                    cmake_used = True
                                    if hasattr(self, 'progress_text'):
                                        self.log(f"Found CMakeLists.txt - using CMake file list", "info")
                            except ImportError:
                                # CMake parser not available, fall back to git search
                                if hasattr(self, 'progress_text'):
                                    self.log("CMake parser not available, using git file search", "warning")
                            except Exception as e:
                                # CMake parsing failed, fall back to git search
                                if hasattr(self, 'progress_text'):
                                    self.log(f"CMake parsing failed: {e}, using git file search", "warning")
                        except Exception as e:
                            if hasattr(self, 'progress_text'):
                                self.log(f"Error parsing CMakeLists.txt: {e}, using git file search", "warning")
                    
                    # Fall back to git-based detection if CMake wasn't used or didn't find files
                    if not cmake_used or not files:
                        # Get C++ source files
                        result_cpp = subprocess.run(
                            ['git', 'ls-files', '*.cpp', '*.cc', '*.cxx', '*.c++'],
                            cwd=str(self.repo_path),
                            capture_output=True,
                            text=True,
                            check=False,
                            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                        )
                        # Get C++ header files
                        result_h = subprocess.run(
                            ['git', 'ls-files', '*.h', '*.hpp', '*.hh', '*.hxx'],
                            cwd=str(self.repo_path),
                            capture_output=True,
                            text=True,
                            check=False,
                            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                        )
                        files = []
                        if result_cpp.stdout:
                            files.extend([os.path.join(str(self.repo_path), f) for f in result_cpp.stdout.strip().split('\n') if f])
                        if result_h.stdout:
                            files.extend([os.path.join(str(self.repo_path), f) for f in result_h.stdout.strip().split('\n') if f])
                    
                    file_type = "C++"
                    if cmake_used:
                        file_type = "C++ (from CMake)"
                
                self.files_listbox.delete(0, tk.END)
                for f in files:
                    self.files_listbox.insert(tk.END, f)
                
                # Only log if progress_text exists (it should, but be safe)
                if hasattr(self, 'progress_text'):
                    if files:
                        self.log(f"Auto-detected {len(files)} {file_type} file(s)", "success")
                    else:
                        self.log("No files found to analyze", "warning")
            except Exception as e:
                error_msg = f"Failed to auto-detect files: {e}"
                if hasattr(self, 'progress_text'):
                    self.log(error_msg, "error")
                else:
                    # Fallback to messagebox if progress_text doesn't exist yet
                    try:
                        messagebox.showerror("Error", error_msg)
                    except:
                        print(error_msg, file=sys.stderr)
        
        def load_commits(self):
            """Load list of commits"""
            # Don't show error popup on startup - just silently fail
            if not self._ensure_analyzer(silent=True):
                return
            try:
                result = subprocess.run(
                    ['git', 'log', '--oneline', '--all'],
                    cwd=str(self.repo_path),
                    capture_output=True,
                    text=True,
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                commit_lines = result.stdout.strip().split('\n')
                commits = [line.split()[0] for line in commit_lines if line.strip()]
                
                self.commits_listbox.delete(0, tk.END)
                for commit in commits:
                    self.commits_listbox.insert(tk.END, commit)
                
                self.log(f"Loaded {len(commits)} commit(s)", "success")
            except Exception as e:
                self.log(f"Error loading commits: {e}", "error")
        
        def get_target_files(self) -> List[str]:
            """Get list of files to analyze"""
            files = []
            for i in range(self.files_listbox.size()):
                files.append(self.files_listbox.get(i))
            return files
        
        def start_analysis(self):
            """Start analysis in background thread"""
            if self.is_analyzing:
                messagebox.showwarning("Warning", "Analysis already in progress")
                return
            
            # Ensure analyzer is initialized
            if not self._ensure_analyzer():
                return
            
            target_files = self.get_target_files()
            if not target_files:
                messagebox.showerror("Error", "Please select at least one file to analyze")
                return
            
            # Get target function if specified
            target_function = self.function_var.get().strip()
            if not target_function:
                target_function = None
            
            if target_function:
                self.log(f"Analyzing function: {target_function}")
            
            self.is_analyzing = True
            self.analyze_button.config(state=tk.DISABLED)
            self.results = {}
            self.results_text.delete(1.0, tk.END)
            
            # Reset progress bar
            self.progress_var.set(0)
            self.progress_label.config(text="Starting...")
            
            def analyze_thread():
                try:
                    def progress_callback(msg):
                        self.root.after(0, lambda: self.log(msg))
                    
                    def update_progress(current, total, status=""):
                        """Update progress bar"""
                        if total > 0:
                            percent = (current / total) * 100
                            self.root.after(0, lambda: self.progress_var.set(percent))
                            self.root.after(0, lambda: self.progress_label.config(text=f"{current}/{total} {status}"))
                        else:
                            self.root.after(0, lambda: self.progress_label.config(text=status))
                    
                    self.root.after(0, lambda: self.log("Starting analysis...", "info"))
                    self.root.after(0, lambda: update_progress(0, 0, "Starting..."))
                    
                    # Get language
                    language = self.language_var.get()
                    
                    # If target_function is specified, analyze current files directly (not git history)
                    if target_function:
                        self.root.after(0, lambda: update_progress(0, 0, "Analyzing function..."))
                        
                        if language == "Python":
                            self.root.after(0, lambda: self.log(f"Running Scalpel analysis on function '{target_function}'...", "info"))
                            if run_complete_dataflow_analysis:
                                result = run_complete_dataflow_analysis(
                                    target_files=target_files,
                                    generate_html=True,  # Generate HTML for function analysis
                                    force=True,
                                    target_function=target_function,
                                    start_server=False  # Don't start server in GUI mode
                                )
                                if result:
                                    # Store result as if it were a commit (use 'current' as key)
                                    self.results['current'] = result
                                    self.root.after(0, lambda: self.progress_var.set(100))
                                    self.root.after(0, lambda: self.progress_label.config(text="Complete!"))
                                    self.root.after(0, lambda: self.log(f"Analysis complete for function '{target_function}'", "success"))
                                    self.root.after(0, lambda: self.display_results({'current': result}))
                                else:
                                    self.root.after(0, lambda: self.log("Analysis returned no results", "warning"))
                            else:
                                self.root.after(0, lambda: self.log("Error: Scalpel analysis module not available", "error"))
                        else:  # C++
                            self.root.after(0, lambda: self.log(f"Running Clang analysis on function '{target_function}'...", "info"))
                            if analyze_cpp_file:
                                # Analyze first file (C++ analyzer handles one file at a time)
                                if target_files:
                                    result = analyze_cpp_file(
                                        filepath=target_files[0],
                                        target_function=target_function,
                                        generate_html=True,
                                        start_server=False
                                    )
                                    if result:
                                        self.results['current'] = result
                                        self.root.after(0, lambda: self.progress_var.set(100))
                                        self.root.after(0, lambda: self.progress_label.config(text="Complete!"))
                                        self.root.after(0, lambda: self.log(f"C++ analysis complete for function '{target_function}'", "success"))
                                        self.root.after(0, lambda: self.display_results({'current': result}))
                                    else:
                                        self.root.after(0, lambda: self.log("C++ analysis returned no results", "warning"))
                                else:
                                    self.root.after(0, lambda: self.log("No files selected for C++ analysis", "error"))
                            else:
                                self.root.after(0, lambda: self.log("Error: Clang analysis module not available", "error"))
                    else:
                        # Analyze git history (all commits)
                        # Get total commits first for progress tracking
                        try:
                            result = subprocess.run(
                                ['git', 'log', '--oneline', '--all'],
                                cwd=str(self.repo_path),
                                capture_output=True,
                                text=True,
                                check=True,
                                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                            )
                            total_commits = len([line for line in result.stdout.strip().split('\n') if line.strip()])
                        except:
                            total_commits = 0
                        
                        # Check language for git history analysis
                        if language == "C++":
                            # For C++, analyze current files only (git history analysis for C++ requires compilation flags)
                            self.root.after(0, lambda: self.log("C++ git history analysis not fully supported - analyzing current files only", "warning"))
                            if analyze_cpp_file:
                                results = {}
                                for i, file_path in enumerate(target_files):
                                    self.root.after(0, lambda f=file_path, idx=i: update_progress(idx+1, len(target_files), f"Analyzing {os.path.basename(f)}"))
                                    self.root.after(0, lambda f=file_path: self.log(f"Analyzing C++ file: {f}", "info"))
                                    result = analyze_cpp_file(
                                        filepath=file_path,
                                        generate_html=True,
                                        start_server=False
                                    )
                                    if result:
                                        results[f'file_{i}'] = result
                                
                                self.results = results
                                self.root.after(0, lambda: self.progress_var.set(100))
                                self.root.after(0, lambda: self.progress_label.config(text=f"Complete! {len(results)} file(s)"))
                                self.root.after(0, lambda: self.display_results(results))
                                self.root.after(0, lambda: self.log(f"\nC++ analysis complete! Analyzed {len(results)} file(s)", "success"))
                            else:
                                self.root.after(0, lambda: self.log("Error: Clang analysis module not available", "error"))
                        else:
                            # Python git history analysis
                            # Custom progress callback that updates both log and progress bar
                            commit_count = [0]  # Use list to allow modification in nested function
                            def enhanced_progress_callback(msg):
                                progress_callback(msg)
                                # Try to extract commit number from message
                                if "Processing commit" in msg:
                                    try:
                                        # Extract "X/Y" from "Processing commit X/Y: hash"
                                        parts = msg.split("Processing commit")[1].split(":")[0].strip()
                                        if "/" in parts:
                                            current, total = parts.split("/")
                                            commit_count[0] = int(current)
                                            update_progress(int(current), int(total), "commits")
                                    except:
                                        pass
                            
                            results = self.analyzer.analyze_all_commits(target_files, progress_callback=enhanced_progress_callback)
                            self.results = results
                            self.root.after(0, lambda: self.progress_var.set(100))
                            self.root.after(0, lambda: self.progress_label.config(text=f"Complete! {len(results)} commit(s)"))
                            self.root.after(0, lambda: self.display_results(results))
                            self.root.after(0, lambda: self.log(f"\nAnalysis complete! Analyzed {len(results)} commit(s)", "success"))
                except Exception as e:
                    self.root.after(0, lambda: self.log(f"Error during analysis: {e}", "error"))
                    self.root.after(0, lambda: self.log(traceback.format_exc(), "error"))
                finally:
                    self.is_analyzing = False
                    self.root.after(0, lambda: self.analyze_button.config(state=tk.NORMAL))
                    self.root.after(0, lambda: self.progress_label.config(text="Ready"))
            
            threading.Thread(target=analyze_thread, daemon=True).start()
        
        def display_results(self, results: Dict[str, Dict]):
            """Display analysis results"""
            self.results_text.delete(1.0, tk.END)
            
            if not results:
                self.results_text.insert(tk.END, "No results to display")
                return
            
            self.results_text.insert(tk.END, f"Analysis Results ({len(results)} commit(s))\n")
            self.results_text.insert(tk.END, "=" * 80 + "\n\n")
            
            for commit_hash, data in results.items():
                self.results_text.insert(tk.END, f"Commit: {commit_hash[:8]}\n")
                self.results_text.insert(tk.END, "-" * 80 + "\n")
                
                if isinstance(data, dict):
                    if 'functions' in data:
                        self.results_text.insert(tk.END, f"Functions: {len(data['functions'])}\n")
                    if 'edges' in data:
                        self.results_text.insert(tk.END, f"Edges: {len(data['edges'])}\n")
                    if 'nodes' in data:
                        self.results_text.insert(tk.END, f"Nodes: {len(data['nodes'])}\n")
                
                self.results_text.insert(tk.END, "\n")
        
        def on_commit_select(self, event):
            """Handle commit selection"""
            selection = self.commits_listbox.curselection()
            if not selection:
                return
            
            commit_hash = self.commits_listbox.get(selection[0])
            if commit_hash in self.results:
                data = self.results[commit_hash]
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, f"Commit: {commit_hash}\n")
                self.results_text.insert(tk.END, "=" * 80 + "\n\n")
                self.results_text.insert(tk.END, json.dumps(data, indent=2))
        
        def clear_results(self):
            """Clear all results"""
            self.results = {}
            self.results_text.delete(1.0, tk.END)
            self.progress_text.delete(1.0, tk.END)
            self.log("Results cleared")
        
        def export_results(self):
            """Export results to JSON file"""
            if not self.results:
                messagebox.showwarning("Warning", "No results to export")
                return
            
            file_path = filedialog.asksaveasfilename(
                title="Export Results",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(self.results, f, indent=2)
                    messagebox.showinfo("Success", f"Results exported to {file_path}")
                    self.log(f"Results exported to {file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to export: {e}")
        
        def launch_server_in_separate_process(self, html_dir: str, port: int = None):
            """Launch HTTP server in a separate process/terminal so it doesn't block the GUI"""
            try:
                import platform
                import tempfile
                
                # Normalize paths to avoid issues with quotes
                html_dir_normalized = os.path.normpath(html_dir)
                
                # Use a higher port range (8080-8180) to avoid permission issues
                # Lower ports (< 1024) often require admin privileges on Windows
                start_port = port if port else 8080
                end_port = start_port + 100
                
                # Create a simple server script using raw strings to avoid escape issues
                # Include port finding logic to avoid permission errors
                server_script = f"""import http.server
import socketserver
import os
import sys
import socket

html_dir = r{repr(html_dir_normalized)}
os.chdir(html_dir)

# Find an available port starting from the requested port
# Try ports in range to avoid permission errors
def find_available_port(start_port):
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('', port))
                return port
        except (OSError, PermissionError):
            continue
    return None

port = find_available_port({start_port})
if port is None:
    print(f"ERROR: Could not find an available port in range {start_port}-{end_port}")
    sys.exit(1)

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=html_dir, **kwargs)
    
    def log_message(self, format, *args):
        pass  # Suppress logs

socketserver.TCPServer.allow_reuse_address = True
try:
    server = socketserver.TCPServer(("", port), CustomHTTPRequestHandler)
    print(f"Server started on http://localhost:{{port}}")
    print(f"Serving directory: {{html_dir}}")
    print("Press Ctrl+C to stop")
    
    server.serve_forever()
except KeyboardInterrupt:
    print("\\nShutting down server...")
    server.shutdown()
except Exception as e:
    print(f"ERROR: Could not start server: {{e}}")
    sys.exit(1)
"""
                
                # Write server script to temp file
                script_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8')
                script_file.write(server_script)
                script_file.close()
                
                script_path = script_file.name
                
                # Launch in separate process without showing window
                if platform.system() == 'Windows':
                    # On Windows, use pythonw.exe if available to avoid console window
                    python_exe = sys.executable
                    if python_exe.endswith('python.exe'):
                        pythonw_exe = python_exe.replace('python.exe', 'pythonw.exe')
                        if os.path.exists(pythonw_exe):
                            python_exe = pythonw_exe
                    
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                    
                    subprocess.Popen(
                        [python_exe, script_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        startupinfo=startupinfo
                    )
                else:
                    # On Linux/Mac, launch in background
                    subprocess.Popen(
                        ['python', script_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                
                self.log(f"Server launched in separate terminal/process on port {port}")
                self.log(f"HTML directory: {html_dir_normalized}")
                self.log(f"Server script: {script_path}")
                return True
            except Exception as e:
                self.log(f"Error launching server in separate process: {e}")
                import traceback
                self.log(traceback.format_exc())
                return False
        
        def generate_html_graphs(self):
            """Generate HTML files with interactive graphs for all analyzed commits"""
            if not self.results:
                messagebox.showwarning("Warning", "No results available. Please run analysis first.")
                return
            
            if not generate_interactive_svg:
                messagebox.showerror("Error", "generate_interactive_svg function not available")
                return
            
            # Ask for output directory
            output_dir = filedialog.askdirectory(
                title="Select Output Directory for HTML Files",
                initialdir=str(self.repo_path)
            )
            if not output_dir:
                return
            
            self.html_output_dir = output_dir
            self.generate_html_button.config(state=tk.DISABLED)
            
            def generate_thread():
                try:
                    self.root.after(0, lambda: self.log("Starting HTML graph generation..."))
                    generated_files = []
                    total = len(self.results)
                    
                    # Get the first file path for display purposes
                    target_files = self.get_target_files()
                    file_path = target_files[0] if target_files else None
                    
                    # Sort commits chronologically (oldest first) for comparison
                    sorted_commits = list(self.results.keys())
                    
                    # Track previous commit's HTML file for diff comparison
                    previous_html_path = None
                    
                    for idx, commit_hash in enumerate(sorted_commits):
                        try:
                            data = self.results[commit_hash]
                            self.root.after(0, lambda ch=commit_hash, i=idx+1, t=total: 
                                          self.log(f"Generating HTML for commit {ch[:8]} ({i}/{t})..."))
                            
                            # Create output filename
                            safe_commit = commit_hash[:8]
                            output_filename = f"dataflow_graph_{safe_commit}.html"
                            output_path = os.path.join(output_dir, output_filename)
                            
                            # Debug: Check data structure
                            if not isinstance(data, dict):
                                raise ValueError(f"Expected dict, got {type(data)}")
                            
                            variables = data.get('variables', {})
                            if not variables:
                                self.root.after(0, lambda ch=commit_hash: 
                                              self.log(f"Warning: No variables found for commit {ch[:8]} - skipping HTML generation"))
                                continue  # Skip this commit - don't generate empty graph
                            
                            # Save JSON data to temporary file first (generate_interactive_svg expects a file path)
                            json_temp_file = os.path.join(output_dir, f"dataflow_{commit_hash[:8]}.json")
                            with open(json_temp_file, 'w', encoding='utf-8') as f:
                                json.dump(data, f, indent=2)
                            
                            # If we have a previous commit, prepare it for diff comparison
                            if idx > 0:
                                prev_commit_hash = sorted_commits[idx - 1]
                                prev_data = self.results.get(prev_commit_hash)
                                if prev_data:
                                    import shutil
                                    script_dir = os.path.dirname(os.path.abspath(json_temp_file))
                                    
                                    # generate_interactive_svg looks for previous JSON in 'graph_backups' directory
                                    # with files starting with 'dataflow_'
                                    backup_dir = os.path.join(script_dir, 'graph_backups')
                                    os.makedirs(backup_dir, exist_ok=True)
                                    
                                    # Save previous commit's JSON with timestamp for backup lookup
                                    # Format: dataflow_YYYYMMDD_HHMMSS.json (matches expected pattern)
                                    import time
                                    from datetime import datetime
                                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                    prev_json_backup = os.path.join(backup_dir, f"dataflow_{timestamp}.json")
                                    
                                    try:
                                        with open(prev_json_backup, 'w', encoding='utf-8') as f:
                                            json.dump(prev_data, f, indent=2)
                                        
                                        self.root.after(0, lambda: self.log(f"Saved previous commit JSON to backup for diff comparison"))
                                    except Exception as e:
                                        self.root.after(0, lambda err=str(e): self.log(f"Warning: Could not save previous JSON: {err}"))
                            
                            # Generate HTML using the JSON file with diff enabled
                            # enable_diff=True will compare with the previous HTML file if it exists
                            html_path = generate_interactive_svg(
                                dataflow_file=json_temp_file,
                                output_file=output_path,
                                enable_diff=True  # Enable diff highlighting
                            )
                            
                            generated_files.append(html_path)
                            var_count = len(variables) if variables else 0
                            diff_note = " (with diff)" if previous_html_path else ""
                            self.root.after(0, lambda p=html_path, vc=var_count, dn=diff_note: 
                                          self.log(f"Generated: {p} ({vc} variables){dn}"))
                            
                            # Pre-generate function pages for all functions using the same code as test_backend_function_generation.py
                            try:
                                # Check if imports are available (they're imported at module level)
                                if not run_complete_dataflow_analysis or not generate_interactive_svg:
                                    self.root.after(0, lambda: self.log("Warning: Required modules not available for function page generation"))
                                else:
                                    metadata = data.get('metadata', {})
                                    defined_functions = metadata.get('defined_functions', [])
                                
                                    if defined_functions:
                                        commit_short = commit_hash[:8]
                                        func_count = len(defined_functions)
                                        self.root.after(0, lambda cs=commit_short, fc=func_count: 
                                                      self.log(f"Pre-generating {fc} function pages for commit {cs}..."))
                                    
                                    # Recreate temp file from commit (same as analyze_commit_safely does)
                                    # This ensures we analyze the exact commit version, not the current file
                                    original_file_path = target_files[0] if target_files else file_path
                                    temp_dir_for_func = None
                                    temp_file_path_for_func = None
                                    
                                    try:
                                        # Create temp directory for this commit's function analysis
                                        temp_dir_for_func = tempfile.mkdtemp(prefix=f'git_func_{commit_hash[:8]}_')
                                        
                                        # Get relative path from repo root
                                        if not self.analyzer:
                                            continue  # Skip if analyzer not initialized
                                        rel_path = os.path.relpath(original_file_path, self.analyzer.repo_path)
                                        if not rel_path.startswith('..'):
                                            # Get file content from commit
                                            content = self.analyzer.get_file_content_at_commit(commit_hash, rel_path)
                                            if content is not None:
                                                # Create temp file
                                                temp_file_path_for_func = Path(temp_dir_for_func) / rel_path
                                                temp_file_path_for_func.parent.mkdir(parents=True, exist_ok=True)
                                                temp_file_path_for_func.write_text(content, encoding='utf-8')
                                                temp_file_path_for_func = str(temp_file_path_for_func)
                                            else:
                                                # Fallback to original file if commit version not found
                                                temp_file_path_for_func = original_file_path
                                        else:
                                            # File outside repo, use original
                                            temp_file_path_for_func = original_file_path
                                    except Exception as temp_err:
                                        # If temp file creation fails, use original file
                                        temp_file_path_for_func = original_file_path
                                    
                                    # Generate function pages for each function using run_complete_dataflow_analysis
                                    for func_name in defined_functions:
                                        try:
                                            # Create safe filename for function page
                                            safe_file = original_file_path.replace('\\', '_').replace('/', '_').replace(':', '_').replace('.', '_')
                                            func_json_file = os.path.join(output_dir, f"function_dataflow_{safe_file}_{func_name}.json")
                                            func_output_file = os.path.join(output_dir, f"function_dataflow_{safe_file}_{func_name}.html")
                                            
                                            # Run Scalpel analysis for this specific function (same as test_backend_function_generation.py)
                                            # Use temp file path (commit version) instead of original file
                                            fn = func_name  # Capture in local variable for lambda
                                            self.root.after(0, lambda f=fn: self.log(f"  Analyzing function: {f}"))
                                            
                                            result = run_complete_dataflow_analysis(
                                                target_files=[temp_file_path_for_func],  # Use commit version, not current file
                                                generate_html=False,  # We'll generate HTML ourselves
                                                force=True,
                                                target_function=func_name,
                                                start_server=False  # Don't start server
                                            )
                                            
                                            # Check if analysis was successful
                                            if 'error' in result.get('metadata', {}):
                                                error_msg = result['metadata']['error']
                                                fn_err = func_name
                                                self.root.after(0, lambda f=fn_err, e=error_msg: self.log(f"  Error analyzing {f}: {e}"))
                                                continue
                                            
                                            # Get the generated JSON (scalpel_complete_dataflow.json in script dir)
                                            script_dir = os.path.dirname(os.path.abspath(__file__))
                                            scalpel_output_json = os.path.join(script_dir, 'scalpel_complete_dataflow.json')
                                            
                                            if not os.path.exists(scalpel_output_json):
                                                fn_warn = func_name
                                                self.root.after(0, lambda f=fn_warn: self.log(f"  Warning: JSON not found for {f}"))
                                                continue
                                            
                                            # Copy JSON to target location
                                            shutil.copy2(scalpel_output_json, func_json_file)
                                            
                                            # Generate HTML from the function-specific JSON
                                            generate_interactive_svg(
                                                dataflow_file=func_json_file,
                                                output_file=func_output_file,
                                                enable_diff=True
                                            )
                                            
                                            if os.path.exists(func_output_file):
                                                generated_files.append(func_output_file)
                                                fn_success = func_name
                                                self.root.after(0, lambda f=fn_success: self.log(f"  Generated function page: {f}"))
                                            else:
                                                fn_fail = func_name
                                                self.root.after(0, lambda f=fn_fail: self.log(f"  Warning: HTML not created for {f}"))
                                        except Exception as func_error:
                                            error_str = str(func_error)
                                            fn_exc = func_name
                                            self.root.after(0, lambda f=fn_exc, e=error_str: self.log(f"  Warning: Could not generate page for {f}: {e}"))
                                    
                                    if defined_functions:
                                        func_count_final = len(defined_functions)
                                        self.root.after(0, lambda fc=func_count_final: self.log(f"Pre-generated {fc} function pages"))
                                    
                                    # Clean up temp directory after function page generation
                                    if temp_dir_for_func and os.path.exists(temp_dir_for_func):
                                        try:
                                            shutil.rmtree(temp_dir_for_func)
                                        except Exception as cleanup_err:
                                            # Non-critical error, just log it
                                            pass
                            except Exception as e:
                                error_str = str(e)
                                self.root.after(0, lambda err=error_str: self.log(f"Warning: Could not pre-generate function pages: {err}"))
                                traceback.print_exc()
                                # Clean up temp directory on error
                                if 'temp_dir_for_func' in locals() and temp_dir_for_func and os.path.exists(temp_dir_for_func):
                                    try:
                                        shutil.rmtree(temp_dir_for_func)
                                    except Exception:
                                        pass
                            
                            # Update previous HTML path for next iteration
                            previous_html_path = html_path
                            
                        except Exception as e:
                            error_msg = f"Error generating HTML for commit {commit_hash[:8]}: {e}"
                            self.root.after(0, lambda msg=error_msg: self.log(msg))
                            traceback.print_exc()
                    
                    success_msg = f"\nHTML generation complete! Generated {len(generated_files)} file(s) in:\n{output_dir}"
                    self.root.after(0, lambda msg=success_msg: self.log(msg))
                    self.root.after(0, lambda dir=output_dir: setattr(self, 'html_output_dir', dir))
                    
                    # Ask user if they want to launch server in separate terminal
                    def ask_server_launch():
                        response = messagebox.askyesno(
                            "Server Launch",
                            f"Generated {len(generated_files)} HTML file(s)\n\n"
                            f"Saved to:\n{output_dir}\n\n"
                            "Would you like to launch a web server in a separate terminal/process?\n"
                            "(This allows you to view graphs while keeping the GUI responsive)"
                        )
                        if response:
                            # Launch server in separate process
                            self.root.after(0, lambda: self.log("Launching server in separate terminal..."))
                            self.root.after(100, lambda: self.launch_server_in_separate_process(output_dir))
                        else:
                            self.root.after(0, lambda: self.log("Server launch skipped. Use 'Serve HTML Files' button to start server later."))
                    
                    self.root.after(0, ask_server_launch)
                    
                except Exception as e:
                    error_msg = f"Error during HTML generation: {e}"
                    self.root.after(0, lambda msg=error_msg: self.log(msg))
                    self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                    traceback.print_exc()
                finally:
                    self.root.after(0, lambda: self.generate_html_button.config(state=tk.NORMAL))
            
            threading.Thread(target=generate_thread, daemon=True).start()
        
        def serve_html_files_auto(self, serve_dir: str):
            """Automatically start HTTP server after HTML generation"""
            if not serve_dir or not os.path.exists(serve_dir):
                return
            
            self.html_output_dir = serve_dir
            
            # Check if server is already running
            if self.server_thread and self.server_thread.is_alive():
                # Server already running, just open browser
                if self.server_port:
                    url = f"http://localhost:{self.server_port}"
                    webbrowser.open(url)
                    self.log(f"Browser opened to existing server: {url}")
                return
            
            # Start new server
            self._start_server(serve_dir)
        
        def serve_html_files(self):
            """Start HTTP server to serve generated HTML files (manual)"""
            
            # Determine directory to serve
            if self.html_output_dir and os.path.exists(self.html_output_dir):
                serve_dir = self.html_output_dir
            else:
                # Ask for directory
                serve_dir = filedialog.askdirectory(
                    title="Select Directory with HTML Files to Serve",
                    initialdir=str(self.repo_path) if self.repo_path.exists() else "."
                )
                if not serve_dir:
                    return
                self.html_output_dir = serve_dir
            
            # Check if server is already running
            if self.server_thread and self.server_thread.is_alive():
                if messagebox.askyesno("Server Running", 
                                       f"Server is already running on port {self.server_port}.\n\n"
                                       "Do you want to stop it and start a new one?"):
                    self.stop_server()
                else:
                    return
            
            self._start_server(serve_dir)
        
        def _start_server(self, serve_dir: str):
            """Internal method to start the HTTP server"""
            
            # Check if server is already running
            if self.server_thread and self.server_thread.is_alive():
                if messagebox.askyesno("Server Running", 
                                       f"Server is already running on port {self.server_port}.\n\n"
                                       "Do you want to stop it and start a new one?"):
                    self.stop_server()
                else:
                    return
            
            # Find available port
            port = 8000
            for p in range(8000, 8100):
                try:
                    test_socket = socketserver.TCPServer(("", p), None)
                    test_socket.server_close()
                    port = p
                    break
                except OSError:
                    continue
            
            self.server_port = port
            
            # Store target_files and port for handler access
            gui_target_files = self.get_target_files() if hasattr(self, 'get_target_files') else []
            repo_path_for_handler = str(self.repo_path) if hasattr(self, 'repo_path') else None
            server_port_for_handler = port  # Store port for handler to use
            
            # Create custom handler for on-demand function page generation
            class FunctionPageHandler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=serve_dir, **kwargs)
                    self.server_port = server_port_for_handler  # Store port in handler
                
                def do_GET(self):
                    # Handle function page generation requests
                    import sys
                    print(f"[DEBUG] do_GET called with path: {self.path}", file=sys.stderr, flush=True)
                    # Check for both with and without query string
                    if '/generate_function_page' in self.path:
                        print(f"[DEBUG] Routing to handle_generate_function_page", file=sys.stderr, flush=True)
                        self.handle_generate_function_page()
                    else:
                        # Default file serving
                        print(f"[DEBUG] Routing to default file serving for: {self.path}", file=sys.stderr, flush=True)
                        super().do_GET()
                
                def handle_generate_function_page(self):
                    """Generate function page on-demand"""
                    try:
                        import urllib.parse
                        import sys
                        print(f"[DEBUG] ===== handle_generate_function_page called =====", file=sys.stderr, flush=True)
                        print(f"[DEBUG] Request path: {self.path}", file=sys.stderr, flush=True)
                        
                        from generate_interactive_dataflow import generate_function_dataflow_page
                        from scalpel_complete_dataflow import build_complete_dataflow_json, analyze_file
                        import json as json_module
                        
                        # Parse query parameters
                        query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                        function_name = query_params.get('function', [None])[0]
                        file_path = query_params.get('file', [None])[0]
                        
                        print(f"[DEBUG] Parsed - function: {function_name}, file: {file_path}", file=sys.stderr, flush=True)
                        
                        if not function_name or not file_path:
                            self.send_error(400, "Missing function or file parameter")
                            return
                        
                        # Find the actual file path
                        func_file_path = None
                        
                        # Note: file_path is already URL-decoded by parse_qs, but ensure it's a string
                        if not isinstance(file_path, str):
                            file_path = str(file_path)
                        
                        # Debug logging
                        import sys
                        print(f"[DEBUG] handle_generate_function_page: function={function_name}, file_path={file_path}", file=sys.stderr, flush=True)
                        print(f"[DEBUG] gui_target_files={gui_target_files}", file=sys.stderr, flush=True)
                        print(f"[DEBUG] repo_path_for_handler={repo_path_for_handler}", file=sys.stderr, flush=True)
                        
                        # Check if this is a temporary file path from git analysis
                        is_temp_path = 'git_analysis_' in file_path or 'Temp' in file_path or 'tmp' in file_path.lower()
                        file_basename = os.path.basename(file_path)
                        print(f"[DEBUG] is_temp_path={is_temp_path}, file_basename={file_basename}", file=sys.stderr, flush=True)
                        
                        # PRIMARY STRATEGY: Try to find file in target_files (from closure)
                        # These are the original files that were analyzed
                        print(f"[DEBUG] Checking {len(gui_target_files)} target files...", file=sys.stderr, flush=True)
                        if not gui_target_files:
                            print(f"[DEBUG] WARNING: gui_target_files is empty!", file=sys.stderr, flush=True)
                        
                        for tf in gui_target_files:
                            print(f"[DEBUG]   Checking target file: {tf}, basename: {os.path.basename(tf)}", file=sys.stderr, flush=True)
                            if is_temp_path:
                                # For temp paths, match by basename only (most common case)
                                if os.path.basename(tf) == file_basename:
                                    if os.path.exists(tf):
                                        func_file_path = tf
                                        print(f"[DEBUG]   ✓ MATCHED by basename: {func_file_path}", file=sys.stderr, flush=True)
                                        break
                                    else:
                                        print(f"[DEBUG]   ✗ Basename matches but file doesn't exist: {tf}", file=sys.stderr, flush=True)
                            else:
                                # For regular paths, try exact match or basename match
                                if tf == file_path or os.path.basename(tf) == file_basename or tf.endswith(file_basename):
                                    if os.path.exists(tf):
                                        func_file_path = tf
                                        print(f"[DEBUG]   ✓ MATCHED: {func_file_path}", file=sys.stderr, flush=True)
                                break
                        
                        # If gui_target_files has only one file and we haven't found a match, use it (if basename matches)
                        if not func_file_path and len(gui_target_files) == 1 and is_temp_path:
                            candidate = gui_target_files[0]
                            print(f"[DEBUG] Single file fallback: checking {candidate}", file=sys.stderr, flush=True)
                            if os.path.exists(candidate):
                                # Even if basename doesn't match, if there's only one file, use it
                                func_file_path = candidate
                                print(f"[DEBUG] Using single target file (basename match not required): {func_file_path}", file=sys.stderr, flush=True)
                            elif os.path.basename(candidate) == file_basename:
                                # Basename matches but file doesn't exist - try to find it
                                print(f"[DEBUG] Single file basename matches but file missing, will try other fallbacks", file=sys.stderr, flush=True)
                        
                        # Fallback 1: Try to reconstruct original path from temp path using repo_path
                        if not func_file_path and is_temp_path and repo_path_for_handler:
                            try:
                                # Extract relative path from temp path
                                # Temp path format: C:\...\Temp\git_analysis_XXXXX\path\to\file.py
                                # The relative path starts after the temp directory name
                                # Find git_analysis_ pattern and extract everything after the temp dir
                                import re
                                # Match pattern: .../git_analysis_HASH_/relative/path/to/file.py
                                # Handle both cases: file in root (git_analysis_HASH/file.py) and in subdir (git_analysis_HASH/path/file.py)
                                normalized_path = file_path.replace('\\', '/')
                                match = re.search(r'git_analysis_[^/]+/(.+)', normalized_path)
                                if match:
                                    rel_path = match.group(1).replace('/', os.sep)  # Convert back to OS-specific separator
                                    original_path = os.path.join(repo_path_for_handler, rel_path)
                                    print(f"[DEBUG] Fallback 1: Trying original_path={original_path}", file=sys.stderr, flush=True)
                                    if os.path.exists(original_path):
                                        func_file_path = original_path
                                        print(f"[DEBUG] Fallback 1: SUCCESS - found file at {func_file_path}", file=sys.stderr, flush=True)
                                    else:
                                        print(f"[DEBUG] Fallback 1: File does not exist at {original_path}", file=sys.stderr, flush=True)
                                else:
                                    print(f"[DEBUG] Fallback 1: Could not extract relative path from {file_path}", file=sys.stderr, flush=True)
                            except Exception as e:
                                print(f"[DEBUG] Fallback 1: Exception: {e}", file=sys.stderr, flush=True)
                                pass
                        
                        # Fallback 2: Try to find the file by checking the JSON metadata in serve_dir
                        if not func_file_path and is_temp_path:
                            try:
                                json_file = os.path.join(serve_dir, 'scalpel_complete_dataflow.json')
                                if os.path.exists(json_file):
                                    import json as json_module
                                    with open(json_file, 'r', encoding='utf-8') as f:
                                        json_data = json_module.load(f)
                                    # Look for the file in variable definitions/uses
                                    for var_name, var_data in json_data.get('variables', {}).items():
                                        for defn in var_data.get('definitions', {}).get('locations', []):
                                            def_file = defn.get('file', '')
                                            if def_file and os.path.basename(def_file) == file_basename:
                                                # Check if this is NOT a temp path (original file)
                                                if 'git_analysis_' not in def_file and 'Temp' not in def_file:
                                                    if os.path.exists(def_file):
                                                        func_file_path = def_file
                                                        break
                                        if func_file_path:
                                            break
                                        for use in var_data.get('uses', {}).get('locations', []):
                                            use_file = use.get('file', '')
                                            if use_file and os.path.basename(use_file) == file_basename:
                                                if 'git_analysis_' not in use_file and 'Temp' not in use_file:
                                                    if os.path.exists(use_file):
                                                        func_file_path = use_file
                                                        break
                                        if func_file_path:
                                            break
                            except Exception as e:
                                # If JSON reading fails, continue with other methods
                                pass
                        
                        # Fallback 3: Try file directly in repo root (common case)
                        if not func_file_path and is_temp_path and repo_path_for_handler:
                            try:
                                candidate = os.path.join(repo_path_for_handler, file_basename)
                                print(f"[DEBUG] Fallback 3: Trying repo root: {candidate}", file=sys.stderr, flush=True)
                                if os.path.exists(candidate):
                                    func_file_path = candidate
                                    print(f"[DEBUG] Fallback 3: SUCCESS - found file at {func_file_path}", file=sys.stderr, flush=True)
                            except Exception as e:
                                print(f"[DEBUG] Fallback 3: Exception: {e}", file=sys.stderr, flush=True)
                                pass
                        
                        # Fallback 4: Try to find file in repo by basename (search subdirectories)
                        if not func_file_path and is_temp_path and repo_path_for_handler:
                            try:
                                for root, dirs, files in os.walk(repo_path_for_handler):
                                    if file_basename in files:
                                        candidate = os.path.join(root, file_basename)
                                        if os.path.exists(candidate):
                                            func_file_path = candidate
                                            print(f"[DEBUG] Fallback 4: SUCCESS - found file at {func_file_path}", file=sys.stderr, flush=True)
                                            break
                                    if func_file_path:
                                        break
                            except Exception as e:
                                print(f"[DEBUG] Fallback 4: Exception: {e}", file=sys.stderr, flush=True)
                                pass
                        
                        # Fallback 5: Try in serve_dir (where the analysis was run)
                        if not func_file_path and is_temp_path:
                            try:
                                candidate = os.path.join(serve_dir, file_basename)
                                print(f"[DEBUG] Fallback 5: Trying serve_dir: {candidate}", file=sys.stderr, flush=True)
                                if os.path.exists(candidate):
                                    func_file_path = candidate
                                    print(f"[DEBUG] Fallback 5: SUCCESS - found file at {func_file_path}", file=sys.stderr, flush=True)
                            except Exception as e:
                                print(f"[DEBUG] Fallback 5: Exception: {e}", file=sys.stderr, flush=True)
                                pass
                        
                        # Last resort: check if the provided path exists (for non-temp paths)
                        if not func_file_path and not is_temp_path and os.path.exists(file_path):
                            func_file_path = file_path
                        
                        # Final fallback: if we have target files and still no match, try all of them
                        if (not func_file_path or not os.path.exists(func_file_path)) and gui_target_files and is_temp_path:
                            print(f"[DEBUG] Final fallback: Trying all {len(gui_target_files)} target files...", file=sys.stderr, flush=True)
                            for tf in gui_target_files:
                                print(f"[DEBUG]   Checking: {tf}, exists: {os.path.exists(tf)}", file=sys.stderr, flush=True)
                                if os.path.exists(tf):
                                    # If basename matches, prefer it
                                    if os.path.basename(tf) == file_basename:
                                        func_file_path = tf
                                        print(f"[DEBUG] Final fallback: Using matching basename {func_file_path}", file=sys.stderr, flush=True)
                                        break
                                    # Otherwise, use the first existing file if we don't have one yet
                                    elif not func_file_path:
                                        func_file_path = tf
                                        print(f"[DEBUG] Final fallback: Using first existing file {func_file_path}", file=sys.stderr, flush=True)
                            
                            # If we still don't have a file and there's only one target file, use it even if it doesn't exist
                            # (Scalpel might be able to handle it, or it might be in a different location)
                            if not func_file_path and len(gui_target_files) == 1:
                                func_file_path = gui_target_files[0]
                                print(f"[DEBUG] Final fallback: Using single target file (even if missing): {func_file_path}", file=sys.stderr, flush=True)
                        
                        # If we have a file path from gui_target_files, use it even if it doesn't exist
                        # (the file might be in a different location that Scalpel can find)
                        proceed_with_file = False
                        if func_file_path:
                            if func_file_path in gui_target_files:
                                print(f"[DEBUG] Using file from gui_target_files (proceeding even if file check fails): {func_file_path}", file=sys.stderr, flush=True)
                                proceed_with_file = True
                            elif os.path.exists(func_file_path):
                                print(f"[DEBUG] Using file that exists: {func_file_path}", file=sys.stderr, flush=True)
                                proceed_with_file = True
                        
                        if not proceed_with_file:
                            # Provide helpful error message with debug info
                            error_msg = f"File not found: {file_path}\n"
                            error_msg += f"Basename: {file_basename}\n"
                            error_msg += f"Is temp path: {is_temp_path}\n"
                            error_msg += f"Target files available: {gui_target_files}\n"
                            error_msg += f"Repo path: {repo_path_for_handler}\n"
                            error_msg += f"Serve dir: {serve_dir}\n"
                            error_msg += f"Resolved path: {func_file_path if func_file_path else 'None'}\n"
                            error_msg += f"\nTroubleshooting:\n"
                            error_msg += f"1. Make sure the file '{file_basename}' exists in the repository\n"
                            error_msg += f"2. Check that the file is in: {repo_path_for_handler if repo_path_for_handler else 'N/A'}\n"
                            error_msg += f"3. Verify the file is listed in the GUI's file list\n"
                            print(f"[ERROR] {error_msg}", file=sys.stderr, flush=True)
                            # Send HTML error page instead of plain text for better UX
                            self.send_response(404)
                            self.send_header('Content-type', 'text/html')
                            self.end_headers()
                            error_html = f"""<html><head><title>File Not Found</title></head><body>
                                <h1>404 - File Not Found</h1>
                                <p><strong>Requested file:</strong> {file_path}</p>
                                <p><strong>Basename:</strong> {file_basename}</p>
                                <p><strong>Is temp path:</strong> {is_temp_path}</p>
                                <h2>Troubleshooting:</h2>
                                <ul>
                                    <li>Make sure the file '{file_basename}' exists in the repository</li>
                                    <li>Check that the file is in: {repo_path_for_handler if repo_path_for_handler else 'N/A'}</li>
                                    <li>Verify the file is listed in the GUI's file list</li>
                                </ul>
                                <p><a href="javascript:history.back()">Go Back</a></p>
                            </body></html>"""
                            self.wfile.write(error_html.encode('utf-8'))
                            return
                        
                        print(f"[DEBUG] SUCCESS: Using file path: {func_file_path}", file=sys.stderr, flush=True)
                        
                        # Generate the function page on-demand using Scalpel CLI with --function argument
                        output_dir = serve_dir
                        safe_file = file_path.replace('\\', '_').replace('/', '_').replace(':', '_').replace('.', '_')
                        
                        func_json_file = os.path.join(output_dir, f"function_dataflow_{safe_file}_{function_name}.json")
                        output_file = os.path.join(output_dir, f"function_dataflow_{safe_file}_{function_name}.html")
                        
                        # Check if HTML already exists (to avoid regenerating if just generated)
                        if os.path.exists(output_file) and os.path.exists(func_json_file):
                            # Check if JSON is recent (within last minute) - if so, just redirect
                            import time
                            json_mtime = os.path.getmtime(func_json_file)
                            if time.time() - json_mtime < 60:  # Generated within last minute
                                self.send_response(302)
                                self.send_header('Location', f'/function_dataflow_{safe_file}_{function_name}.html')
                                self.end_headers()
                                return
                        
                        # Generate JSON on-demand using Scalpel CLI with --function argument
                        # This runs: python scalpel_complete_dataflow.py --file <file> --function <function>
                        scalpel_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scalpel_complete_dataflow.py')
                        
                        if not os.path.exists(scalpel_script):
                            self.send_error(500, f"Scalpel script not found: {scalpel_script}")
                            return
                        
                        # Run Scalpel CLI command in a visible terminal: python scalpel_complete_dataflow.py --file <file> --function <function>
                        # This ensures we're using Scalpel's CLI exactly as the user requested, and output is visible
                        import subprocess
                        import sys
                        import tempfile
                        
                        # Get the absolute path to scalpel_complete_dataflow.py
                        scalpel_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scalpel_complete_dataflow.py')
                        
                        if not os.path.exists(scalpel_script):
                            self.send_error(500, f"Scalpel script not found: {scalpel_script}")
                            return
                        
                        # Create a script that runs Scalpel and waits for JSON, then exits
                        scalpel_wrapper_script = f"""import sys
import os
import time
import subprocess
import shutil

scalpel_script = r{repr(scalpel_script)}
func_file_path = r{repr(func_file_path)}
function_name = r{repr(function_name)}
func_json_file = r{repr(func_json_file)}
scalpel_output_json = os.path.join(os.path.dirname(scalpel_script), 'scalpel_complete_dataflow.json')

# Run Scalpel CLI silently
# Use pythonw.exe if available to avoid console window
python_exe = sys.executable
if sys.platform == 'win32' and python_exe.endswith('python.exe'):
    pythonw_exe = python_exe.replace('python.exe', 'pythonw.exe')
    if os.path.exists(pythonw_exe):
        python_exe = pythonw_exe

cmd = [python_exe, scalpel_script, '--file', func_file_path, '--function', function_name, '--force']

process = subprocess.Popen(
    cmd, 
    cwd=os.path.dirname(scalpel_script),
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0,
    startupinfo=subprocess.STARTUPINFO() if sys.platform == 'win32' else None
)

# Wait for JSON to be generated (but kill before server starts)
max_wait = 30
waited = 0
while not os.path.exists(scalpel_output_json) and waited < max_wait:
    if process.poll() is not None:
        break  # Process finished
    time.sleep(0.5)
    waited += 0.5

if os.path.exists(scalpel_output_json):
    # Copy JSON to target location
    shutil.copy2(scalpel_output_json, func_json_file)
    print(f"\\n[OK] JSON generated and copied to: {{func_json_file}}")
else:
    print(f"\\n[ERROR] Scalpel did not generate JSON file")
    sys.exit(1)

# Kill the process to prevent server from starting
try:
    process.terminate()
    process.wait(timeout=2)
except:
    process.kill()

# Script completes silently - no user interaction needed
"""
                        
                        # Write wrapper script to temp file
                        wrapper_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8')
                        wrapper_file.write(scalpel_wrapper_script)
                        wrapper_file.close()
                        wrapper_path = wrapper_file.name
                        
                        try:
                            # Launch Scalpel silently (Windows)
                            if sys.platform == 'win32':
                                # Use pythonw.exe if available to avoid any console window
                                python_exe = sys.executable
                                if python_exe.endswith('python.exe'):
                                    pythonw_exe = python_exe.replace('python.exe', 'pythonw.exe')
                                    if os.path.exists(pythonw_exe):
                                        python_exe = pythonw_exe
                                
                                subprocess.Popen(
                                    [python_exe, wrapper_path],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    creationflags=subprocess.CREATE_NO_WINDOW,
                                    startupinfo=subprocess.STARTUPINFO() if sys.platform == 'win32' else None
                                )
                            else:
                                # Linux/Mac - use xterm or similar
                                subprocess.Popen(['xterm', '-e', sys.executable, wrapper_path])
                            
                            # Wait for JSON file to appear
                            import time
                            max_wait = 35  # Give it more time since we're waiting for visible terminal
                            waited = 0
                            while not os.path.exists(func_json_file) and waited < max_wait:
                                time.sleep(0.5)
                                waited += 0.5
                            
                            if not os.path.exists(func_json_file):
                                self.send_error(500, f"Scalpel did not generate JSON file: {func_json_file}")
                                return
                            
                        except Exception as e:
                            error_msg = f"Error running Scalpel CLI: {str(e)}"
                            self.send_error(500, error_msg)
                            return
                        finally:
                            # Clean up wrapper script (but don't delete immediately - let it run)
                            try:
                                import threading
                                import time as time_module
                                def cleanup():
                                    time_module.sleep(60)  # Wait a minute before cleanup
                                    try:
                                        os.unlink(wrapper_path)
                                    except:
                                        pass
                                threading.Thread(target=cleanup, daemon=True).start()
                            except:
                                pass
                        
                        # Generate HTML from the freshly generated JSON
                        # Pass the server port so JavaScript knows which port to use
                        generate_function_dataflow_page(
                            dataflow_file=func_json_file,
                            function_name=function_name,
                            file_path=file_path,
                            output_file=output_file,
                            enable_diff=True,
                            server_port=self.server_port  # Pass server port
                        )
                        
                        # Redirect to the generated page
                        self.send_response(302)
                        self.send_header('Location', f'/function_dataflow_{safe_file}_{function_name}.html')
                        self.end_headers()
                        
                    except Exception as e:
                        import traceback
                        error_msg = f"Error generating function page: {str(e)}\n{traceback.format_exc()}"
                        self.send_error(500, error_msg)
                
                def log_message(self, format, *args):
                    # Suppress normal server logs
                    pass
            
            def start_server():
                try:
                    original_dir = os.getcwd()
                    os.chdir(serve_dir)
                    httpd = socketserver.TCPServer(("", port), FunctionPageHandler)
                    
                    self.root.after(0, lambda: self.log(f"Starting HTTP server on port {port}..."))
                    self.root.after(0, lambda: self.log(f"Serving directory: {serve_dir}"))
                    
                    # Store server for stopping
                    self.server_process = httpd
                    
                    # Update button
                    self.root.after(0, lambda: self.serve_html_button.config(
                        text=f"Stop Server (:{port})",
                        command=self.stop_server
                    ))
                    
                    # Open browser after a short delay to ensure server is ready
                    url = f"http://localhost:{port}"
                    self.root.after(500, lambda u=url: webbrowser.open(u))
                    self.root.after(0, lambda u=url: self.log(f"Opening browser: {u}"))
                    
                    # Serve until stopped
                    httpd.serve_forever()
                except Exception as e:
                    self.root.after(0, lambda err=str(e): self.log(f"Server error: {err}"))
                    self.root.after(0, lambda: self.serve_html_button.config(
                        text="Serve HTML Files",
                        command=self.serve_html_files
                    ))
                finally:
                    try:
                        os.chdir(original_dir)
                    except:
                        pass
            
            self.server_thread = threading.Thread(target=start_server, daemon=True)
            self.server_thread.start()
        
        def stop_server(self):
            """Stop the HTTP server"""
            if self.server_process:
                try:
                    self.server_process.shutdown()
                    self.server_process.server_close()
                    self.log(f"Server stopped on port {self.server_port}")
                except Exception as e:
                    self.log(f"Error stopping server: {e}")
                finally:
                    self.server_process = None
                    self.server_port = None
            
            self.serve_html_button.config(
                text="Serve HTML Files",
                command=self.serve_html_files
            )
    
    # Create and run GUI
    root = tk.Tk()
    app = GitHistoryDataflowGUI(root, repo_path, target_files)
    root.mainloop()


def main():
    """Main entry point for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyze git history for dataflow changes (safe mode)',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--repo', type=str, default=None,
                       help='Path to git repository (auto-detected from files if not specified)')
    parser.add_argument('--files', type=str, nargs='+',
                       help='Files to analyze')
    parser.add_argument('--tkinter', action='store_true',
                       help='Launch Tkinter GUI')
    
    args = parser.parse_args()
    
    # Determine repository path
    if args.repo:
        repo_path = os.path.abspath(args.repo)
    elif args.files:
        # Auto-detect repository from first file
        repo_path = find_git_repo_root(args.files[0])
        if not repo_path:
            print(f"Error: Could not find git repository containing {args.files[0]}", file=sys.stderr)
            print("Please specify --repo or ensure the file is in a git repository", file=sys.stderr)
            return
        print(f"Auto-detected repository: {repo_path}", file=sys.stderr)
    else:
        repo_path = os.path.abspath('.')
    
    # Default to GUI mode if no arguments provided
    if not args.tkinter and not args.files and not args.repo:
        args.tkinter = True
    
    if args.tkinter:
        # Launch GUI - don't create analyzer here, let GUI handle it
        launch_tkinter_gui(repo_path, args.files)
    else:
        # Command-line mode - need analyzer for CLI
        try:
            analyzer = SafeGitHistoryAnalyzer(repo_path)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            print("Please specify a valid git repository with --repo", file=sys.stderr)
            return
        
        if args.files:
            target_files = [os.path.abspath(f) for f in args.files]
        else:
            # Find Python files in repo
            result = subprocess.run(
                ['git', 'ls-files', '*.py'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            target_files = [os.path.join(repo_path, f) for f in result.stdout.strip().split('\n') if f]
        
        if not target_files:
            print("No files to analyze", file=sys.stderr)
            return
        
        def progress(msg):
            print(msg, file=sys.stderr)
        
        results = analyzer.analyze_all_commits(target_files, progress_callback=progress)
        print(f"Analyzed {len(results)} commits", file=sys.stderr)


if __name__ == '__main__':
    main()

