def has_ai():
    try:
        import openai  # noqa

        return True
    except ImportError:
        return False
