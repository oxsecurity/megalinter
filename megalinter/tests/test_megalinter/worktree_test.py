#!/usr/bin/env python3
"""
Unit tests for Git worktree handling in MegaLinter

"""
import os
import tempfile
import unittest
from unittest.mock import MagicMock, Mock, patch

import git

from megalinter import Megalinter


class worktree_test(unittest.TestCase):
    """Test Git worktree detection and error handling"""

    def test_is_git_worktree_detection_for_regular_repo(self):
        """Test that a regular repository is NOT detected as a worktree"""
        # Create a mock repo that represents a regular repository
        mock_repo = Mock()
        mock_repo.git_dir = "/path/to/repo/.git"
        mock_repo.working_dir = "/path/to/repo"
        
        # Create a temporary directory to simulate a regular repo
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = os.path.join(tmpdir, ".git")
            os.makedirs(git_dir)
            
            mock_repo.working_dir = tmpdir
            mock_repo.git_dir = git_dir
            
            # Create MegaLinter instance
            megalinter = Megalinter({"workspace": tmpdir, "cli": False})
            
            # Test worktree detection
            is_worktree = megalinter._is_git_worktree(mock_repo)
            
            self.assertFalse(
                is_worktree,
                "Regular repository should NOT be detected as a worktree"
            )

    def test_is_git_worktree_detection_for_worktree_file(self):
        """Test that a worktree (with .git as a file) IS detected"""
        # Create a mock repo that represents a worktree
        mock_repo = Mock()
        mock_repo.git_dir = "/path/to/repo/.git/worktrees/my-worktree"
        
        # Create a temporary directory to simulate a worktree
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .git as a FILE (worktree indicator)
            git_file = os.path.join(tmpdir, ".git")
            with open(git_file, "w") as f:
                f.write("gitdir: /path/to/repo/.git/worktrees/my-worktree\n")
            
            mock_repo.working_dir = tmpdir
            
            # Create MegaLinter instance
            megalinter = Megalinter({"workspace": tmpdir, "cli": False})
            
            # Test worktree detection
            is_worktree = megalinter._is_git_worktree(mock_repo)
            
            self.assertTrue(
                is_worktree,
                "Worktree (with .git file) should be detected as a worktree"
            )

    def test_is_git_worktree_detection_by_path(self):
        """Test that a worktree is detected by 'worktrees' in git_dir path"""
        # Create a mock repo with 'worktrees' in the path
        mock_repo = Mock()
        mock_repo.git_dir = "/path/to/repo/.git/worktrees/my-worktree"
        mock_repo.working_dir = "/path/to/worktree"
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_repo.working_dir = tmpdir
            git_dir_path = os.path.join(tmpdir, ".git")
            os.makedirs(git_dir_path)
            
            # Override git_dir to have 'worktrees' in path
            mock_repo.git_dir = "/main/.git/worktrees/test"
            
            # Create MegaLinter instance
            megalinter = Megalinter({"workspace": tmpdir, "cli": False})
            
            # Test worktree detection
            is_worktree = megalinter._is_git_worktree(mock_repo)
            
            self.assertTrue(
                is_worktree,
                "Worktree should be detected by 'worktrees' in git_dir path"
            )

    @patch("git.Repo")
    def test_git_fetch_error_handling_in_worktree(self, mock_repo_class):
        """Test that git fetch errors are properly handled in worktrees"""
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .git as a file to simulate worktree
            git_file = os.path.join(tmpdir, ".git")
            with open(git_file, "w") as f:
                f.write("gitdir: /main/.git/worktrees/test\n")
            
            # Mock the Repo object
            mock_repo_instance = Mock()
            mock_repo_instance.git_dir = "/main/.git/worktrees/test"
            mock_repo_instance.working_dir = tmpdir
            mock_repo_instance.refs = []
            
            # Mock git.fetch to raise GitCommandError
            mock_repo_instance.git.fetch.side_effect = git.exc.GitCommandError(
                "git fetch",
                128,
                stderr="fatal: not a git repository: /host/path/.git/worktrees/test"
            )
            
            mock_repo_class.return_value = mock_repo_instance
            
            # Create MegaLinter instance
            megalinter = Megalinter({"workspace": tmpdir, "cli": False})
            
            # Try to list files using git diff - should not raise an exception
            try:
                # This should handle the error gracefully
                files = megalinter.list_files_git_diff()
                # If we get here, the error was handled
                self.assertTrue(
                    True,
                    "Git fetch error should be caught and handled"
                )
            except git.exc.GitCommandError:
                self.fail(
                    "GitCommandError should be caught and handled, not raised"
                )

    def test_worktree_detection_handles_exceptions(self):
        """Test that worktree detection handles exceptions gracefully"""
        # Create a mock repo that raises an exception
        mock_repo = Mock()
        mock_repo.git_dir = Mock(side_effect=Exception("Test exception"))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create MegaLinter instance
            megalinter = Megalinter({"workspace": tmpdir, "cli": False})
            
            # Test worktree detection - should not raise exception
            try:
                is_worktree = megalinter._is_git_worktree(mock_repo)
                # Should return False when exception occurs
                self.assertFalse(
                    is_worktree,
                    "Should return False when exception occurs during detection"
                )
            except Exception:
                self.fail(
                    "Worktree detection should handle exceptions gracefully"
                )


if __name__ == "__main__":
    unittest.main()

