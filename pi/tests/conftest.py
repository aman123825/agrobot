"""Make the pi/ package root importable exactly as the modules expect."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
