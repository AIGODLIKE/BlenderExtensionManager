#!/usr/bin/env python3
import asyncio
import time
from multiprocessing import Manager
from queue import Empty, Queue
from typing import Callable, Generator

from nicegui import app, background_tasks, run, ui


class Worker:

    def __init__(self, ui_element, ui_log:ui.log=None) -> None:
        self._queue: Queue
        self.progress: float = 0.0  # use for ui.linear_progress
        self.info: str = ''  # use for ui.notify
        self.error: str = ''  # use for ui.notify
        self.text: str = ''  # use for display

        self.ui_element = ui_element

        self.init: bool = False
        self.is_finished: bool = False
        self.is_running: bool = False
        self.is_cancel = False
        self.ui_log = ui_log

        app.on_startup(self._create_queue)

    async def run(self, func: Callable[..., Generator[dict, None, None]]) -> None:
        self.init = True
        self.task_main = background_tasks.create(run.cpu_bound(self._run_generator, func, self._queue))
        self.task_callback = background_tasks.create(self._consume_queue())

    @staticmethod
    def _run_generator(func: Callable[..., Generator[dict, None, None]], queue: Queue) -> None:
        for result in func():
            queue.put(result)
        # queue.put({'progress': 1.0, 'info': 'Done'})

    def _create_queue(self) -> None:
        self._queue = Manager().Queue()

    async def _consume_queue(self) -> None:
        self.is_running = True
        self.progress = 0.0

        while self.progress < 1.0:
            try:
                msg = self._queue.get_nowait()
            except Empty:
                await asyncio.sleep(0.1)
                continue
            self.progress = msg['progress']
            self.text = msg.get('text', '')
            if self.ui_log:
                self.ui_log.push(self.text)

            # notify
            if info := msg.get('info'):
                self.info = info
                with self.ui_element:
                    if self.progress == 1:
                        ui.notify(info, type='positive')
                    else:
                        ui.notify(info)
            elif error := msg.get('error'):
                self.error = error
                with  self.ui_element:
                    ui.notify(error, close_button='确认', multi_line=True, type='negative')

        if self.ui_log: self.ui_log.push('Done')

        self.is_running = False
        self.is_finished = True

    def cancel(self) -> None:
        self.task_main.cancel()
        self.task_callback.cancel()
        self.is_cancel = True
        self.is_running = False


# test
def heavy_computation() -> Generator[dict, None, None]:
    n = 50
    for i in range(n):
        time.sleep(0.1)
        yield {
            'progress': i / n,
            'info': 'test',
            'error': 'error'
        }

# worker = Worker()
#
#
# @ui.page('/')
# def main_page():
#     ui.button('compute', on_click=lambda: worker.run(heavy_computation))
#     ui.linear_progress().props('instant-feedback') \
#         .bind_value_from(worker, 'progress') \
#         .bind_visibility_from(worker, 'is_running')
#
#
# ui.run(native=True)
