import chime


class SoundPlayer:
    def __init__(self, theme, quiet=False):
        chime.theme(theme)
        self.quiet = quiet

    def toggle(self):
        self.quiet = self.quiet

    def success(self):
        if not self.quiet:
            chime.success()
