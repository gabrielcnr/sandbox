import concurrent.futures
import time
from multiprocessing import get_context

PROBLEM = range(100)  # problem size

IO_SECONDS = 1  # per problem iteration/part
CPU_SECONDS = 1  # per problem iteration/part


def download_some_data(i):
    print(f'Downloading {i}')
    time.sleep(IO_SECONDS)  # Simulates I/O bound operation; releases the GIL
    return i * 2


def process_some_data(data):
    print(f'Processing {data}')
    for _ in range(CPU_SECONDS):
        sum(range(int(1e8)))  # CPU-intensive; takes ~ 1s

    return data * 10


def download_data(i):
    data = download_some_data(i)  # this represents your IO-bound tasks
    return data


def process_data(data):
    result = process_some_data(data)  # this represents your CPU-bound tasks
    return result


def download_and_process_data(i):
    data = download_data(i)
    processed_data = process_data(data)
    return processed_data


def main():
    results = [download_and_process_data(i) for i in PROBLEM]
    for result in results:
        print(result)


def main_naive_parallel_threads():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(download_and_process_data, PROBLEM)

    for result in results:
        print(result)


def main_naive_parallel_processes():
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = executor.map(download_and_process_data, PROBLEM)

    for result in results:
        print(result)


def main_parallel_pipeline():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Start the load operations and mark each future with its URL
        future_to_data = {executor.submit(download_data, i): i for i in PROBLEM}
        mp_context = get_context('forkserver')
        with concurrent.futures.ProcessPoolExecutor(mp_context=mp_context) as process_executor:

            process_future_to_processed_data = {}

            for future in concurrent.futures.as_completed(future_to_data):
                data = future.result()
                # print('Data {} has been downloaded. Now processing...'.format(future_to_data[future]))
                process_future = process_executor.submit(process_data, data)

                process_future_to_processed_data[process_future] = data  # should keep the original arg?

            print('Sent all to processing...')

        for process_future in concurrent.futures.as_completed(process_future_to_processed_data):
            print('->', process_future.result(), flush=True)


def main_parallel_pipeline_preserving_order():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Start the load operations and mark each future with its URL
        future_to_data = {executor.submit(download_data, i): i for i in PROBLEM}
        with concurrent.futures.ProcessPoolExecutor() as process_executor:

            process_future_to_processed_data = {}

            for future in concurrent.futures.as_completed(future_to_data):
                data = future.result()

                args = future_to_data[future]  # or enumeration index?

                # print('Data {} has been downloaded. Now processing...'.format(args))
                process_future = process_executor.submit(process_data, data)

                process_future_to_processed_data[process_future] = (args, data)

        results = [None] * len(process_future_to_processed_data)

        for process_future in concurrent.futures.as_completed(process_future_to_processed_data):
            args, data = process_future_to_processed_data[process_future]
            # args is index here
            results[args] = process_future.result()

        for result in results:
            print(result)


if __name__ == "__main__":
    # main()
    # main_naive_parallel_threads()
    # main_naive_parallel_processes()
    main_parallel_pipeline()
    # main_parallel_pipeline_preserving_order()