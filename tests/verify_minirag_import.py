try:
    import minirag
    print("Successfully imported minirag")
    print(f"MiniRAG location: {minirag.__file__}")
except ImportError as e:
    print(f"Failed to import minirag: {e}")
    exit(1)
