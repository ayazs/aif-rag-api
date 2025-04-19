"""
Pytest configuration and fixtures.
"""

def pytest_addoption(parser):
    """Add command line options."""
    parser.addoption(
        "--use-real-pinecone",
        action="store_true",
        default=False,
        help="Use real Pinecone client instead of mocks"
    ) 