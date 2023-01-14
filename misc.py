import time


def timer(func):
    """
    Add this to a function as a decorator to measure the time taken to run the function
    """
    def wrapper(*args, **kwargs):
        time_before = time.perf_counter()
        ret = func(*args, **kwargs)
        print(f"Time taken: {time.perf_counter() - time_before}")
        return ret

    return wrapper
