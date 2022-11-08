from threading import Thread
import eel
import os


# set the default at double the cpus
DEFAULT_MAX_THREADS = os.cpu_count()

# make a function that multithreads simply: https://www.pythontutorial.net/python-concurrency/python-threading/#:~:text=Use%20the%20Python%20threading%20module%20to%20create%20a%20multi%2Dthreaded,complete%20in%20the%20main%20thread.
# default check all the threads every 5 seconds (this is a bot after all)


def multithread(function, arg_tuples, max_threads=DEFAULT_MAX_THREADS, check_increment=5):
    # create a bunch of threads
    threads = [Thread(target=function, args=arg_tuple)
               for arg_tuple in arg_tuples]
    thread_lives = [False for thread in threads]

    # loop until threads are finished
    thread_start_count = 0
    active_threads = 0
    total_threads = len(threads)

    while (thread_start_count < total_threads) or (active_threads != 0):
        # start as many threads as possible if not all the threads have been started
        if (thread_start_count < total_threads):
            for i in range(min(max_threads - active_threads, total_threads - thread_start_count)):
                threads[thread_start_count].start()

                # note that the thread is active
                thread_lives[thread_start_count] = True

                # increment the thread start count
                thread_start_count += 1

        # check if any of the threads have finished --> set them to inactive
        for i in range(len(thread_lives)):
            if not threads[i].is_alive():
                thread_lives[i] = False

        # wait a check increment
        eel.sleep(check_increment)

        # check how many threads are done
        active_threads = len([life for life in thread_lives if life])


def batch_thread(function, arg_tuples, max_threads):
    # create a bunch of threads
    threads = [Thread(target=function, args=arg_tuple)
               for arg_tuple in arg_tuples]

    # loop until threads are finished
    thread_start_count = 0
    total_threads = len(threads)

    # this allows the threading to work as a pool
    while thread_start_count < total_threads:
        # keep track of new threads
        new_threads = []

        # group in batches of the max threads
        for i in range(max_threads):
            try:
                # get the new thread
                new_thread = threads[thread_start_count]

                # start the thread on the correct index until there are no more
                new_thread.start()

                # add the thread to the list of new threads
                new_threads.append(new_thread)
            except IndexError:
                # break when there are no more threads
                break

            # increment the thread completion count
            thread_start_count += 1

        # join all the new threads
        for thread in new_threads:
            thread.join()
