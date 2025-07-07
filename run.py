from __future__ import absolute_import, unicode_literals

from pacer import PACER

if __name__ == "__main__":
    pacer: PACER = PACER()

    pacer.init_workers()
    pacer.start_consumers()
    pacer.main_background_loop()
