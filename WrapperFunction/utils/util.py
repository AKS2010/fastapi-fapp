def to_dict(obj):
    """Convert SQLAlchemy model instance to dict, excluding internal attributes."""
    return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}