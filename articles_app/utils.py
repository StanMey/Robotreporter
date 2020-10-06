
def is_view_only(user):
    """[summary]

    Args:
        user ([type]): [description]

    Returns:
        [type]: [description]
    """
    return user.groups.filter(name='view_only').exists()