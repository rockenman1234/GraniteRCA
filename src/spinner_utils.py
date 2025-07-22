"""
ASCII Spinner utility for showing progress during long-running operations.

This module provides a simple ASCII spinner that can run alongside tqdm progress bars
to indicate that the program is active and not hung.

SPDX-License-Identifier: Apache-2.0
"""

import threading
import time
import sys
from typing import Optional

class ASCIISpinner:
    """
    ASCII spinner that runs in a separate thread to show activity.
    Can be used alongside tqdm progress bars.
    """
    
    # Different spinner styles
    SPINNERS = {
        'classic': ['|', '/', '-', '\\'],
        'dots': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
        'braille': ['⠁', '⠂', '⠄', '⡀', '⢀', '⠠', '⠐', '⠈'],
        'arrows': ['↑', '↗', '→', '↘', '↓', '↙', '←', '↖'],
        'simple': ['.', 'o', 'O', 'o'],
        'moon': ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘']
    }
    
    def __init__(self, style: str = 'classic', speed: float = 0.1, prefix: str = ""):
        """
        Initialize the spinner.
        
        Args:
            style: Spinner style ('classic', 'dots', 'braille', 'arrows', 'simple', 'moon')
            speed: Animation speed in seconds between frames
            prefix: Optional prefix text to show before the spinner
        """
        self.frames = self.SPINNERS.get(style, self.SPINNERS['classic'])
        self.speed = speed
        self.prefix = prefix
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.current_frame = 0
    
    def _spin(self):
        """Internal method that runs the spinner animation."""
        while self.running:
            frame = self.frames[self.current_frame % len(self.frames)]
            # Use carriage return to overwrite the same line
            sys.stdout.write(f'\r{self.prefix}{frame} ')
            sys.stdout.flush()
            self.current_frame += 1
            time.sleep(self.speed)
    
    def start(self):
        """Start the spinner in a separate thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._spin, daemon=True)
            self.thread.start()
    
    def stop(self):
        """Stop the spinner and clear the line."""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=1.0)
            # Clear the spinner line
            sys.stdout.write('\r' + ' ' * (len(self.prefix) + 5) + '\r')
            sys.stdout.flush()
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()

def spinner_context(style: str = 'classic', speed: float = 0.1, prefix: str = ""):
    """
    Convenience function to create a spinner context manager.
    
    Usage:
        with spinner_context("Working", style='dots'):
            # Long running operation
            time.sleep(5)
    """
    return ASCIISpinner(style=style, speed=speed, prefix=prefix)
