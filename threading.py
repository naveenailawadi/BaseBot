from threading import Thread


# make a function that multithreads simply: https://www.pythontutorial.net/python-concurrency/python-threading/#:~:text=Use%20the%20Python%20threading%20module%20to%20create%20a%20multi%2Dthreaded,complete%20in%20the%20main%20thread.
def multithread(function, arg_tuples, max_threads):
    # create a bunch of threads
    threads = [Thread(target=function, args=arg_tuple)
               for arg_tuple in arg_tuples]

    # loop until threads are finished
    thread_completion_count = 0
    total_threads = len(threads)

    # this allows the threading to work as a pool
    while thread_completion_count < total_threads:
        # keep track of new threads
        new_threads = []

        # group in batches of the max threads
        for i in range(max_threads):
            try:
                # get the new thread
                new_thread = threads[thread_completion_count]

                # start the thread on the correct index until there are no more
                new_thread.start()

                # add the thread to the list of new threads
                new_threads.append(new_thread)
            except IndexError:
                # break when there are no more threads
                break

            # increment the thread completion count
            thread_completion_count += 1

        # join all the new threads
        for thread in new_threads:
            thread.join()
