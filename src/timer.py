import time

class Timer:
    def __init__(self):
        self.recordings = []

    def record(self):
        t = time.time() * 1000.0
        if len(self.recordings) > 0:
            i = len(self.recordings) - 1
            self.recordings[i] = t - self.recordings[i]
        self.recordings.append(t)

    def show(self):
        if len(self.recordings) > 0:
            t = time.time() * 1000.0
            i = len(self.recordings) - 1
            self.recordings[i] = t - self.recordings[i]

            for p, t in enumerate(self.recordings): print(f"{p}: {t:.6}ms",end=' ')
            print()
            return tuple(self.recordings)