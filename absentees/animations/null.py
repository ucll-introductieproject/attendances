from absentees.animations import Animation


class NullAnimation(Animation):
    def tick(self, elapsed_seconds):
        return 0

