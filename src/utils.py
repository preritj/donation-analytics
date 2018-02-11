import math

def get_percentile(sorted_list, p):
    """Calulates percentile using nearest-rank method
    Args:
        sorted_list (list) : sorted list
        p (float) : percentile in %
    Returns:
        p-th percentile of the sorted_list"""
    n = len(sorted_list)
    i = int(math.ceil(p / 100. * n)) - 1
    return sorted_list[i]
