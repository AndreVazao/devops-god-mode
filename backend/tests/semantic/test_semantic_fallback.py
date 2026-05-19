import sys
import os
import pytest
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.semantic import semantic_brain

def test_semantic_fallback_dot_product():
    v1 = [1.0, 2.0, 3.0]
    v2 = [4.0, 5.0, 6.0]
    # 1*4 + 2*5 + 3*6 = 4 + 10 + 18 = 32
    assert semantic_brain.dot_product(v1, v2) == 32.0

def test_semantic_fallback_embed():
    # Should return a vector of zeros of size 384 when transformers are missing
    vec = semantic_brain.embed("test")
    assert len(vec) == 384
    assert all(x == 0.0 for x in vec)

def test_semantic_search_with_data():
    # Clear index if it was persistent in memory during test run
    # Though usually pytest runs each test in a clean environment or we can mock
    semantic_brain.add_to_index('unique_test_file_xyz.py', 'print("hello world")')
    results = semantic_brain.search("hello")
    assert len(results) > 0
    # Check if the unique file is in the results
    files = [r['file'] for r in results]
    assert 'unique_test_file_xyz.py' in files
