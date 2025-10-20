"""Progress bars and visual indicators."""

import time
from ui.colors import Colors


class ProgressBar:
    """Simple progress bar."""
    
    def __init__(self, total: int, width: int = 40):
        self.total = total
        self.width = width
        self.current = 0
    
    def update(self, current: int):
        """Update progress."""
        self.current = current
        self.display()
    
    def display(self):
        """Display progress bar."""
        if self.total == 0:
            percent = 0
        else:
            percent = int((self.current / self.total) * 100)
        
        filled = int((self.current / self.total) * self.width) if self.total > 0 else 0
        bar = "█" * filled + "░" * (self.width - filled)
        
        print(f"\r{Colors.OKCYAN}[{bar}] {percent}%{Colors.ENDC}", end='', flush=True)
    
    def complete(self):
        """Mark as complete."""
        self.current = self.total
        self.display()
        print()


class Spinner:
    """Loading spinner."""
    
    def __init__(self):
        self.frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.idx = 0
    
    def spin(self, message: str = ""):
        """Show next frame."""
        frame = self.frames[self.idx % len(self.frames)]
        print(f"\r{Colors.OKCYAN}{frame} {message}{Colors.ENDC}", end='', flush=True)
        self.idx += 1