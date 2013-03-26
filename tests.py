#!/usr/bin/env python
import logging
import unittest

from kuyruk import Kuyruk, Task, Queue


# This global variable will be checked to determine if the tasks have run.
called = False


# These 2 functions below needs to be module level in order that kuyruk
# to determine their fully qualified name.
kuyruk = Kuyruk()
@kuyruk.task
def print_task(message):
    global called
    called = True
    print message

kuyruk2 = Kuyruk()
@kuyruk2.task(queue='another_queue')
def print_task2(message):
    global called
    called = True
    print message


def run_kuyruk(kuyruk, max_tasks=1):
    """Runs in same thread"""
    kuyruk.max_tasks = max_tasks
    kuyruk.run()


class KuyrukTestCase(unittest.TestCase):

    def setUp(self):
        global called
        called = False

        # Clear messages in default queue
        kuyruk = Kuyruk()
        Queue(kuyruk.queue, kuyruk.connection.channel()).delete()

    def test_task_decorator(self):
        # Decorator without args
        self.assertIsInstance(print_task, Task)
        # Decorator with args
        self.assertIsInstance(print_task2, Task)

    def test_simple_task(self):
        print_task('hello world')  # sends task
        run_kuyruk(kuyruk)
        self.assertEqual(called, True)

    def test_another_queue(self):
        # Clear another_queue
        Queue('another_queue', kuyruk2.connection.channel()).delete()

        print_task2('hello world')
        kuyruk2.queue = 'another_queue'
        run_kuyruk(kuyruk2)
        self.assertEqual(called, True)


if __name__ == '__main__':
    logging.getLogger('pika').setLevel(logging.WARNING)
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
