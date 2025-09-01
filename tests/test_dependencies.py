#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FridAPK - Unit tests for dependencies checker
"""

import unittest
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.dependencies import DependencyChecker
from utils.logger import Logger
from exceptions import DependencyError


class TestDependencyChecker(unittest.TestCase):
    
    def setUp(self):
        self.logger = MagicMock(spec=Logger)
        self.checker = DependencyChecker(self.logger)
    
    def test_dependency_initialization(self):
        """Test that dependencies are properly initialized"""
        self.assertIn('frida', self.checker.dependencies)
        self.assertIn('apktool', self.checker.dependencies)
        self.assertEqual(self.checker.dependencies['frida'].command, 'frida')
    
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_check_dependency_success(self, mock_run, mock_which):
        """Test successful dependency check"""
        # Setup mocks
        mock_which.return_value = '/usr/bin/frida'
        mock_run.return_value = MagicMock(
            stdout='16.0.1', stderr='', returncode=0
        )
        
        # Test
        is_satisfied, message = self.checker.check_dependency('frida')
        
        # Assertions
        self.assertTrue(is_satisfied)
        self.assertIn('Frida is available', message)
        mock_which.assert_called_with('frida')
        mock_run.assert_called_once()
    
    @patch('shutil.which')
    def test_check_dependency_not_found(self, mock_which):
        """Test dependency not found in PATH"""
        mock_which.return_value = None
        
        is_satisfied, message = self.checker.check_dependency('frida')
        
        self.assertFalse(is_satisfied)
        self.assertIn('not found in PATH', message)
    
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_check_dependency_with_output_check(self, mock_run, mock_which):
        """Test dependency with output content check"""
        mock_which.return_value = '/usr/bin/keytool'
        mock_run.return_value = MagicMock(
            stdout='Key and Certificate Management Tool',
            stderr='', returncode=0
        )
        
        is_satisfied, message = self.checker.check_dependency('keytool')
        
        self.assertTrue(is_satisfied)
        self.assertIn('Keytool is available', message)
    
    def test_ensure_dependencies_success(self):
        """Test ensure_dependencies with all deps satisfied"""
        with patch.object(self.checker, 'check_dependency') as mock_check:
            mock_check.return_value = (True, 'Available')
            
            result = self.checker.ensure_dependencies(['frida'])
            
            self.assertTrue(result)
    
    def test_ensure_dependencies_failure(self):
        """Test ensure_dependencies with missing deps"""
        with patch.object(self.checker, 'check_dependency') as mock_check:
            mock_check.return_value = (False, 'Not found')
            
            with self.assertRaises(DependencyError):
                self.checker.ensure_dependencies(['frida'])


if __name__ == '__main__':
    unittest.main()
